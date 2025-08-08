"""
Unit tests for MealTrackingService (US1.8)
Tests for business logic in meal tracking operations
"""

import pytest
from datetime import date, datetime, time, timedelta
from unittest.mock import patch, MagicMock

from services.meal_tracking_service import MealTrackingService
from models.meal_tracking import MealTracking, DailyNutritionSummary, MealStatus
from models.user import User
from models.meal_plan import MealPlan
from models.recipe import Recipe
from database import db


class TestMealTrackingService:
    """Test cases for MealTrackingService"""
    
    def test_create_meal_tracking_from_plan_success(self, sample_user, sample_meal_plan, sample_recipe):
        """Test successful creation of meal tracking from meal plan"""
        today = date.today()
        
        # Create trackings from meal plan
        trackings = MealTrackingService.create_meal_tracking_from_plan(
            user_id=sample_user.id,
            meal_plan_id=sample_meal_plan.id,
            target_date=today
        )
        
        assert len(trackings) == 2  # repas1 and repas2 from sample meal plan
        
        # Check first tracking (repas1)
        breakfast = next(t for t in trackings if t.meal_type == "repas1")
        assert breakfast.user_id == sample_user.id
        assert breakfast.meal_plan_id == sample_meal_plan.id
        assert breakfast.meal_date == today
        assert breakfast.status == MealStatus.PLANNED
        assert breakfast.planned_calories == 400.0
        assert breakfast.planned_protein == 20.0
        assert breakfast.consumption_time_planned == time(8, 0)
        
        # Check second tracking (repas2)
        lunch = next(t for t in trackings if t.meal_type == "repas2")
        assert lunch.user_id == sample_user.id
        assert lunch.meal_date == today
        assert lunch.planned_calories == 600.0
        assert lunch.planned_protein == 35.0
        assert lunch.consumption_time_planned == time(12, 0)
    
    def test_create_meal_tracking_from_plan_invalid_meal_plan(self, sample_user):
        """Test creation with invalid meal plan"""
        today = date.today()
        
        with pytest.raises(ValueError, match="Meal plan not found"):
            MealTrackingService.create_meal_tracking_from_plan(
                user_id=sample_user.id,
                meal_plan_id=99999,  # Non-existent ID
                target_date=today
            )
    
    def test_create_meal_tracking_from_plan_wrong_user(self, sample_user, sample_meal_plan, test_data_factory):
        """Test creation with meal plan belonging to different user"""
        today = date.today()
        other_user = test_data_factory.create_user("Other User", "other@test.com")
        
        with pytest.raises(ValueError, match="doesn't belong to user"):
            MealTrackingService.create_meal_tracking_from_plan(
                user_id=other_user.id,
                meal_plan_id=sample_meal_plan.id,  # Belongs to sample_user
                target_date=today
            )
    
    def test_create_meal_tracking_skip_existing(self, sample_user, sample_meal_plan, sample_meal_tracking):
        """Test that existing trackings are skipped"""
        today = date.today()
        
        # Create trackings (one already exists for repas1)
        trackings = MealTrackingService.create_meal_tracking_from_plan(
            user_id=sample_user.id,
            meal_plan_id=sample_meal_plan.id,
            target_date=today
        )
        
        # Should only create repas2 (repas1 already exists as sample_meal_tracking)
        assert len(trackings) == 1
        assert trackings[0].meal_type == "repas2"
    
    def test_create_meal_tracking_no_meals_for_date(self, sample_user, sample_meal_plan):
        """Test creation when no meals exist for target date"""
        future_date = date.today() + timedelta(days=30)
        
        trackings = MealTrackingService.create_meal_tracking_from_plan(
            user_id=sample_user.id,
            meal_plan_id=sample_meal_plan.id,
            target_date=future_date
        )
        
        assert len(trackings) == 0
    
    def test_update_meal_status_consumed(self, sample_meal_tracking):
        """Test updating meal status to consumed"""
        consumption_data = {
            'consumption_time': datetime(2025, 8, 8, 8, 30),
            'nutrition': {
                'calories': 450.0,
                'protein': 30.0,
                'carbs': 50.0,
                'fat': 18.0,
                'fiber': 6.0,
                'sodium': 220.0,
                'sugar': 12.0
            },
            'portion_size': 1.2,
            'notes': 'Great meal!',
            'satisfaction_rating': 5,
            'difficulty_rating': 2,
            'photo_urls': ['http://example.com/photo.jpg'],
            'modifications': {'sauce': {'added': True}},
            'substitutions': {'oil': 'butter'}
        }
        
        updated_tracking = MealTrackingService.update_meal_status(
            tracking_id=sample_meal_tracking.id,
            user_id=sample_meal_tracking.user_id,
            status=MealStatus.CONSUMED,
            consumption_data=consumption_data
        )
        
        assert updated_tracking.status == MealStatus.CONSUMED
        assert updated_tracking.consumption_datetime == consumption_data['consumption_time']
        assert updated_tracking.consumption_time_actual == time(8, 30)
        assert updated_tracking.actual_calories == 450.0
        assert updated_tracking.actual_protein == 30.0
        assert updated_tracking.actual_portion_size == 1.2
        assert updated_tracking.user_notes == 'Great meal!'
        assert updated_tracking.satisfaction_rating == 5
        assert updated_tracking.difficulty_rating == 2
        assert updated_tracking.photo_urls_list == ['http://example.com/photo.jpg']
        assert updated_tracking.modifications == {'sauce': {'added': True}}
        assert updated_tracking.substitutions == {'oil': 'butter'}
        assert updated_tracking.version == 2  # Should increment version
    
    def test_update_meal_status_skipped(self, sample_meal_tracking):
        """Test updating meal status to skipped"""
        consumption_data = {
            'reason': 'Not hungry'
        }
        
        updated_tracking = MealTrackingService.update_meal_status(
            tracking_id=sample_meal_tracking.id,
            user_id=sample_meal_tracking.user_id,
            status=MealStatus.SKIPPED,
            consumption_data=consumption_data
        )
        
        assert updated_tracking.status == MealStatus.SKIPPED
        assert updated_tracking.skip_reason == 'Not hungry'
        assert updated_tracking.version == 2
    
    def test_update_meal_status_replaced(self, sample_meal_tracking, sample_recipe):
        """Test updating meal status to replaced"""
        consumption_data = {
            'replacement_recipe_id': sample_recipe.id,
            'replacement_name': 'Grilled Chicken Salad',
            'reason': 'Preferred option',
            'nutrition': {
                'calories': 350.0,
                'protein': 28.0,
                'carbs': 35.0,
                'fat': 12.0
            }
        }
        
        updated_tracking = MealTrackingService.update_meal_status(
            tracking_id=sample_meal_tracking.id,
            user_id=sample_meal_tracking.user_id,
            status=MealStatus.REPLACED,
            consumption_data=consumption_data
        )
        
        assert updated_tracking.status == MealStatus.REPLACED
        assert updated_tracking.replacement_recipe_id == sample_recipe.id
        assert updated_tracking.replacement_name == 'Grilled Chicken Salad'
        assert updated_tracking.replacement_reason == 'Preferred option'
        assert updated_tracking.actual_calories == 350.0
        assert updated_tracking.actual_protein == 28.0
    
    def test_update_meal_status_modified(self, sample_meal_tracking):
        """Test updating meal status to modified"""
        consumption_data = {
            'modifications': {'ingredient1': {'old_qty': 100, 'new_qty': 150}},
            'substitutions': {'chicken': 'turkey'},
            'nutrition': {
                'calories': 420.0,
                'protein': 27.0,
                'carbs': 48.0,
                'fat': 16.0
            }
        }
        
        updated_tracking = MealTrackingService.update_meal_status(
            tracking_id=sample_meal_tracking.id,
            user_id=sample_meal_tracking.user_id,
            status=MealStatus.MODIFIED,
            consumption_data=consumption_data
        )
        
        assert updated_tracking.status == MealStatus.MODIFIED
        assert updated_tracking.modifications == {'ingredient1': {'old_qty': 100, 'new_qty': 150}}
        assert updated_tracking.substitutions == {'chicken': 'turkey'}
        assert updated_tracking.actual_calories == 420.0
        assert updated_tracking.actual_protein == 27.0
    
    def test_update_meal_status_not_found(self, sample_user):
        """Test updating non-existent meal tracking"""
        with pytest.raises(ValueError, match="Meal tracking not found"):
            MealTrackingService.update_meal_status(
                tracking_id=99999,  # Non-existent ID
                user_id=sample_user.id,
                status=MealStatus.CONSUMED
            )
    
    def test_update_meal_status_wrong_user(self, sample_meal_tracking, test_data_factory):
        """Test updating meal tracking with wrong user"""
        other_user = test_data_factory.create_user("Other User", "other@test.com")
        
        with pytest.raises(ValueError, match="doesn't belong to user"):
            MealTrackingService.update_meal_status(
                tracking_id=sample_meal_tracking.id,
                user_id=other_user.id,
                status=MealStatus.CONSUMED
            )
    
    @patch.object(MealTrackingService, 'invalidate_daily_summary')
    def test_update_meal_status_invalidates_summary(self, mock_invalidate, sample_meal_tracking):
        """Test that updating meal status invalidates daily summary"""
        MealTrackingService.update_meal_status(
            tracking_id=sample_meal_tracking.id,
            user_id=sample_meal_tracking.user_id,
            status=MealStatus.CONSUMED
        )
        
        mock_invalidate.assert_called_once_with(
            sample_meal_tracking.user_id,
            sample_meal_tracking.meal_date
        )
    
    def test_get_user_meal_trackings_basic(self, sample_user, test_data_factory):
        """Test getting user meal trackings without filters"""
        # Create multiple trackings
        trackings = test_data_factory.create_multiple_trackings(
            sample_user.id, 
            num_days=3, 
            meals_per_day=2
        )
        
        result = MealTrackingService.get_user_meal_trackings(sample_user.id)
        
        assert len(result) == 6  # 3 days * 2 meals
        
        # Should be ordered by date desc, then meal_type
        assert result[0].meal_date >= result[-1].meal_date
    
    def test_get_user_meal_trackings_with_date_filters(self, sample_user, test_data_factory):
        """Test getting meal trackings with date filters"""
        today = date.today()
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)
        
        # Create trackings on different dates
        test_data_factory.create_meal_tracking(sample_user.id, yesterday, "repas1")
        test_data_factory.create_meal_tracking(sample_user.id, today, "repas1")
        test_data_factory.create_meal_tracking(sample_user.id, tomorrow, "repas1")
        
        # Filter by start date
        result = MealTrackingService.get_user_meal_trackings(
            sample_user.id,
            start_date=today
        )
        assert len(result) == 2  # today and tomorrow
        
        # Filter by end date
        result = MealTrackingService.get_user_meal_trackings(
            sample_user.id,
            end_date=today
        )
        assert len(result) == 2  # yesterday and today
        
        # Filter by date range
        result = MealTrackingService.get_user_meal_trackings(
            sample_user.id,
            start_date=today,
            end_date=today
        )
        assert len(result) == 1  # only today
        assert result[0].meal_date == today
    
    def test_get_user_meal_trackings_with_status_filter(self, sample_user, test_data_factory):
        """Test getting meal trackings with status filter"""
        # Create trackings with different statuses
        test_data_factory.create_meal_tracking(
            sample_user.id, 
            status=MealStatus.PLANNED,
            meal_type="repas1"
        )
        test_data_factory.create_meal_tracking(
            sample_user.id, 
            status=MealStatus.CONSUMED,
            meal_type="repas2"
        )
        test_data_factory.create_meal_tracking(
            sample_user.id, 
            status=MealStatus.SKIPPED,
            meal_type="repas3"
        )
        
        # Filter by consumed status
        result = MealTrackingService.get_user_meal_trackings(
            sample_user.id,
            status_filter=[MealStatus.CONSUMED]
        )
        assert len(result) == 1
        assert result[0].status == MealStatus.CONSUMED
        
        # Filter by multiple statuses
        result = MealTrackingService.get_user_meal_trackings(
            sample_user.id,
            status_filter=[MealStatus.PLANNED, MealStatus.SKIPPED]
        )
        assert len(result) == 2
        assert all(t.status in [MealStatus.PLANNED, MealStatus.SKIPPED] for t in result)
    
    def test_calculate_daily_summary_new(self, sample_user, test_data_factory):
        """Test calculating new daily summary"""
        today = date.today()
        
        # Mock user.get_daily_targets() method
        with patch.object(User, 'get_daily_targets') as mock_targets:
            mock_targets.return_value = {
                'calories': 2000.0,
                'protein': 150.0,
                'carbs': 250.0,
                'fat': 65.0,
                'fiber': 30.0,
                'sodium': 2300.0,
                'sugar': 50.0
            }
            
            # Create meal trackings
            trackings = []
            for meal_type in ['repas1', 'repas2', 'repas3']:
                tracking = test_data_factory.create_meal_tracking(
                    user_id=sample_user.id,
                    meal_date=today,
                    meal_type=meal_type,
                    status=MealStatus.CONSUMED,
                    planned_calories=400.0,
                    planned_protein=25.0
                )
                trackings.append(tracking)
            
            summary = MealTrackingService.calculate_daily_summary(
                user_id=sample_user.id,
                summary_date=today
            )
            
            assert summary.user_id == sample_user.id
            assert summary.summary_date == today
            assert summary.meals_planned == 3
            assert summary.meals_consumed == 3
            assert summary.target_calories == 2000.0
            assert summary.target_protein == 150.0
            
            # Check aggregated nutrition
            assert summary.planned_calories == 1200.0  # 3 * 400
            assert summary.planned_protein == 75.0     # 3 * 25
            assert summary.actual_calories == 1200.0   # Same as planned (consumed)
            assert summary.actual_protein == 75.0      # Same as planned (consumed)
            
            # Check week and month context
            expected_week_start = today - timedelta(days=today.weekday())
            assert summary.week_start == expected_week_start
            assert summary.month_year == today.strftime('%Y-%m')
    
    def test_calculate_daily_summary_existing_no_recalc(self, sample_daily_summary):
        """Test getting existing summary without recalculation"""
        summary = MealTrackingService.calculate_daily_summary(
            user_id=sample_daily_summary.user_id,
            summary_date=sample_daily_summary.summary_date,
            force_recalculate=False
        )
        
        # Should return existing summary
        assert summary.id == sample_daily_summary.id
        assert summary.planned_calories == sample_daily_summary.planned_calories
    
    def test_calculate_daily_summary_force_recalculate(self, sample_daily_summary, sample_user):
        """Test force recalculation of existing summary"""
        original_calories = sample_daily_summary.planned_calories
        
        with patch.object(User, 'get_daily_targets') as mock_targets:
            mock_targets.return_value = {
                'calories': 2000.0,
                'protein': 150.0,
                'carbs': 250.0,
                'fat': 65.0,
                'fiber': 30.0,
                'sodium': 2300.0,
                'sugar': 50.0
            }
            
            summary = MealTrackingService.calculate_daily_summary(
                user_id=sample_daily_summary.user_id,
                summary_date=sample_daily_summary.summary_date,
                force_recalculate=True
            )
            
            # Should be the same summary object but recalculated
            assert summary.id == sample_daily_summary.id
            # Values will be recalculated (reset to 0 then aggregated)
            assert summary.planned_calories == 0.0  # No trackings exist, so reset to 0
    
    def test_calculate_daily_summary_needs_recalculation(self, sample_daily_summary):
        """Test summary that needs recalculation"""
        # Mark as needing recalculation
        sample_daily_summary.needs_recalculation = True
        db.session.commit()
        
        with patch.object(User, 'get_daily_targets') as mock_targets:
            mock_targets.return_value = {
                'calories': 2000.0,
                'protein': 150.0,
                'carbs': 250.0,
                'fat': 65.0,
                'fiber': 30.0,
                'sodium': 2300.0,
                'sugar': 50.0
            }
            
            summary = MealTrackingService.calculate_daily_summary(
                user_id=sample_daily_summary.user_id,
                summary_date=sample_daily_summary.summary_date
            )
            
            # Should recalculate and mark as not needing recalculation
            assert summary.needs_recalculation == False
            assert summary.calculation_version == 1
    
    def test_calculate_daily_summary_user_not_found(self):
        """Test calculating summary for non-existent user"""
        with pytest.raises(ValueError, match="User not found"):
            MealTrackingService.calculate_daily_summary(
                user_id=99999,
                summary_date=date.today()
            )
    
    def test_invalidate_daily_summary_existing(self, sample_daily_summary):
        """Test invalidating existing daily summary"""
        assert sample_daily_summary.needs_recalculation == False
        
        MealTrackingService.invalidate_daily_summary(
            user_id=sample_daily_summary.user_id,
            target_date=sample_daily_summary.summary_date
        )
        
        db.session.refresh(sample_daily_summary)
        assert sample_daily_summary.needs_recalculation == True
    
    def test_invalidate_daily_summary_non_existent(self, sample_user):
        """Test invalidating non-existent daily summary"""
        # Should not raise error
        MealTrackingService.invalidate_daily_summary(
            user_id=sample_user.id,
            target_date=date.today()
        )
    
    def test_get_weekly_summary_with_data(self, sample_user, test_data_factory):
        """Test getting weekly summary with data"""
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        
        # Create daily summaries for the week
        for i in range(7):
            day = week_start + timedelta(days=i)
            summary = DailyNutritionSummary(
                user_id=sample_user.id,
                summary_date=day,
                actual_calories=1800.0 + (i * 50),  # Varying calories
                actual_protein=120.0 + (i * 5),     # Varying protein
                plan_adherence_score=90.0 + i,      # Varying adherence
                target_adherence_score=85.0 + i,
                meals_planned=3,
                meals_consumed=2 + (i % 2),  # Varying consumption
                hit_calorie_target=(i % 2 == 0),
                hit_protein_target=(i % 3 == 0),
                avg_satisfaction_rating=4.0 + (i * 0.1) if i < 5 else None
            )
            db.session.add(summary)
        db.session.commit()
        
        weekly_data = MealTrackingService.get_weekly_summary(sample_user.id, week_start)
        
        assert weekly_data['days_tracked'] == 7
        assert weekly_data['week_start'] == week_start.isoformat()
        assert weekly_data['total_meals_planned'] == 21  # 7 days * 3 meals
        assert weekly_data['total_meals_consumed'] == 18  # Calculated based on pattern
        assert 'avg_calories' in weekly_data
        assert 'avg_protein' in weekly_data
        assert 'avg_plan_adherence' in weekly_data
        assert 'weekly_completion_rate' in weekly_data
        assert 'days_hit_calorie_target' in weekly_data
        assert 'avg_satisfaction' in weekly_data
        assert len(weekly_data['daily_summaries']) == 7
    
    def test_get_weekly_summary_no_data(self, sample_user):
        """Test getting weekly summary with no data"""
        future_week = date.today() + timedelta(days=14)
        
        weekly_data = MealTrackingService.get_weekly_summary(sample_user.id, future_week)
        
        assert weekly_data['days_tracked'] == 0
        assert 'summary' in weekly_data
        assert weekly_data['week_start'] == future_week.isoformat()
    
    def test_get_monthly_summary_with_data(self, sample_user):
        """Test getting monthly summary with data"""
        year = 2025
        month = 8
        month_str = f"{year}-{month:02d}"
        
        # Create daily summaries for the month
        for day in range(1, 32):  # August has 31 days
            try:
                day_date = date(year, month, day)
                summary = DailyNutritionSummary(
                    user_id=sample_user.id,
                    summary_date=day_date,
                    month_year=month_str,
                    actual_calories=1700.0 + (day * 10),
                    actual_protein=110.0 + (day * 2),
                    plan_adherence_score=80.0 + (day % 20),
                    target_adherence_score=75.0 + (day % 25),
                    meals_planned=3,
                    meals_consumed=2 if day % 7 != 0 else 3,  # More consumption on "weekends"
                    hit_calorie_target=(day % 3 == 0),
                    hit_protein_target=(day % 4 == 0),
                    overall_nutrition_score=70.0 + (day % 30)
                )
                db.session.add(summary)
            except ValueError:  # Invalid date (e.g., Feb 30)
                continue
        db.session.commit()
        
        monthly_data = MealTrackingService.get_monthly_summary(sample_user.id, year, month)
        
        assert monthly_data['year'] == year
        assert monthly_data['month'] == month
        assert monthly_data['month_year'] == month_str
        assert monthly_data['days_tracked'] == 31
        assert 'avg_daily_calories' in monthly_data
        assert 'avg_daily_protein' in monthly_data
        assert 'total_meals_planned' in monthly_data
        assert 'monthly_completion_rate' in monthly_data
        assert 'calorie_target_success_rate' in monthly_data
        assert 'protein_target_success_rate' in monthly_data
        assert 'best_day' in monthly_data
        assert 'worst_day' in monthly_data
        
        # Check best/worst day structure
        assert 'date' in monthly_data['best_day']
        assert 'score' in monthly_data['best_day']
        assert 'adherence' in monthly_data['best_day']
    
    def test_get_monthly_summary_no_data(self, sample_user):
        """Test getting monthly summary with no data"""
        monthly_data = MealTrackingService.get_monthly_summary(sample_user.id, 2025, 12)
        
        assert monthly_data['days_tracked'] == 0
        assert 'summary' in monthly_data
        assert monthly_data['year'] == 2025
        assert monthly_data['month'] == 12
    
    def test_get_adherence_trends_with_data(self, sample_user):
        """Test getting adherence trends with data"""
        # Create daily summaries over 30 days
        start_date = date.today() - timedelta(days=30)
        
        for i in range(30):
            day = start_date + timedelta(days=i)
            # Create improving trend
            plan_score = 60.0 + (i * 1.2)  # Improving over time
            target_score = 55.0 + (i * 1.0)
            completion = 70.0 + (i * 0.8)
            
            summary = DailyNutritionSummary(
                user_id=sample_user.id,
                summary_date=day,
                plan_adherence_score=min(100.0, plan_score),
                target_adherence_score=min(100.0, target_score),
                meals_planned=3,
                meals_consumed=2 if i < 20 else 3  # Improving completion
            )
            db.session.add(summary)
        db.session.commit()
        
        trends = MealTrackingService.get_adherence_trends(sample_user.id, 30)
        
        assert 'error' not in trends
        assert trends['period_days'] == 30
        assert trends['data_points'] == 30
        assert 'avg_plan_adherence' in trends
        assert 'avg_target_adherence' in trends
        assert 'avg_completion_rate' in trends
        assert 'plan_adherence_trend' in trends
        assert 'target_adherence_trend' in trends
        assert 'completion_trend' in trends
        assert 'recent_7_day_avg' in trends
        
        # Should detect improving trend
        assert trends['plan_adherence_trend'] in ['improving', 'stable']
        assert trends['completion_trend'] in ['improving', 'stable']
    
    def test_get_adherence_trends_insufficient_data(self, sample_user):
        """Test getting adherence trends with insufficient data"""
        # Create only one summary
        summary = DailyNutritionSummary(
            user_id=sample_user.id,
            summary_date=date.today()
        )
        db.session.add(summary)
        db.session.commit()
        
        trends = MealTrackingService.get_adherence_trends(sample_user.id, 30)
        
        assert 'error' in trends
        assert trends['error'] == 'Insufficient data for trend analysis'
    
    def test_get_adherence_trends_trend_calculation(self, sample_user):
        """Test trend calculation logic"""
        # Create declining trend data
        start_date = date.today() - timedelta(days=20)
        
        for i in range(20):
            day = start_date + timedelta(days=i)
            # Declining scores
            plan_score = 90.0 - (i * 2.0)  # Declining
            
            summary = DailyNutritionSummary(
                user_id=sample_user.id,
                summary_date=day,
                plan_adherence_score=max(0.0, plan_score),
                target_adherence_score=max(0.0, plan_score - 5),
                meals_planned=3,
                meals_consumed=2
            )
            db.session.add(summary)
        db.session.commit()
        
        trends = MealTrackingService.get_adherence_trends(sample_user.id, 20)
        
        # Should detect declining trend
        assert trends['plan_adherence_trend'] == 'declining'
        assert trends['target_adherence_trend'] == 'declining'


