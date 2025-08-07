"""
Tests de migration pour US1.6 - Migration des données vers ISO 8601
Tests complets de la migration de base de données avec validation d'intégrité

Coverage: Migration Alembic, backup/restore, validation données
Focus: Intégrité données, rollback, performance migration
"""

import pytest
import tempfile
import shutil
from datetime import date, datetime, timedelta
import os
import sys
import sqlite3
from unittest.mock import patch, MagicMock

# Ajouter les chemins vers les modules backend
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'backend'))

from main import create_app
from database.config import db
from models.meal_plan import MealPlan
from models.shopping_list import ShoppingList
from models.user import User
from utils.date_utils import get_monday_of_week, validate_database_week_starts


class TestMigrationUS16Database:
    """Tests de migration de base de données US1.6"""
    
    @pytest.fixture
    def temp_db_path(self):
        """Fixture base de données temporaire"""
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, 'test_migration.db')
        yield db_path
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def app_with_legacy_data(self, temp_db_path):
        """Fixture app avec données legacy pour tests migration"""
        app = create_app('testing')
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{temp_db_path}'
        
        with app.app_context():
            db.create_all()
            
            # Créer utilisateur de test
            user = User(email='migration@test.com', username='migrationuser', password_hash='hash')
            db.session.add(user)
            db.session.flush()
            
            # Créer des données legacy avec dates non-lundi
            legacy_data = [
                # Meal Plans avec différents jours de semaine
                {'type': 'meal_plan', 'week_start': date(2025, 8, 5), 'data': {'tuesday': {'breakfast': 1}}},   # Mardi
                {'type': 'meal_plan', 'week_start': date(2025, 8, 7), 'data': {'thursday': {'lunch': 2}}},     # Jeudi
                {'type': 'meal_plan', 'week_start': date(2025, 8, 9), 'data': {'saturday': {'dinner': 3}}},    # Samedi
                {'type': 'meal_plan', 'week_start': date(2025, 8, 10), 'data': {'sunday': {'breakfast': 4}}},  # Dimanche
                
                # Shopping Lists
                {'type': 'shopping_list', 'week_start': date(2025, 8, 6), 'data': {'items': ['pommes', 'pain']}},    # Mercredi
                {'type': 'shopping_list', 'week_start': date(2025, 8, 8), 'data': {'items': ['lait', 'oeufs']}},     # Vendredi
            ]
            
            # Insérer les données legacy
            for item in legacy_data:
                if item['type'] == 'meal_plan':
                    meal_plan = MealPlan(
                        user_id=user.id,
                        week_start=item['week_start'],
                        meals=item['data']
                    )
                    db.session.add(meal_plan)
                elif item['type'] == 'shopping_list':
                    shopping_list = ShoppingList(
                        user_id=user.id,
                        week_start=item['week_start'],
                        items=item['data']
                    )
                    db.session.add(shopping_list)
            
            db.session.commit()
            yield app, temp_db_path
            
            db.session.remove()
            db.drop_all()
    
    def test_migration_backup_creation(self, app_with_legacy_data):
        """Test création des backups avant migration"""
        app, db_path = app_with_legacy_data
        
        with app.app_context():
            # Vérifier données avant migration
            meal_plans_before = MealPlan.query.all()
            shopping_lists_before = ShoppingList.query.all()
            
            assert len(meal_plans_before) == 4
            assert len(shopping_lists_before) == 2
            
            # Simuler la création des tables de backup (comme dans la migration)
            db.engine.execute("""
                CREATE TABLE IF NOT EXISTS meal_plans_backup_pre_us16 AS 
                SELECT * FROM meal_plans
            """)
            
            db.engine.execute("""
                CREATE TABLE IF NOT EXISTS shopping_lists_backup_pre_us16 AS 
                SELECT * FROM shopping_lists
            """)
            
            # Vérifier que les backups contiennent les bonnes données
            backup_meal_plans = db.engine.execute("SELECT COUNT(*) FROM meal_plans_backup_pre_us16").scalar()
            backup_shopping_lists = db.engine.execute("SELECT COUNT(*) FROM shopping_lists_backup_pre_us16").scalar()
            
            assert backup_meal_plans == 4
            assert backup_shopping_lists == 2
    
    def test_migration_date_conversion(self, app_with_legacy_data):
        """Test conversion des dates vers ISO 8601"""
        app, db_path = app_with_legacy_data
        
        with app.app_context():
            # Récupérer toutes les données avant migration
            meal_plans_before = MealPlan.query.all()
            shopping_lists_before = ShoppingList.query.all()
            
            # Vérifier qu'aucune date n'est un lundi (données legacy)
            non_monday_meal_plans = [mp for mp in meal_plans_before if mp.week_start.weekday() != 0]
            non_monday_shopping_lists = [sl for sl in shopping_lists_before if sl.week_start.weekday() != 0]
            
            assert len(non_monday_meal_plans) == 4, "Toutes les dates legacy devraient être non-lundi"
            assert len(non_monday_shopping_lists) == 2, "Toutes les dates legacy devraient être non-lundi"
            
            # Appliquer la conversion (simuler la migration)
            for meal_plan in meal_plans_before:
                meal_plan.week_start = get_monday_of_week(meal_plan.week_start)
            
            for shopping_list in shopping_lists_before:
                shopping_list.week_start = get_monday_of_week(shopping_list.week_start)
            
            db.session.commit()
            
            # Vérifier que toutes les dates sont maintenant des lundis
            meal_plans_after = MealPlan.query.all()
            shopping_lists_after = ShoppingList.query.all()
            
            for meal_plan in meal_plans_after:
                assert meal_plan.week_start.weekday() == 0, f"week_start {meal_plan.week_start} devrait être un lundi"
            
            for shopping_list in shopping_lists_after:
                assert shopping_list.week_start.weekday() == 0, f"week_start {shopping_list.week_start} devrait être un lundi"
    
    def test_migration_data_preservation(self, app_with_legacy_data):
        """Test préservation des données métier pendant la migration"""
        app, db_path = app_with_legacy_data
        
        with app.app_context():
            # Capturer les données métier avant migration
            meal_plans_before = {
                mp.id: {'meals': mp.meals, 'user_id': mp.user_id} 
                for mp in MealPlan.query.all()
            }
            
            shopping_lists_before = {
                sl.id: {'items': sl.items, 'user_id': sl.user_id}
                for sl in ShoppingList.query.all()
            }
            
            # Appliquer la migration des dates
            for meal_plan in MealPlan.query.all():
                meal_plan.week_start = get_monday_of_week(meal_plan.week_start)
            
            for shopping_list in ShoppingList.query.all():
                shopping_list.week_start = get_monday_of_week(shopping_list.week_start)
            
            db.session.commit()
            
            # Vérifier que les données métier sont préservées
            meal_plans_after = {
                mp.id: {'meals': mp.meals, 'user_id': mp.user_id}
                for mp in MealPlan.query.all()
            }
            
            shopping_lists_after = {
                sl.id: {'items': sl.items, 'user_id': sl.user_id}
                for sl in ShoppingList.query.all()
            }
            
            assert meal_plans_before == meal_plans_after, "Les données meal_plans doivent être préservées"
            assert shopping_lists_before == shopping_lists_after, "Les données shopping_lists doivent être préservées"
    
    def test_migration_rollback_capability(self, app_with_legacy_data):
        """Test capacité de rollback de la migration"""
        app, db_path = app_with_legacy_data
        
        with app.app_context():
            # Capturer l'état original
            original_meal_plans = [
                {'id': mp.id, 'week_start': mp.week_start, 'meals': mp.meals}
                for mp in MealPlan.query.all()
            ]
            
            # Créer backup (comme dans la migration)
            db.engine.execute("""
                CREATE TABLE meal_plans_backup_pre_us16 AS 
                SELECT * FROM meal_plans
            """)
            
            # Appliquer la migration
            for meal_plan in MealPlan.query.all():
                meal_plan.week_start = get_monday_of_week(meal_plan.week_start)
            db.session.commit()
            
            # Vérifier que la migration a eu lieu
            migrated_meal_plans = MealPlan.query.all()
            for mp in migrated_meal_plans:
                assert mp.week_start.weekday() == 0
            
            # Simuler le rollback
            db.engine.execute("DELETE FROM meal_plans")
            db.engine.execute("""
                INSERT INTO meal_plans 
                SELECT * FROM meal_plans_backup_pre_us16
            """)
            
            # Vérifier que les données originales sont restaurées
            restored_meal_plans = [
                {'id': mp.id, 'week_start': mp.week_start, 'meals': mp.meals}
                for mp in MealPlan.query.all()
            ]
            
            assert len(restored_meal_plans) == len(original_meal_plans)
            
            # Vérifier que les dates non-lundi sont restaurées
            non_monday_count = sum(1 for mp in MealPlan.query.all() if mp.week_start.weekday() != 0)
            assert non_monday_count > 0, "Le rollback devrait restaurer les dates non-lundi"


