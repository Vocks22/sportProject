"""
Unit tests for Meal Tracking models (US1.8)
Tests for MealTracking and DailyNutritionSummary models
"""

import pytest
from datetime import date, datetime, time, timedelta
from sqlalchemy.exc import IntegrityError
import json

from models.meal_tracking import MealTracking, DailyNutritionSummary, MealStatus
from database import db


class TestMealTrackingModel:
    """Test cases for MealTracking model"""
    
    def test_meal_tracking_creation(self, sample_user):
        """Test basic meal tracking creation"""
        tracking = MealTracking(
            user_id=sample_user.id,
            meal_date=date.today(),
            meal_type="repas1",
            meal_name="Test Breakfast",
            status=MealStatus.PLANNED,
            planned_calories=400.0,
            planned_protein=20.0,
            planned_carbs=50.0,
            planned_fat=15.0
        )
        db.session.add(tracking)
        db.session.commit()
        
        assert tracking.id is not None
        assert tracking.user_id == sample_user.id
        assert tracking.meal_type == "repas1"
        assert tracking.status == MealStatus.PLANNED
        assert tracking.planned_calories == 400.0
        assert tracking.planned_portion_size == 1.0  # Default value
    
    def test_meal_tracking_unique_constraint(self, sample_user):
        """Test unique constraint on user_id, meal_date, meal_type"""
        today = date.today()
        
        # Create first tracking
        tracking1 = MealTracking(
            user_id=sample_user.id,
            meal_date=today,
            meal_type="repas1",
            status=MealStatus.PLANNED
        )
        db.session.add(tracking1)
        db.session.commit()
        
        # Try to create duplicate
        tracking2 = MealTracking(
            user_id=sample_user.id,
            meal_date=today,
            meal_type="repas1",
            status=MealStatus.PLANNED
        )
        db.session.add(tracking2)
        
        with pytest.raises(IntegrityError):
            db.session.commit()
    
    def test_meal_status_enum(self, sample_user):
        """Test meal status enum values"""
        today = date.today()
        
        for status in MealStatus:
            tracking = MealTracking(
                user_id=sample_user.id,
                meal_date=today,
                meal_type=f"repas{status.value}",  # Make unique
                status=status
            )
            db.session.add(tracking)
        
        db.session.commit()
        
        # Verify all statuses were saved correctly
        trackings = MealTracking.query.filter_by(user_id=sample_user.id).all()
        assert len(trackings) == len(MealStatus)
    
    def test_check_constraints(self, sample_user):
        """Test database check constraints"""
        today = date.today()
        
        # Test satisfaction rating constraint (1-5)
        with pytest.raises(IntegrityError):
            tracking = MealTracking(
                user_id=sample_user.id,
                meal_date=today,
                meal_type="repas1",
                satisfaction_rating=6  # Invalid: > 5
            )
            db.session.add(tracking)
            db.session.commit()
        
        db.session.rollback()
        
        # Test difficulty rating constraint (1-5)
        with pytest.raises(IntegrityError):
            tracking = MealTracking(
                user_id=sample_user.id,
                meal_date=today,
                meal_type="repas1",
                difficulty_rating=0  # Invalid: < 1
            )
            db.session.add(tracking)
            db.session.commit()
        
        db.session.rollback()
        
        # Test planned portion size constraint (> 0)
        with pytest.raises(IntegrityError):
            tracking = MealTracking(
                user_id=sample_user.id,
                meal_date=today,
                meal_type="repas1",
                planned_portion_size=0  # Invalid: <= 0
            )
            db.session.add(tracking)
            db.session.commit()
    
    def test_json_property_setters_getters(self, sample_meal_tracking):
        """Test JSON property setters and getters"""
        tracking = sample_meal_tracking
        
        # Test photo URLs
        photo_urls = ["http://example.com/photo1.jpg", "http://example.com/photo2.jpg"]
        tracking.photo_urls_list = photo_urls
        db.session.commit()
        
        # Refresh from database
        db.session.refresh(tracking)
        assert tracking.photo_urls_list == photo_urls
        
        # Test modifications
        modifications = {"ingredient1": {"old_qty": 100, "new_qty": 150}}
        tracking.modifications = modifications
        db.session.commit()
        
        db.session.refresh(tracking)
        assert tracking.modifications == modifications
        
        # Test substitutions
        substitutions = {"chicken": "turkey", "rice": "quinoa"}
        tracking.substitutions = substitutions
        db.session.commit()
        
        db.session.refresh(tracking)
        assert tracking.substitutions == substitutions
    
    def test_json_property_error_handling(self, sample_meal_tracking):
        """Test JSON property error handling for malformed data"""
        tracking = sample_meal_tracking
        
        # Directly set malformed JSON
        tracking.photo_urls = "not-valid-json"
        db.session.commit()
        
        # Should return empty list for malformed JSON
        assert tracking.photo_urls_list == []
        
        # Test with None
        tracking.photo_urls = None
        db.session.commit()
        assert tracking.photo_urls_list == []
    
    def test_calculated_properties(self, sample_meal_tracking):
        """Test calculated properties for nutrition variance"""
        tracking = sample_meal_tracking
        
        # Set actual nutrition values
        tracking.actual_calories = 450.0  # planned: 400
        tracking.actual_protein = 30.0    # planned: 25
        tracking.actual_carbs = 40.0      # planned: 45
        tracking.actual_fat = 18.0        # planned: 15
        db.session.commit()
        
        # Test variance calculations
        assert tracking.calories_variance == 50.0
        assert tracking.protein_variance == 5.0
        assert tracking.carbs_variance == -5.0
        assert tracking.fat_variance == 3.0
        
        # Test with no actual values
        tracking.actual_calories = None
        tracking.actual_protein = None
        tracking.actual_carbs = None
        tracking.actual_fat = None
        db.session.commit()
        
        assert tracking.calories_variance is None
        assert tracking.protein_variance is None
        assert tracking.carbs_variance is None
        assert tracking.fat_variance is None
    
    def test_is_consumed_property(self, sample_user):
        """Test is_consumed property for different statuses"""
        today = date.today()
        
        # Test different statuses
        test_cases = [
            (MealStatus.PLANNED, False),
            (MealStatus.CONSUMED, True),
            (MealStatus.MODIFIED, True),
            (MealStatus.REPLACED, True),
            (MealStatus.SKIPPED, False)
        ]
        
        for status, expected in test_cases:
            tracking = MealTracking(
                user_id=sample_user.id,
                meal_date=today,
                meal_type=f"test_{status.value}",
                status=status
            )
            db.session.add(tracking)
            db.session.commit()
            
            assert tracking.is_consumed == expected
    
    def test_effective_nutrition_properties(self, sample_meal_tracking):
        """Test effective nutrition properties (actual if consumed, planned otherwise)"""
        tracking = sample_meal_tracking
        
        # Test with planned status (should use planned values)
        tracking.status = MealStatus.PLANNED
        db.session.commit()
        
        assert tracking.effective_calories == tracking.planned_calories
        assert tracking.effective_protein == tracking.planned_protein
        assert tracking.effective_carbs == tracking.planned_carbs
        assert tracking.effective_fat == tracking.planned_fat
        
        # Test with consumed status and actual values
        tracking.status = MealStatus.CONSUMED
        tracking.actual_calories = 500.0
        tracking.actual_protein = 35.0
        tracking.actual_carbs = 55.0
        tracking.actual_fat = 20.0
        tracking.actual_fiber = 8.0
        tracking.actual_sodium = 250.0
        tracking.actual_sugar = 12.0
        db.session.commit()
        
        assert tracking.effective_calories == tracking.actual_calories
        assert tracking.effective_protein == tracking.actual_protein
        assert tracking.effective_carbs == tracking.actual_carbs
        assert tracking.effective_fat == tracking.actual_fat
        assert tracking.effective_fiber == tracking.actual_fiber
        assert tracking.effective_sodium == tracking.actual_sodium
        assert tracking.effective_sugar == tracking.actual_sugar
        
        # Test with consumed status but no actual values (should use planned)
        tracking.actual_calories = None
        tracking.actual_protein = None
        db.session.commit()
        
        assert tracking.effective_calories == tracking.planned_calories
        assert tracking.effective_protein == tracking.planned_protein
    
    def test_timing_variance_calculation(self, sample_meal_tracking):
        """Test timing variance calculation"""
        tracking = sample_meal_tracking
        
        # Set planned and actual times
        tracking.consumption_time_planned = time(8, 0)    # 8:00 AM
        tracking.consumption_time_actual = time(8, 30)    # 8:30 AM
        db.session.commit()
        
        # Should be 30 minutes late
        assert tracking.timing_variance_minutes == 30
        
        # Test early consumption
        tracking.consumption_time_actual = time(7, 45)    # 7:45 AM
        db.session.commit()
        
        # Should be -15 minutes (15 minutes early)
        assert tracking.timing_variance_minutes == -15
        
        # Test with missing times
        tracking.consumption_time_planned = None
        db.session.commit()
        
        assert tracking.timing_variance_minutes is None
    
    def test_mark_as_consumed_method(self, sample_meal_tracking):
        """Test mark_as_consumed method"""
        tracking = sample_meal_tracking
        
        consumption_time = datetime.now()
        actual_nutrition = {
            'calories': 450.0,
            'protein': 30.0,
            'carbs': 50.0,
            'fat': 18.0,
            'fiber': 6.0,
            'sodium': 220.0,
            'sugar': 12.0
        }
        
        tracking.mark_as_consumed(
            consumption_time=consumption_time,
            actual_nutrition=actual_nutrition,
            portion_size=1.2,
            notes="Delicious meal!",
            rating=5
        )
        db.session.commit()
        
        assert tracking.status == MealStatus.CONSUMED
        assert tracking.consumption_datetime == consumption_time
        assert tracking.consumption_time_actual == consumption_time.time()
        assert tracking.actual_calories == 450.0
        assert tracking.actual_protein == 30.0
        assert tracking.actual_portion_size == 1.2
        assert tracking.user_notes == "Delicious meal!"
        assert tracking.satisfaction_rating == 5
    
    def test_mark_as_skipped_method(self, sample_meal_tracking):
        """Test mark_as_skipped method"""
        tracking = sample_meal_tracking
        
        tracking.mark_as_skipped(reason="Not hungry")
        db.session.commit()
        
        assert tracking.status == MealStatus.SKIPPED
        assert tracking.skip_reason == "Not hungry"
    
    def test_mark_as_replaced_method(self, sample_meal_tracking, sample_recipe):
        """Test mark_as_replaced method"""
        tracking = sample_meal_tracking
        
        replacement_nutrition = {
            'calories': 350.0,
            'protein': 28.0,
            'carbs': 35.0,
            'fat': 12.0
        }
        
        tracking.mark_as_replaced(
            replacement_recipe_id=sample_recipe.id,
            replacement_name="Grilled Chicken Salad",
            reason="Preferred option",
            actual_nutrition=replacement_nutrition
        )
        db.session.commit()
        
        assert tracking.status == MealStatus.REPLACED
        assert tracking.replacement_recipe_id == sample_recipe.id
        assert tracking.replacement_name == "Grilled Chicken Salad"
        assert tracking.replacement_reason == "Preferred option"
        assert tracking.actual_calories == 350.0
        assert tracking.actual_protein == 28.0
    
    def test_to_dict_method(self, sample_meal_tracking):
        """Test to_dict method output"""
        tracking = sample_meal_tracking
        
        # Add some actual nutrition data
        tracking.actual_calories = 450.0
        tracking.actual_protein = 30.0
        tracking.satisfaction_rating = 4
        tracking.photo_urls_list = ["http://example.com/photo.jpg"]
        tracking.modifications = {"sauce": {"added": True}}
        db.session.commit()
        
        result = tracking.to_dict()
        
        # Check required fields
        assert 'id' in result
        assert 'user_id' in result
        assert 'meal_date' in result
        assert 'meal_type' in result
        assert 'status' in result
        assert 'planned_nutrition' in result
        assert 'actual_nutrition' in result
        assert 'effective_nutrition' in result
        assert 'nutrition_variance' in result
        assert 'is_consumed' in result
        
        # Check planned nutrition structure
        planned = result['planned_nutrition']
        assert planned['calories'] == tracking.planned_calories
        assert planned['protein'] == tracking.planned_protein
        
        # Check actual nutrition structure
        actual = result['actual_nutrition']
        assert actual['calories'] == tracking.actual_calories
        assert actual['protein'] == tracking.actual_protein
        
        # Check effective nutrition
        effective = result['effective_nutrition']
        assert effective['calories'] == tracking.effective_calories
        
        # Check variance
        variance = result['nutrition_variance']
        assert variance['calories'] == tracking.calories_variance
        
        # Check other fields
        assert result['satisfaction_rating'] == 4
        assert result['photo_urls'] == ["http://example.com/photo.jpg"]
        assert result['modifications'] == {"sauce": {"added": True}}
    
    def test_create_from_meal_plan_static_method(self, sample_user, sample_recipe):
        """Test create_from_meal_plan static method"""
        today = date.today()
        
        tracking = MealTracking.create_from_meal_plan(
            user_id=sample_user.id,
            meal_plan_id=1,  # Mock meal plan ID
            meal_date=today,
            meal_type="repas1",
            recipe_id=sample_recipe.id
        )
        
        assert tracking.user_id == sample_user.id
        assert tracking.meal_plan_id == 1
        assert tracking.meal_date == today
        assert tracking.meal_type == "repas1"
        assert tracking.recipe_id == sample_recipe.id
        assert tracking.status == MealStatus.PLANNED
        assert tracking.meal_name == sample_recipe.name
        # Note: Nutrition values depend on recipe's calculated totals
    
    def test_relationships(self, sample_meal_tracking, sample_user, sample_meal_plan, sample_recipe):
        """Test model relationships"""
        tracking = sample_meal_tracking
        
        # Test user relationship
        assert tracking.user == sample_user
        assert tracking in sample_user.meal_trackings
        
        # Test meal plan relationship
        assert tracking.meal_plan == sample_meal_plan
        assert tracking in sample_meal_plan.meal_trackings
        
        # Test recipe relationship
        assert tracking.recipe == sample_recipe
        assert tracking in sample_recipe.meal_trackings


