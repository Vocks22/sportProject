"""
Tests d'intégration pour US1.6 - API Meal Plans avec logique ISO 8601
Tests complets des endpoints API avec validation des semaines lundi-dimanche

Coverage: Endpoints meal_plans avec nouvelles contraintes calendrier
Focus: Intégration, validation, cohérence données
"""

import pytest
import json
from datetime import date, timedelta
from flask import Flask
from flask.testing import FlaskClient
import sys
import os

# Ajouter les chemins vers les modules backend
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'backend'))

from main import create_app
from database.config import db
from models.meal_plan import MealPlan
from models.user import User
from utils.date_utils import get_monday_of_week, next_monday, previous_monday


class TestMealPlansAPIUS16Integration:
    """Tests d'intégration API Meal Plans avec logique ISO 8601"""
    
    @pytest.fixture
    def app(self):
        """Fixture Flask app pour les tests"""
        app = create_app('testing')
        
        with app.app_context():
            db.create_all()
            
            # Créer un utilisateur test
            test_user = User(
                email='test@diettracker.com',
                username='testuser',
                password_hash='hashed_password'
            )
            db.session.add(test_user)
            db.session.commit()
            
            yield app
            
            db.session.remove()
            db.drop_all()
    
    @pytest.fixture
    def client(self, app):
        """Client de test Flask"""
        return app.test_client()
    
    @pytest.fixture
    def test_user_id(self, app):
        """ID de l'utilisateur de test"""
        with app.app_context():
            user = User.query.filter_by(email='test@diettracker.com').first()
            return user.id
    
    def test_create_meal_plan_with_valid_monday(self, client, test_user_id):
        """Test création d'un meal plan avec un lundi valide"""
        monday = get_monday_of_week(date.today())
        
        meal_plan_data = {
            'user_id': test_user_id,
            'week_start': monday.isoformat(),
            'meals': {
                'monday': {'breakfast': 1, 'lunch': 2, 'dinner': 3},
                'tuesday': {'breakfast': 2, 'lunch': 3, 'dinner': 1},
                'wednesday': {'breakfast': 3, 'lunch': 1, 'dinner': 2},
                'thursday': {'breakfast': 1, 'lunch': 2, 'dinner': 3},
                'friday': {'breakfast': 2, 'lunch': 3, 'dinner': 1},
                'saturday': {'breakfast': 3, 'lunch': 1, 'dinner': 2},
                'sunday': {'breakfast': 1, 'lunch': 2, 'dinner': 3},
            }
        }
        
        response = client.post(
            '/api/meal-plans',
            data=json.dumps(meal_plan_data),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        
        response_data = json.loads(response.data)
        assert response_data['week_start'] == monday.isoformat()
        assert response_data['user_id'] == test_user_id
        
        # Vérifier que la semaine est bien un lundi
        week_start_date = date.fromisoformat(response_data['week_start'])
        assert week_start_date.weekday() == 0, "week_start doit être un lundi"
    
    def test_create_meal_plan_with_invalid_weekday(self, client, test_user_id):
        """Test création d'un meal plan avec une date qui n'est pas lundi"""
        wednesday = date.today() + timedelta(days=(2 - date.today().weekday()) % 7)
        
        meal_plan_data = {
            'user_id': test_user_id,
            'week_start': wednesday.isoformat(),
            'meals': {
                'monday': {'breakfast': 1},
            }
        }
        
        response = client.post(
            '/api/meal-plans',
            data=json.dumps(meal_plan_data),
            content_type='application/json'
        )
        
        # Devrait être rejeté avec une erreur 400
        assert response.status_code == 400
        
        response_data = json.loads(response.data)
        assert 'error' in response_data
        assert 'lundi' in response_data['error'].lower()
        assert 'iso 8601' in response_data['error'].lower()
    
    def test_get_meal_plans_by_week_range(self, client, test_user_id, app):
        """Test récupération des meal plans par plage de semaines"""
        with app.app_context():
            # Créer plusieurs meal plans pour différentes semaines
            current_monday = get_monday_of_week(date.today())
            next_monday_date = next_monday(current_monday - timedelta(days=1))
            previous_monday_date = previous_monday(current_monday + timedelta(days=1))
            
            meal_plans = [
                MealPlan(
                    user_id=test_user_id,
                    week_start=previous_monday_date,
                    meals={'monday': {'breakfast': 1}}
                ),
                MealPlan(
                    user_id=test_user_id,
                    week_start=current_monday,
                    meals={'monday': {'breakfast': 2}}
                ),
                MealPlan(
                    user_id=test_user_id,
                    week_start=next_monday_date,
                    meals={'monday': {'breakfast': 3}}
                ),
            ]
            
            for meal_plan in meal_plans:
                db.session.add(meal_plan)
            db.session.commit()
        
        # Test récupération avec filtre par semaine
        response = client.get(f'/api/meal-plans?week_start={current_monday.isoformat()}')
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        
        assert len(response_data) == 1
        assert response_data[0]['week_start'] == current_monday.isoformat()
        assert response_data[0]['meals']['monday']['breakfast'] == 2
    
    def test_update_meal_plan_week_start_validation(self, client, test_user_id, app):
        """Test mise à jour d'un meal plan avec validation week_start"""
        with app.app_context():
            # Créer un meal plan initial
            monday = get_monday_of_week(date.today())
            meal_plan = MealPlan(
                user_id=test_user_id,
                week_start=monday,
                meals={'monday': {'breakfast': 1}}
            )
            db.session.add(meal_plan)
            db.session.commit()
            meal_plan_id = meal_plan.id
        
        # Tentative de mise à jour avec une date invalide (mardi)
        tuesday = monday + timedelta(days=1)
        update_data = {
            'week_start': tuesday.isoformat(),
            'meals': {'monday': {'breakfast': 2}}
        }
        
        response = client.put(
            f'/api/meal-plans/{meal_plan_id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        # Devrait être rejeté
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert 'error' in response_data
        assert 'lundi' in response_data['error'].lower()
    
    def test_bulk_create_meal_plans_validation(self, client, test_user_id):
        """Test création en lot avec validation de toutes les dates"""
        current_monday = get_monday_of_week(date.today())
        next_monday_date = next_monday(current_monday - timedelta(days=1))
        invalid_wednesday = current_monday + timedelta(days=2)
        
        bulk_data = {
            'meal_plans': [
                {
                    'user_id': test_user_id,
                    'week_start': current_monday.isoformat(),
                    'meals': {'monday': {'breakfast': 1}}
                },
                {
                    'user_id': test_user_id,
                    'week_start': next_monday_date.isoformat(),
                    'meals': {'monday': {'breakfast': 2}}
                },
                {
                    'user_id': test_user_id,
                    'week_start': invalid_wednesday.isoformat(),  # Invalide
                    'meals': {'monday': {'breakfast': 3}}
                },
            ]
        }
        
        response = client.post(
            '/api/meal-plans/bulk',
            data=json.dumps(bulk_data),
            content_type='application/json'
        )
        
        # Devrait être rejeté à cause de la date invalide
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert 'error' in response_data
        assert 'mercredi' in response_data['error'].lower()
    
    def test_meal_plan_week_overlap_detection(self, client, test_user_id, app):
        """Test détection des chevauchements de semaines"""
        with app.app_context():
            # Créer un meal plan pour une semaine
            monday = get_monday_of_week(date.today())
            existing_meal_plan = MealPlan(
                user_id=test_user_id,
                week_start=monday,
                meals={'monday': {'breakfast': 1}}
            )
            db.session.add(existing_meal_plan)
            db.session.commit()
        
        # Tentative de création d'un autre meal plan pour la même semaine
        duplicate_meal_plan_data = {
            'user_id': test_user_id,
            'week_start': monday.isoformat(),
            'meals': {'monday': {'breakfast': 2}}
        }
        
        response = client.post(
            '/api/meal-plans',
            data=json.dumps(duplicate_meal_plan_data),
            content_type='application/json'
        )
        
        # Devrait être rejeté ou géré selon la logique métier
        # (dépend de si on autorise plusieurs plans par semaine ou non)
        assert response.status_code in [400, 409]  # Bad Request ou Conflict


class TestShoppingListsAPIUS16Integration:
    """Tests d'intégration API Shopping Lists avec logique ISO 8601"""
    
    @pytest.fixture
    def app(self):
        """Fixture Flask app pour les tests shopping lists"""
        app = create_app('testing')
        
        with app.app_context():
            db.create_all()
            
            # Créer utilisateur et meal plan de test
            test_user = User(
                email='test@diettracker.com',
                username='testuser',
                password_hash='hashed_password'
            )
            db.session.add(test_user)
            db.session.commit()
            
            # Créer un meal plan avec un lundi valide
            monday = get_monday_of_week(date.today())
            meal_plan = MealPlan(
                user_id=test_user.id,
                week_start=monday,
                meals={'monday': {'breakfast': 1, 'lunch': 2}}
            )
            db.session.add(meal_plan)
            db.session.commit()
            
            yield app
            
            db.session.remove()
            db.drop_all()
    
    @pytest.fixture
    def client(self, app):
        """Client de test Flask"""
        return app.test_client()
    
    def test_generate_shopping_list_from_meal_plan(self, client, app):
        """Test génération de liste de courses depuis un meal plan ISO 8601"""
        with app.app_context():
            user = User.query.filter_by(email='test@diettracker.com').first()
            meal_plan = MealPlan.query.filter_by(user_id=user.id).first()
            
            generation_data = {
                'meal_plan_id': meal_plan.id,
                'week_start': meal_plan.week_start.isoformat()
            }
            
            response = client.post(
                '/api/shopping-lists/generate',
                data=json.dumps(generation_data),
                content_type='application/json'
            )
            
            assert response.status_code == 201
            response_data = json.loads(response.data)
            
            # Vérifier que week_start est cohérent
            assert response_data['week_start'] == meal_plan.week_start.isoformat()
            
            # Vérifier que week_start est un lundi
            week_start_date = date.fromisoformat(response_data['week_start'])
            assert week_start_date.weekday() == 0
    
    def test_shopping_list_next_week_logic(self, client, app):
        """Test logique 'semaine prochaine' pour liste de courses"""
        with app.app_context():
            user = User.query.filter_by(email='test@diettracker.com').first()
            current_monday = get_monday_of_week(date.today())
            next_monday_date = next_monday(current_monday - timedelta(days=1))
            
            # Créer un meal plan pour la semaine prochaine
            next_week_meal_plan = MealPlan(
                user_id=user.id,
                week_start=next_monday_date,
                meals={'monday': {'breakfast': 1}}
            )
            db.session.add(next_week_meal_plan)
            db.session.commit()
            
            # Générer liste de courses pour "semaine prochaine"
            request_data = {
                'for_next_week': True
            }
            
            response = client.post(
                '/api/shopping-lists/generate-next-week',
                data=json.dumps(request_data),
                content_type='application/json'
            )
            
            assert response.status_code == 201
            response_data = json.loads(response.data)
            
            # Vérifier que la semaine correspond au lundi suivant
            assert response_data['week_start'] == next_monday_date.isoformat()


class TestCalendarLogicConsistency:
    """Tests de cohérence de la logique calendrier across components"""
    
    @pytest.fixture
    def app(self):
        """Fixture Flask app"""
        app = create_app('testing')
        with app.app_context():
            db.create_all()
            yield app
            db.session.remove()
            db.drop_all()
    
    def test_week_calculation_consistency(self, app):
        """Test cohérence des calculs de semaine entre composants"""
        with app.app_context():
            # Test sur plusieurs dates pour vérifier la cohérence
            test_dates = [
                date(2025, 8, 7),   # Jeudi
                date(2025, 1, 1),   # Mercredi (transition année)
                date(2025, 12, 31), # Mercredi (fin année)
                date(2024, 2, 29),  # Jeudi (année bissextile)
            ]
            
            for test_date in test_dates:
                # Calculer via utilitaires
                from utils.date_utils import get_monday_of_week, get_sunday_of_week
                monday_util = get_monday_of_week(test_date)
                sunday_util = get_sunday_of_week(test_date)
                
                # Vérifier cohérence interne
                assert monday_util.weekday() == 0, f"Lundi calculé invalide pour {test_date}"
                assert sunday_util.weekday() == 6, f"Dimanche calculé invalide pour {test_date}"
                assert (sunday_util - monday_util).days == 6, f"Plage de semaine incorrecte pour {test_date}"
    
    def test_api_frontend_calendar_alignment(self, app):
        """Test alignement calendrier entre API et logique frontend attendue"""
        with app.app_context():
            # Simuler une requête frontend pour obtenir les semaines d'un mois
            from utils.date_utils import get_monday_of_week
            
            # Août 2025 pour exemple
            first_day_august = date(2025, 8, 1)
            last_day_august = date(2025, 8, 31)
            
            # Calculer toutes les semaines du mois
            current_date = first_day_august
            weeks_in_august = []
            
            while current_date <= last_day_august:
                monday = get_monday_of_week(current_date)
                if monday not in [week[0] for week in weeks_in_august]:
                    sunday = monday + timedelta(days=6)
                    weeks_in_august.append((monday, sunday))
                current_date += timedelta(days=7)
            
            # Vérifications attendues pour le frontend
            assert len(weeks_in_august) >= 4, "Un mois devrait avoir au moins 4 semaines"
            assert len(weeks_in_august) <= 6, "Un mois ne devrait pas avoir plus de 6 semaines"
            
            # Vérifier que les semaines sont bien ordonnées
            for i in range(1, len(weeks_in_august)):
                prev_monday = weeks_in_august[i-1][0]
                curr_monday = weeks_in_august[i][0]
                assert (curr_monday - prev_monday).days == 7, "Les semaines doivent être consécutives"


# Configuration des tests pytest
@pytest.mark.integration
class TestMigrationDataIntegrity:
    """Tests d'intégrité des données lors de la migration"""
    
    @pytest.fixture
    def app_with_legacy_data(self):
        """Fixture avec des données legacy (pré-migration)"""
        app = create_app('testing')
        
        with app.app_context():
            db.create_all()
            
            # Simuler des données avec anciennes dates week_start
            from models.user import User
            from models.meal_plan import MealPlan
            
            user = User(email='legacy@test.com', username='legacy', password_hash='hash')
            db.session.add(user)
            db.session.flush()  # Pour obtenir l'ID
            
            # Créer des meal plans avec des dates non-lundi (pré-migration)
            legacy_meal_plans = [
                MealPlan(user_id=user.id, week_start=date(2025, 8, 5), meals={'tuesday': {}}),  # Mardi
                MealPlan(user_id=user.id, week_start=date(2025, 8, 7), meals={'thursday': {}}), # Jeudi  
                MealPlan(user_id=user.id, week_start=date(2025, 8, 10), meals={'sunday': {}}),  # Dimanche
            ]
            
            for meal_plan in legacy_meal_plans:
                db.session.add(meal_plan)
            
            db.session.commit()
            yield app
            
            db.session.remove()
            db.drop_all()
    
    def test_migration_preserves_data_relationships(self, app_with_legacy_data):
        """Test que la migration préserve les relations de données"""
        with app_with_legacy_data.app_context():
            # Avant migration - vérifier l'état initial
            meal_plans_before = MealPlan.query.all()
            assert len(meal_plans_before) == 3
            
            # Simuler la migration
            from utils.date_utils import convert_week_start_to_iso8601
            
            for meal_plan in meal_plans_before:
                original_week_start = meal_plan.week_start
                new_week_start = convert_week_start_to_iso8601(original_week_start)
                meal_plan.week_start = new_week_start
            
            db.session.commit()
            
            # Après migration - vérifier l'intégrité
            meal_plans_after = MealPlan.query.all()
            assert len(meal_plans_after) == 3, "Aucun meal plan ne devrait être perdu"
            
            # Vérifier que toutes les dates sont maintenant des lundis
            for meal_plan in meal_plans_after:
                assert meal_plan.week_start.weekday() == 0, f"week_start {meal_plan.week_start} devrait être un lundi"
            
            # Vérifier que les relations utilisateur sont préservées
            user = User.query.filter_by(email='legacy@test.com').first()
            assert len(user.meal_plans) == 3, "Les relations utilisateur doivent être préservées"


if __name__ == "__main__":
    # Configuration pour exécution directe
    pytest.main([__file__, "-v", "--tb=short", "-m", "integration"])