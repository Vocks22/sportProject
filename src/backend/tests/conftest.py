"""
Test configuration and fixtures for US1.8 Meal Tracking tests
"""

import pytest
import tempfile
import os
from datetime import date, datetime, time, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import our app components
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import db
from models.user import User
from models.recipe import Recipe, Ingredient, RecipeIngredient
from models.meal_plan import MealPlan
from models.meal_tracking import MealTracking, DailyNutritionSummary, MealStatus
from main import create_app


@pytest.fixture(scope='session')
def app():
    """Create test Flask app"""
    # Create temporary database file
    db_fd, db_path = tempfile.mkstemp()
    
    # Create test app with SQLite in-memory database
    test_app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'SECRET_KEY': 'test-secret-key'
    })
    
    with test_app.app_context():
        # Create all tables
        db.create_all()
        yield test_app
        
        # Cleanup
        db.drop_all()
        os.close(db_fd)
        os.unlink(db_path)


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture
def app_context(app):
    """Create app context for tests"""
    with app.app_context():
        yield app


@pytest.fixture(autouse=True)
def clean_db(app_context):
    """Clean database before each test"""
    # Clean all tables in reverse order of dependencies
    db.session.query(DailyNutritionSummary).delete()
    db.session.query(MealTracking).delete()
    db.session.query(RecipeIngredient).delete()
    db.session.query(Recipe).delete()
    db.session.query(Ingredient).delete()
    db.session.query(MealPlan).delete()
    db.session.query(User).delete()
    db.session.commit()
    yield
    # Clean again after test
    db.session.rollback()


@pytest.fixture
def sample_user():
    """Create a sample user for testing"""
    user = User(
        name="Test User",
        email="test@example.com",
        age=30,
        sex="M",
        height=175,
        weight=75.0,
        activity_level="moderate",
        goal="maintenance"
    )
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def sample_ingredient():
    """Create a sample ingredient for testing"""
    ingredient = Ingredient(
        name="Chicken Breast",
        category="protein",
        calories_per_100g=165.0,
        protein_per_100g=31.0,
        carbs_per_100g=0.0,
        fat_per_100g=3.6,
        fiber_per_100g=0.0,
        sodium_per_100g=74.0,
        sugar_per_100g=0.0
    )
    db.session.add(ingredient)
    db.session.commit()
    return ingredient


@pytest.fixture
def sample_recipe(sample_ingredient):
    """Create a sample recipe for testing"""
    recipe = Recipe(
        name="Grilled Chicken",
        description="Simple grilled chicken breast",
        instructions=["Grill chicken until cooked"],
        prep_time=5,
        cook_time=15,
        difficulty="easy",
        category="main",
        servings=2,
        created_by_user=True
    )
    db.session.add(recipe)
    db.session.flush()  # Get ID without committing
    
    # Add ingredient to recipe
    recipe_ingredient = RecipeIngredient(
        recipe_id=recipe.id,
        ingredient_id=sample_ingredient.id,
        quantity=200.0,
        unit="g"
    )
    db.session.add(recipe_ingredient)
    db.session.commit()
    return recipe


@pytest.fixture
def sample_meal_plan(sample_user):
    """Create a sample meal plan for testing"""
    today = date.today()
    week_start = today - timedelta(days=today.weekday())  # Monday
    
    meals_data = {
        today.isoformat(): {
            "repas1": {
                "recipe_id": None,
                "name": "Breakfast",
                "time": "08:00",
                "nutrition": {
                    "calories": 400,
                    "protein": 20,
                    "carbs": 50,
                    "fat": 15,
                    "fiber": 5,
                    "sodium": 200,
                    "sugar": 10
                }
            },
            "repas2": {
                "recipe_id": None,
                "name": "Lunch",
                "time": "12:00",
                "nutrition": {
                    "calories": 600,
                    "protein": 35,
                    "carbs": 60,
                    "fat": 20,
                    "fiber": 8,
                    "sodium": 400,
                    "sugar": 5
                }
            }
        }
    }
    
    meal_plan = MealPlan(
        user_id=sample_user.id,
        name="Test Meal Plan",
        week_start=week_start,
        meals=meals_data,
        is_active=True,
        total_days=7
    )
    db.session.add(meal_plan)
    db.session.commit()
    return meal_plan


