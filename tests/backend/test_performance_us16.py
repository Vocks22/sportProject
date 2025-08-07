"""
Tests de performance pour US1.6 - Optimisation calculs calendrier ISO 8601
Tests de performance et benchmarks pour valider les optimisations calendrier

Coverage: Performance calculs date, queries DB, charge utilisateur
Focus: Scalabilité, optimisation, métriques temps réponse
"""

import pytest
import time
import statistics
import psutil
import os
from datetime import date, timedelta, datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import sys

# Ajouter les chemins vers les modules backend
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'backend'))

from main import create_app
from database.config import db
from models.meal_plan import MealPlan
from models.shopping_list import ShoppingList
from models.user import User
from utils.date_utils import (
    get_monday_of_week, get_sunday_of_week, get_week_range_iso8601,
    batch_convert_week_starts, validate_database_week_starts,
    format_week_display, next_monday, previous_monday
)


class TestDateUtilsPerformance:
    """Tests de performance des utilitaires de date"""
    
    def test_get_monday_performance_single_calls(self):
        """Test performance calculs individuels get_monday_of_week"""
        # Générer 10000 dates aléatoires sur 10 ans
        import random
        base_date = date(2020, 1, 1)
        test_dates = []
        
        for _ in range(10000):
            random_days = random.randint(0, 365 * 10)
            test_date = base_date + timedelta(days=random_days)
            test_dates.append(test_date)
        
        # Mesurer le temps d'exécution
        start_time = time.time()
        
        results = []
        for test_date in test_dates:
            monday = get_monday_of_week(test_date)
            results.append(monday)
        
        execution_time = time.time() - start_time
        
        # Vérifications de performance
        avg_time_per_calc = (execution_time / len(test_dates)) * 1000  # ms
        
        assert execution_time < 1.0, f"10k calculs trop lents: {execution_time:.3f}s"
        assert avg_time_per_calc < 0.1, f"Temps moyen par calcul trop élevé: {avg_time_per_calc:.3f}ms"
        
        # Vérifier la cohérence des résultats
        for monday in results:
            assert monday.weekday() == 0, "Tous les résultats doivent être des lundis"
        
        print(f"✅ 10k calculs get_monday_of_week: {execution_time:.3f}s ({avg_time_per_calc:.3f}ms/calcul)")
    
    def test_batch_operations_performance(self):
        """Test performance opérations en lot"""
        # Créer une grande liste de dates
        base_date = date(2020, 1, 1)
        large_date_list = []
        
        for i in range(50000):  # 50k dates
            test_date = base_date + timedelta(days=i % (365 * 5))
            large_date_list.append(test_date)
        
        # Test performance batch_convert_week_starts
        start_time = time.time()
        batch_results = batch_convert_week_starts(large_date_list)
        batch_time = time.time() - start_time
        
        # Comparaison avec appels individuels
        start_time = time.time()
        individual_results = [(d, get_monday_of_week(d)) for d in large_date_list]
        individual_time = time.time() - start_time
        
        # Vérifications
        assert len(batch_results) == len(individual_results) == 50000
        assert batch_time < 5.0, f"Batch operation trop lente: {batch_time:.3f}s"
        
        # La version batch ne devrait pas être significativement plus lente
        performance_ratio = batch_time / individual_time
        assert performance_ratio < 1.5, f"Batch operation pas optimale: {performance_ratio:.2f}x plus lente"
        
        print(f"✅ 50k conversions batch: {batch_time:.3f}s vs individual: {individual_time:.3f}s")
        print(f"   Performance ratio: {performance_ratio:.2f}x")
    
    def test_week_formatting_performance(self):
        """Test performance formatage d'affichage des semaines"""
        # Tester sur toutes les semaines d'une année
        start_date = date(2025, 1, 6)  # Premier lundi de 2025
        weeks_2025 = []
        
        current_monday = start_date
        while current_monday.year == 2025:
            weeks_2025.append(current_monday)
            current_monday += timedelta(weeks=1)
        
        # Test performance formatage français
        start_time = time.time()
        french_formats = [format_week_display(monday, 'fr') for monday in weeks_2025]
        french_time = time.time() - start_time
        
        # Test performance formatage anglais
        start_time = time.time()
        english_formats = [format_week_display(monday, 'en') for monday in weeks_2025]
        english_time = time.time() - start_time
        
        # Vérifications
        assert len(french_formats) == len(weeks_2025)
        assert len(english_formats) == len(weeks_2025)
        assert french_time < 0.5, f"Formatage français trop lent: {french_time:.3f}s"
        assert english_time < 0.5, f"Formatage anglais trop lent: {english_time:.3f}s"
        
        # Vérifier la cohérence des formats
        for french_text in french_formats:
            assert 'Semaine du' in french_text
            assert '2025' in french_text
        
        print(f"✅ Formatage {len(weeks_2025)} semaines - FR: {french_time:.3f}s, EN: {english_time:.3f}s")
    
    def test_memory_usage_large_operations(self):
        """Test utilisation mémoire pour les grandes opérations"""
        process = psutil.Process(os.getpid())
        
        # Mesurer mémoire initiale
        memory_before = process.memory_info().rss / 1024 / 1024  # MB
        
        # Opération avec beaucoup de dates
        large_date_range = [
            date(2020, 1, 1) + timedelta(days=i) 
            for i in range(100000)  # 100k dates (~274 années)
        ]
        
        # Calculer tous les lundis
        monday_results = [get_monday_of_week(d) for d in large_date_range]
        
        # Mesurer mémoire après opération
        memory_after = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = memory_after - memory_before
        
        # Nettoyer
        del large_date_range
        del monday_results
        
        # Vérifications mémoire
        assert memory_increase < 200, f"Augmentation mémoire excessive: {memory_increase:.1f}MB"
        
        print(f"✅ Mémoire 100k dates: {memory_before:.1f}MB → {memory_after:.1f}MB (+{memory_increase:.1f}MB)")


