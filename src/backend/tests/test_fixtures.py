"""
Advanced test fixtures and utilities for US1.8 Meal Tracking tests
Comprehensive data fixtures for complex testing scenarios
"""

import pytest
from datetime import date, datetime, time, timedelta
from typing import List, Dict, Any, Optional
import random
import json

from database import db
from models.meal_tracking import MealTracking, DailyNutritionSummary, MealStatus
from models.user import User
from models.recipe import Recipe, Ingredient, RecipeIngredient
from models.meal_plan import MealPlan


class MealTrackingDataFactory:
    """Advanced factory for creating complex meal tracking test scenarios"""
    
    @staticmethod
    def create_week_of_meals(user_id: int, start_date: date = None) -> List[MealTracking]:
        """Create a full week of meal trackings with realistic patterns"""
        if start_date is None:
            start_date = date.today() - timedelta(days=7)
        
        trackings = []
        meal_types = ['repas1', 'repas2', 'repas3', 'collation']
        
        for day in range(7):
            current_date = start_date + timedelta(days=day)
            
            # Realistic meal patterns
            # Breakfast (almost always eaten)
            tracking = MealTracking(
                user_id=user_id,
                meal_date=current_date,
                meal_type='repas1',
                meal_name=f'Petit déjeuner {day + 1}',
                status=MealStatus.CONSUMED if random.random() > 0.1 else MealStatus.PLANNED,
                planned_calories=300 + random.randint(-50, 50),
                planned_protein=15 + random.randint(-3, 5),
                planned_carbs=35 + random.randint(-10, 10),
                planned_fat=12 + random.randint(-3, 3),
                planned_fiber=4 + random.randint(0, 2),
                planned_sodium=150 + random.randint(-50, 50),
                planned_sugar=8 + random.randint(-3, 5),
                consumption_time_planned=time(7, 30)
            )
            
            # Add actual consumption data if consumed
            if tracking.status == MealStatus.CONSUMED:
                tracking.consumption_datetime = datetime.combine(
                    current_date, 
                    time(7, 30 + random.randint(-30, 60))
                )
                tracking.consumption_time_actual = tracking.consumption_datetime.time()
                tracking.satisfaction_rating = random.randint(3, 5)
                
                # Sometimes eat more or less than planned
                multiplier = random.uniform(0.8, 1.3)
                tracking.actual_calories = tracking.planned_calories * multiplier
                tracking.actual_protein = tracking.planned_protein * multiplier
                tracking.actual_carbs = tracking.planned_carbs * multiplier
                tracking.actual_fat = tracking.planned_fat * multiplier
                tracking.actual_portion_size = multiplier
            
            trackings.append(tracking)
            
            # Lunch (usually eaten, sometimes modified)
            lunch_status = random.choices(
                [MealStatus.CONSUMED, MealStatus.MODIFIED, MealStatus.SKIPPED],
                weights=[0.7, 0.2, 0.1]
            )[0]
            
            lunch = MealTracking(
                user_id=user_id,
                meal_date=current_date,
                meal_type='repas2',
                meal_name=f'Déjeuner {day + 1}',
                status=lunch_status,
                planned_calories=500 + random.randint(-100, 100),
                planned_protein=30 + random.randint(-5, 10),
                planned_carbs=60 + random.randint(-15, 15),
                planned_fat=18 + random.randint(-5, 5),
                planned_fiber=8 + random.randint(0, 4),
                planned_sodium=400 + random.randint(-100, 100),
                planned_sugar=12 + random.randint(-5, 8),
                consumption_time_planned=time(12, 30)
            )
            
            if lunch_status in [MealStatus.CONSUMED, MealStatus.MODIFIED]:
                lunch.consumption_datetime = datetime.combine(
                    current_date,
                    time(12, 30 + random.randint(-60, 120))
                )
                lunch.consumption_time_actual = lunch.consumption_datetime.time()
                lunch.satisfaction_rating = random.randint(2, 5)
                
                if lunch_status == MealStatus.MODIFIED:
                    # Modified portions
                    multiplier = random.uniform(0.5, 1.8)
                    lunch.modifications = {
                        'portion_adjustment': True,
                        'original_multiplier': 1.0,
                        'new_multiplier': multiplier
                    }
                else:
                    multiplier = random.uniform(0.9, 1.2)
                
                lunch.actual_calories = lunch.planned_calories * multiplier
                lunch.actual_protein = lunch.planned_protein * multiplier
                lunch.actual_carbs = lunch.planned_carbs * multiplier
                lunch.actual_fat = lunch.planned_fat * multiplier
                lunch.actual_portion_size = multiplier
            
            elif lunch_status == MealStatus.SKIPPED:
                lunch.skip_reason = random.choice([
                    'Pas faim', 'Pas le temps', 'Meeting important', 'Pas disponible'
                ])
            
            trackings.append(lunch)
            
            # Dinner (variable patterns)
            dinner_status = random.choices(
                [MealStatus.CONSUMED, MealStatus.REPLACED, MealStatus.SKIPPED],
                weights=[0.75, 0.15, 0.1]
            )[0]
            
            dinner = MealTracking(
                user_id=user_id,
                meal_date=current_date,
                meal_type='repas3',
                meal_name=f'Dîner {day + 1}',
                status=dinner_status,
                planned_calories=600 + random.randint(-150, 150),
                planned_protein=35 + random.randint(-8, 12),
                planned_carbs=70 + random.randint(-20, 20),
                planned_fat=22 + random.randint(-5, 8),
                planned_fiber=10 + random.randint(0, 5),
                planned_sodium=500 + random.randint(-150, 150),
                planned_sugar=15 + random.randint(-8, 10),
                consumption_time_planned=time(19, 0)
            )
            
            if dinner_status == MealStatus.CONSUMED:
                dinner.consumption_datetime = datetime.combine(
                    current_date,
                    time(19, 0 + random.randint(-60, 120))
                )
                dinner.consumption_time_actual = dinner.consumption_datetime.time()
                dinner.satisfaction_rating = random.randint(3, 5)
                dinner.difficulty_rating = random.randint(1, 4)
                
                multiplier = random.uniform(0.8, 1.3)
                dinner.actual_calories = dinner.planned_calories * multiplier
                dinner.actual_protein = dinner.planned_protein * multiplier
                dinner.actual_carbs = dinner.planned_carbs * multiplier
                dinner.actual_fat = dinner.planned_fat * multiplier
                dinner.actual_portion_size = multiplier
                
            elif dinner_status == MealStatus.REPLACED:
                dinner.replacement_name = random.choice([
                    'Pizza commandée', 'Sushi', 'Salade Caesar', 'Sandwich',
                    'Pâtes carbonara', 'Burger végétarien'
                ])
                dinner.replacement_reason = random.choice([
                    'Pas envie de cuisiner', 'Invité restaurant', 'Livraison',
                    'Plus simple', 'Envie de changement'
                ])
                
                # Replacement nutrition (usually different from planned)
                dinner.actual_calories = dinner.planned_calories * random.uniform(0.6, 1.8)
                dinner.actual_protein = dinner.planned_protein * random.uniform(0.5, 1.5)
                dinner.actual_carbs = dinner.planned_carbs * random.uniform(0.7, 2.0)
                dinner.actual_fat = dinner.planned_fat * random.uniform(0.8, 2.5)
                dinner.satisfaction_rating = random.randint(3, 5)
                
            elif dinner_status == MealStatus.SKIPPED:
                dinner.skip_reason = random.choice([
                    'Trop fatigué', 'Repas de midi copieux', 'Sortie prévue',
                    'Pas faim', 'Régime'
                ])
            
            trackings.append(dinner)
            
            # Snack (optional, weekend more likely)
            is_weekend = current_date.weekday() >= 5
            snack_probability = 0.4 if is_weekend else 0.2
            
            if random.random() < snack_probability:
                snack = MealTracking(
                    user_id=user_id,
                    meal_date=current_date,
                    meal_type='collation',
                    meal_name=f'Collation {day + 1}',
                    status=MealStatus.CONSUMED,
                    planned_calories=150 + random.randint(-50, 100),
                    planned_protein=5 + random.randint(0, 10),
                    planned_carbs=20 + random.randint(-10, 15),
                    planned_fat=6 + random.randint(-2, 8),
                    planned_fiber=2 + random.randint(0, 3),
                    planned_sodium=100 + random.randint(-50, 100),
                    planned_sugar=12 + random.randint(-5, 15),
                    consumption_time_planned=time(15, 30)
                )
                
                snack.consumption_datetime = datetime.combine(
                    current_date,
                    time(15, 30 + random.randint(-120, 120))
                )
                snack.consumption_time_actual = snack.consumption_datetime.time()
                snack.satisfaction_rating = random.randint(3, 5)
                
                multiplier = random.uniform(0.7, 1.5)
                snack.actual_calories = snack.planned_calories * multiplier
                snack.actual_protein = snack.planned_protein * multiplier
                snack.actual_carbs = snack.planned_carbs * multiplier
                snack.actual_fat = snack.planned_fat * multiplier
                snack.actual_portion_size = multiplier
                
                trackings.append(snack)
        
        # Add to database
        for tracking in trackings:
            db.session.add(tracking)
        db.session.commit()
        
        return trackings
    
    @staticmethod
    def create_adherence_progression_data(user_id: int, days: int = 30) -> List[DailyNutritionSummary]:
        """Create data showing adherence improvement over time"""
        summaries = []
        start_date = date.today() - timedelta(days=days)
        
        for day in range(days):
            current_date = start_date + timedelta(days=day)
            
            # Simulate improving adherence over time
            progress_factor = day / days  # 0 to 1
            base_adherence = 60 + (30 * progress_factor)  # 60% to 90%
            
            # Add some realistic variation
            daily_variation = random.uniform(-10, 10)
            plan_adherence = min(100, max(0, base_adherence + daily_variation))
            target_adherence = min(100, max(0, base_adherence - 5 + daily_variation))
            
            # Meal stats
            meals_planned = 3 + random.choice([0, 1])  # 3-4 meals
            completion_rate = 0.5 + (0.4 * progress_factor) + random.uniform(-0.1, 0.1)
            meals_consumed = int(meals_planned * completion_rate)
            meals_skipped = meals_planned - meals_consumed
            
            # Nutrition values
            target_calories = 1800 + random.randint(-200, 200)
            actual_calories = target_calories * (0.7 + 0.4 * progress_factor) * random.uniform(0.9, 1.1)
            
            summary = DailyNutritionSummary(
                user_id=user_id,
                summary_date=current_date,
                planned_calories=target_calories * random.uniform(0.95, 1.05),
                planned_protein=120 * random.uniform(0.9, 1.1),
                planned_carbs=225 * random.uniform(0.9, 1.1),
                planned_fat=60 * random.uniform(0.9, 1.1),
                actual_calories=actual_calories,
                actual_protein=120 * (actual_calories / target_calories) * random.uniform(0.8, 1.2),
                actual_carbs=225 * (actual_calories / target_calories) * random.uniform(0.8, 1.2),
                actual_fat=60 * (actual_calories / target_calories) * random.uniform(0.8, 1.2),
                target_calories=target_calories,
                target_protein=120,
                target_carbs=225,
                target_fat=60,
                plan_adherence_score=plan_adherence,
                target_adherence_score=target_adherence,
                meals_planned=meals_planned,
                meals_consumed=meals_consumed,
                meals_skipped=meals_skipped,
                week_start=current_date - timedelta(days=current_date.weekday()),
                month_year=current_date.strftime('%Y-%m'),
                avg_satisfaction_rating=3.0 + (1.5 * progress_factor) + random.uniform(-0.5, 0.5),
                hit_calorie_target=abs(actual_calories - target_calories) < (target_calories * 0.1),
                hit_protein_target=random.random() < (0.6 + 0.3 * progress_factor)
            )
            
            summary.calculate_all_scores()
            summaries.append(summary)
        
        # Add to database
        for summary in summaries:
            db.session.add(summary)
        db.session.commit()
        
        return summaries
    
    @staticmethod
    def create_diverse_user_patterns(num_users: int = 5) -> List[Dict[str, Any]]:
        """Create diverse users with different eating patterns"""
        user_patterns = []
        
        for i in range(num_users):
            # Create user
            user = User(
                name=f"Test User {i+1}",
                email=f"testuser{i+1}@example.com",
                age=25 + random.randint(0, 40),
                sex=random.choice(['M', 'F']),
                height=160 + random.randint(0, 30),
                weight=60.0 + random.randint(0, 40),
                activity_level=random.choice(['sedentary', 'light', 'moderate', 'active', 'very_active']),
                goal=random.choice(['weight_loss', 'maintenance', 'muscle_gain'])
            )
            db.session.add(user)
            db.session.flush()
            
            # Create pattern type
            pattern_type = random.choice([
                'consistent_high_adherence',
                'improving_over_time',
                'inconsistent_weekends',
                'frequent_replacements',
                'portion_adjuster'
            ])
            
            trackings = []
            if pattern_type == 'consistent_high_adherence':
                # User who consistently follows their plan
                trackings = MealTrackingDataFactory._create_consistent_pattern(user.id)
            elif pattern_type == 'improving_over_time':
                # User who starts poorly but improves
                trackings = MealTrackingDataFactory._create_improvement_pattern(user.id)
            elif pattern_type == 'inconsistent_weekends':
                # Good during week, poor on weekends
                trackings = MealTrackingDataFactory._create_weekend_inconsistent_pattern(user.id)
            elif pattern_type == 'frequent_replacements':
                # Often replaces meals
                trackings = MealTrackingDataFactory._create_replacement_heavy_pattern(user.id)
            elif pattern_type == 'portion_adjuster':
                # Frequently adjusts portions
                trackings = MealTrackingDataFactory._create_portion_adjustment_pattern(user.id)
            
            user_patterns.append({
                'user': user,
                'pattern_type': pattern_type,
                'trackings': trackings
            })
        
        db.session.commit()
        return user_patterns
    
    @staticmethod
    def _create_consistent_pattern(user_id: int) -> List[MealTracking]:
        """Create consistent high-adherence pattern"""
        trackings = []
        start_date = date.today() - timedelta(days=14)
        
        for day in range(14):
            current_date = start_date + timedelta(days=day)
            
            for meal_type, base_nutrition in [
                ('repas1', {'calories': 350, 'protein': 20, 'carbs': 40, 'fat': 14}),
                ('repas2', {'calories': 550, 'protein': 35, 'carbs': 65, 'fat': 18}),
                ('repas3', {'calories': 500, 'protein': 30, 'carbs': 55, 'fat': 16})
            ]:
                tracking = MealTracking(
                    user_id=user_id,
                    meal_date=current_date,
                    meal_type=meal_type,
                    meal_name=f'{meal_type} {day+1}',
                    status=MealStatus.CONSUMED,
                    planned_calories=base_nutrition['calories'],
                    planned_protein=base_nutrition['protein'],
                    planned_carbs=base_nutrition['carbs'],
                    planned_fat=base_nutrition['fat'],
                    consumption_datetime=datetime.combine(current_date, time(8, 12, 19)[['repas1', 'repas2', 'repas3'].index(meal_type)]),
                    satisfaction_rating=random.randint(4, 5)
                )
                
                # Very close to planned nutrition
                multiplier = random.uniform(0.95, 1.05)
                tracking.actual_calories = tracking.planned_calories * multiplier
                tracking.actual_protein = tracking.planned_protein * multiplier
                tracking.actual_carbs = tracking.planned_carbs * multiplier
                tracking.actual_fat = tracking.planned_fat * multiplier
                tracking.actual_portion_size = multiplier
                
                trackings.append(tracking)
        
        return trackings
    
    @staticmethod
    def _create_improvement_pattern(user_id: int) -> List[MealTracking]:
        """Create improving adherence pattern"""
        trackings = []
        start_date = date.today() - timedelta(days=21)
        
        for day in range(21):
            current_date = start_date + timedelta(days=day)
            improvement_factor = day / 20  # 0 to 1
            
            # Early days: more skips and replacements
            # Later days: better adherence
            skip_probability = 0.3 * (1 - improvement_factor)
            replace_probability = 0.2 * (1 - improvement_factor)
            
            for meal_type in ['repas1', 'repas2', 'repas3']:
                rand = random.random()
                if rand < skip_probability:
                    status = MealStatus.SKIPPED
                elif rand < skip_probability + replace_probability:
                    status = MealStatus.REPLACED
                else:
                    status = MealStatus.CONSUMED
                
                tracking = MealTracking(
                    user_id=user_id,
                    meal_date=current_date,
                    meal_type=meal_type,
                    meal_name=f'{meal_type} improvement {day+1}',
                    status=status,
                    planned_calories=400 + random.randint(-50, 50),
                    planned_protein=25 + random.randint(-5, 5),
                    planned_carbs=50 + random.randint(-10, 10),
                    planned_fat=15 + random.randint(-3, 3)
                )
                
                if status == MealStatus.CONSUMED:
                    tracking.satisfaction_rating = 2 + int(3 * improvement_factor)
                    multiplier = random.uniform(0.8, 1.2)
                    tracking.actual_calories = tracking.planned_calories * multiplier
                    tracking.actual_protein = tracking.planned_protein * multiplier
                    tracking.actual_carbs = tracking.planned_carbs * multiplier
                    tracking.actual_fat = tracking.planned_fat * multiplier
                
                elif status == MealStatus.REPLACED:
                    tracking.replacement_name = "Quick substitute"
                    tracking.replacement_reason = "No time to cook"
                
                elif status == MealStatus.SKIPPED:
                    tracking.skip_reason = "Forgot" if day < 10 else "Not hungry"
                
                trackings.append(tracking)
        
        return trackings
    
    @staticmethod
    def _create_weekend_inconsistent_pattern(user_id: int) -> List[MealTracking]:
        """Create pattern with poor weekend adherence"""
        trackings = []
        start_date = date.today() - timedelta(days=14)
        
        for day in range(14):
            current_date = start_date + timedelta(days=day)
            is_weekend = current_date.weekday() >= 5
            
            for meal_type in ['repas1', 'repas2', 'repas3']:
                if is_weekend and random.random() < 0.4:
                    # Weekend: more skips and replacements
                    status = random.choice([MealStatus.SKIPPED, MealStatus.REPLACED, MealStatus.CONSUMED])
                else:
                    # Weekday: mostly consumed
                    status = MealStatus.CONSUMED if random.random() > 0.1 else MealStatus.PLANNED
                
                tracking = MealTracking(
                    user_id=user_id,
                    meal_date=current_date,
                    meal_type=meal_type,
                    meal_name=f'{meal_type} weekend pattern {day+1}',
                    status=status,
                    planned_calories=400,
                    planned_protein=25,
                    planned_carbs=50,
                    planned_fat=15
                )
                
                if status == MealStatus.CONSUMED:
                    if is_weekend:
                        # Weekend portions often larger
                        multiplier = random.uniform(1.2, 1.8)
                        tracking.satisfaction_rating = random.randint(4, 5)
                    else:
                        multiplier = random.uniform(0.9, 1.1)
                        tracking.satisfaction_rating = random.randint(3, 4)
                    
                    tracking.actual_calories = tracking.planned_calories * multiplier
                    tracking.actual_protein = tracking.planned_protein * multiplier
                    tracking.actual_carbs = tracking.planned_carbs * multiplier
                    tracking.actual_fat = tracking.planned_fat * multiplier
                    tracking.actual_portion_size = multiplier
                
                trackings.append(tracking)
        
        return trackings
    
    @staticmethod
    def _create_replacement_heavy_pattern(user_id: int) -> List[MealTracking]:
        """Create pattern with frequent meal replacements"""
        trackings = []
        start_date = date.today() - timedelta(days=10)
        
        replacement_options = [
            'Commande pizza', 'Sushi takeout', 'McDonald\'s', 'Subway sandwich',
            'Salade achetée', 'Livraison thaï', 'Burger végétarien', 'Poke bowl'
        ]
        
        replacement_reasons = [
            'Pas le temps de cuisiner', 'Envie de quelque chose de différent',
            'Meeting de travail', 'Sortie avec des amis', 'Trop fatigué pour cuisiner'
        ]
        
        for day in range(10):
            current_date = start_date + timedelta(days=day)
            
            for meal_type in ['repas1', 'repas2', 'repas3']:
                # High probability of replacement
                if random.random() < 0.6:
                    status = MealStatus.REPLACED
                else:
                    status = MealStatus.CONSUMED
                
                tracking = MealTracking(
                    user_id=user_id,
                    meal_date=current_date,
                    meal_type=meal_type,
                    meal_name=f'Planned {meal_type} {day+1}',
                    status=status,
                    planned_calories=400,
                    planned_protein=25,
                    planned_carbs=50,
                    planned_fat=15
                )
                
                if status == MealStatus.REPLACED:
                    tracking.replacement_name = random.choice(replacement_options)
                    tracking.replacement_reason = random.choice(replacement_reasons)
                    tracking.satisfaction_rating = random.randint(3, 5)
                    
                    # Replacement nutrition often different
                    tracking.actual_calories = random.randint(300, 800)
                    tracking.actual_protein = random.randint(15, 40)
                    tracking.actual_carbs = random.randint(30, 100)
                    tracking.actual_fat = random.randint(10, 50)
                
                elif status == MealStatus.CONSUMED:
                    multiplier = random.uniform(0.9, 1.2)
                    tracking.actual_calories = tracking.planned_calories * multiplier
                    tracking.actual_protein = tracking.planned_protein * multiplier
                    tracking.actual_carbs = tracking.planned_carbs * multiplier
                    tracking.actual_fat = tracking.planned_fat * multiplier
                    tracking.actual_portion_size = multiplier
                    tracking.satisfaction_rating = random.randint(3, 4)
                
                trackings.append(tracking)
        
        return trackings
    
    @staticmethod
    def _create_portion_adjustment_pattern(user_id: int) -> List[MealTracking]:
        """Create pattern with frequent portion adjustments"""
        trackings = []
        start_date = date.today() - timedelta(days=12)
        
        for day in range(12):
            current_date = start_date + timedelta(days=day)
            
            for meal_type in ['repas1', 'repas2', 'repas3']:
                # High probability of modification
                if random.random() < 0.7:
                    status = MealStatus.MODIFIED
                else:
                    status = MealStatus.CONSUMED
                
                tracking = MealTracking(
                    user_id=user_id,
                    meal_date=current_date,
                    meal_type=meal_type,
                    meal_name=f'Portion-adjusted {meal_type} {day+1}',
                    status=status,
                    planned_calories=400,
                    planned_protein=25,
                    planned_carbs=50,
                    planned_fat=15
                )
                
                if status == MealStatus.MODIFIED:
                    # Various portion adjustments
                    multiplier = random.choice([0.5, 0.75, 1.25, 1.5, 1.75, 2.0])
                    
                    tracking.modifications = {
                        'portion_adjustment': True,
                        'reason': random.choice(['Plus faim', 'Moins faim', 'Ajustement calorique']),
                        'multiplier': multiplier
                    }
                    
                    tracking.actual_calories = tracking.planned_calories * multiplier
                    tracking.actual_protein = tracking.planned_protein * multiplier
                    tracking.actual_carbs = tracking.planned_carbs * multiplier
                    tracking.actual_fat = tracking.planned_fat * multiplier
                    tracking.actual_portion_size = multiplier
                    tracking.satisfaction_rating = random.randint(3, 5)
                
                elif status == MealStatus.CONSUMED:
                    multiplier = random.uniform(0.95, 1.05)
                    tracking.actual_calories = tracking.planned_calories * multiplier
                    tracking.actual_protein = tracking.planned_protein * multiplier
                    tracking.actual_carbs = tracking.planned_carbs * multiplier
                    tracking.actual_fat = tracking.planned_fat * multiplier
                    tracking.actual_portion_size = multiplier
                    tracking.satisfaction_rating = random.randint(4, 5)
                
                trackings.append(tracking)
        
        return trackings