@pytest.fixture
def sample_meal_tracking(sample_user, sample_meal_plan, sample_recipe):
    """Create a sample meal tracking entry"""
    today = date.today()
    
    tracking = MealTracking(
        user_id=sample_user.id,
        meal_plan_id=sample_meal_plan.id,
        recipe_id=sample_recipe.id,
        meal_date=today,
        meal_type="repas1",
        meal_name="Test Meal",
        status=MealStatus.PLANNED,
        planned_calories=400.0,
        planned_protein=25.0,
        planned_carbs=45.0,
        planned_fat=15.0,
        planned_fiber=5.0,
        planned_sodium=200.0,
        planned_sugar=10.0,
        planned_portion_size=1.0,
        consumption_time_planned=time(8, 0)
    )
    db.session.add(tracking)
    db.session.commit()
    return tracking


@pytest.fixture
def sample_daily_summary(sample_user):
    """Create a sample daily nutrition summary"""
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    
    summary = DailyNutritionSummary(
        user_id=sample_user.id,
        summary_date=today,
        planned_calories=1800.0,
        planned_protein=120.0,
        planned_carbs=225.0,
        planned_fat=60.0,
        planned_fiber=25.0,
        planned_sodium=2000.0,
        planned_sugar=50.0,
        actual_calories=1750.0,
        actual_protein=115.0,
        actual_carbs=220.0,
        actual_fat=58.0,
        actual_fiber=23.0,
        actual_sodium=1900.0,
        actual_sugar=45.0,
        target_calories=1800.0,
        target_protein=120.0,
        target_carbs=225.0,
        target_fat=60.0,
        target_fiber=25.0,
        target_sodium=2000.0,
        target_sugar=50.0,
        meals_planned=3,
        meals_consumed=2,
        meals_skipped=1,
        week_start=week_start,
        month_year=today.strftime('%Y-%m')
    )
    db.session.add(summary)
    db.session.commit()
    return summary


class TestDataFactory:
    """Factory for creating test data"""
    
    @staticmethod
    def create_user(name="Test User", email=None, **kwargs):
        """Create a test user with optional parameters"""
        if email is None:
            email = f"{name.lower().replace(' ', '.')}@test.com"
        
        defaults = {
            'age': 30,
            'sex': 'M',
            'height': 175,
            'weight': 75.0,
            'activity_level': 'moderate',
            'goal': 'maintenance'
        }
        defaults.update(kwargs)
        
        user = User(name=name, email=email, **defaults)
        db.session.add(user)
        db.session.commit()
        return user
    
    @staticmethod
    def create_meal_tracking(user_id, meal_date=None, meal_type="repas1", 
                           status=MealStatus.PLANNED, **kwargs):
        """Create a test meal tracking entry"""
        if meal_date is None:
            meal_date = date.today()
        
        defaults = {
            'meal_name': f'Test {meal_type}',
            'planned_calories': 400.0,
            'planned_protein': 25.0,
            'planned_carbs': 45.0,
            'planned_fat': 15.0,
            'planned_fiber': 5.0,
            'planned_sodium': 200.0,
            'planned_sugar': 10.0,
            'planned_portion_size': 1.0
        }
        defaults.update(kwargs)
        
        tracking = MealTracking(
            user_id=user_id,
            meal_date=meal_date,
            meal_type=meal_type,
            status=status,
            **defaults
        )
        db.session.add(tracking)
        db.session.commit()
        return tracking
    
    @staticmethod
    def create_multiple_trackings(user_id, num_days=7, meals_per_day=3):
        """Create multiple meal tracking entries for testing"""
        trackings = []
        start_date = date.today() - timedelta(days=num_days)
        meal_types = ['repas1', 'repas2', 'repas3']
        
        for day in range(num_days):
            current_date = start_date + timedelta(days=day)
            
            for i in range(meals_per_day):
                meal_type = meal_types[i % len(meal_types)]
                
                tracking = TestDataFactory.create_meal_tracking(
                    user_id=user_id,
                    meal_date=current_date,
                    meal_type=meal_type,
                    status=MealStatus.CONSUMED if i < 2 else MealStatus.PLANNED,
                    planned_calories=300 + (i * 100),
                    planned_protein=15 + (i * 10),
                    planned_carbs=30 + (i * 15),
                    planned_fat=10 + (i * 5)
                )
                trackings.append(tracking)
        
        return trackings


@pytest.fixture
def test_data_factory():
    """Provide TestDataFactory for tests"""
    return TestDataFactory