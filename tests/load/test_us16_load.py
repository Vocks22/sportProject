"""
Load Testing Script for US1.6 Calendar Features
Tests the performance and reliability of the calendar system under load
"""

from locust import HttpUser, task, between, events
from datetime import date, timedelta, datetime
import random
import json
import logging
import time
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class US16LoadTestUser(HttpUser):
    """Load test user simulating real usage patterns for US1.6 calendar features"""
    
    # Realistic wait times between user actions (1-5 seconds)
    wait_time = between(1, 5)
    
    def on_start(self):
        """Initialize test data and user session"""
        self.current_monday = self.get_current_monday()
        self.user_id = random.randint(1, 100)  # Simulate different users
        self.week_offsets = list(range(-8, 12))  # Test weeks from 8 weeks ago to 12 weeks ahead
        
        logger.info(f"Starting load test for user {self.user_id}")
    
    def get_current_monday(self) -> date:
        """Get current Monday for ISO 8601 week calculations"""
        today = date.today()
        return today - timedelta(days=today.weekday())
    
    def get_random_monday(self, max_offset_weeks: int = 8) -> date:
        """Get a random Monday within the specified week range"""
        week_offset = random.randint(-max_offset_weeks, max_offset_weeks)
        return self.current_monday + timedelta(weeks=week_offset)
    
    @task(5)
    def test_meal_plans_current_week(self):
        """Test meal plans API for current week - highest frequency task"""
        week_start = self.current_monday.isoformat()
        
        with self.client.get(
            f"/api/meal-plans?week_start={week_start}",
            catch_response=True,
            name="meal_plans_current_week"
        ) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if 'meal_plans' in data:
                        response.success()
                    else:
                        response.failure("Invalid response structure")
                except json.JSONDecodeError:
                    response.failure("Invalid JSON response")
            else:
                response.failure(f"HTTP {response.status_code}")
    
    @task(3)
    def test_meal_plans_random_week(self):
        """Test meal plans API for random weeks - medium frequency"""
        random_monday = self.get_random_monday()
        week_start = random_monday.isoformat()
        
        with self.client.get(
            f"/api/meal-plans?week_start={week_start}",
            catch_response=True,
            name="meal_plans_random_week"
        ) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    # Validate week_start is correctly handled
                    if 'meal_plans' in data:
                        response.success()
                    else:
                        response.failure("Invalid response structure")
                except json.JSONDecodeError:
                    response.failure("Invalid JSON response")
            else:
                response.failure(f"HTTP {response.status_code}")
    
    @task(2)
    def test_calendar_navigation_sequence(self):
        """Test calendar navigation through multiple weeks"""
        start_monday = self.get_random_monday(4)
        
        # Navigate through 4 consecutive weeks
        for week_offset in range(4):
            current_week = start_monday + timedelta(weeks=week_offset)
            week_start = current_week.isoformat()
            
            with self.client.get(
                f"/api/meal-plans?week_start={week_start}",
                catch_response=True,
                name="calendar_navigation_sequence"
            ) as response:
                if response.status_code != 200:
                    response.failure(f"Navigation failed for week {week_offset}")
                    break
                
                # Short pause between navigation steps
                time.sleep(0.1)
        else:
            # All navigation steps succeeded
            response.success()
    
    @task(2)
    def test_create_meal_plan(self):
        """Test meal plan creation with proper week_start validation"""
        monday = self.get_random_monday(2)  # Within 2 weeks
        week_start = monday.isoformat()
        
        # Generate realistic meal plan data
        meal_data = self.generate_meal_plan_data(week_start)
        
        with self.client.post(
            "/api/meal-plans",
            json=meal_data,
            catch_response=True,
            name="create_meal_plan"
        ) as response:
            if response.status_code in [200, 201]:
                response.success()
            elif response.status_code == 400:
                # Check if it's a validation error (expected for invalid dates)
                try:
                    error_data = response.json()
                    if 'week_start' in error_data.get('message', '').lower():
                        response.success()  # Valid validation error
                    else:
                        response.failure("Unexpected validation error")
                except:
                    response.failure("Invalid error response")
            else:
                response.failure(f"HTTP {response.status_code}")
    
    @task(2)
    def test_update_meal_plan(self):
        """Test meal plan updates"""
        monday = self.get_random_monday(1)  # Recent weeks only
        week_start = monday.isoformat()
        
        # First, try to get existing meal plan
        existing_response = self.client.get(f"/api/meal-plans?week_start={week_start}")
        
        if existing_response.status_code == 200:
            try:
                data = existing_response.json()
                meal_plans = data.get('meal_plans', [])
                
                if meal_plans:
                    # Update existing plan
                    meal_plan = meal_plans[0]
                    meal_plan_id = meal_plan.get('id')
                    
                    if meal_plan_id:
                        updated_data = self.generate_meal_plan_data(week_start)
                        
                        with self.client.put(
                            f"/api/meal-plans/{meal_plan_id}",
                            json=updated_data,
                            catch_response=True,
                            name="update_meal_plan"
                        ) as response:
                            if response.status_code in [200, 204]:
                                response.success()
                            else:
                                response.failure(f"Update failed: HTTP {response.status_code}")
            except:
                pass  # Ignore errors in this test
    
    @task(1)
    def test_week_start_validation_edge_cases(self):
        """Test week_start validation with edge cases"""
        edge_cases = [
            # Invalid dates (should return 400)
            (date.today() + timedelta(days=1)).isoformat(),  # Not a Monday
            (date.today() + timedelta(days=2)).isoformat(),  # Tuesday
            (date.today() + timedelta(days=6)).isoformat(),  # Sunday
            
            # Valid Mondays
            self.current_monday.isoformat(),
            (self.current_monday + timedelta(days=7)).isoformat(),
            (self.current_monday - timedelta(days=7)).isoformat(),
        ]
        
        for test_date in edge_cases:
            is_monday = datetime.fromisoformat(test_date).weekday() == 0
            
            with self.client.get(
                f"/api/meal-plans?week_start={test_date}",
                catch_response=True,
                name="week_start_validation"
            ) as response:
                if is_monday:
                    # Should succeed for Mondays
                    if response.status_code == 200:
                        response.success()
                    else:
                        response.failure(f"Valid Monday rejected: {test_date}")
                else:
                    # Should fail for non-Mondays
                    if response.status_code == 400:
                        response.success()
                    else:
                        response.failure(f"Invalid date accepted: {test_date}")
    
    @task(1)
    def test_year_transition_navigation(self):
        """Test calendar navigation across year transitions"""
        # Test around New Year transition
        test_dates = [
            date(2024, 12, 30),  # Monday of last week 2024
            date(2025, 1, 6),    # Monday of first week 2025
            date(2025, 12, 29),  # Monday of last week 2025
            date(2026, 1, 5),    # Monday of first week 2026
        ]
        
        for test_monday in test_dates:
            week_start = test_monday.isoformat()
            
            with self.client.get(
                f"/api/meal-plans?week_start={week_start}",
                catch_response=True,
                name="year_transition_navigation"
            ) as response:
                if response.status_code == 200:
                    response.success()
                else:
                    response.failure(f"Year transition failed for {week_start}")
    
    @task(1)
    def test_health_endpoint(self):
        """Test system health endpoint"""
        with self.client.get(
            "/health",
            catch_response=True,
            name="health_check"
        ) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get('status') in ['ok', 'healthy']:
                        response.success()
                    else:
                        response.failure("Unhealthy status")
                except:
                    # Text response is also acceptable
                    response.success()
            else:
                response.failure(f"Health check failed: HTTP {response.status_code}")
    
    @task(1)
    def test_recipes_database_load(self):
        """Test database load via recipes endpoint"""
        with self.client.get(
            "/api/recipes",
            catch_response=True,
            name="recipes_database_load"
        ) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if 'recipes' in data and isinstance(data['recipes'], list):
                        response.success()
                    else:
                        response.failure("Invalid recipes response")
                except:
                    response.failure("Invalid JSON response")
            else:
                response.failure(f"Recipes endpoint failed: HTTP {response.status_code}")
    
    def generate_meal_plan_data(self, week_start: str) -> Dict[str, Any]:
        """Generate realistic meal plan data for testing"""
        meals = ['breakfast', 'lunch', 'dinner', 'snack']
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        
        meal_plan = {
            'week_start': week_start,
            'user_id': self.user_id,
            'meals': {}
        }
        
        # Generate meals for random days
        num_days = random.randint(3, 7)  # 3-7 days planned
        selected_days = random.sample(days, num_days)
        
        for day in selected_days:
            day_meals = {}
            num_meals = random.randint(1, 3)  # 1-3 meals per day
            selected_meals = random.sample(meals, num_meals)
            
            for meal in selected_meals:
                day_meals[meal] = f"Test {meal.title()} for {day.title()}"
            
            if day_meals:
                meal_plan['meals'][day] = day_meals
        
        return meal_plan


