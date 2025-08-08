from database import db
from datetime import datetime, date, time
from sqlalchemy.orm import relationship
from typing import Dict, Any, Optional, List
import json
import enum

class MealStatus(enum.Enum):
    """Enum for meal tracking status"""
    PLANNED = 'planned'
    CONSUMED = 'consumed'
    MODIFIED = 'modified'
    SKIPPED = 'skipped'
    REPLACED = 'replaced'

class MealTracking(db.Model):
    """
    Model for tracking meal consumption and modifications
    Links users with their meal plans and actual consumption data
    """
    __tablename__ = 'meal_tracking'
    
    # Primary identification
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    meal_plan_id = db.Column(db.Integer, db.ForeignKey('meal_plans.id', ondelete='CASCADE'), nullable=True, index=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id', ondelete='SET NULL'), nullable=True, index=True)
    
    # Meal identification
    meal_date = db.Column(db.Date, nullable=False, index=True)
    meal_type = db.Column(db.String(20), nullable=False)  # repas1, repas2, repas3, collation
    meal_name = db.Column(db.String(200), nullable=True)
    
    # Status tracking
    status = db.Column(db.Enum(MealStatus), default=MealStatus.PLANNED, nullable=False, index=True)
    
    # Planned vs Actual nutritional values
    # Planned values (from meal plan/recipe)
    planned_calories = db.Column(db.Float, default=0, nullable=False)
    planned_protein = db.Column(db.Float, default=0, nullable=False)
    planned_carbs = db.Column(db.Float, default=0, nullable=False)
    planned_fat = db.Column(db.Float, default=0, nullable=False)
    planned_fiber = db.Column(db.Float, default=0, nullable=False)
    planned_sodium = db.Column(db.Float, default=0, nullable=False)
    planned_sugar = db.Column(db.Float, default=0, nullable=False)
    
    # Actual consumed values (user-reported or modified)
    actual_calories = db.Column(db.Float, nullable=True)
    actual_protein = db.Column(db.Float, nullable=True)
    actual_carbs = db.Column(db.Float, nullable=True)
    actual_fat = db.Column(db.Float, nullable=True)
    actual_fiber = db.Column(db.Float, nullable=True)
    actual_sodium = db.Column(db.Float, nullable=True)
    actual_sugar = db.Column(db.Float, nullable=True)
    
    # Portion adjustments
    planned_portion_size = db.Column(db.Float, default=1.0, nullable=False)  # Multiplier (1.0 = 100%)
    actual_portion_size = db.Column(db.Float, nullable=True)  # Actual portion consumed
    
    # Consumption tracking
    consumption_datetime = db.Column(db.DateTime, nullable=True)  # When meal was actually consumed
    consumption_time_planned = db.Column(db.Time, nullable=True)  # Planned consumption time
    consumption_time_actual = db.Column(db.Time, nullable=True)   # Actual consumption time
    
    # User feedback and notes
    user_notes = db.Column(db.Text, nullable=True)
    satisfaction_rating = db.Column(db.Integer, nullable=True)  # 1-5 scale
    difficulty_rating = db.Column(db.Integer, nullable=True)    # 1-5 scale
    
    # Photo tracking
    photo_urls = db.Column(db.Text, nullable=True)  # JSON array of photo URLs
    
    # Modification tracking
    modifications_json = db.Column(db.Text, nullable=True)  # JSON of ingredient modifications
    substitutions_json = db.Column(db.Text, nullable=True)  # JSON of ingredient substitutions
    
    # Replacement meal tracking (if status = REPLACED)
    replacement_recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id', ondelete='SET NULL'), nullable=True)
    replacement_name = db.Column(db.String(200), nullable=True)
    replacement_reason = db.Column(db.String(200), nullable=True)
    
    # Skip tracking (if status = SKIPPED)
    skip_reason = db.Column(db.String(200), nullable=True)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Sync and versioning for mobile apps
    last_sync_at = db.Column(db.DateTime, nullable=True)
    version = db.Column(db.Integer, default=1, nullable=False)
    
    # Relations (backrefs defined in parent models to avoid duplicates)
    # user relationship is defined in User model with backref='user'
    # meal_plan relationship is defined in MealPlan model with backref='meal_plan'  
    # recipe relationships are defined in Recipe model with backrefs
    
    # Unique constraint to prevent duplicate tracking
    __table_args__ = (
        db.UniqueConstraint('user_id', 'meal_date', 'meal_type', name='uq_meal_tracking_user_date_type'),
        db.CheckConstraint('satisfaction_rating IS NULL OR (satisfaction_rating >= 1 AND satisfaction_rating <= 5)', name='check_satisfaction_rating'),
        db.CheckConstraint('difficulty_rating IS NULL OR (difficulty_rating >= 1 AND difficulty_rating <= 5)', name='check_difficulty_rating'),
        db.CheckConstraint('planned_portion_size > 0', name='check_planned_portion_positive'),
        db.CheckConstraint('actual_portion_size IS NULL OR actual_portion_size > 0', name='check_actual_portion_positive'),
        db.Index('idx_meal_tracking_user_date', 'user_id', 'meal_date'),
        db.Index('idx_meal_tracking_status_date', 'status', 'meal_date'),
        db.Index('idx_meal_tracking_consumption_time', 'consumption_datetime'),
    )
    
    def __repr__(self):
        return f'<MealTracking {self.user_id}: {self.meal_type} on {self.meal_date} ({self.status.value})>'
    
    # Property methods for JSON fields
    @property
    def photo_urls_list(self) -> List[str]:
        """Returns list of photo URLs from JSON storage"""
        if self.photo_urls:
            try:
                return json.loads(self.photo_urls)
            except (json.JSONDecodeError, TypeError):
                return []
        return []
    
    @photo_urls_list.setter
    def photo_urls_list(self, value: List[str]):
        """Sets photo URLs as JSON"""
        if isinstance(value, list):
            self.photo_urls = json.dumps(value)
        else:
            self.photo_urls = None
    
    @property
    def modifications(self) -> Dict[str, Any]:
        """Returns modifications from JSON storage"""
        if self.modifications_json:
            try:
                return json.loads(self.modifications_json)
            except (json.JSONDecodeError, TypeError):
                return {}
        return {}
    
    @modifications.setter
    def modifications(self, value: Dict[str, Any]):
        """Sets modifications as JSON"""
        if isinstance(value, dict):
            self.modifications_json = json.dumps(value)
        else:
            self.modifications_json = None
    
    @property
    def substitutions(self) -> Dict[str, Any]:
        """Returns substitutions from JSON storage"""
        if self.substitutions_json:
            try:
                return json.loads(self.substitutions_json)
            except (json.JSONDecodeError, TypeError):
                return {}
        return {}
    
    @substitutions.setter
    def substitutions(self, value: Dict[str, Any]):
        """Sets substitutions as JSON"""
        if isinstance(value, dict):
            self.substitutions_json = json.dumps(value)
        else:
            self.substitutions_json = None
    
    # Calculated properties
    @property
    def calories_variance(self) -> Optional[float]:
        """Calculate variance between planned and actual calories"""
        if self.actual_calories is not None:
            return self.actual_calories - self.planned_calories
        return None
    
    @property
    def protein_variance(self) -> Optional[float]:
        """Calculate variance between planned and actual protein"""
        if self.actual_protein is not None:
            return self.actual_protein - self.planned_protein
        return None
    
    @property
    def carbs_variance(self) -> Optional[float]:
        """Calculate variance between planned and actual carbs"""
        if self.actual_carbs is not None:
            return self.actual_carbs - self.planned_carbs
        return None
    
    @property
    def fat_variance(self) -> Optional[float]:
        """Calculate variance between planned and actual fat"""
        if self.actual_fat is not None:
            return self.actual_fat - self.planned_fat
        return None
    
    @property
    def is_consumed(self) -> bool:
        """Check if meal was actually consumed"""
        return self.status in [MealStatus.CONSUMED, MealStatus.MODIFIED, MealStatus.REPLACED]
    
    @property
    def effective_calories(self) -> float:
        """Get effective calories (actual if consumed, planned otherwise)"""
        if self.is_consumed and self.actual_calories is not None:
            return self.actual_calories
        return self.planned_calories
    
    @property
    def effective_protein(self) -> float:
        """Get effective protein (actual if consumed, planned otherwise)"""
        if self.is_consumed and self.actual_protein is not None:
            return self.actual_protein
        return self.planned_protein
    
    @property
    def effective_carbs(self) -> float:
        """Get effective carbs (actual if consumed, planned otherwise)"""
        if self.is_consumed and self.actual_carbs is not None:
            return self.actual_carbs
        return self.planned_carbs
    
    @property
    def effective_fat(self) -> float:
        """Get effective fat (actual if consumed, planned otherwise)"""
        if self.is_consumed and self.actual_fat is not None:
            return self.actual_fat
        return self.planned_fat
    
    @property
    def effective_fiber(self) -> float:
        """Get effective fiber (actual if consumed, planned otherwise)"""
        if self.is_consumed and self.actual_fiber is not None:
            return self.actual_fiber
        return self.planned_fiber
    
    @property
    def effective_sodium(self) -> float:
        """Get effective sodium (actual if consumed, planned otherwise)"""
        if self.is_consumed and self.actual_sodium is not None:
            return self.actual_sodium
        return self.planned_sodium
    
    @property
    def effective_sugar(self) -> float:
        """Get effective sugar (actual if consumed, planned otherwise)"""
        if self.is_consumed and self.actual_sugar is not None:
            return self.actual_sugar
        return self.planned_sugar
    
    @property
    def timing_variance_minutes(self) -> Optional[int]:
        """Calculate timing variance in minutes"""
        if self.consumption_time_planned and self.consumption_time_actual:
            planned_minutes = self.consumption_time_planned.hour * 60 + self.consumption_time_planned.minute
            actual_minutes = self.consumption_time_actual.hour * 60 + self.consumption_time_actual.minute
            return actual_minutes - planned_minutes
        return None
    
    def mark_as_consumed(self, consumption_time: Optional[datetime] = None, 
                        actual_nutrition: Optional[Dict[str, float]] = None,
                        portion_size: Optional[float] = None,
                        notes: Optional[str] = None,
                        rating: Optional[int] = None) -> None:
        """Mark meal as consumed with optional actual data"""
        self.status = MealStatus.CONSUMED
        self.consumption_datetime = consumption_time or datetime.utcnow()
        self.consumption_time_actual = (consumption_time or datetime.utcnow()).time()
        
        if actual_nutrition:
            self.actual_calories = actual_nutrition.get('calories')
            self.actual_protein = actual_nutrition.get('protein')
            self.actual_carbs = actual_nutrition.get('carbs')
            self.actual_fat = actual_nutrition.get('fat')
            self.actual_fiber = actual_nutrition.get('fiber')
            self.actual_sodium = actual_nutrition.get('sodium')
            self.actual_sugar = actual_nutrition.get('sugar')
        
        if portion_size:
            self.actual_portion_size = portion_size
            
        if notes:
            self.user_notes = notes
            
        if rating:
            self.satisfaction_rating = rating
    
    def mark_as_skipped(self, reason: Optional[str] = None) -> None:
        """Mark meal as skipped with optional reason"""
        self.status = MealStatus.SKIPPED
        self.skip_reason = reason
    
    def mark_as_replaced(self, replacement_recipe_id: Optional[int] = None,
                        replacement_name: Optional[str] = None,
                        reason: Optional[str] = None,
                        actual_nutrition: Optional[Dict[str, float]] = None) -> None:
        """Mark meal as replaced with new recipe/meal"""
        self.status = MealStatus.REPLACED
        self.replacement_recipe_id = replacement_recipe_id
        self.replacement_name = replacement_name
        self.replacement_reason = reason
        
        if actual_nutrition:
            self.actual_calories = actual_nutrition.get('calories')
            self.actual_protein = actual_nutrition.get('protein')
            self.actual_carbs = actual_nutrition.get('carbs')
            self.actual_fat = actual_nutrition.get('fat')
            self.actual_fiber = actual_nutrition.get('fiber')
            self.actual_sodium = actual_nutrition.get('sodium')
            self.actual_sugar = actual_nutrition.get('sugar')
    
    def to_dict(self, include_sensitive: bool = False) -> Dict[str, Any]:
        """Convert to dictionary with optional sensitive data"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'meal_plan_id': self.meal_plan_id,
            'recipe_id': self.recipe_id,
            'meal_date': self.meal_date.isoformat(),
            'meal_type': self.meal_type,
            'meal_name': self.meal_name,
            'status': self.status.value,
            
            # Planned nutrition
            'planned_nutrition': {
                'calories': self.planned_calories,
                'protein': self.planned_protein,
                'carbs': self.planned_carbs,
                'fat': self.planned_fat,
                'fiber': self.planned_fiber,
                'sodium': self.planned_sodium,
                'sugar': self.planned_sugar
            },
            
            # Actual nutrition (if available)
            'actual_nutrition': {
                'calories': self.actual_calories,
                'protein': self.actual_protein,
                'carbs': self.actual_carbs,
                'fat': self.actual_fat,
                'fiber': self.actual_fiber,
                'sodium': self.actual_sodium,
                'sugar': self.actual_sugar
            } if any([self.actual_calories, self.actual_protein, self.actual_carbs, self.actual_fat]) else None,
            
            # Effective nutrition (for calculations)
            'effective_nutrition': {
                'calories': self.effective_calories,
                'protein': self.effective_protein,
                'carbs': self.effective_carbs,
                'fat': self.effective_fat,
                'fiber': self.effective_fiber,
                'sodium': self.effective_sodium,
                'sugar': self.effective_sugar
            },
            
            # Variance calculations
            'nutrition_variance': {
                'calories': self.calories_variance,
                'protein': self.protein_variance,
                'carbs': self.carbs_variance,
                'fat': self.fat_variance
            } if any([self.calories_variance, self.protein_variance, self.carbs_variance, self.fat_variance]) else None,
            
            # Portion sizes
            'planned_portion_size': self.planned_portion_size,
            'actual_portion_size': self.actual_portion_size,
            
            # Timing
            'consumption_datetime': self.consumption_datetime.isoformat() if self.consumption_datetime else None,
            'consumption_time_planned': self.consumption_time_planned.isoformat() if self.consumption_time_planned else None,
            'consumption_time_actual': self.consumption_time_actual.isoformat() if self.consumption_time_actual else None,
            'timing_variance_minutes': self.timing_variance_minutes,
            
            # User feedback
            'user_notes': self.user_notes,
            'satisfaction_rating': self.satisfaction_rating,
            'difficulty_rating': self.difficulty_rating,
            
            # Media
            'photo_urls': self.photo_urls_list,
            
            # Modifications
            'modifications': self.modifications,
            'substitutions': self.substitutions,
            
            # Replacement data
            'replacement_recipe_id': self.replacement_recipe_id,
            'replacement_name': self.replacement_name,
            'replacement_reason': self.replacement_reason,
            
            # Skip data
            'skip_reason': self.skip_reason,
            
            # Metadata
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'last_sync_at': self.last_sync_at.isoformat() if self.last_sync_at else None,
            'version': self.version,
            
            # Calculated fields
            'is_consumed': self.is_consumed
        }
    
    @staticmethod
    def create_from_meal_plan(user_id: int, meal_plan_id: int, meal_date: date,
                             meal_type: str, recipe_id: Optional[int] = None) -> 'MealTracking':
        """Create meal tracking entry from meal plan"""
        tracking = MealTracking(
            user_id=user_id,
            meal_plan_id=meal_plan_id,
            recipe_id=recipe_id,
            meal_date=meal_date,
            meal_type=meal_type,
            status=MealStatus.PLANNED
        )
        
        # If recipe_id provided, populate planned nutrition from recipe
        if recipe_id:
            from models.recipe import Recipe
            recipe = Recipe.query.get(recipe_id)
            if recipe:
                tracking.meal_name = recipe.name
                tracking.planned_calories = recipe.total_calories
                tracking.planned_protein = recipe.total_protein
                tracking.planned_carbs = recipe.total_carbs
                tracking.planned_fat = recipe.total_fat
        
        return tracking


class DailyNutritionSummary(db.Model):
    """
    Model for daily aggregated nutritional data and adherence tracking
    Provides daily summaries of planned vs actual nutrition intake
    """
    __tablename__ = 'daily_nutrition_summary'
    
    # Primary identification
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    summary_date = db.Column(db.Date, nullable=False, index=True)
    
    # Planned nutritional totals (sum from meal plans)
    planned_calories = db.Column(db.Float, default=0, nullable=False)
    planned_protein = db.Column(db.Float, default=0, nullable=False)
    planned_carbs = db.Column(db.Float, default=0, nullable=False)
    planned_fat = db.Column(db.Float, default=0, nullable=False)
    planned_fiber = db.Column(db.Float, default=0, nullable=False)
    planned_sodium = db.Column(db.Float, default=0, nullable=False)
    planned_sugar = db.Column(db.Float, default=0, nullable=False)
    
    # Actual consumed totals (sum from meal tracking)
    actual_calories = db.Column(db.Float, default=0, nullable=False)
    actual_protein = db.Column(db.Float, default=0, nullable=False)
    actual_carbs = db.Column(db.Float, default=0, nullable=False)
    actual_fat = db.Column(db.Float, default=0, nullable=False)
    actual_fiber = db.Column(db.Float, default=0, nullable=False)
    actual_sodium = db.Column(db.Float, default=0, nullable=False)
    actual_sugar = db.Column(db.Float, default=0, nullable=False)
    
    # User targets (from user profile)
    target_calories = db.Column(db.Float, nullable=True)
    target_protein = db.Column(db.Float, nullable=True)
    target_carbs = db.Column(db.Float, nullable=True)
    target_fat = db.Column(db.Float, nullable=True)
    target_fiber = db.Column(db.Float, nullable=True)
    target_sodium = db.Column(db.Float, nullable=True)
    target_sugar = db.Column(db.Float, nullable=True)
    
    # Adherence scores (0-100%)
    plan_adherence_score = db.Column(db.Float, default=0, nullable=False)  # How well actual matches planned
    target_adherence_score = db.Column(db.Float, default=0, nullable=False)  # How well actual matches targets
    
    # Meal completion statistics
    meals_planned = db.Column(db.Integer, default=0, nullable=False)
    meals_consumed = db.Column(db.Integer, default=0, nullable=False)
    meals_skipped = db.Column(db.Integer, default=0, nullable=False)
    meals_replaced = db.Column(db.Integer, default=0, nullable=False)
    meals_modified = db.Column(db.Integer, default=0, nullable=False)
    
    # Deficit/surplus calculations (vs targets)
    calorie_deficit_surplus = db.Column(db.Float, default=0, nullable=False)  # negative = deficit, positive = surplus
    protein_deficit_surplus = db.Column(db.Float, default=0, nullable=False)
    carbs_deficit_surplus = db.Column(db.Float, default=0, nullable=False)
    fat_deficit_surplus = db.Column(db.Float, default=0, nullable=False)
    fiber_deficit_surplus = db.Column(db.Float, default=0, nullable=False)
    sodium_deficit_surplus = db.Column(db.Float, default=0, nullable=False)
    sugar_deficit_surplus = db.Column(db.Float, default=0, nullable=False)
    
    # Timing adherence
    avg_meal_timing_variance_minutes = db.Column(db.Float, nullable=True)  # Average timing variance
    on_time_meals = db.Column(db.Integer, default=0, nullable=False)  # Meals within ±15 min of planned time
    
    # Quality metrics
    avg_satisfaction_rating = db.Column(db.Float, nullable=True)  # Average of all meal satisfaction ratings
    avg_difficulty_rating = db.Column(db.Float, nullable=True)    # Average of all meal difficulty ratings
    
    # Achievement flags
    hit_calorie_target = db.Column(db.Boolean, default=False, nullable=False)
    hit_protein_target = db.Column(db.Boolean, default=False, nullable=False)
    hit_carbs_target = db.Column(db.Boolean, default=False, nullable=False)
    hit_fat_target = db.Column(db.Boolean, default=False, nullable=False)
    hit_fiber_target = db.Column(db.Boolean, default=False, nullable=False)
    stayed_under_sodium_limit = db.Column(db.Boolean, default=False, nullable=False)
    stayed_under_sugar_limit = db.Column(db.Boolean, default=False, nullable=False)
    
    # Weekly/monthly context
    week_start = db.Column(db.Date, nullable=True, index=True)  # ISO week start (Monday)
    month_year = db.Column(db.String(7), nullable=True, index=True)  # YYYY-MM format
    
    # Data freshness and versioning
    last_calculated = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    calculation_version = db.Column(db.Integer, default=1, nullable=False)
    needs_recalculation = db.Column(db.Boolean, default=False, nullable=False)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relations (backref defined in User model to avoid duplicate)
    # user relationship is defined in User model
    
    # Unique constraint for one summary per user per day
    __table_args__ = (
        db.UniqueConstraint('user_id', 'summary_date', name='uq_daily_nutrition_user_date'),
        db.CheckConstraint('plan_adherence_score >= 0 AND plan_adherence_score <= 100', name='check_plan_adherence_range'),
        db.CheckConstraint('target_adherence_score >= 0 AND target_adherence_score <= 100', name='check_target_adherence_range'),
        db.CheckConstraint('meals_consumed <= meals_planned', name='check_consumed_le_planned'),
        db.CheckConstraint('avg_satisfaction_rating IS NULL OR (avg_satisfaction_rating >= 1 AND avg_satisfaction_rating <= 5)', name='check_avg_satisfaction_range'),
        db.CheckConstraint('avg_difficulty_rating IS NULL OR (avg_difficulty_rating >= 1 AND avg_difficulty_rating <= 5)', name='check_avg_difficulty_range'),
        db.Index('idx_nutrition_summary_user_date', 'user_id', 'summary_date'),
        db.Index('idx_nutrition_summary_week', 'user_id', 'week_start'),
        db.Index('idx_nutrition_summary_month', 'user_id', 'month_year'),
        db.Index('idx_nutrition_summary_calculation', 'needs_recalculation', 'last_calculated'),
    )
    
    def __repr__(self):
        return f'<DailyNutritionSummary {self.user_id}: {self.summary_date} ({self.plan_adherence_score:.1f}% adherence)>'
    
    # Calculated properties
    @property
    def completion_rate(self) -> float:
        """Calculate meal completion rate (0-100%)"""
        if self.meals_planned == 0:
            return 0.0
        return (self.meals_consumed / self.meals_planned) * 100
    
    @property
    def skip_rate(self) -> float:
        """Calculate meal skip rate (0-100%)"""
        if self.meals_planned == 0:
            return 0.0
        return (self.meals_skipped / self.meals_planned) * 100
    
    @property
    def modification_rate(self) -> float:
        """Calculate meal modification rate (0-100%)"""
        if self.meals_planned == 0:
            return 0.0
        return ((self.meals_modified + self.meals_replaced) / self.meals_planned) * 100
    
    @property
    def timing_adherence_rate(self) -> float:
        """Calculate timing adherence rate (0-100%)"""
        if self.meals_consumed == 0:
            return 0.0
        return (self.on_time_meals / self.meals_consumed) * 100
    
    @property
    def calorie_adherence_to_target(self) -> float:
        """Calculate calorie adherence to target (0-100%)"""
        if not self.target_calories or self.target_calories == 0:
            return 0.0
        
        # Perfect score if within 5% of target
        variance = abs(self.actual_calories - self.target_calories) / self.target_calories
        if variance <= 0.05:  # Within 5%
            return 100.0
        elif variance <= 0.10:  # Within 10%
            return 95.0 - (variance - 0.05) * 1000  # Linear decrease
        elif variance <= 0.20:  # Within 20%
            return 85.0 - (variance - 0.10) * 500   # Slower decrease
        else:
            return max(0.0, 75.0 - (variance - 0.20) * 200)  # Even slower decrease
    
    @property
    def protein_adherence_to_target(self) -> float:
        """Calculate protein adherence to target (0-100%)"""
        if not self.target_protein or self.target_protein == 0:
            return 0.0
        
        # Protein is often "more is better" up to 2x target
        if self.actual_protein >= self.target_protein:
            if self.actual_protein <= self.target_protein * 2:
                return 100.0  # Perfect if between target and 2x target
            else:
                excess = (self.actual_protein - self.target_protein * 2) / self.target_protein
                return max(80.0, 100.0 - excess * 50)  # Gentle penalty for excess
        else:
            deficit = (self.target_protein - self.actual_protein) / self.target_protein
            return max(0.0, 100.0 - deficit * 150)  # Steeper penalty for deficit
    
    @property
    def overall_nutrition_score(self) -> float:
        """Calculate overall nutrition score (weighted average)"""
        scores = []
        weights = []
        
        # Calorie adherence (30% weight)
        scores.append(self.calorie_adherence_to_target)
        weights.append(0.30)
        
        # Protein adherence (25% weight)
        scores.append(self.protein_adherence_to_target)
        weights.append(0.25)
        
        # Plan adherence (20% weight)
        scores.append(self.plan_adherence_score)
        weights.append(0.20)
        
        # Meal completion (15% weight)
        scores.append(self.completion_rate)
        weights.append(0.15)
        
        # Timing adherence (10% weight)
        scores.append(self.timing_adherence_rate)
        weights.append(0.10)
        
        # Weighted average
        weighted_sum = sum(score * weight for score, weight in zip(scores, weights))
        return round(weighted_sum, 1)
    
    @property
    def nutrition_balance_score(self) -> float:
        """Score based on macronutrient balance"""
        if not all([self.target_calories, self.target_protein, self.target_carbs, self.target_fat]):
            return 0.0
        
        # Calculate percentage of calories from each macro
        actual_protein_cal = self.actual_protein * 4
        actual_carbs_cal = self.actual_carbs * 4
        actual_fat_cal = self.actual_fat * 9
        
        target_protein_cal = self.target_protein * 4
        target_carbs_cal = self.target_carbs * 4
        target_fat_cal = self.target_fat * 9
        
        if self.actual_calories == 0 or self.target_calories == 0:
            return 0.0
        
        actual_protein_pct = (actual_protein_cal / self.actual_calories) * 100
        actual_carbs_pct = (actual_carbs_cal / self.actual_calories) * 100
        actual_fat_pct = (actual_fat_cal / self.actual_calories) * 100
        
        target_protein_pct = (target_protein_cal / self.target_calories) * 100
        target_carbs_pct = (target_carbs_cal / self.target_calories) * 100
        target_fat_pct = (target_fat_cal / self.target_calories) * 100
        
        # Calculate deviations
        protein_dev = abs(actual_protein_pct - target_protein_pct)
        carbs_dev = abs(actual_carbs_pct - target_carbs_pct)
        fat_dev = abs(actual_fat_pct - target_fat_pct)
        
        # Average deviation (lower is better)
        avg_deviation = (protein_dev + carbs_dev + fat_dev) / 3
        
        # Convert to score (100 - deviation, with floor at 0)
        return max(0.0, 100.0 - avg_deviation * 2)
    
    def calculate_all_scores(self) -> None:
        """Recalculate all adherence scores"""
        # Plan adherence score
        if self.planned_calories > 0:
            calorie_diff = abs(self.actual_calories - self.planned_calories) / self.planned_calories
            self.plan_adherence_score = max(0.0, 100.0 - calorie_diff * 100)
        
        # Target adherence score  
        self.target_adherence_score = self.calorie_adherence_to_target
        
        # Update achievement flags
        tolerance = 0.05  # 5% tolerance
        
        if self.target_calories:
            self.hit_calorie_target = abs(self.actual_calories - self.target_calories) / self.target_calories <= tolerance
        
        if self.target_protein:
            self.hit_protein_target = self.actual_protein >= self.target_protein * (1 - tolerance)
        
        if self.target_carbs:
            self.hit_carbs_target = abs(self.actual_carbs - self.target_carbs) / self.target_carbs <= tolerance
        
        if self.target_fat:
            self.hit_fat_target = abs(self.actual_fat - self.target_fat) / self.target_fat <= tolerance
        
        if self.target_fiber:
            self.hit_fiber_target = self.actual_fiber >= self.target_fiber * (1 - tolerance)
        
        if self.target_sodium:
            self.stayed_under_sodium_limit = self.actual_sodium <= self.target_sodium
        
        if self.target_sugar:
            self.stayed_under_sugar_limit = self.actual_sugar <= self.target_sugar
    
    def calculate_deficits_surpluses(self) -> None:
        """Calculate deficit/surplus values vs targets"""
        self.calorie_deficit_surplus = (self.target_calories - self.actual_calories) if self.target_calories else 0
        self.protein_deficit_surplus = (self.actual_protein - self.target_protein) if self.target_protein else 0
        self.carbs_deficit_surplus = (self.actual_carbs - self.target_carbs) if self.target_carbs else 0
        self.fat_deficit_surplus = (self.actual_fat - self.target_fat) if self.target_fat else 0
        self.fiber_deficit_surplus = (self.actual_fiber - self.target_fiber) if self.target_fiber else 0
        self.sodium_deficit_surplus = (self.actual_sodium - self.target_sodium) if self.target_sodium else 0
        self.sugar_deficit_surplus = (self.actual_sugar - self.target_sugar) if self.target_sugar else 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'summary_date': self.summary_date.isoformat(),
            
            # Planned vs Actual nutrition
            'planned_nutrition': {
                'calories': self.planned_calories,
                'protein': self.planned_protein,
                'carbs': self.planned_carbs,
                'fat': self.planned_fat,
                'fiber': self.planned_fiber,
                'sodium': self.planned_sodium,
                'sugar': self.planned_sugar
            },
            
            'actual_nutrition': {
                'calories': self.actual_calories,
                'protein': self.actual_protein,
                'carbs': self.actual_carbs,
                'fat': self.actual_fat,
                'fiber': self.actual_fiber,
                'sodium': self.actual_sodium,
                'sugar': self.actual_sugar
            },
            
            'target_nutrition': {
                'calories': self.target_calories,
                'protein': self.target_protein,
                'carbs': self.target_carbs,
                'fat': self.target_fat,
                'fiber': self.target_fiber,
                'sodium': self.target_sodium,
                'sugar': self.target_sugar
            },
            
            # Adherence scores
            'adherence_scores': {
                'plan_adherence': self.plan_adherence_score,
                'target_adherence': self.target_adherence_score,
                'calorie_adherence': self.calorie_adherence_to_target,
                'protein_adherence': self.protein_adherence_to_target,
                'overall_nutrition': self.overall_nutrition_score,
                'balance_score': self.nutrition_balance_score
            },
            
            # Meal statistics
            'meal_stats': {
                'planned': self.meals_planned,
                'consumed': self.meals_consumed,
                'skipped': self.meals_skipped,
                'replaced': self.meals_replaced,
                'modified': self.meals_modified,
                'completion_rate': self.completion_rate,
                'skip_rate': self.skip_rate,
                'modification_rate': self.modification_rate
            },
            
            # Deficit/surplus
            'deficit_surplus': {
                'calories': self.calorie_deficit_surplus,
                'protein': self.protein_deficit_surplus,
                'carbs': self.carbs_deficit_surplus,
                'fat': self.fat_deficit_surplus,
                'fiber': self.fiber_deficit_surplus,
                'sodium': self.sodium_deficit_surplus,
                'sugar': self.sugar_deficit_surplus
            },
            
            # Timing
            'timing': {
                'avg_variance_minutes': self.avg_meal_timing_variance_minutes,
                'on_time_meals': self.on_time_meals,
                'timing_adherence_rate': self.timing_adherence_rate
            },
            
            # Quality metrics
            'quality': {
                'avg_satisfaction_rating': self.avg_satisfaction_rating,
                'avg_difficulty_rating': self.avg_difficulty_rating
            },
            
            # Achievement flags
            'achievements': {
                'hit_calorie_target': self.hit_calorie_target,
                'hit_protein_target': self.hit_protein_target,
                'hit_carbs_target': self.hit_carbs_target,
                'hit_fat_target': self.hit_fat_target,
                'hit_fiber_target': self.hit_fiber_target,
                'stayed_under_sodium_limit': self.stayed_under_sodium_limit,
                'stayed_under_sugar_limit': self.stayed_under_sugar_limit
            },
            
            # Context
            'week_start': self.week_start.isoformat() if self.week_start else None,
            'month_year': self.month_year,
            
            # Metadata
            'last_calculated': self.last_calculated.isoformat(),
            'calculation_version': self.calculation_version,
            'needs_recalculation': self.needs_recalculation,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    @staticmethod
    def create_from_tracking_data(user_id: int, summary_date: date, 
                                 meal_trackings: List[MealTracking],
                                 user_targets: Optional[Dict[str, float]] = None) -> 'DailyNutritionSummary':
        """Create daily summary from meal tracking data"""
        from datetime import timedelta
        import calendar
        
        summary = DailyNutritionSummary(
            user_id=user_id,
            summary_date=summary_date
        )
        
        # Set week start (Monday of the week)
        days_since_monday = summary_date.weekday()
        summary.week_start = summary_date - timedelta(days=days_since_monday)
        
        # Set month_year
        summary.month_year = summary_date.strftime('%Y-%m')
        
        # Set user targets
        if user_targets:
            summary.target_calories = user_targets.get('calories')
            summary.target_protein = user_targets.get('protein')
            summary.target_carbs = user_targets.get('carbs')
            summary.target_fat = user_targets.get('fat')
            summary.target_fiber = user_targets.get('fiber')
            summary.target_sodium = user_targets.get('sodium')
            summary.target_sugar = user_targets.get('sugar')
        
        # Aggregate data from meal trackings
        timing_variances = []
        satisfaction_ratings = []
        difficulty_ratings = []
        
        for tracking in meal_trackings:
            # Planned nutrition totals
            summary.planned_calories += tracking.planned_calories
            summary.planned_protein += tracking.planned_protein
            summary.planned_carbs += tracking.planned_carbs
            summary.planned_fat += tracking.planned_fat
            summary.planned_fiber += tracking.planned_fiber
            summary.planned_sodium += tracking.planned_sodium
            summary.planned_sugar += tracking.planned_sugar
            
            # Actual nutrition totals
            summary.actual_calories += tracking.effective_calories
            summary.actual_protein += tracking.effective_protein
            summary.actual_carbs += tracking.effective_carbs
            summary.actual_fat += tracking.effective_fat
            summary.actual_fiber += tracking.effective_fiber
            summary.actual_sodium += tracking.effective_sodium
            summary.actual_sugar += tracking.effective_sugar
            
            # Meal statistics
            summary.meals_planned += 1
            
            if tracking.status == MealStatus.CONSUMED:
                summary.meals_consumed += 1
            elif tracking.status == MealStatus.SKIPPED:
                summary.meals_skipped += 1
            elif tracking.status == MealStatus.REPLACED:
                summary.meals_replaced += 1
                summary.meals_consumed += 1  # Replaced meals are still consumed
            elif tracking.status == MealStatus.MODIFIED:
                summary.meals_modified += 1
                summary.meals_consumed += 1  # Modified meals are still consumed
            
            # Timing data
            if tracking.timing_variance_minutes is not None:
                timing_variances.append(tracking.timing_variance_minutes)
                if abs(tracking.timing_variance_minutes) <= 15:  # Within 15 minutes
                    summary.on_time_meals += 1
            
            # Ratings
            if tracking.satisfaction_rating:
                satisfaction_ratings.append(tracking.satisfaction_rating)
            if tracking.difficulty_rating:
                difficulty_ratings.append(tracking.difficulty_rating)
        
        # Calculate averages
        if timing_variances:
            summary.avg_meal_timing_variance_minutes = sum(timing_variances) / len(timing_variances)
        
        if satisfaction_ratings:
            summary.avg_satisfaction_rating = sum(satisfaction_ratings) / len(satisfaction_ratings)
        
        if difficulty_ratings:
            summary.avg_difficulty_rating = sum(difficulty_ratings) / len(difficulty_ratings)
        
        # Calculate scores and deficits
        summary.calculate_all_scores()
        summary.calculate_deficits_surpluses()
        
        return summary