@pytest.fixture
def meal_tracking_factory():
    """Fixture providing the MealTrackingDataFactory"""
    return MealTrackingDataFactory


@pytest.fixture
def realistic_week_data(sample_user, meal_tracking_factory):
    """Fixture providing realistic week of meal data"""
    return meal_tracking_factory.create_week_of_meals(sample_user.id)


@pytest.fixture
def adherence_progression_data(sample_user, meal_tracking_factory):
    """Fixture providing adherence progression data"""
    return meal_tracking_factory.create_adherence_progression_data(sample_user.id, days=21)


@pytest.fixture
def diverse_user_patterns(meal_tracking_factory):
    """Fixture providing diverse user eating patterns"""
    return meal_tracking_factory.create_diverse_user_patterns(3)


@pytest.fixture
def performance_test_data(test_data_factory):
    """Fixture for performance testing with large datasets"""
    users = []
    for i in range(10):
        user = test_data_factory.create_user(f"Perf User {i}", f"perf{i}@test.com")
        users.append(user)
        
        # Create large amount of tracking data
        for day in range(90):  # 3 months of data
            current_date = date.today() - timedelta(days=day)
            for meal_num in range(4):  # 4 meals per day
                test_data_factory.create_meal_tracking(
                    user_id=user.id,
                    meal_date=current_date,
                    meal_type=f"meal_{meal_num}",
                    status=random.choice(list(MealStatus))
                )
    
    return users


