"""
API endpoint tests for Meal Tracking routes (US1.8)
Tests for Flask API endpoints in meal_tracking.py
"""

import pytest
import json
from datetime import date, datetime, time, timedelta
from unittest.mock import patch, MagicMock

from models.meal_tracking import MealTracking, DailyNutritionSummary, MealStatus
from models.user import User
from models.meal_plan import MealPlan
from models.recipe import Recipe
from services.meal_tracking_service import MealTrackingService
from database import db


class TestMealTrackingAPI:
    """Test cases for meal tracking API endpoints"""
    
    def test_get_today_meal_tracking_success(self, client, sample_user, sample_meal_plan):
        """Test GET /meal-tracking/today with data"""
        today = date.today()
        
        # Create meal tracking for today
        tracking = MealTracking(
            user_id=sample_user.id,
            meal_plan_id=sample_meal_plan.id,
            meal_date=today,
            meal_type="repas1",
            meal_name="Breakfast",
            status=MealStatus.PLANNED,
            planned_calories=400.0,
            planned_protein=25.0
        )
        db.session.add(tracking)
        db.session.commit()
        
        response = client.get(f'/meal-tracking/today?user_id={sample_user.id}')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['date'] == today.isoformat()
        assert data['user_id'] == sample_user.id
        assert data['total_trackings'] == 1
        assert len(data['meal_trackings']) == 1
        
        tracking_data = data['meal_trackings'][0]
        assert tracking_data['meal_type'] == 'repas1'
        assert tracking_data['status'] == 'planned'
        assert tracking_data['planned_nutrition']['calories'] == 400.0
    
    def test_get_today_meal_tracking_create_from_plan(self, client, sample_user, sample_meal_plan):
        """Test GET /meal-tracking/today creates trackings from active meal plan"""
        today = date.today()
        
        # Ensure meal plan is active
        sample_meal_plan.is_active = True
        db.session.commit()
        
        # Mock the service method to return trackings
        with patch.object(MealTrackingService, 'create_meal_tracking_from_plan') as mock_create:
            mock_tracking = MealTracking(
                id=1,
                user_id=sample_user.id,
                meal_plan_id=sample_meal_plan.id,
                meal_date=today,
                meal_type="repas1",
                status=MealStatus.PLANNED
            )
            mock_create.return_value = [mock_tracking]
            
            response = client.get(f'/meal-tracking/today?user_id={sample_user.id}')
            
            assert response.status_code == 200
            mock_create.assert_called_once_with(
                user_id=sample_user.id,
                meal_plan_id=sample_meal_plan.id,
                target_date=today
            )
    
    def test_get_today_meal_tracking_no_user_id(self, client):
        """Test GET /meal-tracking/today without user_id parameter"""
        response = client.get('/meal-tracking/today')
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'user_id parameter is required' in data['error']
    
    def test_get_today_meal_tracking_user_not_found(self, client):
        """Test GET /meal-tracking/today with non-existent user"""
        response = client.get('/meal-tracking/today?user_id=99999')
        
        assert response.status_code == 404
        data = response.get_json()
        assert 'User not found' in data['error']
    
    def test_get_today_meal_tracking_no_active_plan(self, client, sample_user):
        """Test GET /meal-tracking/today with no active meal plan"""
        response = client.get(f'/meal-tracking/today?user_id={sample_user.id}')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['total_trackings'] == 0
        assert data['meal_trackings'] == []
    
    def test_mark_meal_consumed_success(self, client, sample_meal_tracking):
        """Test POST /meal-tracking/<id>/consume success"""
        consumption_data = {
            'user_id': sample_meal_tracking.user_id,
            'consumption_data': {
                'consumption_time': '2025-08-08T08:30:00',
                'nutrition': {
                    'calories': 450.0,
                    'protein': 30.0,
                    'carbs': 50.0,
                    'fat': 18.0
                },
                'portion_size': 1.2,
                'notes': 'Delicious!',
                'satisfaction_rating': 5,
                'photo_urls': ['http://example.com/photo.jpg']
            }
        }
        
        response = client.post(
            f'/meal-tracking/{sample_meal_tracking.id}/consume',
            json=consumption_data
        )
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['success'] == True
        assert data['message'] == 'Meal marked as consumed'
        
        meal_data = data['meal_tracking']
        assert meal_data['status'] == 'consumed'
        assert meal_data['actual_nutrition']['calories'] == 450.0
        assert meal_data['user_notes'] == 'Delicious!'
        assert meal_data['satisfaction_rating'] == 5
    
    def test_mark_meal_consumed_no_user_id(self, client, sample_meal_tracking):
        """Test POST /meal-tracking/<id>/consume without user_id"""
        response = client.post(
            f'/meal-tracking/{sample_meal_tracking.id}/consume',
            json={}
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'user_id is required' in data['error']
    
    def test_mark_meal_consumed_invalid_data(self, client, sample_meal_tracking):
        """Test POST /meal-tracking/<id>/consume with invalid data"""
        consumption_data = {
            'user_id': sample_meal_tracking.user_id,
            'consumption_data': {
                'satisfaction_rating': 6  # Invalid: > 5
            }
        }
        
        response = client.post(
            f'/meal-tracking/{sample_meal_tracking.id}/consume',
            json=consumption_data
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'Invalid consumption data' in data['error']
        assert 'details' in data
    
    def test_mark_meal_consumed_not_found(self, client, sample_user):
        """Test POST /meal-tracking/<id>/consume with non-existent tracking"""
        response = client.post(
            '/meal-tracking/99999/consume',
            json={'user_id': sample_user.id}
        )
        
        assert response.status_code == 404
        data = response.get_json()
        assert 'Meal tracking not found' in data['error']
    
    def test_adjust_meal_portions_success(self, client, sample_meal_tracking):
        """Test PUT /meal-tracking/<id>/adjust success"""
        adjustment_data = {
            'user_id': sample_meal_tracking.user_id,
            'portion_multiplier': 1.5,
            'nutrition': {
                'calories': 600.0  # Custom override
            }
        }
        
        response = client.put(
            f'/meal-tracking/{sample_meal_tracking.id}/adjust',
            json=adjustment_data
        )
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['success'] == True
        assert data['message'] == 'Meal portions adjusted'
        
        adjustments = data['adjustments']
        assert adjustments['portion_multiplier'] == 1.5
        assert adjustments['adjusted_nutrition']['calories'] == 600.0  # Custom value
        
        # Calculated values (planned * multiplier, except overridden ones)
        expected_protein = sample_meal_tracking.planned_protein * 1.5
        assert adjustments['adjusted_nutrition']['protein'] == expected_protein
    
    def test_adjust_meal_portions_invalid_multiplier(self, client, sample_meal_tracking):
        """Test PUT /meal-tracking/<id>/adjust with invalid multiplier"""
        adjustment_data = {
            'user_id': sample_meal_tracking.user_id,
            'portion_multiplier': -1.0  # Invalid: <= 0
        }
        
        response = client.put(
            f'/meal-tracking/{sample_meal_tracking.id}/adjust',
            json=adjustment_data
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'Invalid adjustment data' in data['error']
    
    def test_adjust_meal_portions_not_found(self, client, sample_user):
        """Test PUT /meal-tracking/<id>/adjust with non-existent tracking"""
        response = client.put(
            '/meal-tracking/99999/adjust',
            json={
                'user_id': sample_user.id,
                'portion_multiplier': 1.5
            }
        )
        
        assert response.status_code == 404
        data = response.get_json()
        assert 'Meal tracking not found' in data['error']
    
    def test_skip_meal_success(self, client, sample_meal_tracking):
        """Test POST /meal-tracking/<id>/skip success"""
        skip_data = {
            'user_id': sample_meal_tracking.user_id,
            'skip_data': {
                'reason': 'Not feeling well'
            }
        }
        
        response = client.post(
            f'/meal-tracking/{sample_meal_tracking.id}/skip',
            json=skip_data
        )
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['success'] == True
        assert data['message'] == 'Meal marked as skipped'
        
        meal_data = data['meal_tracking']
        assert meal_data['status'] == 'skipped'
        assert meal_data['skip_reason'] == 'Not feeling well'
    
    def test_skip_meal_no_reason(self, client, sample_meal_tracking):
        """Test POST /meal-tracking/<id>/skip without reason"""
        skip_data = {
            'user_id': sample_meal_tracking.user_id
        }
        
        response = client.post(
            f'/meal-tracking/{sample_meal_tracking.id}/skip',
            json=skip_data
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == True
    
    def test_replace_meal_success(self, client, sample_meal_tracking, sample_recipe):
        """Test POST /meal-tracking/<id>/replace success"""
        replace_data = {
            'user_id': sample_meal_tracking.user_id,
            'replacement_data': {
                'replacement_recipe_id': sample_recipe.id,
                'replacement_name': 'Grilled Chicken Salad',
                'reason': 'Preferred healthier option',
                'nutrition': {
                    'calories': 350.0,
                    'protein': 28.0,
                    'carbs': 35.0,
                    'fat': 12.0
                }
            }
        }
        
        response = client.post(
            f'/meal-tracking/{sample_meal_tracking.id}/replace',
            json=replace_data
        )
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['success'] == True
        assert data['message'] == 'Meal replaced successfully'
        
        meal_data = data['meal_tracking']
        assert meal_data['status'] == 'replaced'
        assert meal_data['replacement_recipe_id'] == sample_recipe.id
        assert meal_data['replacement_name'] == 'Grilled Chicken Salad'
        assert meal_data['replacement_reason'] == 'Preferred healthier option'
    
    def test_replace_meal_with_recipe_auto_nutrition(self, client, sample_meal_tracking, sample_recipe):
        """Test POST /meal-tracking/<id>/replace with recipe auto-filling nutrition"""
        replace_data = {
            'user_id': sample_meal_tracking.user_id,
            'replacement_data': {
                'replacement_recipe_id': sample_recipe.id,
                'reason': 'Better option'
                # No nutrition provided - should use recipe nutrition
            }
        }
        
        response = client.post(
            f'/meal-tracking/{sample_meal_tracking.id}/replace',
            json=replace_data
        )
        
        assert response.status_code == 200
        data = response.get_json()
        
        meal_data = data['meal_tracking']
        assert meal_data['replacement_name'] == sample_recipe.name
        # Should have nutrition from recipe
        assert 'actual_nutrition' in meal_data
    
    def test_get_daily_summary_success(self, client, sample_daily_summary):
        """Test GET /meal-tracking/summary/<date> success"""
        date_str = sample_daily_summary.summary_date.isoformat()
        
        response = client.get(
            f'/meal-tracking/summary/{date_str}?user_id={sample_daily_summary.user_id}'
        )
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['success'] == True
        assert data['date'] == date_str
        assert 'daily_summary' in data
        
        summary = data['daily_summary']
        assert summary['user_id'] == sample_daily_summary.user_id
        assert summary['summary_date'] == date_str
    
    def test_get_daily_summary_force_recalculate(self, client, sample_daily_summary):
        """Test GET /meal-tracking/summary/<date> with force_recalculate"""
        date_str = sample_daily_summary.summary_date.isoformat()
        
        with patch.object(MealTrackingService, 'calculate_daily_summary') as mock_calc:
            mock_calc.return_value = sample_daily_summary
            
            response = client.get(
                f'/meal-tracking/summary/{date_str}?user_id={sample_daily_summary.user_id}&force_recalculate=true'
            )
            
            assert response.status_code == 200
            mock_calc.assert_called_once_with(
                user_id=sample_daily_summary.user_id,
                summary_date=sample_daily_summary.summary_date,
                force_recalculate=True
            )
    
    def test_get_daily_summary_invalid_date(self, client, sample_user):
        """Test GET /meal-tracking/summary/<date> with invalid date"""
        response = client.get(
            f'/meal-tracking/summary/invalid-date?user_id={sample_user.id}'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'Invalid date format' in data['error']
    
    def test_get_daily_summary_no_user_id(self, client):
        """Test GET /meal-tracking/summary/<date> without user_id"""
        response = client.get('/meal-tracking/summary/2025-08-08')
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'user_id parameter is required' in data['error']
    
    def test_analyze_eating_patterns_success(self, client, sample_user, test_data_factory):
        """Test GET /meal-tracking/patterns success"""
        # Create sample tracking data
        test_data_factory.create_multiple_trackings(sample_user.id, num_days=7)
        
        with patch.object(MealTrackingService, 'get_adherence_trends') as mock_trends:
            mock_trends.return_value = {
                'period_days': 30,
                'data_points': 20,
                'avg_plan_adherence': 85.0,
                'plan_adherence_trend': 'improving'
            }
            
            response = client.get(
                f'/meal-tracking/patterns?user_id={sample_user.id}&days=30'
            )
            
            assert response.status_code == 200
            data = response.get_json()
            
            assert data['success'] == True
            assert data['user_id'] == sample_user.id
            assert 'analysis_period' in data
            assert 'adherence_trends' in data
            assert 'eating_patterns' in data
            assert data['total_meals_analyzed'] > 0
            
            mock_trends.assert_called_once_with(sample_user.id, 30)
    
    def test_analyze_eating_patterns_invalid_days(self, client, sample_user):
        """Test GET /meal-tracking/patterns with invalid days parameter"""
        response = client.get(
            f'/meal-tracking/patterns?user_id={sample_user.id}&days=500'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'days must be between 1 and 365' in data['error']
    
    def test_get_monthly_report_success(self, client, sample_user):
        """Test GET /meal-tracking/report/<month> success"""
        month_str = '2025-08'
        
        with patch.object(MealTrackingService, 'get_monthly_summary') as mock_monthly:
            mock_monthly.return_value = {
                'year': 2025,
                'month': 8,
                'days_tracked': 15,
                'avg_daily_calories': 1800.0
            }
            
            with patch.object(MealTrackingService, 'get_weekly_summary') as mock_weekly:
                mock_weekly.return_value = {
                    'days_tracked': 7,
                    'avg_calories': 1850.0
                }
                
                response = client.get(
                    f'/meal-tracking/report/{month_str}?user_id={sample_user.id}'
                )
                
                assert response.status_code == 200
                data = response.get_json()
                
                assert data['success'] == True
                assert data['month'] == month_str
                assert 'monthly_summary' in data
                assert 'weekly_summaries' in data
                assert 'daily_summaries' in data
                assert 'report_metadata' in data
    
    def test_get_monthly_report_invalid_month(self, client, sample_user):
        """Test GET /meal-tracking/report/<month> with invalid month"""
        response = client.get(
            f'/meal-tracking/report/invalid-month?user_id={sample_user.id}'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'Invalid month format' in data['error']
    
    def test_get_meal_tracking_history_success(self, client, sample_user, test_data_factory):
        """Test GET /meal-tracking/history success"""
        # Create sample trackings
        test_data_factory.create_multiple_trackings(sample_user.id, num_days=5)
        
        response = client.get(
            f'/meal-tracking/history?user_id={sample_user.id}'
        )
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['success'] == True
        assert data['user_id'] == sample_user.id
        assert 'filters' in data
        assert 'meal_trackings' in data
        assert 'statistics' in data
        assert data['total_results'] > 0
    
    def test_get_meal_tracking_history_with_filters(self, client, sample_user, test_data_factory):
        """Test GET /meal-tracking/history with filters"""
        # Create trackings with different statuses and dates
        today = date.today()
        yesterday = today - timedelta(days=1)
        
        test_data_factory.create_meal_tracking(
            sample_user.id,
            meal_date=yesterday,
            meal_type="repas1",
            status=MealStatus.CONSUMED
        )
        test_data_factory.create_meal_tracking(
            sample_user.id,
            meal_date=today,
            meal_type="repas2",
            status=MealStatus.SKIPPED
        )
        
        # Filter by date range and status
        response = client.get(
            f'/meal-tracking/history?user_id={sample_user.id}&'
            f'start_date={yesterday.isoformat()}&'
            f'end_date={today.isoformat()}&'
            f'status=consumed&status=skipped&'
            f'meal_type=repas1'
        )
        
        assert response.status_code == 200
        data = response.get_json()
        
        filters = data['filters']
        assert filters['start_date'] == yesterday.isoformat()
        assert filters['end_date'] == today.isoformat()
        assert 'consumed' in filters['status_filter']
        assert 'skipped' in filters['status_filter']
        assert filters['meal_type_filter'] == 'repas1'
        
        # Should only return repas1 meals (filtered by meal_type)
        trackings = data['meal_trackings']
        assert all(t['meal_type'] == 'repas1' for t in trackings)
    
    def test_get_meal_tracking_history_invalid_date_filter(self, client, sample_user):
        """Test GET /meal-tracking/history with invalid date filter"""
        response = client.get(
            f'/meal-tracking/history?user_id={sample_user.id}&start_date=invalid-date'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'Invalid start_date format' in data['error']
    
    def test_get_meal_tracking_history_invalid_status_filter(self, client, sample_user):
        """Test GET /meal-tracking/history with invalid status filter"""
        response = client.get(
            f'/meal-tracking/history?user_id={sample_user.id}&status=invalid_status'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'Invalid status filter' in data['error']


class TestMealTrackingAPIHelpers:
    """Test cases for helper functions in meal tracking API"""
    
    def test_analyze_meal_patterns_empty(self):
        """Test analyze_meal_patterns with empty data"""
        from routes.meal_tracking import analyze_meal_patterns
        
        result = analyze_meal_patterns([])
        assert result == {}
    
    def test_analyze_meal_patterns_with_data(self, sample_user, test_data_factory):
        """Test analyze_meal_patterns with actual data"""
        from routes.meal_tracking import analyze_meal_patterns
        
        # Create trackings with varied data
        trackings = []
        today = date.today()
        
        for i in range(3):
            # Create repas1 with consistent timing and high satisfaction
            tracking = test_data_factory.create_meal_tracking(
                user_id=sample_user.id,
                meal_date=today - timedelta(days=i),
                meal_type="repas1",
                status=MealStatus.CONSUMED
            )
            tracking.consumption_time_actual = time(8, 0)  # Consistent timing
            tracking.satisfaction_rating = 5
            trackings.append(tracking)
            
            # Create repas2 with varied timing and satisfaction
            tracking2 = test_data_factory.create_meal_tracking(
                user_id=sample_user.id,
                meal_date=today - timedelta(days=i),
                meal_type="repas2",
                status=MealStatus.SKIPPED if i == 0 else MealStatus.CONSUMED
            )
            if tracking2.status == MealStatus.CONSUMED:
                tracking2.consumption_time_actual = time(12 + i, 0)  # Varied timing
                tracking2.satisfaction_rating = 3 + i
            trackings.append(tracking2)
        
        result = analyze_meal_patterns(trackings)
        
        assert 'meal_type_statistics' in result
        assert 'timing_patterns' in result
        assert 'overall_completion_rate' in result
        
        # Check repas1 stats (all consumed)
        repas1_stats = result['meal_type_statistics']['repas1']
        assert repas1_stats['total'] == 3
        assert repas1_stats['consumed'] == 3
        assert repas1_stats['completion_rate'] == 100.0
        assert repas1_stats['avg_satisfaction'] == 5.0
        
        # Check repas2 stats (1 skipped, 2 consumed)
        repas2_stats = result['meal_type_statistics']['repas2']
        assert repas2_stats['total'] == 3
        assert repas2_stats['consumed'] == 2
        assert repas2_stats['skipped'] == 1
        assert repas2_stats['completion_rate'] == pytest.approx(66.67, abs=0.1)
        
        # Check timing patterns
        assert 'repas1' in result['timing_patterns']
        repas1_timing = result['timing_patterns']['repas1']
        assert repas1_timing['avg_hour'] == 8.0  # All at 8:00
        assert repas1_timing['consistency_score'] == 100.0  # Perfect consistency
        
        # Check most consistent meal
        assert result['most_consistent_meal'] == 'repas1'
    
    def test_calculate_history_stats_empty(self):
        """Test calculate_history_stats with empty data"""
        from routes.meal_tracking import calculate_history_stats
        
        result = calculate_history_stats([])
        assert result == {}
    
    def test_calculate_history_stats_with_data(self, sample_user, test_data_factory):
        """Test calculate_history_stats with actual data"""
        from routes.meal_tracking import calculate_history_stats
        
        # Create trackings with varied statuses and nutrition
        trackings = []
        
        # 3 consumed meals
        for i in range(3):
            tracking = test_data_factory.create_meal_tracking(
                user_id=sample_user.id,
                meal_type=f"repas{i+1}",
                status=MealStatus.CONSUMED,
                planned_calories=400.0 + (i * 100),
                planned_protein=20.0 + (i * 5)
            )
            tracking.satisfaction_rating = 4 + i % 2  # 4, 5, 4
            trackings.append(tracking)
        
        # 1 skipped meal
        tracking = test_data_factory.create_meal_tracking(
            user_id=sample_user.id,
            meal_type="collation",
            status=MealStatus.SKIPPED,
            planned_calories=200.0,
            planned_protein=10.0
        )
        trackings.append(tracking)
        
        result = calculate_history_stats(trackings)
        
        assert result['total_meals'] == 4
        
        completion_stats = result['completion_stats']
        assert completion_stats['consumed'] == 3
        assert completion_stats['skipped'] == 1
        assert completion_stats['completion_rate'] == 75.0
        assert completion_stats['skip_rate'] == 25.0
        
        nutrition_totals = result['nutrition_totals']
        # Only consumed meals count: 400 + 500 + 600 = 1500 (skipped = 0)
        assert nutrition_totals['total_calories'] == 1500.0
        assert nutrition_totals['total_protein'] == 75.0  # 20 + 25 + 30
        assert nutrition_totals['avg_calories_per_meal'] == 375.0  # 1500 / 4
        
        satisfaction = result['satisfaction']
        assert satisfaction['avg_rating'] == 4.3  # (4 + 5 + 4) / 3
        assert satisfaction['total_ratings'] == 3


class TestMealTrackingAPIIntegration:
    """Integration tests for meal tracking API"""
    
    def test_complete_meal_workflow_api(self, client, sample_user, sample_meal_plan, sample_recipe):
        """Test complete meal tracking workflow through API"""
        today = date.today()
        
        # Step 1: Get today's meal trackings (should create from plan)
        sample_meal_plan.is_active = True
        db.session.commit()
        
        with patch.object(MealTrackingService, 'create_meal_tracking_from_plan') as mock_create:
            mock_tracking = MealTracking(
                id=1,
                user_id=sample_user.id,
                meal_plan_id=sample_meal_plan.id,
                meal_date=today,
                meal_type="repas1",
                meal_name="Breakfast",
                status=MealStatus.PLANNED,
                planned_calories=400.0,
                planned_protein=25.0
            )
            mock_create.return_value = [mock_tracking]
            
            response = client.get(f'/meal-tracking/today?user_id={sample_user.id}')
            assert response.status_code == 200
            
            trackings = response.get_json()['meal_trackings']
            tracking_id = trackings[0]['id']
        
        # Create actual tracking for further steps
        actual_tracking = MealTracking(
            user_id=sample_user.id,
            meal_date=today,
            meal_type="repas1",
            status=MealStatus.PLANNED,
            planned_calories=400.0,
            planned_protein=25.0
        )
        db.session.add(actual_tracking)
        db.session.commit()
        
        # Step 2: Mark meal as consumed
        consumption_data = {
            'user_id': sample_user.id,
            'consumption_data': {
                'nutrition': {
                    'calories': 450.0,
                    'protein': 30.0
                },
                'satisfaction_rating': 5
            }
        }
        
        response = client.post(
            f'/meal-tracking/{actual_tracking.id}/consume',
            json=consumption_data
        )
        assert response.status_code == 200
        
        # Step 3: Get daily summary
        with patch.object(MealTrackingService, 'calculate_daily_summary') as mock_summary:
            mock_summary.return_value = DailyNutritionSummary(
                user_id=sample_user.id,
                summary_date=today,
                actual_calories=450.0,
                meals_consumed=1
            )
            
            response = client.get(
                f'/meal-tracking/summary/{today.isoformat()}?user_id={sample_user.id}'
            )
            assert response.status_code == 200
            
            summary = response.get_json()['daily_summary']
            assert summary['actual_calories'] == 450.0
    
    def test_api_error_handling(self, client, sample_user):
        """Test API error handling for various scenarios"""
        # Test with invalid JSON
        response = client.post(
            '/meal-tracking/1/consume',
            data='invalid json',
            content_type='application/json'
        )
        assert response.status_code == 400
        
        # Test server error simulation
        with patch.object(MealTrackingService, 'get_user_meal_trackings') as mock_get:
            mock_get.side_effect = Exception("Database error")
            
            response = client.get(f'/meal-tracking/history?user_id={sample_user.id}')
            assert response.status_code == 500
            assert 'Database error' in response.get_json()['error']
    
    def test_api_data_consistency(self, client, sample_user, test_data_factory):
        """Test data consistency across API endpoints"""
        today = date.today()
        
        # Create tracking
        tracking = test_data_factory.create_meal_tracking(
            sample_user.id,
            meal_date=today,
            status=MealStatus.PLANNED,
            planned_calories=500.0
        )
        
        # Mark as consumed through API
        response = client.post(
            f'/meal-tracking/{tracking.id}/consume',
            json={
                'user_id': sample_user.id,
                'consumption_data': {
                    'nutrition': {'calories': 550.0}
                }
            }
        )
        assert response.status_code == 200
        
        # Verify through history API
        response = client.get(
            f'/meal-tracking/history?user_id={sample_user.id}&'
            f'start_date={today.isoformat()}&end_date={today.isoformat()}'
        )
        assert response.status_code == 200
        
        trackings = response.get_json()['meal_trackings']
        assert len(trackings) == 1
        assert trackings[0]['status'] == 'consumed'
        assert trackings[0]['actual_nutrition']['calories'] == 550.0
        
        # Verify statistics
        stats = response.get_json()['statistics']
        assert stats['total_meals'] == 1
        assert stats['completion_stats']['consumed'] == 1
        assert stats['nutrition_totals']['total_calories'] == 550.0