class TestDailyNutritionSummaryModel:
    """Test cases for DailyNutritionSummary model"""
    
    def test_daily_summary_creation(self, sample_user):
        """Test basic daily nutrition summary creation"""
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        
        summary = DailyNutritionSummary(
            user_id=sample_user.id,
            summary_date=today,
            planned_calories=1800.0,
            planned_protein=120.0,
            actual_calories=1750.0,
            actual_protein=115.0,
            target_calories=1800.0,
            target_protein=120.0,
            meals_planned=3,
            meals_consumed=2,
            week_start=week_start,
            month_year=today.strftime('%Y-%m')
        )
        db.session.add(summary)
        db.session.commit()
        
        assert summary.id is not None
        assert summary.user_id == sample_user.id
        assert summary.summary_date == today
        assert summary.planned_calories == 1800.0
        assert summary.actual_calories == 1750.0
    
    def test_unique_constraint_user_date(self, sample_user):
        """Test unique constraint on user_id and summary_date"""
        today = date.today()
        
        # Create first summary
        summary1 = DailyNutritionSummary(
            user_id=sample_user.id,
            summary_date=today
        )
        db.session.add(summary1)
        db.session.commit()
        
        # Try to create duplicate
        summary2 = DailyNutritionSummary(
            user_id=sample_user.id,
            summary_date=today
        )
        db.session.add(summary2)
        
        with pytest.raises(IntegrityError):
            db.session.commit()
    
    def test_check_constraints(self, sample_user):
        """Test database check constraints"""
        today = date.today()
        
        # Test adherence score constraints (0-100)
        with pytest.raises(IntegrityError):
            summary = DailyNutritionSummary(
                user_id=sample_user.id,
                summary_date=today,
                plan_adherence_score=105.0  # Invalid: > 100
            )
            db.session.add(summary)
            db.session.commit()
        
        db.session.rollback()
        
        # Test satisfaction rating constraints (1-5)
        with pytest.raises(IntegrityError):
            summary = DailyNutritionSummary(
                user_id=sample_user.id,
                summary_date=today,
                avg_satisfaction_rating=6.0  # Invalid: > 5
            )
            db.session.add(summary)
            db.session.commit()
        
        db.session.rollback()
        
        # Test meals consumed <= planned constraint
        with pytest.raises(IntegrityError):
            summary = DailyNutritionSummary(
                user_id=sample_user.id,
                summary_date=today,
                meals_planned=2,
                meals_consumed=3  # Invalid: consumed > planned
            )
            db.session.add(summary)
            db.session.commit()
    
    def test_calculated_properties(self, sample_daily_summary):
        """Test calculated properties"""
        summary = sample_daily_summary
        
        # Test completion rate
        expected_completion = (2 / 3) * 100  # 2 consumed out of 3 planned
        assert abs(summary.completion_rate - expected_completion) < 0.01
        
        # Test skip rate
        expected_skip = (1 / 3) * 100  # 1 skipped out of 3 planned
        assert abs(summary.skip_rate - expected_skip) < 0.01
        
        # Test modification rate (0 modified/replaced in sample data)
        assert summary.modification_rate == 0.0
        
        # Test timing adherence rate (no timing data in sample)
        assert summary.timing_adherence_rate == 0.0
    
    def test_calorie_adherence_to_target(self, sample_daily_summary):
        """Test calorie adherence calculation"""
        summary = sample_daily_summary
        
        # Sample data: actual=1750, target=1800 (2.8% under target)
        adherence = summary.calorie_adherence_to_target
        assert adherence == 100.0  # Should be perfect (within 5% tolerance)
        
        # Test with larger variance
        summary.actual_calories = 1600.0  # 11.1% under target
        assert summary.calorie_adherence_to_target < 95.0
        
        # Test with no target
        summary.target_calories = None
        assert summary.calorie_adherence_to_target == 0.0
    
    def test_protein_adherence_to_target(self, sample_daily_summary):
        """Test protein adherence calculation"""
        summary = sample_daily_summary
        
        # Sample data: actual=115, target=120 (4.2% under target)
        adherence = summary.protein_adherence_to_target
        assert adherence > 90.0  # Should be good but penalized for deficit
        
        # Test with excess protein (should be good)
        summary.actual_protein = 150.0  # 25% over target
        assert summary.protein_adherence_to_target == 100.0
        
        # Test with excessive protein
        summary.actual_protein = 300.0  # 150% over target (2.5x target)
        assert summary.protein_adherence_to_target < 100.0
    
    def test_overall_nutrition_score(self, sample_daily_summary):
        """Test overall nutrition score calculation"""
        summary = sample_daily_summary
        
        score = summary.overall_nutrition_score
        assert 0 <= score <= 100
        assert isinstance(score, float)
        
        # Score should be reasonable for decent adherence
        assert score > 50.0  # Sample data has good adherence
    
    def test_nutrition_balance_score(self, sample_daily_summary):
        """Test nutrition balance score calculation"""
        summary = sample_daily_summary
        
        score = summary.nutrition_balance_score
        assert 0 <= score <= 100
        assert isinstance(score, float)
        
        # Test with zero calories (should return 0)
        summary.actual_calories = 0.0
        assert summary.nutrition_balance_score == 0.0
        
        # Test with no targets
        summary.target_calories = None
        assert summary.nutrition_balance_score == 0.0
    
    def test_calculate_all_scores_method(self, sample_daily_summary):
        """Test calculate_all_scores method"""
        summary = sample_daily_summary
        
        # Reset scores to test calculation
        summary.plan_adherence_score = 0.0
        summary.target_adherence_score = 0.0
        summary.hit_calorie_target = False
        summary.hit_protein_target = False
        
        summary.calculate_all_scores()
        db.session.commit()
        
        # Scores should be recalculated
        assert summary.plan_adherence_score > 0.0
        assert summary.target_adherence_score > 0.0
        
        # Achievement flags should be set based on data
        # Sample data has good adherence, so targets should be hit
        assert summary.hit_calorie_target == True
        assert summary.hit_protein_target == True
    
    def test_calculate_deficits_surpluses_method(self, sample_daily_summary):
        """Test calculate_deficits_surpluses method"""
        summary = sample_daily_summary
        
        summary.calculate_deficits_surpluses()
        db.session.commit()
        
        # Sample data: actual=1750, target=1800
        # Calorie deficit should be positive (50 calories deficit)
        assert summary.calorie_deficit_surplus == 50.0
        
        # Protein surplus should be negative (5g deficit: 120-115)
        assert summary.protein_deficit_surplus == -5.0
    
    def test_to_dict_method(self, sample_daily_summary):
        """Test to_dict method output"""
        summary = sample_daily_summary
        
        result = summary.to_dict()
        
        # Check required top-level fields
        assert 'id' in result
        assert 'user_id' in result
        assert 'summary_date' in result
        assert 'planned_nutrition' in result
        assert 'actual_nutrition' in result
        assert 'target_nutrition' in result
        assert 'adherence_scores' in result
        assert 'meal_stats' in result
        assert 'deficit_surplus' in result
        assert 'timing' in result
        assert 'quality' in result
        assert 'achievements' in result
        
        # Check nested structure
        planned = result['planned_nutrition']
        assert 'calories' in planned
        assert 'protein' in planned
        
        adherence = result['adherence_scores']
        assert 'plan_adherence' in adherence
        assert 'target_adherence' in adherence
        assert 'overall_nutrition' in adherence
        
        meal_stats = result['meal_stats']
        assert 'planned' in meal_stats
        assert 'consumed' in meal_stats
        assert 'completion_rate' in meal_stats
        
        achievements = result['achievements']
        assert 'hit_calorie_target' in achievements
        assert 'hit_protein_target' in achievements
    
    def test_create_from_tracking_data_static_method(self, sample_user, test_data_factory):
        """Test create_from_tracking_data static method"""
        # Create sample tracking data
        trackings = []
        today = date.today()
        
        for meal_type in ['repas1', 'repas2', 'repas3']:
            tracking = test_data_factory.create_meal_tracking(
                user_id=sample_user.id,
                meal_date=today,
                meal_type=meal_type,
                status=MealStatus.CONSUMED
            )
            trackings.append(tracking)
        
        # User targets
        user_targets = {
            'calories': 1800.0,
            'protein': 120.0,
            'carbs': 225.0,
            'fat': 60.0,
            'fiber': 25.0,
            'sodium': 2000.0,
            'sugar': 50.0
        }
        
        summary = DailyNutritionSummary.create_from_tracking_data(
            user_id=sample_user.id,
            summary_date=today,
            meal_trackings=trackings,
            user_targets=user_targets
        )
        
        assert summary.user_id == sample_user.id
        assert summary.summary_date == today
        assert summary.meals_planned == 3
        assert summary.meals_consumed == 3
        assert summary.target_calories == 1800.0
        assert summary.target_protein == 120.0
        
        # Check aggregated nutrition
        expected_calories = sum(t.effective_calories for t in trackings)
        assert summary.actual_calories == expected_calories
        
        # Check week context
        expected_week_start = today - timedelta(days=today.weekday())
        assert summary.week_start == expected_week_start
        
        # Check month context
        assert summary.month_year == today.strftime('%Y-%m')
    
    def test_relationship_with_user(self, sample_daily_summary, sample_user):
        """Test relationship with User model"""
        summary = sample_daily_summary
        
        assert summary.user == sample_user
        assert summary in sample_user.daily_nutrition_summaries