class TestDatabasePerformanceUS16:
    """Tests de performance base de données avec logique ISO 8601"""
    
    @pytest.fixture
    def app_with_performance_data(self):
        """Fixture avec dataset important pour tests performance"""
        app = create_app('testing')
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        with app.app_context():
            db.create_all()
            
            # Créer 100 utilisateurs
            users = []
            for i in range(100):
                user = User(
                    email=f'perf_user_{i}@test.com',
                    username=f'perfuser{i}',
                    password_hash='hash'
                )
                db.session.add(user)
                users.append(user)
            
            db.session.flush()
            
            # Créer des meal plans sur 2 ans (52 semaines * 2 * 100 utilisateurs = 10400 records)
            import random
            base_monday = get_monday_of_week(date(2024, 1, 1))
            
            for user in users:
                for week_num in range(104):  # 2 ans de semaines
                    week_monday = base_monday + timedelta(weeks=week_num)
                    
                    # Pas tous les utilisateurs ont des plans chaque semaine
                    if random.random() < 0.7:  # 70% de probabilité
                        meal_plan = MealPlan(
                            user_id=user.id,
                            week_start=week_monday,
                            meals={
                                'monday': {'breakfast': random.randint(1, 10)},
                                'friday': {'dinner': random.randint(1, 10)}
                            }
                        )
                        db.session.add(meal_plan)
            
            # Créer shopping lists
            for user in users:
                for week_num in range(0, 104, 2):  # Une liste toutes les 2 semaines
                    week_monday = base_monday + timedelta(weeks=week_num)
                    
                    shopping_list = ShoppingList(
                        user_id=user.id,
                        week_start=week_monday,
                        items={'items': ['item1', 'item2', 'item3']}
                    )
                    db.session.add(shopping_list)
            
            db.session.commit()
            
            print(f"Created performance dataset:")
            print(f"  - Users: {len(users)}")
            print(f"  - Meal plans: {MealPlan.query.count()}")
            print(f"  - Shopping lists: {ShoppingList.query.count()}")
            
            yield app
            
            db.session.remove()
            db.drop_all()
    
    def test_week_start_index_performance(self, app_with_performance_data):
        """Test performance des requêtes avec index sur week_start"""
        with app_with_performance_data.app_context():
            test_monday = get_monday_of_week(date(2024, 6, 15))  # Milieu de dataset
            
            # Test requête simple par week_start
            start_time = time.time()
            meal_plans = MealPlan.query.filter(MealPlan.week_start == test_monday).all()
            query_time = time.time() - start_time
            
            assert query_time < 0.1, f"Requête week_start trop lente: {query_time:.3f}s"
            
            # Test requête par plage de dates
            start_monday = test_monday - timedelta(weeks=4)
            end_monday = test_monday + timedelta(weeks=4)
            
            start_time = time.time()
            range_plans = MealPlan.query.filter(
                MealPlan.week_start >= start_monday,
                MealPlan.week_start <= end_monday
            ).all()
            range_query_time = time.time() - start_time
            
            assert range_query_time < 0.2, f"Requête plage dates trop lente: {range_query_time:.3f}s"
            
            print(f"✅ Query performance - Single week: {query_time:.3f}s, Range: {range_query_time:.3f}s")
            print(f"   Results: {len(meal_plans)} single, {len(range_plans)} range")
    
    def test_user_week_filtering_performance(self, app_with_performance_data):
        """Test performance filtrage par utilisateur et semaine"""
        with app_with_performance_data.app_context():
            # Sélectionner un utilisateur avec beaucoup de données
            user = User.query.first()
            test_monday = get_monday_of_week(date(2024, 6, 15))
            
            # Test filtrage combiné user + week
            start_time = time.time()
            user_week_plans = MealPlan.query.filter(
                MealPlan.user_id == user.id,
                MealPlan.week_start == test_monday
            ).all()
            combined_query_time = time.time() - start_time
            
            assert combined_query_time < 0.05, f"Requête combinée trop lente: {combined_query_time:.3f}s"
            
            # Test récupération de toutes les semaines d'un utilisateur
            start_time = time.time()
            all_user_plans = MealPlan.query.filter(
                MealPlan.user_id == user.id
            ).order_by(MealPlan.week_start).all()
            user_query_time = time.time() - start_time
            
            assert user_query_time < 0.1, f"Requête utilisateur trop lente: {user_query_time:.3f}s"
            
            print(f"✅ User query performance - Combined: {combined_query_time:.3f}s, All user: {user_query_time:.3f}s")
            print(f"   User plans: {len(all_user_plans)}")
    
    def test_bulk_validation_performance(self, app_with_performance_data):
        """Test performance validation en lot des dates"""
        with app_with_performance_data.app_context():
            # Récupérer toutes les dates week_start
            all_meal_plan_dates = [mp.week_start for mp in MealPlan.query.all()]
            all_shopping_list_dates = [sl.week_start for sl in ShoppingList.query.all()]
            
            # Test validation meal plans
            start_time = time.time()
            mp_valid, mp_errors = validate_database_week_starts(all_meal_plan_dates)
            mp_validation_time = time.time() - start_time
            
            # Test validation shopping lists
            start_time = time.time()
            sl_valid, sl_errors = validate_database_week_starts(all_shopping_list_dates)
            sl_validation_time = time.time() - start_time
            
            # Vérifications performance
            assert mp_validation_time < 1.0, f"Validation meal plans trop lente: {mp_validation_time:.3f}s"
            assert sl_validation_time < 1.0, f"Validation shopping lists trop lente: {sl_validation_time:.3f}s"
            
            # Toutes les dates devraient être valides (lundis)
            assert mp_valid is True, f"Dates meal plans invalides: {len(mp_errors)} erreurs"
            assert sl_valid is True, f"Dates shopping lists invalides: {len(sl_errors)} erreurs"
            
            print(f"✅ Bulk validation - MP: {mp_validation_time:.3f}s ({len(all_meal_plan_dates)} dates)")
            print(f"                    SL: {sl_validation_time:.3f}s ({len(all_shopping_list_dates)} dates)")


