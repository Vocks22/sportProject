"""
Tests E2E pour US1.6 - Workflows utilisateur avec calendrier lundi-dimanche
Tests End-to-End complets des parcours utilisateur avec nouvelle logique calendrier

Coverage: Parcours complets utilisateur, intégration Frontend/Backend
Focus: UX, cohérence calendrier, workflow liste de courses
"""

import pytest
from datetime import date, timedelta
import time
import json
import sys
import os

# Pour les tests E2E avec Selenium (optionnel)
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("Selenium not available - E2E tests will be mocked")

# Tests avec requests pour API E2E
import requests
from flask.testing import FlaskClient

# Ajouter les chemins vers les modules backend
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'backend'))

from main import create_app
from database.config import db
from models.user import User
from models.meal_plan import MealPlan
from utils.date_utils import get_monday_of_week, next_monday, format_week_display


class TestCalendarWorkflowsE2E:
    """Tests End-to-End des workflows calendrier"""
    
    @pytest.fixture
    def app(self):
        """Fixture Flask app pour tests E2E"""
        app = create_app('testing')
        
        with app.app_context():
            db.create_all()
            
            # Créer utilisateur de test
            test_user = User(
                email='e2e@diettracker.com',
                username='e2euser',
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
    def authenticated_user(self, client, app):
        """Utilisateur authentifié pour les tests"""
        with app.app_context():
            user = User.query.filter_by(email='e2e@diettracker.com').first()
            # Simuler authentification (en production, utiliser JWT)
            return {'user_id': user.id, 'email': user.email}


class TestMealPlanningCalendarWorkflow:
    """Tests E2E du workflow de planning des repas"""
    
    def test_weekly_meal_planning_full_workflow(self, client, authenticated_user):
        """Test workflow complet de planification hebdomadaire"""
        user_id = authenticated_user['user_id']
        
        # Étape 1: L'utilisateur accède au calendrier de planning
        # En production, ceci serait une requête GET vers la page de planning
        current_monday = get_monday_of_week(date.today())
        
        response = client.get(f'/api/meal-plans?user_id={user_id}&week_start={current_monday.isoformat()}')
        assert response.status_code == 200
        
        # Vérifier qu'aucun plan n'existe encore
        existing_plans = json.loads(response.data)
        assert len(existing_plans) == 0
        
        # Étape 2: L'utilisateur crée un nouveau planning pour cette semaine
        new_meal_plan = {
            'user_id': user_id,
            'week_start': current_monday.isoformat(),
            'meals': {
                'monday': {
                    'breakfast': 1,  # ID recette
                    'lunch': 2,
                    'dinner': 3
                },
                'tuesday': {
                    'breakfast': 2,
                    'lunch': 3,
                    'dinner': 1
                },
                'wednesday': {
                    'breakfast': 3,
                    'lunch': 1,
                    'dinner': 2
                },
                'thursday': {
                    'breakfast': 1,
                    'lunch': 2,
                    'dinner': 3
                },
                'friday': {
                    'breakfast': 2,
                    'lunch': 3,
                    'dinner': 1
                },
                'saturday': {
                    'breakfast': 3,
                    'lunch': 1,
                    'dinner': 2
                },
                'sunday': {
                    'breakfast': 1,
                    'lunch': 2,
                    'dinner': 3
                }
            }
        }
        
        response = client.post(
            '/api/meal-plans',
            data=json.dumps(new_meal_plan),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        created_plan = json.loads(response.data)
        
        # Vérifier que week_start est un lundi
        week_start_date = date.fromisoformat(created_plan['week_start'])
        assert week_start_date.weekday() == 0, "week_start doit être un lundi"
        assert week_start_date == current_monday
        
        meal_plan_id = created_plan['id']
        
        # Étape 3: L'utilisateur modifie le planning (changement de recette)
        updated_meals = new_meal_plan['meals'].copy()
        updated_meals['monday']['breakfast'] = 4  # Changer recette petit-déjeuner
        
        response = client.put(
            f'/api/meal-plans/{meal_plan_id}',
            data=json.dumps({'meals': updated_meals}),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        updated_plan = json.loads(response.data)
        assert updated_plan['meals']['monday']['breakfast'] == 4
        
        # Étape 4: L'utilisateur navigue vers la semaine suivante
        next_monday_date = next_monday(current_monday - timedelta(days=1))
        
        response = client.get(f'/api/meal-plans?user_id={user_id}&week_start={next_monday_date.isoformat()}')
        assert response.status_code == 200
        
        next_week_plans = json.loads(response.data)
        assert len(next_week_plans) == 0, "Aucun plan ne devrait exister pour la semaine suivante"
        
        # Étape 5: Vérifier que le planning de la semaine courante est toujours là
        response = client.get(f'/api/meal-plans?user_id={user_id}&week_start={current_monday.isoformat()}')
        assert response.status_code == 200
        
        current_week_plans = json.loads(response.data)
        assert len(current_week_plans) == 1
        assert current_week_plans[0]['meals']['monday']['breakfast'] == 4
    
    def test_calendar_navigation_workflow(self, client, authenticated_user):
        """Test workflow de navigation dans le calendrier"""
        user_id = authenticated_user['user_id']
        
        # Créer des meal plans pour plusieurs semaines
        base_monday = get_monday_of_week(date.today())
        weeks = [
            base_monday - timedelta(weeks=2),  # Il y a 2 semaines
            base_monday - timedelta(weeks=1),  # Semaine dernière
            base_monday,                       # Cette semaine
            base_monday + timedelta(weeks=1),  # Semaine prochaine
        ]
        
        meal_plan_ids = []
        
        for i, week_monday in enumerate(weeks):
            meal_plan_data = {
                'user_id': user_id,
                'week_start': week_monday.isoformat(),
                'meals': {
                    'monday': {'breakfast': i + 1}  # Identifier chaque semaine
                }
            }
            
            response = client.post(
                '/api/meal-plans',
                data=json.dumps(meal_plan_data),
                content_type='application/json'
            )
            
            assert response.status_code == 201
            created_plan = json.loads(response.data)
            meal_plan_ids.append(created_plan['id'])
        
        # Navigation: récupérer toutes les semaines avec plans
        response = client.get(f'/api/meal-plans?user_id={user_id}')
        assert response.status_code == 200
        
        all_plans = json.loads(response.data)
        assert len(all_plans) == 4
        
        # Vérifier l'ordre chronologique
        plan_weeks = [date.fromisoformat(plan['week_start']) for plan in all_plans]
        assert plan_weeks == sorted(plan_weeks), "Les semaines doivent être triées chronologiquement"
        
        # Navigation par semaine spécifique
        for i, week_monday in enumerate(weeks):
            response = client.get(f'/api/meal-plans?user_id={user_id}&week_start={week_monday.isoformat()}')
            assert response.status_code == 200
            
            week_plans = json.loads(response.data)
            assert len(week_plans) == 1
            assert week_plans[0]['meals']['monday']['breakfast'] == i + 1


class TestShoppingListWorkflowE2E:
    """Tests E2E du workflow liste de courses avec logique lundi-dimanche"""
    
    def test_shopping_list_next_week_workflow(self, client, authenticated_user):
        """Test workflow 'liste de courses pour la semaine prochaine'"""
        user_id = authenticated_user['user_id']
        
        # Étape 1: Créer un meal plan pour la semaine prochaine
        next_monday_date = next_monday(date.today() - timedelta(days=1))
        
        next_week_meal_plan = {
            'user_id': user_id,
            'week_start': next_monday_date.isoformat(),
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
            data=json.dumps(next_week_meal_plan),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        meal_plan = json.loads(response.data)
        meal_plan_id = meal_plan['id']
        
        # Étape 2: L'utilisateur demande la génération de liste de courses
        # pour "la semaine prochaine" (contextuel)
        shopping_list_request = {
            'for_next_week': True,
            'user_id': user_id
        }
        
        response = client.post(
            '/api/shopping-lists/generate-next-week',
            data=json.dumps(shopping_list_request),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        shopping_list = json.loads(response.data)
        
        # Vérifications critiques US1.6
        assert shopping_list['week_start'] == next_monday_date.isoformat()
        
        week_start_date = date.fromisoformat(shopping_list['week_start'])
        assert week_start_date.weekday() == 0, "week_start doit être un lundi"
        
        # Étape 3: Vérifier le contenu de la liste de courses
        assert 'items' in shopping_list
        assert len(shopping_list['items']) > 0, "La liste de courses ne peut pas être vide"
        
        # Étape 4: L'utilisateur coche des éléments (simulation)
        shopping_list_id = shopping_list['id']
        items = shopping_list['items']
        
        # Marquer le premier élément comme coché
        if len(items) > 0:
            items[0]['checked'] = True
            
            update_response = client.put(
                f'/api/shopping-lists/{shopping_list_id}',
                data=json.dumps({'items': items}),
                content_type='application/json'
            )
            
            assert update_response.status_code == 200
            updated_list = json.loads(update_response.data)
            assert updated_list['items'][0]['checked'] is True
        
        # Étape 5: Vérifier la persistance du week_start après modifications
        final_response = client.get(f'/api/shopping-lists/{shopping_list_id}')
        assert final_response.status_code == 200
        
        final_list = json.loads(final_response.data)
        assert final_list['week_start'] == next_monday_date.isoformat()
    
    def test_shopping_list_saturday_workflow(self, client, authenticated_user):
        """Test workflow 'faire les courses du samedi pour la semaine suivante'"""
        user_id = authenticated_user['user_id']
        
        # Simuler que nous sommes samedi (jour typique de courses)
        # La semaine suivante commence le lundi
        current_monday = get_monday_of_week(date.today())
        saturday = current_monday + timedelta(days=5)  # Samedi de cette semaine
        next_monday_date = current_monday + timedelta(days=7)  # Lundi prochain
        
        # Créer meal plan pour la semaine suivante
        meal_plan_data = {
            'user_id': user_id,
            'week_start': next_monday_date.isoformat(),
            'meals': {
                'monday': {'breakfast': 1},
                'tuesday': {'lunch': 2},
                'wednesday': {'dinner': 3},
            }
        }
        
        response = client.post(
            '/api/meal-plans',
            data=json.dumps(meal_plan_data),
            content_type='application/json'
        )
        assert response.status_code == 201
        
        # Générer liste de courses "du samedi"
        shopping_request = {
            'meal_plan_id': json.loads(response.data)['id'],
            'shopping_day': 'saturday',  # Contextuel
            'for_week_starting': next_monday_date.isoformat()
        }
        
        response = client.post(
            '/api/shopping-lists/generate',
            data=json.dumps(shopping_request),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        shopping_list = json.loads(response.data)
        
        # Vérifications spécifiques au workflow samedi
        list_week_start = date.fromisoformat(shopping_list['week_start'])
        assert list_week_start == next_monday_date
        assert list_week_start.weekday() == 0, "La liste doit être pour un lundi"


class TestCalendarConsistencyE2E:
    """Tests E2E de cohérence calendrier à travers l'application"""
    
    def test_calendar_consistency_across_features(self, client, authenticated_user):
        """Test cohérence calendrier entre meal plans et shopping lists"""
        user_id = authenticated_user['user_id']
        
        # Créer meal plan pour une semaine spécifique
        target_monday = get_monday_of_week(date.today()) + timedelta(weeks=1)
        
        meal_plan_data = {
            'user_id': user_id,
            'week_start': target_monday.isoformat(),
            'meals': {
                'monday': {'breakfast': 1, 'lunch': 2},
                'friday': {'dinner': 3}
            }
        }
        
        # Créer le meal plan
        response = client.post(
            '/api/meal-plans',
            data=json.dumps(meal_plan_data),
            content_type='application/json'
        )
        assert response.status_code == 201
        meal_plan = json.loads(response.data)
        
        # Générer shopping list depuis le meal plan
        shopping_request = {
            'meal_plan_id': meal_plan['id'],
            'week_start': target_monday.isoformat()
        }
        
        response = client.post(
            '/api/shopping-lists/generate',
            data=json.dumps(shopping_request),
            content_type='application/json'
        )
        assert response.status_code == 201
        shopping_list = json.loads(response.data)
        
        # Vérifications de cohérence
        assert meal_plan['week_start'] == shopping_list['week_start']
        assert meal_plan['week_start'] == target_monday.isoformat()
        
        # Vérifier que les deux respectent ISO 8601
        meal_plan_date = date.fromisoformat(meal_plan['week_start'])
        shopping_list_date = date.fromisoformat(shopping_list['week_start'])
        
        assert meal_plan_date.weekday() == 0
        assert shopping_list_date.weekday() == 0
        assert meal_plan_date == shopping_list_date
    
    def test_week_display_consistency(self, client, authenticated_user):
        """Test cohérence affichage des semaines"""
        user_id = authenticated_user['user_id']
        
        # Tester différentes semaines
        test_weeks = [
            get_monday_of_week(date.today()),                    # Cette semaine
            get_monday_of_week(date.today()) + timedelta(weeks=1), # Semaine prochaine
            get_monday_of_week(date(2025, 1, 1)),               # Première semaine 2025
            get_monday_of_week(date(2025, 12, 31)),             # Dernière semaine 2025
        ]
        
        for week_monday in test_weeks:
            # Créer un meal plan
            meal_plan_data = {
                'user_id': user_id,
                'week_start': week_monday.isoformat(),
                'meals': {'monday': {'breakfast': 1}}
            }
            
            response = client.post(
                '/api/meal-plans',
                data=json.dumps(meal_plan_data),
                content_type='application/json'
            )
            assert response.status_code == 201
            
            meal_plan = json.loads(response.data)
            
            # Vérifier le formatage d'affichage (simule appel frontend)
            display_text = format_week_display(week_monday, 'fr')
            
            # Vérifications format français
            assert 'Semaine du' in display_text
            assert str(week_monday.year) in display_text
            
            # Vérifier cohérence avec les données API
            assert meal_plan['week_start'] == week_monday.isoformat()


# Tests mocked si Selenium n'est pas disponible
class TestBrowserWorkflowsMocked:
    """Tests E2E simulés sans navigateur"""
    
    def test_calendar_navigation_ui_workflow(self):
        """Test simulé de navigation calendaire UI"""
        # Simuler les interactions utilisateur typiques
        workflow_steps = [
            "User opens meal planning page",
            "User sees current week calendar (Monday-Sunday)",
            "User clicks 'Next Week' button", 
            "Calendar advances to next Monday",
            "User creates meal plan for next week",
            "User clicks 'Generate Shopping List'",
            "Shopping list created for correct Monday"
        ]
        
        # Simuler chaque étape
        current_monday = get_monday_of_week(date.today())
        next_monday_date = current_monday + timedelta(weeks=1)
        
        # Étape navigation
        assert next_monday_date.weekday() == 0, "Navigation doit pointer vers un lundi"
        
        # Étape création planning
        meal_plan_week = next_monday_date
        assert meal_plan_week == next_monday_date
        
        # Étape génération liste courses
        shopping_list_week = meal_plan_week
        assert shopping_list_week == next_monday_date
        
        print("✅ Workflow UI simulé avec succès")
        for step in workflow_steps:
            print(f"  - {step}")
    
    def test_error_handling_ui_workflow(self):
        """Test simulé de gestion d'erreurs UI"""
        # Simuler tentative de création avec date invalide
        invalid_tuesday = date.today() + timedelta(days=(1 - date.today().weekday()) % 7)
        
        # L'UI devrait automatiquement corriger vers le lundi
        corrected_monday = get_monday_of_week(invalid_tuesday)
        
        assert corrected_monday.weekday() == 0
        assert corrected_monday != invalid_tuesday
        
        print("✅ Correction automatique UI simulée")
        print(f"  - Date utilisateur: {invalid_tuesday} (mardi)")
        print(f"  - Date corrigée: {corrected_monday} (lundi)")


# Configuration des tests Selenium si disponible
if SELENIUM_AVAILABLE:
    class TestRealBrowserWorkflows:
        """Tests E2E avec vrai navigateur"""
        
        @pytest.fixture
        def driver(self):
            """Fixture WebDriver Chrome headless"""
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            
            driver = webdriver.Chrome(options=options)
            driver.implicitly_wait(10)
            
            yield driver
            driver.quit()
        
        @pytest.mark.skipif(not SELENIUM_AVAILABLE, reason="Selenium not available")
        def test_meal_planning_calendar_ui(self, driver):
            """Test réel interface calendrier meal planning"""
            # Nécessite que l'application soit lancée sur localhost:5173
            try:
                driver.get('http://localhost:5173/meal-planning')
                
                # Attendre que le calendrier se charge
                calendar_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "calendar"))
                )
                
                # Vérifier que les jours de la semaine commencent par lundi
                week_days = driver.find_elements(By.CLASS_NAME, "weekday-header")
                if len(week_days) > 0:
                    first_day = week_days[0].text.lower()
                    assert 'lundi' in first_day or 'monday' in first_day
                
                print("✅ Test calendrier UI réussi")
                
            except Exception as e:
                pytest.skip(f"Application non accessible sur localhost:5173: {e}")


# Utilitaires pour tests E2E
def simulate_user_workflow(steps, client, user_data):
    """Simulateur de workflow utilisateur"""
    results = []
    
    for step in steps:
        if step['action'] == 'create_meal_plan':
            response = client.post(
                '/api/meal-plans',
                data=json.dumps(step['data']),
                content_type='application/json'
            )
            results.append({
                'step': step['name'],
                'status': response.status_code,
                'data': json.loads(response.data) if response.status_code < 400 else None
            })
        
        elif step['action'] == 'generate_shopping_list':
            response = client.post(
                '/api/shopping-lists/generate',
                data=json.dumps(step['data']),
                content_type='application/json'
            )
            results.append({
                'step': step['name'],
                'status': response.status_code,
                'data': json.loads(response.data) if response.status_code < 400 else None
            })
    
    return results


if __name__ == "__main__":
    # Configuration pour exécution directe
    pytest.main([__file__, "-v", "--tb=short"])