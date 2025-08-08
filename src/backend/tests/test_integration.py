"""
Integration tests for US1.8 Meal Tracking feature
Tests the complete workflow from API to database and back
"""

import pytest
from datetime import date, datetime, time, timedelta
import json
from unittest.mock import patch

from database import db
from models.meal_tracking import MealTracking, DailyNutritionSummary, MealStatus
from models.user import User
from services.meal_tracking_service import MealTrackingService
from test_fixtures import MealTrackingDataFactory


class TestMealTrackingIntegration:
    """Integration tests for complete meal tracking workflows"""
    
    def test_complete_daily_workflow(self, client, sample_user, sample_meal_plan):
        """Test complete daily meal tracking workflow"""
        today = date.today()
        sample_meal_plan.is_active = True
        db.session.commit()
        
        # Step 1: Get today's meals (should create from plan)
        response = client.get(f'/meal-tracking/today?user_id={sample_user.id}')
        assert response.status_code == 200
        
        data = response.get_json()
        trackings = data['meal_trackings']
        assert len(trackings) >= 1
        
        tracking_id = trackings[0]['id']
        
        # Step 2: Mark first meal as consumed
        consume_data = {
            'user_id': sample_user.id,
            'consumption_data': {
                'nutrition': {'calories': 450, 'protein': 30},
                'satisfaction_rating': 5,
                'notes': 'Délicieux!'
            }
        }
        
        response = client.post(f'/meal-tracking/{tracking_id}/consume', json=consume_data)
        assert response.status_code == 200
        
        # Step 3: Adjust second meal portions
        if len(trackings) > 1:
            second_tracking_id = trackings[1]['id']
            adjust_data = {
                'user_id': sample_user.id,
                'portion_multiplier': 1.5
            }
            
            response = client.put(f'/meal-tracking/{second_tracking_id}/adjust', json=adjust_data)
            assert response.status_code == 200
        
        # Step 4: Skip third meal if exists
        if len(trackings) > 2:
            third_tracking_id = trackings[2]['id']
            skip_data = {
                'user_id': sample_user.id,
                'skip_data': {'reason': 'Pas faim'}
            }
            
            response = client.post(f'/meal-tracking/{third_tracking_id}/skip', json=skip_data)
            assert response.status_code == 200
        
        # Step 5: Get daily summary
        with patch.object(User, 'get_daily_targets') as mock_targets:
            mock_targets.return_value = {
                'calories': 2000, 'protein': 150, 'carbs': 250, 'fat': 65,
                'fiber': 30, 'sodium': 2300, 'sugar': 50
            }
            
            response = client.get(f'/meal-tracking/summary/{today.isoformat()}?user_id={sample_user.id}')
            assert response.status_code == 200
            
            summary_data = response.get_json()['daily_summary']
            assert summary_data['meals_consumed'] >= 1
            assert summary_data['actual_nutrition']['calories'] >= 450
    
    def test_week_tracking_patterns(self, client, sample_user, meal_tracking_factory):
        """Test tracking patterns over a week"""
        # Create realistic week data
        trackings = meal_tracking_factory.create_week_of_meals(sample_user.id)
        
        # Test daily summaries for each day
        week_start = date.today() - timedelta(days=7)
        daily_summaries = []
        
        with patch.object(User, 'get_daily_targets') as mock_targets:
            mock_targets.return_value = {
                'calories': 2000, 'protein': 150, 'carbs': 250, 'fat': 65,
                'fiber': 30, 'sodium': 2300, 'sugar': 50
            }
            
            for day in range(7):
                current_date = week_start + timedelta(days=day)
                
                # Calculate daily summary
                summary = MealTrackingService.calculate_daily_summary(
                    user_id=sample_user.id,
                    summary_date=current_date
                )
                daily_summaries.append(summary)
                
                # Verify summary data consistency
                day_trackings = [t for t in trackings if t.meal_date == current_date]
                expected_planned_calories = sum(t.planned_calories for t in day_trackings)
                
                assert abs(summary.planned_calories - expected_planned_calories) < 0.01
        
        # Test weekly summary
        weekly_data = MealTrackingService.get_weekly_summary(sample_user.id, week_start)
        
        assert weekly_data['days_tracked'] == 7
        assert weekly_data['total_meals_planned'] > 0
        assert 'avg_calories' in weekly_data
        assert 'weekly_completion_rate' in weekly_data
    
    def test_adherence_trend_analysis(self, client, sample_user, meal_tracking_factory):
        """Test adherence trend analysis over time"""
        # Create progression data
        summaries = meal_tracking_factory.create_adherence_progression_data(sample_user.id, days=30)
        
        # Test trend analysis API
        response = client.get(f'/meal-tracking/patterns?user_id={sample_user.id}&days=30')
        assert response.status_code == 200
        
        data = response.get_json()
        trends = data['adherence_trends']
        
        assert 'plan_adherence_trend' in trends
        assert 'target_adherence_trend' in trends
        assert 'completion_trend' in trends
        assert trends['data_points'] == 30
        
        # Should detect improvement trend
        assert trends['plan_adherence_trend'] in ['improving', 'stable']
    
    def test_monthly_reporting_integration(self, client, sample_user):
        """Test comprehensive monthly reporting"""
        # Create month of data
        month_start = date(2025, 8, 1)
        
        with patch.object(User, 'get_daily_targets') as mock_targets:
            mock_targets.return_value = {
                'calories': 2000, 'protein': 150, 'carbs': 250, 'fat': 65,
                'fiber': 30, 'sodium': 2300, 'sugar': 50
            }
            
            # Create daily summaries for August 2025
            for day in range(1, 32):  # August has 31 days
                try:
                    current_date = date(2025, 8, day)
                    
                    # Create some meal trackings
                    for meal_type in ['repas1', 'repas2', 'repas3']:
                        tracking = MealTracking(
                            user_id=sample_user.id,
                            meal_date=current_date,
                            meal_type=meal_type,
                            status=MealStatus.CONSUMED,
                            planned_calories=400,
                            planned_protein=25,
                            actual_calories=420,
                            actual_protein=27
                        )
                        db.session.add(tracking)
                    
                    # Calculate daily summary
                    MealTrackingService.calculate_daily_summary(
                        user_id=sample_user.id,
                        summary_date=current_date
                    )
                    
                except ValueError:
                    continue  # Skip invalid dates
        
        # Test monthly report API
        response = client.get(f'/meal-tracking/report/2025-08?user_id={sample_user.id}')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] == True
        
        monthly_summary = data['monthly_summary']
        assert monthly_summary['days_tracked'] == 31
        assert monthly_summary['total_meals_planned'] == 93  # 31 days * 3 meals
        assert 'avg_daily_calories' in monthly_summary
        assert 'calorie_target_success_rate' in monthly_summary
        
        # Should have weekly summaries
        assert len(data['weekly_summaries']) > 0
        
        # Should have daily summaries
        assert len(data['daily_summaries']) == 31
    
    def test_offline_sync_integration(self, client, sample_user):
        """Test offline mode synchronization"""
        # Create a meal tracking
        tracking = MealTracking(
            user_id=sample_user.id,
            meal_date=date.today(),
            meal_type='repas1',
            status=MealStatus.PLANNED,
            planned_calories=400,
            planned_protein=25
        )
        db.session.add(tracking)
        db.session.commit()
        
        # Simulate offline actions (this would normally be handled by the frontend)
        # For testing, we'll directly test the service sync functionality
        from services.meal_tracking_service import MealTrackingService
        
        # Mock pending actions (in real app, these come from frontend store)
        pending_actions = [
            {
                'id': '1',
                'type': 'MARK_CONSUMED',
                'trackingId': tracking.id,
                'data': {
                    'satisfaction_rating': 4,
                    'notes': 'Offline consumption'
                },
                'timestamp': datetime.now().timestamp()
            }
        ]
        
        # Test that actions can be synced when back online
        updated_tracking = MealTrackingService.update_meal_status(
            tracking_id=tracking.id,
            user_id=sample_user.id,
            status=MealStatus.CONSUMED,
            consumption_data={
                'satisfaction_rating': 4,
                'notes': 'Offline consumption'
            }
        )
        
        assert updated_tracking.status == MealStatus.CONSUMED
        assert updated_tracking.satisfaction_rating == 4
        assert updated_tracking.user_notes == 'Offline consumption'
    
    def test_data_consistency_across_operations(self, client, sample_user):
        """Test data consistency across multiple operations"""
        today = date.today()
        
        # Create initial tracking
        tracking = MealTracking(
            user_id=sample_user.id,
            meal_date=today,
            meal_type='repas1',
            status=MealStatus.PLANNED,
            planned_calories=500,
            planned_protein=30,
            planned_carbs=60,
            planned_fat=18
        )
        db.session.add(tracking)
        db.session.commit()
        
        # Operation 1: Mark as consumed
        consume_response = client.post(
            f'/meal-tracking/{tracking.id}/consume',
            json={
                'user_id': sample_user.id,
                'consumption_data': {
                    'nutrition': {'calories': 520, 'protein': 32},
                    'satisfaction_rating': 5
                }
            }
        )
        assert consume_response.status_code == 200
        
        # Verify tracking was updated
        updated_tracking = MealTracking.query.get(tracking.id)
        assert updated_tracking.status == MealStatus.CONSUMED
        assert updated_tracking.actual_calories == 520
        assert updated_tracking.satisfaction_rating == 5
        
        # Operation 2: Get updated tracking through API
        history_response = client.get(
            f'/meal-tracking/history?user_id={sample_user.id}&'
            f'start_date={today.isoformat()}&end_date={today.isoformat()}'
        )
        assert history_response.status_code == 200
        
        history_data = history_response.get_json()
        trackings = history_data['meal_trackings']
        assert len(trackings) == 1
        assert trackings[0]['status'] == 'consumed'
        assert trackings[0]['actual_nutrition']['calories'] == 520
        
        # Operation 3: Calculate daily summary
        with patch.object(User, 'get_daily_targets') as mock_targets:
            mock_targets.return_value = {
                'calories': 2000, 'protein': 150, 'carbs': 250, 'fat': 65,
                'fiber': 30, 'sodium': 2300, 'sugar': 50
            }
            
            summary_response = client.get(
                f'/meal-tracking/summary/{today.isoformat()}?user_id={sample_user.id}'
            )
            assert summary_response.status_code == 200
            
            summary_data = summary_response.get_json()['daily_summary']
            assert summary_data['actual_nutrition']['calories'] == 520
            assert summary_data['meals_consumed'] == 1
    
    def test_error_handling_integration(self, client, sample_user):
        """Test error handling across the system"""
        # Test API error handling
        response = client.get('/meal-tracking/today?user_id=99999')
        assert response.status_code == 404
        
        response = client.post('/meal-tracking/99999/consume', json={'user_id': sample_user.id})
        assert response.status_code == 404
        
        # Test invalid data handling
        response = client.post(
            '/meal-tracking/1/consume',
            json={
                'user_id': sample_user.id,
                'consumption_data': {
                    'satisfaction_rating': 10  # Invalid: > 5
                }
            }
        )
        assert response.status_code == 400
        
        # Test database constraint violations
        today = date.today()
        
        # Create first tracking
        tracking1 = MealTracking(
            user_id=sample_user.id,
            meal_date=today,
            meal_type='repas1',
            status=MealStatus.PLANNED
        )
        db.session.add(tracking1)
        db.session.commit()
        
        # Try to create duplicate (should fail due to unique constraint)
        tracking2 = MealTracking(
            user_id=sample_user.id,
            meal_date=today,
            meal_type='repas1',  # Same meal type, same date
            status=MealStatus.PLANNED
        )
        db.session.add(tracking2)
        
        with pytest.raises(Exception):  # Should raise IntegrityError
            db.session.commit()
        
        db.session.rollback()
    
    def test_performance_with_large_datasets(self, client, performance_test_data):
        """Test system performance with large datasets"""
        # performance_test_data fixture creates 10 users with 90 days of data each
        users = performance_test_data
        
        # Test loading user data doesn't timeout
        import time
        
        for user in users[:3]:  # Test first 3 users to avoid long test times
            start_time = time.time()
            
            # Test today's meal loading
            response = client.get(f'/meal-tracking/today?user_id={user.id}')
            
            load_time = time.time() - start_time
            assert load_time < 2.0  # Should load in under 2 seconds
            assert response.status_code == 200
            
            # Test pattern analysis
            start_time = time.time()
            response = client.get(f'/meal-tracking/patterns?user_id={user.id}&days=30')
            
            analysis_time = time.time() - start_time
            assert analysis_time < 5.0  # Should analyze in under 5 seconds
            assert response.status_code == 200
    
    def test_concurrent_operations(self, client, sample_user):
        """Test handling of concurrent operations on same data"""
        import threading
        import time
        
        # Create tracking
        tracking = MealTracking(
            user_id=sample_user.id,
            meal_date=date.today(),
            meal_type='repas1',
            status=MealStatus.PLANNED,
            planned_calories=400
        )
        db.session.add(tracking)
        db.session.commit()
        
        results = []
        
        def consume_meal():
            try:
                response = client.post(
                    f'/meal-tracking/{tracking.id}/consume',
                    json={
                        'user_id': sample_user.id,
                        'consumption_data': {'satisfaction_rating': 4}
                    }
                )
                results.append(('consume', response.status_code))
            except Exception as e:
                results.append(('consume', str(e)))
        
        def adjust_meal():
            try:
                response = client.put(
                    f'/meal-tracking/{tracking.id}/adjust',
                    json={
                        'user_id': sample_user.id,
                        'portion_multiplier': 1.5
                    }
                )
                results.append(('adjust', response.status_code))
            except Exception as e:
                results.append(('adjust', str(e)))
        
        # Run concurrent operations
        threads = [
            threading.Thread(target=consume_meal),
            threading.Thread(target=adjust_meal)
        ]
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # One should succeed, one should fail or both succeed with different final states
        assert len(results) == 2
        
        # At least one operation should have succeeded
        success_count = sum(1 for _, status in results if status == 200)
        assert success_count >= 1
    
    def test_data_migration_compatibility(self, sample_user):
        """Test that data works correctly after simulated migration"""
        # Create tracking with old-style data structure
        tracking = MealTracking(
            user_id=sample_user.id,
            meal_date=date.today(),
            meal_type='repas1',
            status=MealStatus.CONSUMED,
            planned_calories=400,
            planned_protein=25,
            # Simulate missing new fields that might be added later
            planned_fiber=None,
            planned_sodium=None,
            planned_sugar=None
        )
        db.session.add(tracking)
        db.session.commit()
        
        # Test that system handles missing data gracefully
        dict_repr = tracking.to_dict()
        assert dict_repr is not None
        assert 'planned_nutrition' in dict_repr
        
        # Effective nutrition should work even with missing data
        assert tracking.effective_calories == 400
        assert tracking.effective_protein == 25
        assert tracking.effective_fiber == 0  # Default for None
    
    def test_api_versioning_compatibility(self, client, sample_user):
        """Test API backward compatibility"""
        # Test that API works with minimal required data
        tracking = MealTracking(
            user_id=sample_user.id,
            meal_date=date.today(),
            meal_type='repas1',
            status=MealStatus.PLANNED,
            planned_calories=400
        )
        db.session.add(tracking)
        db.session.commit()
        
        # Minimal consume request
        response = client.post(
            f'/meal-tracking/{tracking.id}/consume',
            json={'user_id': sample_user.id}  # No consumption_data
        )
        assert response.status_code == 200
        
        # API should handle missing optional fields
        response = client.get(f'/meal-tracking/today?user_id={sample_user.id}')
        assert response.status_code == 200
        
        data = response.get_json()
        assert len(data['meal_trackings']) >= 1