class TestMealTrackingServiceIntegration:
    """Integration tests for MealTrackingService with other components"""
    
    def test_end_to_end_meal_tracking_workflow(self, sample_user, sample_meal_plan, sample_recipe):
        """Test complete meal tracking workflow"""
        today = date.today()
        
        # Step 1: Create trackings from meal plan
        trackings = MealTrackingService.create_meal_tracking_from_plan(
            user_id=sample_user.id,
            meal_plan_id=sample_meal_plan.id,
            target_date=today
        )
        
        assert len(trackings) >= 1
        breakfast = trackings[0]
        
        # Step 2: Mark as consumed
        consumption_data = {
            'consumption_time': datetime.now(),
            'nutrition': {
                'calories': 420.0,
                'protein': 22.0,
                'carbs': 52.0,
                'fat': 16.0
            },
            'satisfaction_rating': 4
        }
        
        consumed_tracking = MealTrackingService.update_meal_status(
            tracking_id=breakfast.id,
            user_id=sample_user.id,
            status=MealStatus.CONSUMED,
            consumption_data=consumption_data
        )
        
        assert consumed_tracking.status == MealStatus.CONSUMED
        assert consumed_tracking.actual_calories == 420.0
        
        # Step 3: Calculate daily summary
        with patch.object(User, 'get_daily_targets') as mock_targets:
            mock_targets.return_value = {
                'calories': 2000.0,
                'protein': 150.0,
                'carbs': 250.0,
                'fat': 65.0,
                'fiber': 30.0,
                'sodium': 2300.0,
                'sugar': 50.0
            }
            
            summary = MealTrackingService.calculate_daily_summary(
                user_id=sample_user.id,
                summary_date=today
            )
            
            assert summary.actual_calories >= 420.0  # At least the consumed meal
            assert summary.meals_consumed >= 1
    
    def test_summary_aggregation_accuracy(self, sample_user, test_data_factory):
        """Test accuracy of summary aggregation from multiple trackings"""
        today = date.today()
        
        # Create precise tracking data
        tracking_data = [
            {'meal_type': 'repas1', 'calories': 400.0, 'protein': 25.0, 'status': MealStatus.CONSUMED},
            {'meal_type': 'repas2', 'calories': 600.0, 'protein': 35.0, 'status': MealStatus.CONSUMED},
            {'meal_type': 'repas3', 'calories': 500.0, 'protein': 30.0, 'status': MealStatus.SKIPPED},
            {'meal_type': 'collation', 'calories': 200.0, 'protein': 10.0, 'status': MealStatus.REPLACED}
        ]
        
        trackings = []
        for data in tracking_data:
            tracking = test_data_factory.create_meal_tracking(
                user_id=sample_user.id,
                meal_date=today,
                meal_type=data['meal_type'],
                status=data['status'],
                planned_calories=data['calories'],
                planned_protein=data['protein']
            )
            trackings.append(tracking)
        
        # Mark replaced meal with different actual nutrition
        replaced_tracking = next(t for t in trackings if t.meal_type == 'collation')
        MealTrackingService.update_meal_status(
            tracking_id=replaced_tracking.id,
            user_id=sample_user.id,
            status=MealStatus.REPLACED,
            consumption_data={
                'nutrition': {
                    'calories': 250.0,  # Different from planned
                    'protein': 15.0
                }
            }
        )
        
        with patch.object(User, 'get_daily_targets') as mock_targets:
            mock_targets.return_value = {
                'calories': 2000.0,
                'protein': 150.0,
                'carbs': 250.0,
                'fat': 65.0,
                'fiber': 30.0,
                'sodium': 2300.0,
                'sugar': 50.0
            }
            
            summary = MealTrackingService.calculate_daily_summary(
                user_id=sample_user.id,
                summary_date=today
            )
            
            # Check planned totals
            expected_planned_calories = 400 + 600 + 500 + 200  # All planned
            assert summary.planned_calories == expected_planned_calories
            
            # Check actual totals (effective nutrition)
            # repas1: 400 (consumed), repas2: 600 (consumed), repas3: 0 (skipped), collation: 250 (replaced)
            expected_actual_calories = 400 + 600 + 0 + 250
            assert summary.actual_calories == expected_actual_calories
            
            # Check meal counts
            assert summary.meals_planned == 4
            assert summary.meals_consumed == 3  # consumed + replaced (skipped not counted)
            assert summary.meals_skipped == 1
            assert summary.meals_replaced == 1