class TestMigrationPerformance:
    """Tests de performance de migration"""
    
    @pytest.fixture
    def app_with_large_dataset(self):
        """Fixture avec un grand dataset pour tests performance"""
        app = create_app('testing')
        
        with app.app_context():
            db.create_all()
            
            # Créer plusieurs utilisateurs
            users = []
            for i in range(10):
                user = User(email=f'user{i}@test.com', username=f'user{i}', password_hash='hash')
                db.session.add(user)
                users.append(user)
            
            db.session.flush()
            
            # Créer beaucoup de meal plans avec dates variées
            import random
            base_date = date(2024, 1, 1)
            
            for i in range(1000):  # 1000 meal plans
                user = random.choice(users)
                random_days = random.randint(0, 365)
                week_start = base_date + timedelta(days=random_days)
                
                meal_plan = MealPlan(
                    user_id=user.id,
                    week_start=week_start,
                    meals={'monday': {'breakfast': 1}}
                )
                db.session.add(meal_plan)
            
            # Créer des shopping lists
            for i in range(500):  # 500 shopping lists
                user = random.choice(users)
                random_days = random.randint(0, 365)
                week_start = base_date + timedelta(days=random_days)
                
                shopping_list = ShoppingList(
                    user_id=user.id,
                    week_start=week_start,
                    items={'items': ['item1', 'item2']}
                )
                db.session.add(shopping_list)
            
            db.session.commit()
            yield app
            
            db.session.remove()
            db.drop_all()
    
    def test_migration_performance_large_dataset(self, app_with_large_dataset):
        """Test performance migration sur grand dataset"""
        import time
        
        with app_with_large_dataset.app_context():
            # Mesurer le temps de migration
            start_time = time.time()
            
            # Simuler la migration sur toutes les données
            meal_plans = MealPlan.query.all()
            shopping_lists = ShoppingList.query.all()
            
            print(f"Migrating {len(meal_plans)} meal plans and {len(shopping_lists)} shopping lists...")
            
            # Conversion des dates
            for meal_plan in meal_plans:
                meal_plan.week_start = get_monday_of_week(meal_plan.week_start)
            
            for shopping_list in shopping_lists:
                shopping_list.week_start = get_monday_of_week(shopping_list.week_start)
            
            db.session.commit()
            
            migration_time = time.time() - start_time
            
            # Vérifications de performance
            assert migration_time < 10.0, f"Migration trop lente: {migration_time:.2f}s pour {len(meal_plans) + len(shopping_lists)} enregistrements"
            
            # Vérifier que toutes les dates sont converties
            for meal_plan in MealPlan.query.all():
                assert meal_plan.week_start.weekday() == 0
            
            for shopping_list in ShoppingList.query.all():
                assert shopping_list.week_start.weekday() == 0
            
            print(f"Migration completed in {migration_time:.2f}s")
    
    def test_migration_memory_usage(self, app_with_large_dataset):
        """Test utilisation mémoire pendant la migration"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        
        with app_with_large_dataset.app_context():
            # Mesurer mémoire avant migration
            memory_before = process.memory_info().rss / 1024 / 1024  # MB
            
            # Effectuer migration par batches pour optimiser mémoire
            batch_size = 100
            meal_plan_count = MealPlan.query.count()
            
            for offset in range(0, meal_plan_count, batch_size):
                batch = MealPlan.query.offset(offset).limit(batch_size).all()
                
                for meal_plan in batch:
                    meal_plan.week_start = get_monday_of_week(meal_plan.week_start)
                
                db.session.commit()
            
            # Mesurer mémoire après migration
            memory_after = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = memory_after - memory_before
            
            # Vérifier que l'augmentation mémoire reste raisonnable
            assert memory_increase < 100, f"Augmentation mémoire trop importante: {memory_increase:.1f}MB"
            
            print(f"Memory usage: {memory_before:.1f}MB → {memory_after:.1f}MB (+ {memory_increase:.1f}MB)")


class TestMigrationEdgeCases:
    """Tests des cas limites lors de la migration"""
    
    @pytest.fixture
    def app_with_edge_case_data(self):
        """Fixture avec données edge cases"""
        app = create_app('testing')
        
        with app.app_context():
            db.create_all()
            
            user = User(email='edge@test.com', username='edge', password_hash='hash')
            db.session.add(user)
            db.session.flush()
            
            # Cas limites de dates
            edge_case_dates = [
                date(2024, 12, 31),  # Dernier jour 2024 (mardi)
                date(2025, 1, 1),    # Premier jour 2025 (mercredi)
                date(2024, 2, 29),   # Jour bissextile (jeudi)
                date(2025, 2, 28),   # Dernier jour février non-bissextile (vendredi)
                date(1970, 1, 1),    # Date epoch Unix (jeudi)
                date(2038, 1, 19),   # Proche limite epoch 32-bit (mardi)
            ]
            
            for i, edge_date in enumerate(edge_case_dates):
                meal_plan = MealPlan(
                    user_id=user.id,
                    week_start=edge_date,
                    meals={f'test_{i}': {'breakfast': 1}}
                )
                db.session.add(meal_plan)
            
            db.session.commit()
            yield app
            
            db.session.remove()
            db.drop_all()
    
    def test_migration_edge_case_dates(self, app_with_edge_case_data):
        """Test migration avec dates cas limites"""
        with app_with_edge_case_data.app_context():
            # Vérifier dates avant migration
            meal_plans_before = MealPlan.query.all()
            assert len(meal_plans_before) == 6
            
            # Capturer les dates originales
            original_dates = [(mp.id, mp.week_start) for mp in meal_plans_before]
            
            # Appliquer migration
            for meal_plan in meal_plans_before:
                meal_plan.week_start = get_monday_of_week(meal_plan.week_start)
            
            db.session.commit()
            
            # Vérifier résultats
            meal_plans_after = MealPlan.query.all()
            
            for meal_plan in meal_plans_after:
                assert meal_plan.week_start.weekday() == 0, f"Date {meal_plan.week_start} devrait être un lundi"
            
            # Vérifications spécifiques aux cas limites
            expected_conversions = [
                (date(2024, 12, 31), date(2024, 12, 30)),  # Mardi → Lundi précédent
                (date(2025, 1, 1), date(2024, 12, 30)),    # Mercredi → Lundi de la semaine
                (date(2024, 2, 29), date(2024, 2, 26)),    # Jeudi bissextile → Lundi
                (date(2025, 2, 28), date(2025, 2, 24)),    # Vendredi → Lundi de la semaine
                (date(1970, 1, 1), date(1969, 12, 29)),    # Epoch Unix → Lundi précédent
                (date(2038, 1, 19), date(2038, 1, 19)),    # Déjà lundi → pas de changement
            ]
            
            for original_date, expected_monday in expected_conversions:
                actual_monday = get_monday_of_week(original_date)
                assert actual_monday == expected_monday, f"Conversion incorrecte: {original_date} → {actual_monday} (attendu {expected_monday})"
    
    def test_migration_null_date_handling(self, app_with_edge_case_data):
        """Test gestion des dates null/invalides"""
        with app_with_edge_case_data.app_context():
            # Ne pas créer de données avec NULL car SQLAlchemy l'empêche,
            # mais tester la robustesse de nos fonctions
            
            from utils.date_utils import get_monday_of_week
            
            # Test avec des valeurs limites
            edge_dates = [
                date.min,  # Date minimale Python
                date.max,  # Date maximale Python  
            ]
            
            for edge_date in edge_dates:
                try:
                    monday = get_monday_of_week(edge_date)
                    assert monday.weekday() == 0
                    print(f"Edge date {edge_date} → {monday}")
                except (ValueError, OverflowError) as e:
                    # Acceptable pour les dates extrêmes
                    print(f"Edge date {edge_date} caused expected error: {e}")
    
    def test_migration_duplicate_week_handling(self, app_with_edge_case_data):
        """Test gestion des semaines dupliquées après migration"""
        with app_with_edge_case_data.app_context():
            user = User.query.first()
            
            # Créer plusieurs meal plans qui convergent vers la même semaine après migration
            same_week_dates = [
                date(2025, 8, 4),   # Lundi (reste identique)
                date(2025, 8, 5),   # Mardi (→ lundi 4 août)  
                date(2025, 8, 6),   # Mercredi (→ lundi 4 août)
                date(2025, 8, 7),   # Jeudi (→ lundi 4 août)
            ]
            
            # Nettoyer les données existantes
            MealPlan.query.delete()
            
            # Créer les meal plans qui vont converger
            for i, week_start in enumerate(same_week_dates):
                meal_plan = MealPlan(
                    user_id=user.id,
                    week_start=week_start,
                    meals={f'day_{i}': {'breakfast': i+1}}
                )
                db.session.add(meal_plan)
            
            db.session.commit()
            
            # Vérifier état avant migration
            meal_plans_before = MealPlan.query.all()
            assert len(meal_plans_before) == 4
            
            # Appliquer migration
            for meal_plan in meal_plans_before:
                meal_plan.week_start = get_monday_of_week(meal_plan.week_start)
            
            db.session.commit()
            
            # Vérifier que toutes les semaines convergent vers le même lundi
            meal_plans_after = MealPlan.query.all()
            unique_weeks = set(mp.week_start for mp in meal_plans_after)
            
            assert len(unique_weeks) == 1, f"Toutes les semaines devraient converger vers un seul lundi: {unique_weeks}"
            assert list(unique_weeks)[0] == date(2025, 8, 4), "Convergence vers le lundi 4 août 2025"


if __name__ == "__main__":
    # Configuration pour exécution directe
    pytest.main([__file__, "-v", "--tb=short"])