class TestComplexScenarios:
    """Test complex real-world scenarios"""
    
    def test_user_journey_weight_loss(self, client, diverse_user_patterns):
        """Test complete user journey for weight loss"""
        patterns = diverse_user_patterns
        improving_user = next(p for p in patterns if p['pattern_type'] == 'improving_over_time')
        user = improving_user['user']
        
        # Test that improvement is reflected in trends
        response = client.get(f'/meal-tracking/patterns?user_id={user.id}&days=21')
        assert response.status_code == 200
        
        trends = response.get_json()['adherence_trends']
        # Should show improvement or stable (not declining)
        assert trends['plan_adherence_trend'] in ['improving', 'stable']
    
    def test_weekend_pattern_analysis(self, client, diverse_user_patterns):
        """Test analysis of weekend eating patterns"""
        patterns = diverse_user_patterns
        weekend_user = next(p for p in patterns if p['pattern_type'] == 'inconsistent_weekends')
        user = weekend_user['user']
        
        # Get eating patterns
        response = client.get(f'/meal-tracking/patterns?user_id={user.id}')
        assert response.status_code == 200
        
        data = response.get_json()
        eating_patterns = data['eating_patterns']
        
        # Should show variation in completion rates
        assert 'meal_type_statistics' in eating_patterns
        assert 'overall_completion_rate' in eating_patterns
    
    def test_portion_adjustment_insights(self, client, diverse_user_patterns):
        """Test insights for users who frequently adjust portions"""
        patterns = diverse_user_patterns
        portion_user = next(p for p in patterns if p['pattern_type'] == 'portion_adjuster')
        user = portion_user['user']
        
        # Get meal history
        response = client.get(f'/meal-tracking/history?user_id={user.id}&status=modified')
        assert response.status_code == 200
        
        data = response.get_json()
        trackings = data['meal_trackings']
        
        # Should have many modified meals
        modified_count = len([t for t in trackings if t['status'] == 'modified'])
        assert modified_count > 0
        
        # Statistics should reflect modification patterns
        stats = data['statistics']
        assert stats['total_meals'] > 0


