#!/usr/bin/env python3
"""
Test script for US1.8 - Meal Tracking Models
Tests model creation and basic functionality
"""

import sys
import os
from datetime import datetime, date

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from models.meal_tracking import MealTracking, DailyNutritionSummary, MealStatus
    from models.user import User
    from models.recipe import Recipe
    from models.meal_plan import MealPlan
    
    print("✅ Successfully imported all meal tracking models")
    
    # Test MealStatus enum
    print("\n🧪 Testing MealStatus enum:")
    for status in MealStatus:
        print(f"  - {status.name}: {status.value}")
    
    # Test MealTracking model structure
    print("\n🧪 Testing MealTracking model structure:")
    sample_tracking = MealTracking(
        user_id=1,
        meal_date=date.today(),
        meal_type='repas1',
        status=MealStatus.PLANNED,
        planned_calories=500.0,
        planned_protein=25.0,
        planned_carbs=45.0,
        planned_fat=15.0
    )
    
    print(f"  - Created sample tracking: {sample_tracking}")
    print(f"  - Status: {sample_tracking.status}")
    print(f"  - Effective calories: {sample_tracking.effective_calories}")
    print(f"  - Is consumed: {sample_tracking.is_consumed}")
    
    # Test property methods
    sample_tracking.photo_urls_list = ['photo1.jpg', 'photo2.jpg']
    print(f"  - Photo URLs: {sample_tracking.photo_urls_list}")
    
    sample_tracking.modifications = {'ingredient1': 'reduced by 50%'}
    print(f"  - Modifications: {sample_tracking.modifications}")
    
    # Test methods
    sample_tracking.mark_as_consumed(
        actual_nutrition={'calories': 480.0, 'protein': 24.0},
        notes='Delicious meal'
    )
    print(f"  - After marking consumed: {sample_tracking.status}")
    print(f"  - Calories variance: {sample_tracking.calories_variance}")
    
    # Test DailyNutritionSummary model
    print("\n🧪 Testing DailyNutritionSummary model structure:")
    sample_summary = DailyNutritionSummary(
        user_id=1,
        summary_date=date.today(),
        planned_calories=2000.0,
        actual_calories=1950.0,
        target_calories=2000.0,
        meals_planned=4,
        meals_consumed=3,
        meals_skipped=1
    )
    
    print(f"  - Created sample summary: {sample_summary}")
    print(f"  - Completion rate: {sample_summary.completion_rate:.1f}%")
    print(f"  - Skip rate: {sample_summary.skip_rate:.1f}%")
    
    # Test score calculations
    sample_summary.calculate_all_scores()
    print(f"  - Plan adherence score: {sample_summary.plan_adherence_score:.1f}%")
    print(f"  - Calorie adherence to target: {sample_summary.calorie_adherence_to_target:.1f}%")
    print(f"  - Overall nutrition score: {sample_summary.overall_nutrition_score:.1f}%")
    
    # Test to_dict method
    tracking_dict = sample_tracking.to_dict()
    summary_dict = sample_summary.to_dict()
    
    print("\n🧪 Testing serialization:")
    print(f"  - MealTracking dict keys: {len(tracking_dict.keys())} keys")
    print(f"  - DailyNutritionSummary dict keys: {len(summary_dict.keys())} keys")
    
    # Test static methods
    print("\n🧪 Testing static creation methods:")
    created_tracking = MealTracking.create_from_meal_plan(
        user_id=1,
        meal_plan_id=1,
        meal_date=date.today(),
        meal_type='repas1',
        recipe_id=1
    )
    print(f"  - Created tracking from meal plan: {created_tracking}")
    
    print("\n✅ All model tests passed successfully!")
    print("\n📊 Model Summary:")
    print(f"  - MealTracking: {len([attr for attr in dir(MealTracking) if not attr.startswith('_')])} attributes/methods")
    print(f"  - DailyNutritionSummary: {len([attr for attr in dir(DailyNutritionSummary) if not attr.startswith('_')])} attributes/methods")
    print(f"  - MealStatus: {len(list(MealStatus))} status values")
    
    print("\n🚀 Models are ready for US1.8 implementation!")

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running from the backend directory and all dependencies are installed")
    sys.exit(1)

except Exception as e:
    print(f"❌ Test error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)