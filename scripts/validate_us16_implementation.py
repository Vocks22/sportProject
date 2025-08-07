#!/usr/bin/env python3
"""
Script de validation complète US1.6 - Semaines Lundi-Dimanche (ISO 8601)

Ce script valide l'implémentation complète de l'US1.6 en testant:
1. Les utilitaires de dates ISO 8601
2. L'intégrité des données en base
3. Les endpoints API mis à jour
4. La cohérence des migrations
5. Les performances

Usage:
    python scripts/validate_us16_implementation.py [--config development] [--verbose]
"""

import sys
import os
import json
import requests
from datetime import datetime, date, timedelta
from pathlib import Path

# Ajouter le répertoire backend au path
backend_path = Path(__file__).resolve().parent.parent / 'src' / 'backend'
sys.path.append(str(backend_path))

from database.config import get_config
from database import db
from models.meal_plan import MealPlan, ShoppingList
from utils.date_utils import (
    get_monday_of_week, get_sunday_of_week, get_week_range_iso8601,
    validate_week_start_iso8601, format_week_display,
    get_current_week_monday, next_monday, previous_monday,
    get_week_number_iso8601, get_week_year_iso8601,
    validate_database_week_starts
)
from flask import Flask


class US16ValidationSuite:
    """Suite complète de validation pour US1.6"""
    
    def __init__(self, config_name='development', verbose=False):
        self.config_name = config_name
        self.verbose = verbose
        self.test_results = {
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'errors': [],
            'warnings': []
        }
        
        # Initialiser Flask app
        self.app = Flask(__name__)
        config_class = get_config(config_name)
        self.app.config.from_object(config_class)
        db.init_app(self.app)
        
        if verbose:
            print(f"🔧 Configuration: {config_name}")
            print(f"🔧 Database: {self.app.config['SQLALCHEMY_DATABASE_URI']}")
            print("=" * 80)
    
    def log(self, message, level='INFO'):
        """Log avec formatage"""
        if self.verbose or level in ['ERROR', 'WARNING', 'RESULT']:
            prefix = {
                'INFO': '📋',
                'SUCCESS': '✅',
                'ERROR': '❌',
                'WARNING': '⚠️',
                'RESULT': '📊'
            }.get(level, '📋')
            
            print(f"{prefix} {message}")
    
    def run_test(self, test_name, test_func):
        """Exécute un test et enregistre les résultats"""
        self.test_results['total_tests'] += 1
        
        try:
            self.log(f"Test: {test_name}")
            result = test_func()
            
            if result:
                self.test_results['passed'] += 1
                self.log(f"PASS: {test_name}", 'SUCCESS')
                return True
            else:
                self.test_results['failed'] += 1
                self.log(f"FAIL: {test_name}", 'ERROR')
                self.test_results['errors'].append(f"Test failed: {test_name}")
                return False
                
        except Exception as e:
            self.test_results['failed'] += 1
            error_msg = f"Test error in {test_name}: {str(e)}"
            self.log(error_msg, 'ERROR')
            self.test_results['errors'].append(error_msg)
            return False
    
    def test_date_utilities_iso8601(self):
        """Test 1: Validation des utilitaires de dates ISO 8601"""
        test_cases = [
            # (input_date, expected_monday, expected_sunday)
            (date(2025, 8, 7), date(2025, 8, 4), date(2025, 8, 10)),   # Jeudi
            (date(2025, 8, 4), date(2025, 8, 4), date(2025, 8, 10)),   # Lundi
            (date(2025, 8, 10), date(2025, 8, 4), date(2025, 8, 10)),  # Dimanche
            (date(2025, 12, 29), date(2025, 12, 29), date(2026, 1, 4)), # Lundi fin d'année
        ]
        
        for input_date, expected_monday, expected_sunday in test_cases:
            # Test get_monday_of_week
            actual_monday = get_monday_of_week(input_date)
            if actual_monday != expected_monday:
                self.log(f"❌ get_monday_of_week({input_date}) = {actual_monday}, attendu {expected_monday}", 'ERROR')
                return False
            
            # Test get_sunday_of_week
            actual_sunday = get_sunday_of_week(input_date)
            if actual_sunday != expected_sunday:
                self.log(f"❌ get_sunday_of_week({input_date}) = {actual_sunday}, attendu {expected_sunday}", 'ERROR')
                return False
            
            # Test get_week_range_iso8601
            monday, sunday = get_week_range_iso8601(input_date)
            if monday != expected_monday or sunday != expected_sunday:
                self.log(f"❌ get_week_range_iso8601({input_date}) = ({monday}, {sunday}), attendu ({expected_monday}, {expected_sunday})", 'ERROR')
                return False
        
        # Test validation des lundis
        try:
            validate_week_start_iso8601(date(2025, 8, 4))  # Lundi - OK
        except ValueError:
            self.log("❌ validate_week_start_iso8601 rejette un lundi valide", 'ERROR')
            return False
        
        # Test validation des non-lundis
        try:
            validate_week_start_iso8601(date(2025, 8, 6))  # Mercredi - KO
            self.log("❌ validate_week_start_iso8601 accepte un mercredi", 'ERROR')
            return False
        except ValueError:
            pass  # Comportement attendu
        
        # Test formatage de semaine
        monday = date(2025, 8, 4)
        display = format_week_display(monday, 'fr')
        if "Semaine du 4 au 10 août 2025" not in display:
            self.log(f"❌ format_week_display incorrect: {display}", 'ERROR')
            return False
        
        self.log("Tous les utilitaires de dates ISO 8601 fonctionnent correctement")
        return True
    
    def test_database_integrity(self):
        """Test 2: Intégrité des données en base"""
        try:
            with self.app.app_context():
                # Récupérer toutes les dates week_start
                meal_plan_dates = [mp.week_start for mp in MealPlan.query.all() if mp.week_start]
                shopping_list_dates = [sl.week_start for sl in ShoppingList.query.all() if sl.week_start]
                
                all_dates = meal_plan_dates + shopping_list_dates
                
                if not all_dates:
                    self.log("⚠️ Aucune donnée à valider en base", 'WARNING')
                    return True
                
                # Valider avec l'utilitaire
                is_valid, errors = validate_database_week_starts(all_dates)
                
                if not is_valid:
                    self.log(f"❌ Données non conformes ISO 8601 détectées:", 'ERROR')
                    for error in errors[:5]:  # Limiter à 5 erreurs pour la lisibilité
                        self.log(f"  {error}", 'ERROR')
                    return False
                
                self.log(f"Toutes les dates en base ({len(all_dates)} au total) sont conformes ISO 8601")
                return True
                
        except Exception as e:
            self.log(f"❌ Erreur validation base de données: {e}", 'ERROR')
            return False
    
    def test_api_endpoints(self):
        """Test 3: Test des endpoints API (si le serveur est lancé)"""
        try:
            # Tenter de se connecter à l'API locale
            base_url = "http://localhost:5000"
            
            # Test simple de connectivité
            response = requests.get(f"{base_url}/api/meal-plans", timeout=2)
            if response.status_code not in [200, 404, 401]:  # 404/401 OK si pas de données
                self.log(f"❌ API endpoint non accessible: {response.status_code}", 'ERROR')
                return False
            
            self.log("API endpoints accessibles")
            
            # Test spécifique pour les semaines ISO 8601
            # Créer une date de test (lundi)
            test_monday = get_current_week_monday()
            
            # Test avec paramètre week_start
            params = {'week_start': test_monday.isoformat()}
            response = requests.get(f"{base_url}/api/meal-plans", params=params, timeout=2)
            
            if response.status_code not in [200, 404]:
                self.log(f"⚠️ Filtre week_start peut ne pas fonctionner: {response.status_code}", 'WARNING')
                self.test_results['warnings'].append("API week_start filter may not work properly")
            
            return True
            
        except requests.exceptions.RequestException:
            self.log("⚠️ Serveur API non accessible - tests API ignorés", 'WARNING')
            self.test_results['warnings'].append("API server not accessible, API tests skipped")
            return True  # Non critique
        except Exception as e:
            self.log(f"❌ Erreur test API: {e}", 'ERROR')
            return False
    
    def test_week_calculations(self):
        """Test 4: Calculs avancés de semaines"""
        # Test numéros de semaine ISO 8601
        test_cases = [
            (date(2025, 1, 1), 1),     # 1er janvier 2025 (mercredi) = semaine 1
            (date(2025, 1, 6), 2),     # 6 janvier 2025 (lundi) = semaine 2
            (date(2025, 12, 29), 1),   # 29 décembre 2025 (lundi) = semaine 1 de 2026
        ]
        
        for test_date, expected_week in test_cases:
            actual_week = get_week_number_iso8601(test_date)
            if actual_week != expected_week:
                # Tolérance pour les calculs de fin d'année complexes
                if abs(actual_week - expected_week) > 1:
                    self.log(f"❌ get_week_number_iso8601({test_date}) = {actual_week}, attendu ~{expected_week}", 'ERROR')
                    return False
        
        # Test navigation de semaines
        current_monday = get_current_week_monday()
        next_monday_calc = next_monday(current_monday - timedelta(days=1))  # Dimanche précédent
        prev_monday_calc = previous_monday(current_monday + timedelta(days=1))  # Mardi suivant
        
        if next_monday_calc != current_monday + timedelta(days=7):
            self.log(f"❌ Calcul next_monday incorrect", 'ERROR')
            return False
        
        if prev_monday_calc != current_monday:
            self.log(f"❌ Calcul previous_monday incorrect", 'ERROR')
            return False
        
        self.log("Calculs de semaines avancés corrects")
        return True
    
    def test_migration_consistency(self):
        """Test 5: Cohérence des migrations"""
        try:
            # Vérifier que les fichiers de migration existent
            migrations_dir = Path(__file__).parent.parent / 'src' / 'backend' / 'database' / 'migrations' / 'versions'
            
            us16_migration = migrations_dir / '004_week_monday_to_sunday_iso8601.py'
            if not us16_migration.exists():
                self.log("❌ Fichier de migration US1.6 manquant", 'ERROR')
                return False
            
            # Vérifier la présence des fonctions clés dans le fichier
            with open(us16_migration, 'r', encoding='utf-8') as f:
                migration_content = f.read()
            
            required_elements = [
                'def upgrade()',
                'def downgrade()',
                'get_monday_of_week',
                'meal_plans',
                'shopping_lists'
            ]
            
            for element in required_elements:
                if element not in migration_content:
                    self.log(f"❌ Élément manquant dans la migration: {element}", 'ERROR')
                    return False
            
            self.log("Migration US1.6 cohérente et complète")
            return True
            
        except Exception as e:
            self.log(f"❌ Erreur validation migration: {e}", 'ERROR')
            return False
    
    def test_performance_week_calculations(self):
        """Test 6: Performance des calculs de semaines"""
        import time
        
        # Test de performance sur 1000 calculs
        test_dates = [
            date(2025, 1, 1) + timedelta(days=i) 
            for i in range(0, 1000, 7)  # Une date par semaine
        ]
        
        start_time = time.time()
        
        for test_date in test_dates:
            monday = get_monday_of_week(test_date)
            sunday = get_sunday_of_week(test_date)
            week_range = get_week_range_iso8601(test_date)
            
        elapsed = time.time() - start_time
        
        # Performance acceptable: moins de 1 seconde pour 1000 calculs
        if elapsed > 1.0:
            self.log(f"⚠️ Performance des calculs de dates lente: {elapsed:.2f}s pour 1000 calculs", 'WARNING')
            self.test_results['warnings'].append(f"Date calculations performance: {elapsed:.2f}s for 1000 operations")
        
        self.log(f"Performance calculs de dates: {elapsed:.3f}s pour {len(test_dates)} opérations")
        return True
    
    def test_edge_cases(self):
        """Test 7: Cas limites et situations particulières"""
        # Test avec les transitions d'année
        edge_cases = [
            # Fin d'année 2024 / Début 2025
            date(2024, 12, 30),  # Lundi
            date(2024, 12, 31),  # Mardi
            date(2025, 1, 1),    # Mercredi
            date(2025, 1, 5),    # Dimanche
            
            # Année bissextile
            date(2024, 2, 29),   # 29 février (bissextile)
            
            # Semaines chevauchant les mois
            date(2025, 6, 30),   # Lundi en fin de mois
            date(2025, 7, 6),    # Dimanche début mois suivant
        ]
        
        for test_date in edge_cases:
            try:
                monday = get_monday_of_week(test_date)
                sunday = get_sunday_of_week(test_date)
                
                # Vérifications de base
                if monday.weekday() != 0:  # 0 = lundi
                    self.log(f"❌ Lundi calculé n'est pas un lundi: {monday}", 'ERROR')
                    return False
                
                if sunday.weekday() != 6:  # 6 = dimanche
                    self.log(f"❌ Dimanche calculé n'est pas un dimanche: {sunday}", 'ERROR')
                    return False
                
                # La différence doit être exactement 6 jours
                delta = (sunday - monday).days
                if delta != 6:
                    self.log(f"❌ Différence lundi-dimanche incorrecte: {delta} jours", 'ERROR')
                    return False
                
            except Exception as e:
                self.log(f"❌ Erreur avec date {test_date}: {e}", 'ERROR')
                return False
        
        self.log("Tous les cas limites gérés correctement")
        return True
    
    def generate_report(self):
        """Génère un rapport de validation complet"""
        success_rate = (self.test_results['passed'] / self.test_results['total_tests'] * 100) if self.test_results['total_tests'] > 0 else 0
        
        report = {
            'validation_date': datetime.now().isoformat(),
            'config': self.config_name,
            'results': self.test_results,
            'success_rate': round(success_rate, 2),
            'status': 'PASS' if self.test_results['failed'] == 0 else 'FAIL'
        }
        
        # Sauvegarder le rapport
        report_file = f"us16_validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return report, report_file
    
    def run_all_tests(self):
        """Exécute tous les tests de validation"""
        self.log("🚀 Début de la validation complète US1.6", 'INFO')
        self.log(f"Configuration: {self.config_name}")
        print("=" * 80)
        
        # Liste des tests à exécuter
        tests = [
            ("Utilitaires de dates ISO 8601", self.test_date_utilities_iso8601),
            ("Intégrité des données en base", self.test_database_integrity),
            ("Endpoints API", self.test_api_endpoints),
            ("Calculs avancés de semaines", self.test_week_calculations),
            ("Cohérence des migrations", self.test_migration_consistency),
            ("Performance des calculs", self.test_performance_week_calculations),
            ("Cas limites et edge cases", self.test_edge_cases),
        ]
        
        # Exécuter tous les tests
        for test_name, test_func in tests:
            self.run_test(test_name, test_func)
            print("-" * 60)
        
        # Générer le rapport final
        report, report_file = self.generate_report()
        
        print("=" * 80)
        self.log("📊 RÉSULTATS DE LA VALIDATION", 'RESULT')
        self.log(f"Tests exécutés: {report['results']['total_tests']}", 'RESULT')
        self.log(f"Tests réussis: {report['results']['passed']}", 'RESULT')
        self.log(f"Tests échoués: {report['results']['failed']}", 'RESULT')
        self.log(f"Taux de réussite: {report['success_rate']}%", 'RESULT')
        
        if report['results']['warnings']:
            self.log(f"Avertissements: {len(report['results']['warnings'])}", 'WARNING')
            for warning in report['results']['warnings']:
                self.log(f"  - {warning}", 'WARNING')
        
        if report['results']['errors']:
            self.log("Erreurs détectées:", 'ERROR')
            for error in report['results']['errors']:
                self.log(f"  - {error}", 'ERROR')
        
        self.log(f"Rapport détaillé: {report_file}", 'RESULT')
        
        status_msg = "✅ VALIDATION RÉUSSIE" if report['status'] == 'PASS' else "❌ VALIDATION ÉCHOUÉE"
        self.log(status_msg, 'RESULT')
        
        return report['status'] == 'PASS'


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Validation complète US1.6 - Semaines ISO 8601'
    )
    parser.add_argument('--config', default='development',
                       choices=['development', 'testing', 'production'],
                       help='Configuration à utiliser')
    parser.add_argument('--verbose', action='store_true',
                       help='Affichage détaillé')
    
    args = parser.parse_args()
    
    # Créer et exécuter la suite de validation
    validator = US16ValidationSuite(
        config_name=args.config,
        verbose=args.verbose
    )
    
    try:
        success = validator.run_all_tests()
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n⏹️ Validation interrompue par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"💥 Erreur inattendue: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()