class TestSystemIntegrity:
    """Test system integrity and data consistency"""
    
    def test_referential_integrity(self, sample_user, sample_recipe):
        """Test that referential integrity is maintained"""
        # Create tracking referencing recipe
        tracking = MealTracking(
            user_id=sample_user.id,
            recipe_id=sample_recipe.id,
            meal_date=date.today(),
            meal_type='repas1',
            status=MealStatus.PLANNED
        )
        db.session.add(tracking)
        db.session.commit()
        
        # Verify relationship works
        assert tracking.recipe == sample_recipe
        assert tracking in sample_recipe.meal_trackings
        
        # Test cascade behavior when user is deleted
        tracking_id = tracking.id
        db.session.delete(sample_user)
        db.session.commit()
        
        # Tracking should be deleted due to CASCADE
        assert MealTracking.query.get(tracking_id) is None
    
    def test_data_consistency_checks(self, sample_user):
        """Test that data consistency is maintained"""
        today = date.today()
        
        # Create tracking
        tracking = MealTracking(
            user_id=sample_user.id,
            meal_date=today,
            meal_type='repas1',
            status=MealStatus.CONSUMED,
            planned_calories=400,
            actual_calories=450
        )
        db.session.add(tracking)
        db.session.commit()
        
        # Create daily summary
        with patch.object(User, 'get_daily_targets') as mock_targets:
            mock_targets.return_value = {
                'calories': 2000, 'protein': 150, 'carbs': 250, 'fat': 65,
                'fiber': 30, 'sodium': 2300, 'sugar': 50
            }
            
            summary = MealTrackingService.calculate_daily_summary(
                user_id=sample_user.id,
                summary_date=today
            )
            
            # Summary should reflect tracking data
            assert summary.actual_calories == 450
            assert summary.meals_consumed == 1
    
    def test_audit_trail(self, sample_user):
        """Test that changes are properly tracked"""
        tracking = MealTracking(
            user_id=sample_user.id,
            meal_date=date.today(),
            meal_type='repas1',
            status=MealStatus.PLANNED,
            version=1
        )
        db.session.add(tracking)
        db.session.commit()
        
        original_updated_at = tracking.updated_at
        original_version = tracking.version
        
        # Update tracking
        tracking.status = MealStatus.CONSUMED
        tracking.version += 1
        db.session.commit()
        
        # Verify audit fields are updated
        assert tracking.updated_at > original_updated_at
        assert tracking.version > original_version