@pytest.fixture
def edge_case_data(sample_user, test_data_factory):
    """Fixture providing edge case scenarios"""
    edge_cases = {}
    
    # Meal with zero nutrition
    edge_cases['zero_nutrition'] = test_data_factory.create_meal_tracking(
        sample_user.id,
        planned_calories=0,
        planned_protein=0,
        planned_carbs=0,
        planned_fat=0
    )
    
    # Meal with extreme nutrition values
    edge_cases['extreme_nutrition'] = test_data_factory.create_meal_tracking(
        sample_user.id,
        planned_calories=5000,
        planned_protein=300,
        planned_carbs=800,
        planned_fat=200
    )
    
    # Meal with very small portions
    edge_cases['tiny_portion'] = test_data_factory.create_meal_tracking(
        sample_user.id,
        planned_portion_size=0.1,
        status=MealStatus.CONSUMED
    )
    
    # Meal with very large portions
    edge_cases['huge_portion'] = test_data_factory.create_meal_tracking(
        sample_user.id,
        planned_portion_size=5.0,
        status=MealStatus.CONSUMED
    )
    
    # Meal with extreme timing variance
    today = date.today()
    edge_cases['extreme_timing'] = MealTracking(
        user_id=sample_user.id,
        meal_date=today,
        meal_type="test_timing",
        status=MealStatus.CONSUMED,
        consumption_time_planned=time(8, 0),
        consumption_time_actual=time(14, 30)  # 6.5 hours late
    )
    db.session.add(edge_cases['extreme_timing'])
    
    db.session.commit()
    return edge_cases


