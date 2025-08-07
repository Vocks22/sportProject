import pytest
import json
from flask import Flask
from flask_testing import TestCase
import sys
import os
from datetime import datetime, date, timedelta

# Ajouter le chemin src/backend au path pour les imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src/backend'))

from database import db
from models.meal_plan import MealPlan, ShoppingList
from models.recipe import Recipe
from models.ingredient import Ingredient
from models.user import User
from routes.meal_plans import meal_plans_bp

class TestMealPlansAPI(TestCase):
    
    def create_app(self):
        """Créer l'application Flask pour les tests"""
        app = Flask(__name__)
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        db.init_app(app)
        app.register_blueprint(meal_plans_bp, url_prefix='/api')
        
        return app
    
    def setUp(self):
        """Configuration avant chaque test"""
        db.create_all()
        
        # Créer des ingrédients de test
        self.ingredient1 = Ingredient(
            name="Farine",
            category="grain",
            calories_per_100g=364,
            protein_per_100g=10.3,
            carbs_per_100g=76.3,
            fat_per_100g=0.9,
            unit="g"
        )
        self.ingredient2 = Ingredient(
            name="Œuf",
            category="protein",
            calories_per_100g=155,
            protein_per_100g=13.0,
            carbs_per_100g=1.1,
            fat_per_100g=11.0,
            unit="g"
        )
        
        db.session.add_all([self.ingredient1, self.ingredient2])
        db.session.commit()
        
        # Créer des recettes de test
        self.recipe1 = Recipe(
            name="Crêpes au petit-déjeuner",
            category="breakfast",
            meal_type="repas1",
            prep_time=15,
            cook_time=10,
            servings=2
        )
        self.recipe1.ingredients = [
            {"ingredient_id": 1, "name": "Farine", "quantity": 200, "unit": "g"},
            {"ingredient_id": 2, "name": "Œuf", "quantity": 100, "unit": "g"}
        ]
        self.recipe1.instructions = [
            {"step": 1, "description": "Mélanger la farine avec les œufs"},
            {"step": 2, "description": "Cuire les crêpes"}
        ]
        
        # Calculer les valeurs nutritionnelles pour recipe1
        # Farine 200g: 364*2 = 728 cal, 10.3*2 = 20.6 protein, 76.3*2 = 152.6 carbs, 0.9*2 = 1.8 fat
        # Œuf 100g: 155*1 = 155 cal, 13*1 = 13 protein, 1.1*1 = 1.1 carbs, 11*1 = 11 fat
        # Total: 883 cal, 33.6 protein, 153.7 carbs, 12.8 fat
        self.recipe1.total_calories = 883.0
        self.recipe1.total_protein = 33.6
        self.recipe1.total_carbs = 153.7
        self.recipe1.total_fat = 12.8
        
        self.recipe2 = Recipe(
            name="Salade déjeuner",
            category="lunch", 
            meal_type="repas2",
            prep_time=10,
            cook_time=0,
            servings=1
        )
        self.recipe2.ingredients = [
            {"ingredient_id": 1, "name": "Farine", "quantity": 50, "unit": "g"}
        ]
        self.recipe2.instructions = [
            {"step": 1, "description": "Préparer la salade"}
        ]
        
        # Calculer les valeurs nutritionnelles pour recipe2
        # Farine 50g: 364*0.5 = 182 cal, 10.3*0.5 = 5.15 protein, 76.3*0.5 = 38.15 carbs, 0.9*0.5 = 0.45 fat
        self.recipe2.total_calories = 182.0
        self.recipe2.total_protein = 5.15
        self.recipe2.total_carbs = 38.15
        self.recipe2.total_fat = 0.45
        
        db.session.add_all([self.recipe1, self.recipe2])
        db.session.commit()
        
        # Créer un utilisateur de test
        self.user = User(
            username="testuser",
            email="test@example.com",
            daily_calories_target=2000,
            daily_protein_target=150,
            daily_carbs_target=200,
            daily_fat_target=75
        )
        db.session.add(self.user)
        db.session.commit()
        
        # Données de test pour les plans de repas
        self.sample_meal_plan_data = {
            "user_id": str(self.user.id),
            "week_start": date.today().isoformat(),
            "meals": {
                "monday": {
                    "repas1": self.recipe1.id,
                    "repas2": self.recipe2.id
                },
                "tuesday": {
                    "repas1": self.recipe1.id
                }
            }
        }
    
    def tearDown(self):
        """Nettoyage après chaque test"""
        db.session.remove()
        db.drop_all()
    
    def test_get_meal_plans_empty(self):
        """Test de récupération des plans de repas quand aucun n'existe"""
        response = self.client.get('/api/meal-plans')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertEqual(len(data['meal_plans']), 0)
        self.assertIn('pagination', data)
        self.assertEqual(data['pagination']['total'], 0)
    
    def test_get_meal_plans_with_pagination(self):
        """Test de récupération des plans de repas avec pagination"""
        # Créer d'abord un plan de repas
        self.client.post(
            '/api/meal-plans',
            data=json.dumps(self.sample_meal_plan_data),
            content_type='application/json'
        )
        
        response = self.client.get('/api/meal-plans?page=1&per_page=10')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertEqual(len(data['meal_plans']), 1)
        self.assertIn('pagination', data)
        self.assertEqual(data['pagination']['page'], 1)
        self.assertEqual(data['pagination']['per_page'], 10)
        self.assertEqual(data['pagination']['total'], 1)
    
    def test_get_meal_plans_with_filters(self):
        """Test de récupération des plans de repas avec filtres"""
        # Créer d'abord un plan de repas
        self.client.post(
            '/api/meal-plans',
            data=json.dumps(self.sample_meal_plan_data),
            content_type='application/json'
        )
        
        # Test filtre par user_id
        response = self.client.get(f'/api/meal-plans?user_id={self.user.id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data['meal_plans']), 1)
        
        # Test filtre par user_id inexistant
        response = self.client.get('/api/meal-plans?user_id=999')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data['meal_plans']), 0)
    
    def test_create_meal_plan_success(self):
        """Test de création d'un plan de repas valide"""
        response = self.client.post(
            '/api/meal-plans',
            data=json.dumps(self.sample_meal_plan_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        
        self.assertEqual(data['user_id'], str(self.user.id))
        self.assertEqual(data['week_start'], self.sample_meal_plan_data['week_start'])
        self.assertIn('meals', data)
        self.assertIn('nutrition_summary', data)
        self.assertGreater(data['nutrition_summary']['daily_calories'], 0)
    
    def test_create_meal_plan_invalid_content_type(self):
        """Test de création d'un plan de repas sans Content-Type JSON"""
        response = self.client.post(
            '/api/meal-plans',
            data='invalid data',
            content_type='text/plain'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('Content-Type doit être application/json', data['error'])
    
    def test_create_meal_plan_missing_required_field(self):
        """Test de création d'un plan de repas avec champ obligatoire manquant"""
        invalid_data = self.sample_meal_plan_data.copy()
        del invalid_data['week_start']
        
        response = self.client.post(
            '/api/meal-plans',
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('Données invalides', data['error'])
    
    def test_create_meal_plan_invalid_meals_structure(self):
        """Test de création d'un plan de repas avec structure de repas invalide"""
        invalid_data = self.sample_meal_plan_data.copy()
        invalid_data['meals'] = {}  # Aucun repas planifié
        
        response = self.client.post(
            '/api/meal-plans',
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('Données invalides', data['error'])
    
    def test_get_meal_plan_by_id_success(self):
        """Test de récupération d'un plan de repas par ID"""
        # Créer d'abord un plan de repas
        create_response = self.client.post(
            '/api/meal-plans',
            data=json.dumps(self.sample_meal_plan_data),
            content_type='application/json'
        )
        
        plan_id = json.loads(create_response.data)['id']
        
        response = self.client.get(f'/api/meal-plans/{plan_id}')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['id'], plan_id)
        self.assertEqual(data['user_id'], str(self.user.id))
    
    def test_get_meal_plan_by_id_not_found(self):
        """Test de récupération d'un plan de repas inexistant"""
        response = self.client.get('/api/meal-plans/999')
        
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('Plan de repas non trouvé', data['error'])
    
    def test_get_meal_plan_by_id_invalid_id(self):
        """Test de récupération d'un plan de repas avec ID invalide"""
        response = self.client.get('/api/meal-plans/0')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('ID de plan invalide', data['error'])
    
    def test_update_meal_plan_success(self):
        """Test de mise à jour d'un plan de repas"""
        # Créer d'abord un plan de repas
        create_response = self.client.post(
            '/api/meal-plans',
            data=json.dumps(self.sample_meal_plan_data),
            content_type='application/json'
        )
        
        plan_id = json.loads(create_response.data)['id']
        
        update_data = {
            "meals": {
                "wednesday": {
                    "repas1": self.recipe1.id
                }
            }
        }
        
        response = self.client.put(
            f'/api/meal-plans/{plan_id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('wednesday', data['meals'])
        self.assertEqual(data['meals']['wednesday']['repas1'], self.recipe1.id)
    
    def test_update_meal_plan_not_found(self):
        """Test de mise à jour d'un plan de repas inexistant"""
        update_data = {"is_active": False}
        
        response = self.client.put(
            '/api/meal-plans/999',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('Plan de repas non trouvé', data['error'])
    
    def test_delete_meal_plan_success(self):
        """Test de suppression d'un plan de repas"""
        # Créer d'abord un plan de repas
        create_response = self.client.post(
            '/api/meal-plans',
            data=json.dumps(self.sample_meal_plan_data),
            content_type='application/json'
        )
        
        plan_id = json.loads(create_response.data)['id']
        
        response = self.client.delete(f'/api/meal-plans/{plan_id}')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('Plan de repas supprimé avec succès', data['message'])
        
        # Vérifier que le plan n'existe plus
        get_response = self.client.get(f'/api/meal-plans/{plan_id}')
        self.assertEqual(get_response.status_code, 404)
    
    def test_delete_meal_plan_not_found(self):
        """Test de suppression d'un plan de repas inexistant"""
        response = self.client.delete('/api/meal-plans/999')
        
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('Plan de repas non trouvé', data['error'])
    
    def test_generate_meal_plan_success(self):
        """Test de génération automatique d'un plan de repas"""
        generation_data = {
            "user_id": str(self.user.id),
            "week_start": date.today().isoformat(),
            "target_calories": 2000,
            "target_protein": 150,
            "meal_types_to_include": ["repas1", "repas2"]
        }
        
        response = self.client.post(
            '/api/meal-plans/generate',
            data=json.dumps(generation_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        
        self.assertIn('meal_plan', data)
        self.assertIn('generation_info', data)
        self.assertIn('target_nutrition', data['generation_info'])
        self.assertIn('actual_nutrition', data['generation_info'])
        self.assertIn('accuracy', data['generation_info'])
    
    def test_generate_meal_plan_with_user_goals(self):
        """Test de génération avec les objectifs de l'utilisateur"""
        generation_data = {
            "user_id": str(self.user.id),
            "week_start": date.today().isoformat()
        }
        
        response = self.client.post(
            '/api/meal-plans/generate',
            data=json.dumps(generation_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        
        # Vérifier que les objectifs de l'utilisateur sont utilisés
        target_nutrition = data['generation_info']['target_nutrition']
        self.assertEqual(target_nutrition['target_calories'], self.user.daily_calories_target)
        self.assertEqual(target_nutrition['target_protein'], self.user.daily_protein_target)
    
    def test_generate_shopping_list_success(self):
        """Test de génération d'une liste de courses"""
        # Créer d'abord un plan de repas
        create_response = self.client.post(
            '/api/meal-plans',
            data=json.dumps(self.sample_meal_plan_data),
            content_type='application/json'
        )
        
        plan_id = json.loads(create_response.data)['id']
        
        response = self.client.post(f'/api/meal-plans/{plan_id}/shopping-list')
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        
        self.assertEqual(data['meal_plan_id'], plan_id)
        self.assertIn('items', data)
        self.assertGreater(len(data['items']), 0)
        
        # Vérifier la structure des articles
        item = data['items'][0]
        self.assertIn('ingredient_id', item)
        self.assertIn('name', item)
        self.assertIn('quantity', item)
        self.assertIn('unit', item)
        self.assertIn('category', item)
        self.assertIn('checked', item)
    
    def test_generate_shopping_list_plan_not_found(self):
        """Test de génération de liste de courses pour un plan inexistant"""
        response = self.client.post('/api/meal-plans/999/shopping-list')
        
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('Plan de repas non trouvé', data['error'])
    
    def test_generate_shopping_list_already_exists(self):
        """Test de génération de liste de courses quand une existe déjà"""
        # Créer d'abord un plan de repas
        create_response = self.client.post(
            '/api/meal-plans',
            data=json.dumps(self.sample_meal_plan_data),
            content_type='application/json'
        )
        
        plan_id = json.loads(create_response.data)['id']
        
        # Générer la première liste de courses
        self.client.post(f'/api/meal-plans/{plan_id}/shopping-list')
        
        # Essayer de générer une seconde liste
        response = self.client.post(f'/api/meal-plans/{plan_id}/shopping-list')
        
        self.assertEqual(response.status_code, 409)
        data = json.loads(response.data)
        self.assertIn('Une liste de courses existe déjà', data['error'])
    
    def test_get_shopping_lists_success(self):
        """Test de récupération des listes de courses"""
        # Créer un plan de repas et sa liste de courses
        create_response = self.client.post(
            '/api/meal-plans',
            data=json.dumps(self.sample_meal_plan_data),
            content_type='application/json'
        )
        
        plan_id = json.loads(create_response.data)['id']
        self.client.post(f'/api/meal-plans/{plan_id}/shopping-list')
        
        response = self.client.get('/api/shopping-lists')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['meal_plan_id'], plan_id)
    
    def test_get_shopping_lists_with_filter(self):
        """Test de récupération des listes de courses avec filtre"""
        # Créer un plan de repas et sa liste de courses
        create_response = self.client.post(
            '/api/meal-plans',
            data=json.dumps(self.sample_meal_plan_data),
            content_type='application/json'
        )
        
        plan_id = json.loads(create_response.data)['id']
        self.client.post(f'/api/meal-plans/{plan_id}/shopping-list')
        
        response = self.client.get(f'/api/shopping-lists?meal_plan_id={plan_id}')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['meal_plan_id'], plan_id)
    
    def test_update_shopping_list_success(self):
        """Test de mise à jour d'une liste de courses"""
        # Créer un plan de repas et sa liste de courses
        create_response = self.client.post(
            '/api/meal-plans',
            data=json.dumps(self.sample_meal_plan_data),
            content_type='application/json'
        )
        
        plan_id = json.loads(create_response.data)['id']
        list_response = self.client.post(f'/api/meal-plans/{plan_id}/shopping-list')
        list_id = json.loads(list_response.data)['id']
        
        update_data = {
            "is_completed": True
        }
        
        response = self.client.put(
            f'/api/shopping-lists/{list_id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['is_completed'])
    
    def test_update_shopping_list_not_found(self):
        """Test de mise à jour d'une liste de courses inexistante"""
        update_data = {"is_completed": True}
        
        response = self.client.put(
            '/api/shopping-lists/999',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('Liste de courses non trouvée', data['error'])
    
    def test_query_parameters_validation(self):
        """Test de validation des paramètres de requête"""
        # Test avec paramètres invalides
        response = self.client.get('/api/meal-plans?page=0')  # page doit être >= 1
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('Paramètres de requête invalides', data['error'])
        
        # Test avec per_page trop grand
        response = self.client.get('/api/meal-plans?per_page=200')  # per_page max 100
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('Paramètres de requête invalides', data['error'])


if __name__ == '__main__':
    pytest.main([__file__])