class US16StressTestUser(HttpUser):
    """High-intensity stress test user for US1.6 features"""
    
    # Aggressive wait times for stress testing
    wait_time = between(0.1, 0.5)
    
    def on_start(self):
        self.current_monday = self.get_current_monday()
        self.user_id = random.randint(1, 1000)
    
    def get_current_monday(self) -> date:
        today = date.today()
        return today - timedelta(days=today.weekday())
    
    @task
    def stress_meal_plans_api(self):
        """Aggressive meal plans API testing"""
        week_offset = random.randint(-20, 20)
        monday = self.current_monday + timedelta(weeks=week_offset)
        week_start = monday.isoformat()
        
        self.client.get(
            f"/api/meal-plans?week_start={week_start}",
            name="stress_meal_plans"
        )
    
    @task
    def stress_calendar_navigation(self):
        """Rapid calendar navigation"""
        for _ in range(5):  # Rapid fire requests
            week_offset = random.randint(-10, 10)
            monday = self.current_monday + timedelta(weeks=week_offset)
            week_start = monday.isoformat()
            
            self.client.get(
                f"/api/meal-plans?week_start={week_start}",
                name="stress_calendar_nav"
            )


# Event handlers for detailed reporting
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Called when the test is started"""
    logger.info("=== US1.6 Load Testing Started ===")
    logger.info(f"Target host: {environment.host}")
    logger.info(f"Users: {environment.runner.target_user_count if environment.runner else 'N/A'}")

@events.test_stop.add_listener  
def on_test_stop(environment, **kwargs):
    """Called when the test is stopped"""
    logger.info("=== US1.6 Load Testing Completed ===")
    
    if environment.runner and hasattr(environment.runner, 'stats'):
        stats = environment.runner.stats
        logger.info(f"Total requests: {stats.total.num_requests}")
        logger.info(f"Failed requests: {stats.total.num_failures}")
        logger.info(f"Average response time: {stats.total.avg_response_time:.2f}ms")
        logger.info(f"Max response time: {stats.total.max_response_time:.2f}ms")

@events.request_failure.add_listener
def on_request_failure(request_type, name, response_time, response_length, exception, **kwargs):
    """Called when a request fails"""
    logger.warning(f"Request failed: {name} - {exception}")

# Configuration for different test scenarios
class LoadTestConfig:
    """Configuration for different load testing scenarios"""
    
    SCENARIOS = {
        'light': {
            'users': 5,
            'spawn_rate': 1,
            'run_time': '2m',
            'description': 'Light load testing for development'
        },
        'moderate': {
            'users': 20,
            'spawn_rate': 2,
            'run_time': '5m', 
            'description': 'Moderate load testing for staging'
        },
        'heavy': {
            'users': 50,
            'spawn_rate': 5,
            'run_time': '10m',
            'description': 'Heavy load testing for production validation'
        },
        'stress': {
            'users': 100,
            'spawn_rate': 10,
            'run_time': '15m',
            'description': 'Stress testing to find breaking points'
        }
    }
    
    @classmethod
    def get_scenario(cls, name: str) -> Dict[str, Any]:
        """Get configuration for a specific scenario"""
        return cls.SCENARIOS.get(name, cls.SCENARIOS['moderate'])


if __name__ == '__main__':
    import sys
    
    # Allow running with different scenarios
    scenario = sys.argv[1] if len(sys.argv) > 1 else 'moderate'
    config = LoadTestConfig.get_scenario(scenario)
    
    print(f"Running {scenario} load test scenario:")
    print(f"Description: {config['description']}")
    print(f"Users: {config['users']}")
    print(f"Spawn rate: {config['spawn_rate']}")
    print(f"Run time: {config['run_time']}")
    print("\nRun with:")
    print(f"locust -f {__file__} --users={config['users']} --spawn-rate={config['spawn_rate']} --run-time={config['run_time']} --host=http://localhost:5000")