@pytest.fixture
def api_mock_responses():
    """Fixture providing mock API responses for different scenarios"""
    return {
        'successful_load': {
            'meal_trackings': [
                {
                    'id': 1,
                    'meal_name': 'Test Meal',
                    'status': 'planned',
                    'planned_nutrition': {'calories': 400, 'protein': 25}
                }
            ],
            'total_trackings': 1
        },
        'empty_response': {
            'meal_trackings': [],
            'total_trackings': 0
        },
        'server_error': {
            'error': 'Internal server error'
        },
        'network_timeout': None,  # Represents network timeout
        'malformed_response': {
            'unexpected_field': 'value'
        },
        'successful_consume': {
            'success': True,
            'meal_tracking': {
                'id': 1,
                'status': 'consumed',
                'satisfaction_rating': 5
            }
        },
        'consume_error': {
            'error': 'Meal tracking not found'
        }
    }


class TestScenarioBuilder:
    """Builder for creating complex test scenarios"""
    
    def __init__(self, user):
        self.user = user
        self.trackings = []
        self.summaries = []
    
    def with_consistent_meals(self, days: int = 7):
        """Add consistent meal pattern"""
        start_date = date.today() - timedelta(days=days)
        for day in range(days):
            current_date = start_date + timedelta(days=day)
            for meal_type in ['repas1', 'repas2', 'repas3']:
                tracking = MealTracking(
                    user_id=self.user.id,
                    meal_date=current_date,
                    meal_type=meal_type,
                    status=MealStatus.CONSUMED,
                    planned_calories=400,
                    planned_protein=25,
                    actual_calories=400,
                    actual_protein=25,
                    satisfaction_rating=4
                )
                self.trackings.append(tracking)
        return self
    
    def with_weekend_deviations(self):
        """Add weekend deviation pattern"""
        start_date = date.today() - timedelta(days=7)
        for day in range(7):
            current_date = start_date + timedelta(days=day)
            if current_date.weekday() >= 5:  # Weekend
                tracking = MealTracking(
                    user_id=self.user.id,
                    meal_date=current_date,
                    meal_type='repas2',
                    status=MealStatus.REPLACED,
                    planned_calories=400,
                    planned_protein=25,
                    replacement_name='Pizza',
                    actual_calories=800,
                    actual_protein=35
                )
                self.trackings.append(tracking)
        return self
    
    def with_improvement_trend(self, days: int = 14):
        """Add improving adherence trend"""
        start_date = date.today() - timedelta(days=days)
        for day in range(days):
            current_date = start_date + timedelta(days=day)
            # Improving adherence over time
            adherence = 60 + (30 * day / days)
            
            summary = DailyNutritionSummary(
                user_id=self.user.id,
                summary_date=current_date,
                plan_adherence_score=adherence,
                target_adherence_score=adherence - 5,
                meals_planned=3,
                meals_consumed=int(3 * (adherence / 100))
            )
            self.summaries.append(summary)
        return self
    
    def build(self):
        """Build and save the scenario"""
        for tracking in self.trackings:
            db.session.add(tracking)
        for summary in self.summaries:
            db.session.add(summary)
        db.session.commit()
        
        return {
            'user': self.user,
            'trackings': self.trackings,
            'summaries': self.summaries
        }


@pytest.fixture
def scenario_builder(sample_user):
    """Fixture providing TestScenarioBuilder"""
    return TestScenarioBuilder(sample_user)