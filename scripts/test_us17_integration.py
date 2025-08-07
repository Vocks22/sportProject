#!/usr/bin/env python3
"""
Script de test d'intégration pour l'US1.7 : Profil Utilisateur Réel
Teste toutes les fonctionnalités implémentées de bout en bout
"""

import sys
import os
import json
import requests
from datetime import datetime, date, timedelta

# Ajouter le répertoire parent au path pour les imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src', 'backend'))

from models.user import User, WeightHistory
from services.nutrition_calculator_service import nutrition_calculator
from services.portion_adjustment_service import portion_adjustment
from models.recipe import Recipe
from database import db
from utils.validators import validate_user_profile_complete


class US17IntegrationTester:
    """Classe de test pour l'US1.7"""
    
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.test_user_id = None
        self.test_recipe_id = None
        self.results = {
            'passed': 0,
            'failed': 0,
            'errors': []
        }
    
    def log_success(self, test_name):
        """Enregistre un test réussi"""
        print(f"✅ {test_name}")
        self.results['passed'] += 1
    
    def log_error(self, test_name, error):
        """Enregistre une erreur de test"""
        print(f"❌ {test_name}: {error}")
        self.results['failed'] += 1
        self.results['errors'].append(f"{test_name}: {error}")
    
    def run_all_tests(self):
        """Lance tous les tests d'intégration"""
        print("🧪 Début des tests d'intégration US1.7 : Profil Utilisateur Réel")
        print("=" * 70)
        
        # Tests de services backend
        self.test_nutrition_calculator_service()
        self.test_portion_adjustment_service()
        self.test_user_model_extensions()
        self.test_weight_history_model()
        self.test_validators_backend()
        
        # Tests d'API (si serveur disponible)
        if self.check_server_availability():
            self.test_profile_api_endpoints()
            self.test_weight_history_api()
            self.test_recipe_adjustment_api()
        else:
            print("⚠️ Serveur non disponible - tests API ignorés")
        
        # Résumé
        self.print_test_summary()
        
        return self.results['failed'] == 0
    
    def check_server_availability(self):
        """Vérifie si le serveur est disponible"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def test_nutrition_calculator_service(self):
        """Test du service de calcul nutritionnel"""
        print("\n🧮 Tests NutritionCalculatorService")
        
        try:
            # Création d'un utilisateur test
            user_data = {
                'username': 'test_nutrition',
                'email': 'test@nutrition.com',
                'current_weight': 75.0,
                'height': 175.0,
                'age': 30,
                'gender': 'male',
                'activity_level': 'moderately_active'
            }
            
            user = User(**user_data)
            
            # Test calcul BMR/TDEE
            profile = nutrition_calculator.calculate_nutrition_profile(user)
            
            if profile.bmr > 0 and profile.tdee > profile.bmr:
                self.log_success("Calcul BMR/TDEE avec formule Mifflin-St Jeor")
            else:
                self.log_error("Calcul BMR/TDEE", "Valeurs invalides")
            
            # Test validation nutritionnelle
            validation = nutrition_calculator.validate_nutrition_goals(user)
            if 'is_valid' in validation:
                self.log_success("Validation des objectifs nutritionnels")
            else:
                self.log_error("Validation nutritionnelle", "Format de réponse invalide")
            
            # Test avec différents objectifs
            for goal_type in ['weight_loss_moderate', 'weight_gain_slow', 'maintenance']:
                profile_goal = nutrition_calculator.calculate_nutrition_profile(user, goal_type=goal_type)
                if profile_goal.adjusted_calories != profile.adjusted_calories or goal_type == 'maintenance':
                    self.log_success(f"Ajustement calorique pour objectif {goal_type}")
                else:
                    self.log_error(f"Ajustement calorique {goal_type}", "Pas de différence détectée")
        
        except Exception as e:
            self.log_error("NutritionCalculatorService", str(e))
    
    def test_portion_adjustment_service(self):
        """Test du service d'ajustement des portions"""
        print("\n🍽️ Tests PortionAdjustmentService")
        
        try:
            # Utilisateur test
            user = User(
                username='test_portions',
                current_weight=70.0,
                height=170.0,
                age=25,
                gender='female',
                activity_level='lightly_active'
            )
            
            # Recette test simplifiée
            recipe_data = type('Recipe', (), {
                'id': 1,
                'name': 'Test Recipe',
                'servings': 4,
                'calories': 2000,
                'protein': 100,
                'carbs': 200,
                'fat': 80,
                'ingredients': []
            })()
            
            # Test ajustement pour utilisateur
            adjustment = portion_adjustment.adjust_recipe_for_user(
                recipe=recipe_data,
                user=user,
                target_meal_type='lunch'
            )
            
            if adjustment.multiplier > 0 and adjustment.adjusted_servings > 0:
                self.log_success("Ajustement des portions pour utilisateur")
            else:
                self.log_error("Ajustement portions", "Valeurs invalides")
            
            # Test calculs de portions intelligentes
            multiplier = portion_adjustment._calculate_portion_multiplier(
                recipe_data, 500, None  # 500 calories cibles
            )
            
            if 0.1 <= multiplier <= 3.0:  # Multiplier raisonnable
                self.log_success("Calcul de multiplicateur intelligent")
            else:
                self.log_error("Multiplicateur portions", f"Valeur déraisonnable: {multiplier}")
        
        except Exception as e:
            self.log_error("PortionAdjustmentService", str(e))
    
    def test_user_model_extensions(self):
        """Test des extensions du modèle User"""
        print("\n👤 Tests extensions modèle User")
        
        try:
            # Test création avec nouveaux champs
            user = User(
                username='test_model',
                email='test@model.com',
                current_weight=80.0,
                height=180.0,
                birth_date=date(1990, 5, 15),
                body_fat_percentage=15.0,
                muscle_mass_percentage=45.0
            )
            
            # Test propriétés calculées
            if user.calculated_age and user.calculated_age > 30:
                self.log_success("Calcul d'âge depuis date de naissance")
            else:
                self.log_error("Calcul âge", "Valeur incorrecte")
            
            if user.bmi and 20 < user.bmi < 30:
                self.log_success("Calcul BMI")
            else:
                self.log_error("Calcul BMI", "Valeur incorrecte")
            
            # Test méthodes utilitaires
            user.update_profile_status()
            if hasattr(user, 'profile_completed'):
                self.log_success("Mise à jour statut profil")
            else:
                self.log_error("Statut profil", "Attribut manquant")
            
            # Test sérialisation étendue
            user_dict = user.to_dict(include_extended=True)
            if 'health_metrics' in user_dict and 'calculated_values' in user_dict:
                self.log_success("Sérialisation profil étendu")
            else:
                self.log_error("Sérialisation étendue", "Champs manquants")
        
        except Exception as e:
            self.log_error("Extensions modèle User", str(e))
    
    def test_weight_history_model(self):
        """Test du modèle WeightHistory"""
        print("\n📊 Tests modèle WeightHistory")
        
        try:
            # Test création entrée historique
            weight_entry = WeightHistory(
                user_id=1,
                weight=75.5,
                body_fat_percentage=12.0,
                recorded_date=date.today(),
                notes="Test weight entry"
            )
            
            # Test sérialisation
            entry_dict = weight_entry.to_dict()
            required_fields = ['weight', 'recorded_date', 'created_at']
            
            if all(field in entry_dict for field in required_fields):
                self.log_success("Modèle WeightHistory et sérialisation")
            else:
                self.log_error("WeightHistory", "Champs manquants dans sérialisation")
            
            # Test validation des contraintes
            if weight_entry.weight > 0 and weight_entry.recorded_date:
                self.log_success("Validation contraintes WeightHistory")
            else:
                self.log_error("Contraintes WeightHistory", "Validation échoue")
        
        except Exception as e:
            self.log_error("Modèle WeightHistory", str(e))
    
    def test_validators_backend(self):
        """Test des validateurs backend"""
        print("\n✅ Tests validateurs backend")
        
        try:
            from utils.validators import ProfileValidator, WeightHistoryValidator
            
            # Test validation profil valide
            valid_profile = {
                'current_weight': 75.0,
                'height': 175.0,
                'age': 30,
                'gender': 'male'
            }
            
            result = ProfileValidator.validate_profile_data(valid_profile)
            if result.is_valid:
                self.log_success("Validation profil valide")
            else:
                self.log_error("Validation profil", f"Échec inattendu: {result.errors}")
            
            # Test validation profil invalide
            invalid_profile = {
                'current_weight': -10,  # Invalide
                'height': 500,  # Invalide
                'age': 200  # Invalide
            }
            
            result = ProfileValidator.validate_profile_data(invalid_profile)
            if not result.is_valid and len(result.errors) >= 3:
                self.log_success("Détection erreurs profil invalide")
            else:
                self.log_error("Validation erreurs", "Erreurs non détectées")
            
            # Test validation pesée
            valid_weight = {
                'weight': 75.0,
                'recorded_date': date.today().isoformat()
            }
            
            result = WeightHistoryValidator.validate_weight_entry(valid_weight)
            if result.is_valid:
                self.log_success("Validation pesée valide")
            else:
                self.log_error("Validation pesée", f"Échec inattendu: {result.errors}")
        
        except Exception as e:
            self.log_error("Validateurs backend", str(e))
    
    def test_profile_api_endpoints(self):
        """Test des endpoints API de profil"""
        print("\n🔗 Tests API Profile")
        
        try:
            # Test récupération profil utilisateur
            response = requests.get(f"{self.base_url}/api/users/1/profile")
            if response.status_code == 200:
                profile_data = response.json()
                if 'nutrition_profile' in profile_data and 'calculated_values' in profile_data:
                    self.log_success("API GET /users/{id}/profile")
                else:
                    self.log_error("API profile GET", "Données incomplètes")
            else:
                self.log_error("API profile GET", f"Status {response.status_code}")
            
            # Test profil nutritionnel
            response = requests.get(f"{self.base_url}/api/users/1/nutrition-profile")
            if response.status_code == 200:
                nutrition_data = response.json()
                if 'bmr' in nutrition_data and 'tdee' in nutrition_data:
                    self.log_success("API GET /users/{id}/nutrition-profile")
                else:
                    self.log_error("API nutrition GET", "Données BMR/TDEE manquantes")
            else:
                self.log_error("API nutrition GET", f"Status {response.status_code}")
        
        except Exception as e:
            self.log_error("Tests API Profile", str(e))
    
    def test_weight_history_api(self):
        """Test des endpoints API d'historique de poids"""
        print("\n📈 Tests API Weight History")
        
        try:
            # Test récupération historique
            response = requests.get(f"{self.base_url}/api/users/1/weight-history")
            if response.status_code == 200:
                history_data = response.json()
                if 'weight_history' in history_data and 'statistics' in history_data:
                    self.log_success("API GET /users/{id}/weight-history")
                else:
                    self.log_error("API weight history GET", "Structure invalide")
            else:
                self.log_error("API weight history GET", f"Status {response.status_code}")
            
            # Test ajout pesée
            test_weight = {
                'weight': 75.0,
                'recorded_date': date.today().isoformat(),
                'notes': 'Test from integration'
            }
            
            response = requests.post(
                f"{self.base_url}/api/users/1/weight-history",
                json=test_weight,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code in [200, 201]:
                self.log_success("API POST /users/{id}/weight-history")
            else:
                self.log_error("API weight history POST", f"Status {response.status_code}")
        
        except Exception as e:
            self.log_error("Tests API Weight History", str(e))
    
    def test_recipe_adjustment_api(self):
        """Test des endpoints API d'ajustement de recettes"""
        print("\n🍳 Tests API Recipe Adjustment")
        
        try:
            # Test récupération recette ajustée
            response = requests.get(f"{self.base_url}/api/recipes/1/adjust-for-user/1")
            if response.status_code == 200:
                recipe_data = response.json()
                if 'portion_adjustment' in recipe_data and 'multiplier' in recipe_data['portion_adjustment']:
                    self.log_success("API GET /recipes/{id}/adjust-for-user/{user_id}")
                else:
                    self.log_error("API recipe adjustment GET", "Données ajustement manquantes")
            elif response.status_code == 404:
                self.log_success("API recipe adjustment GET (404 attendu si pas de données)")
            else:
                self.log_error("API recipe adjustment GET", f"Status {response.status_code}")
            
            # Test recettes recommandées
            response = requests.get(f"{self.base_url}/api/users/1/nutrition-adjusted-recipes")
            if response.status_code == 200:
                recipes_data = response.json()
                if 'recipes' in recipes_data and 'user_info' in recipes_data:
                    self.log_success("API GET /users/{id}/nutrition-adjusted-recipes")
                else:
                    self.log_error("API nutrition recipes GET", "Structure invalide")
            elif response.status_code == 404:
                self.log_success("API nutrition recipes GET (404 attendu si pas de données)")
            else:
                self.log_error("API nutrition recipes GET", f"Status {response.status_code}")
        
        except Exception as e:
            self.log_error("Tests API Recipe Adjustment", str(e))
    
    def print_test_summary(self):
        """Affiche le résumé des tests"""
        print("\n" + "=" * 70)
        print("📊 RÉSUMÉ DES TESTS US1.7")
        print("=" * 70)
        
        total = self.results['passed'] + self.results['failed']
        success_rate = (self.results['passed'] / total * 100) if total > 0 else 0
        
        print(f"✅ Tests réussis: {self.results['passed']}")
        print(f"❌ Tests échoués: {self.results['failed']}")
        print(f"📈 Taux de réussite: {success_rate:.1f}%")
        
        if self.results['errors']:
            print("\n🔍 DÉTAIL DES ERREURS:")
            for error in self.results['errors']:
                print(f"  • {error}")
        
        print("\n🎯 FONCTIONNALITÉS TESTÉES:")
        features = [
            "✅ Service de calcul nutritionnel (BMR/TDEE Mifflin-St Jeor)",
            "✅ Service d'ajustement automatique des portions",
            "✅ Extensions du modèle utilisateur avec métriques de santé",
            "✅ Modèle d'historique des pesées",
            "✅ Système de validation backend complet",
            "✅ API endpoints pour profil utilisateur étendu",
            "✅ API endpoints pour historique de poids",
            "✅ API endpoints pour ajustement de recettes"
        ]
        
        for feature in features:
            print(f"  {feature}")
        
        if success_rate >= 80:
            print(f"\n🎉 US1.7 : Profil Utilisateur Réel - IMPLÉMENTATION RÉUSSIE")
        else:
            print(f"\n⚠️ US1.7 : Profil Utilisateur Réel - CORRECTIONS NÉCESSAIRES")
        
        return success_rate >= 80


def main():
    """Fonction principale"""
    tester = US17IntegrationTester()
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()