class TestMealStatusEnum:
    """Test cases for MealStatus enum"""
    
    def test_enum_values(self):
        """Test enum values are correct"""
        assert MealStatus.PLANNED.value == 'planned'
        assert MealStatus.CONSUMED.value == 'consumed'
        assert MealStatus.MODIFIED.value == 'modified'
        assert MealStatus.SKIPPED.value == 'skipped'
        assert MealStatus.REPLACED.value == 'replaced'
    
    def test_enum_in_database(self, sample_user):
        """Test enum values work in database"""
        today = date.today()
        
        for status in MealStatus:
            tracking = MealTracking(
                user_id=sample_user.id,
                meal_date=today,
                meal_type=f"test_{status.value}",
                status=status
            )
            db.session.add(tracking)
        
        db.session.commit()
        
        # Verify all were saved correctly
        for status in MealStatus:
            tracking = MealTracking.query.filter_by(
                meal_type=f"test_{status.value}"
            ).first()
            assert tracking is not None
            assert tracking.status == status


class TestModelIntegration:
    """Test integration between models"""
    
    def test_cascade_deletes(self, sample_user, test_data_factory):
        """Test cascade delete behavior"""
        # Create tracking and summary for user
        tracking = test_data_factory.create_meal_tracking(sample_user.id)
        
        today = date.today()
        summary = DailyNutritionSummary(
            user_id=sample_user.id,
            summary_date=today
        )
        db.session.add(summary)
        db.session.commit()
        
        tracking_id = tracking.id
        summary_id = summary.id
        
        # Delete user
        db.session.delete(sample_user)
        db.session.commit()
        
        # Related records should be deleted (CASCADE)
        assert MealTracking.query.get(tracking_id) is None
        assert DailyNutritionSummary.query.get(summary_id) is None
    
    def test_meal_tracking_summary_consistency(self, sample_user, test_data_factory):
        """Test data consistency between tracking and summary"""
        today = date.today()
        
        # Create meal trackings
        trackings = []
        for meal_type in ['repas1', 'repas2']:
            tracking = test_data_factory.create_meal_tracking(
                user_id=sample_user.id,
                meal_date=today,
                meal_type=meal_type,
                status=MealStatus.CONSUMED,
                planned_calories=400.0,
                planned_protein=25.0
            )
            trackings.append(tracking)
        
        # Create summary from trackings
        user_targets = {'calories': 1800.0, 'protein': 120.0}
        summary = DailyNutritionSummary.create_from_tracking_data(
            user_id=sample_user.id,
            summary_date=today,
            meal_trackings=trackings,
            user_targets=user_targets
        )
        
        # Verify consistency
        expected_total_calories = sum(t.effective_calories for t in trackings)
        assert summary.actual_calories == expected_total_calories
        
        expected_total_protein = sum(t.effective_protein for t in trackings)
        assert summary.actual_protein == expected_total_protein
        
        assert summary.meals_planned == len(trackings)
        assert summary.meals_consumed == len(trackings)  # All consumed