class TestConcurrentAccessPerformance:
    """Tests de performance avec accès concurrent"""
    
    @pytest.fixture
    def app_concurrent(self):
        """Fixture pour tests concurrents"""
        app = create_app('testing')
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'pool_pre_ping': True,
            'pool_recycle': 300,
        }
        
        with app.app_context():
            db.create_all()
            
            # Créer des utilisateurs pour tests concurrents
            for i in range(20):
                user = User(
                    email=f'concurrent_user_{i}@test.com',
                    username=f'concuser{i}',
                    password_hash='hash'
                )
                db.session.add(user)
            
            db.session.commit()
            yield app
            
            db.session.remove()
            db.drop_all()
    
    def test_concurrent_meal_plan_creation(self, app_concurrent):
        """Test création simultanée de meal plans"""
        def create_meal_plan_worker(user_id, week_offset):
            with app_concurrent.app_context():
                week_monday = get_monday_of_week(date.today()) + timedelta(weeks=week_offset)
                
                meal_plan = MealPlan(
                    user_id=user_id,
                    week_start=week_monday,
                    meals={'monday': {'breakfast': 1}}
                )
                
                try:
                    db.session.add(meal_plan)
                    db.session.commit()
                    return {'success': True, 'user_id': user_id, 'week': week_monday}
                except Exception as e:
                    db.session.rollback()
                    return {'success': False, 'error': str(e)}
        
        # Lancer 20 créations simultanées
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            
            for user_id in range(1, 21):  # Users 1-20
                future = executor.submit(create_meal_plan_worker, user_id, user_id % 5)
                futures.append(future)
            
            start_time = time.time()
            results = [future.result() for future in as_completed(futures)]
            concurrent_time = time.time() - start_time
        
        # Vérifications
        successful_creates = [r for r in results if r['success']]
        failed_creates = [r for r in results if not r['success']]
        
        assert len(successful_creates) == 20, f"Échecs concurrence: {len(failed_creates)} failed"
        assert concurrent_time < 2.0, f"Créations concurrentes trop lentes: {concurrent_time:.3f}s"
        
        print(f"✅ 20 créations concurrentes: {concurrent_time:.3f}s")
        print(f"   Succès: {len(successful_creates)}, Échecs: {len(failed_creates)}")
    
    def test_concurrent_date_calculations(self):
        """Test calculs de dates en parallèle"""
        def date_calculation_worker(date_batch):
            results = []
            for test_date in date_batch:
                monday = get_monday_of_week(test_date)
                sunday = get_sunday_of_week(test_date)
                week_range = get_week_range_iso8601(test_date)
                
                results.append({
                    'original': test_date,
                    'monday': monday,
                    'sunday': sunday,
                    'range': week_range
                })
            return results
        
        # Créer des batches de dates
        import random
        base_date = date(2024, 1, 1)
        all_dates = [base_date + timedelta(days=random.randint(0, 730)) for _ in range(10000)]
        
        # Diviser en batches pour traitement parallèle
        batch_size = 1000
        date_batches = [all_dates[i:i+batch_size] for i in range(0, len(all_dates), batch_size)]
        
        # Traitement séquentiel pour comparaison
        start_time = time.time()
        sequential_results = date_calculation_worker(all_dates)
        sequential_time = time.time() - start_time
        
        # Traitement parallèle
        with ThreadPoolExecutor(max_workers=4) as executor:
            start_time = time.time()
            
            futures = [executor.submit(date_calculation_worker, batch) for batch in date_batches]
            parallel_results = []
            
            for future in as_completed(futures):
                parallel_results.extend(future.result())
            
            parallel_time = time.time() - start_time
        
        # Vérifications
        assert len(sequential_results) == len(parallel_results) == 10000
        
        # Le traitement parallèle devrait être plus rapide sur multi-core
        speedup = sequential_time / parallel_time
        print(f"✅ 10k calculs dates - Séquentiel: {sequential_time:.3f}s, Parallèle: {parallel_time:.3f}s")
        print(f"   Speedup: {speedup:.2f}x")
        
        # Vérifier cohérence des résultats
        for seq_result, par_result in zip(sequential_results[:100], parallel_results[:100]):
            assert seq_result['monday'] == par_result['monday']
            assert seq_result['sunday'] == par_result['sunday']


class TestRegressionPerformanceUS16:
    """Tests de régression performance entre versions"""
    
    def test_performance_baseline_establishment(self):
        """Établir baseline de performance pour régression"""
        # Tester différentes opérations avec métriques
        performance_metrics = {}
        
        # Test 1: Calculs de dates basiques
        test_dates = [date(2024, 1, 1) + timedelta(days=i) for i in range(1000)]
        
        start_time = time.time()
        monday_results = [get_monday_of_week(d) for d in test_dates]
        performance_metrics['basic_date_calc'] = time.time() - start_time
        
        # Test 2: Formatage d'affichage
        mondates = [get_monday_of_week(d) for d in test_dates[::10]]  # Sous-échantillon
        
        start_time = time.time()
        format_results = [format_week_display(monday, 'fr') for monday in mondates]
        performance_metrics['date_formatting'] = time.time() - start_time
        
        # Test 3: Opérations batch
        start_time = time.time()
        batch_results = batch_convert_week_starts(test_dates)
        performance_metrics['batch_operations'] = time.time() - start_time
        
        # Sauvegarder les métriques baseline
        baseline = {
            'basic_date_calc': 0.1,    # 100ms pour 1000 calculs
            'date_formatting': 0.05,   # 50ms pour 100 formatages
            'batch_operations': 0.2,   # 200ms pour 1000 conversions batch
        }
        
        # Vérifications régression
        for metric, actual_time in performance_metrics.items():
            baseline_time = baseline[metric]
            regression_factor = actual_time / baseline_time
            
            assert regression_factor < 2.0, f"Régression performance {metric}: {regression_factor:.2f}x plus lent"
            
            if regression_factor > 1.5:
                print(f"⚠️  Possible régression {metric}: {regression_factor:.2f}x plus lent")
            else:
                print(f"✅ Performance OK {metric}: {regression_factor:.2f}x vs baseline")
    
    def test_memory_regression_tracking(self):
        """Suivi régression utilisation mémoire"""
        process = psutil.Process(os.getpid())
        
        # Mesurer mémoire de base
        baseline_memory = process.memory_info().rss / 1024 / 1024
        
        # Opération intensive en mémoire
        large_dataset = []
        for i in range(100000):
            test_date = date(2020, 1, 1) + timedelta(days=i % 1000)
            monday = get_monday_of_week(test_date)
            formatted = format_week_display(monday, 'fr')
            
            large_dataset.append({
                'original': test_date,
                'monday': monday,
                'formatted': formatted
            })
        
        # Mesurer mémoire après opération
        peak_memory = process.memory_info().rss / 1024 / 1024
        memory_increase = peak_memory - baseline_memory
        
        # Nettoyer
        del large_dataset
        
        # Vérification régression mémoire
        memory_baseline = 100  # MB acceptable pour 100k opérations
        regression_factor = memory_increase / memory_baseline
        
        assert regression_factor < 2.0, f"Régression mémoire: {regression_factor:.2f}x plus que baseline"
        
        print(f"✅ Mémoire 100k ops: {memory_increase:.1f}MB (baseline: {memory_baseline}MB)")
        print(f"   Facteur: {regression_factor:.2f}x")


if __name__ == "__main__":
    # Configuration pour exécution directe avec métriques détaillées
    pytest.main([__file__, "-v", "--tb=short", "-s"])  # -s pour voir les prints