"""
Meal Tracking Service - Business Logic for US1.8

This service handles all meal tracking operations including:
- Creating and updating meal tracking entries
- Calculating daily nutrition summaries
- Managing meal status transitions
- Handling adherence score calculations
- Synchronizing with meal plans
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from database import db
from models.meal_tracking import MealTracking, DailyNutritionSummary, MealStatus
from models.user import User
from models.meal_plan import MealPlan
from models.recipe import Recipe


class MealTrackingService:
    """Service class for meal tracking operations"""
    
    @staticmethod
    def create_meal_tracking_from_plan(user_id: int, meal_plan_id: int, 
                                      target_date: date) -> List[MealTracking]:
        """
        Create meal tracking entries from a meal plan for a specific date
        
        Args:
            user_id: User ID
            meal_plan_id: Meal plan ID
            target_date: Date to create tracking for
            
        Returns:
            List of created MealTracking instances
        """
        meal_plan = MealPlan.query.get(meal_plan_id)
        if not meal_plan or meal_plan.user_id != user_id:
            raise ValueError("Meal plan not found or doesn't belong to user")
        
        # Get meals for the specific day from the meal plan
        meals = meal_plan.meals
        day_key = target_date.strftime('%Y-%m-%d')
        
        if day_key not in meals:
            return []
        
        created_trackings = []
        day_meals = meals[day_key]
        
        for meal_type, meal_data in day_meals.items():
            # Check if tracking already exists
            existing = MealTracking.query.filter_by(
                user_id=user_id,
                meal_date=target_date,
                meal_type=meal_type
            ).first()
            
            if existing:
                continue  # Skip if already exists
            
            # Create new tracking entry
            tracking = MealTracking(
                user_id=user_id,
                meal_plan_id=meal_plan_id,
                meal_date=target_date,
                meal_type=meal_type,
                status=MealStatus.PLANNED
            )
            
            # Extract nutrition data from meal plan
            if isinstance(meal_data, dict):
                recipe_id = meal_data.get('recipe_id')
                if recipe_id:
                    recipe = Recipe.query.get(recipe_id)
                    if recipe:
                        tracking.recipe_id = recipe_id
                        tracking.meal_name = recipe.name
                        tracking.planned_calories = recipe.total_calories
                        tracking.planned_protein = recipe.total_protein
                        tracking.planned_carbs = recipe.total_carbs
                        tracking.planned_fat = recipe.total_fat
                
                # Set planned nutrition from meal data if available
                nutrition = meal_data.get('nutrition', {})
                if nutrition:
                    tracking.planned_calories = nutrition.get('calories', tracking.planned_calories)
                    tracking.planned_protein = nutrition.get('protein', tracking.planned_protein)
                    tracking.planned_carbs = nutrition.get('carbs', tracking.planned_carbs)
                    tracking.planned_fat = nutrition.get('fat', tracking.planned_fat)
                    tracking.planned_fiber = nutrition.get('fiber', 0)
                    tracking.planned_sodium = nutrition.get('sodium', 0)
                    tracking.planned_sugar = nutrition.get('sugar', 0)
                
                # Set planned timing
                timing = meal_data.get('time')
                if timing:
                    try:
                        tracking.consumption_time_planned = datetime.strptime(timing, '%H:%M').time()
                    except ValueError:
                        pass  # Invalid time format, ignore
            
            db.session.add(tracking)
            created_trackings.append(tracking)
        
        db.session.commit()
        return created_trackings
    
    @staticmethod
    def update_meal_status(tracking_id: int, user_id: int, status: MealStatus,
                          consumption_data: Optional[Dict[str, Any]] = None) -> MealTracking:
        """
        Update meal tracking status with optional consumption data
        
        Args:
            tracking_id: Meal tracking ID
            user_id: User ID for security
            status: New meal status
            consumption_data: Optional data for consumed/modified meals
            
        Returns:
            Updated MealTracking instance
        """
        tracking = MealTracking.query.filter_by(
            id=tracking_id,
            user_id=user_id
        ).first()
        
        if not tracking:
            raise ValueError("Meal tracking not found or doesn't belong to user")
        
        # Update status
        tracking.status = status
        
        # Handle status-specific data
        if status == MealStatus.CONSUMED:
            tracking.consumption_datetime = consumption_data.get('consumption_time', datetime.utcnow())
            if tracking.consumption_datetime:
                tracking.consumption_time_actual = tracking.consumption_datetime.time()
            
            # Update actual nutrition values
            nutrition = consumption_data.get('nutrition', {})
            if nutrition:
                tracking.actual_calories = nutrition.get('calories')
                tracking.actual_protein = nutrition.get('protein')
                tracking.actual_carbs = nutrition.get('carbs')
                tracking.actual_fat = nutrition.get('fat')
                tracking.actual_fiber = nutrition.get('fiber')
                tracking.actual_sodium = nutrition.get('sodium')
                tracking.actual_sugar = nutrition.get('sugar')
            
            # Update portion size
            if 'portion_size' in consumption_data:
                tracking.actual_portion_size = consumption_data['portion_size']
            
            # Update user feedback
            if 'notes' in consumption_data:
                tracking.user_notes = consumption_data['notes']
            if 'satisfaction_rating' in consumption_data:
                tracking.satisfaction_rating = consumption_data['satisfaction_rating']
            if 'difficulty_rating' in consumption_data:
                tracking.difficulty_rating = consumption_data['difficulty_rating']
            
            # Update photos
            if 'photo_urls' in consumption_data:
                tracking.photo_urls_list = consumption_data['photo_urls']
            
            # Update modifications
            if 'modifications' in consumption_data:
                tracking.modifications = consumption_data['modifications']
            if 'substitutions' in consumption_data:
                tracking.substitutions = consumption_data['substitutions']
        
        elif status == MealStatus.SKIPPED:
            tracking.skip_reason = consumption_data.get('reason') if consumption_data else None
        
        elif status == MealStatus.REPLACED:
            if consumption_data:
                tracking.replacement_recipe_id = consumption_data.get('replacement_recipe_id')
                tracking.replacement_name = consumption_data.get('replacement_name')
                tracking.replacement_reason = consumption_data.get('reason')
                
                # Update actual nutrition for replacement
                nutrition = consumption_data.get('nutrition', {})
                if nutrition:
                    tracking.actual_calories = nutrition.get('calories')
                    tracking.actual_protein = nutrition.get('protein')
                    tracking.actual_carbs = nutrition.get('carbs')
                    tracking.actual_fat = nutrition.get('fat')
                    tracking.actual_fiber = nutrition.get('fiber')
                    tracking.actual_sodium = nutrition.get('sodium')
                    tracking.actual_sugar = nutrition.get('sugar')
        
        elif status == MealStatus.MODIFIED:
            if consumption_data:
                # Update modifications
                if 'modifications' in consumption_data:
                    tracking.modifications = consumption_data['modifications']
                if 'substitutions' in consumption_data:
                    tracking.substitutions = consumption_data['substitutions']
                
                # Update actual nutrition values
                nutrition = consumption_data.get('nutrition', {})
                if nutrition:
                    tracking.actual_calories = nutrition.get('calories')
                    tracking.actual_protein = nutrition.get('protein')
                    tracking.actual_carbs = nutrition.get('carbs')
                    tracking.actual_fat = nutrition.get('fat')
                    tracking.actual_fiber = nutrition.get('fiber')
                    tracking.actual_sodium = nutrition.get('sodium')
                    tracking.actual_sugar = nutrition.get('sugar')
        
        # Update version for sync
        tracking.version += 1
        
        db.session.commit()
        
        # Invalidate daily summary
        MealTrackingService.invalidate_daily_summary(user_id, tracking.meal_date)
        
        return tracking
    
    @staticmethod
    def get_user_meal_trackings(user_id: int, start_date: Optional[date] = None,
                               end_date: Optional[date] = None,
                               status_filter: Optional[List[MealStatus]] = None) -> List[MealTracking]:
        """
        Get meal trackings for a user with optional filters
        
        Args:
            user_id: User ID
            start_date: Optional start date filter
            end_date: Optional end date filter
            status_filter: Optional status filter
            
        Returns:
            List of MealTracking instances
        """
        query = MealTracking.query.filter_by(user_id=user_id)
        
        if start_date:
            query = query.filter(MealTracking.meal_date >= start_date)
        if end_date:
            query = query.filter(MealTracking.meal_date <= end_date)
        if status_filter:
            query = query.filter(MealTracking.status.in_(status_filter))
        
        return query.order_by(MealTracking.meal_date.desc(), MealTracking.meal_type).all()
    
    @staticmethod
    def calculate_daily_summary(user_id: int, summary_date: date,
                               force_recalculate: bool = False) -> DailyNutritionSummary:
        """
        Calculate or retrieve daily nutrition summary
        
        Args:
            user_id: User ID
            summary_date: Date to calculate summary for
            force_recalculate: Force recalculation even if exists
            
        Returns:
            DailyNutritionSummary instance
        """
        # Check if summary exists
        existing_summary = DailyNutritionSummary.query.filter_by(
            user_id=user_id,
            summary_date=summary_date
        ).first()
        
        if existing_summary and not force_recalculate and not existing_summary.needs_recalculation:
            return existing_summary
        
        # Get user for targets
        user = User.query.get(user_id)
        if not user:
            raise ValueError("User not found")
        
        # Get meal trackings for the date
        meal_trackings = MealTracking.query.filter_by(
            user_id=user_id,
            meal_date=summary_date
        ).all()
        
        if existing_summary:
            # Update existing summary
            summary = existing_summary
        else:
            # Create new summary
            summary = DailyNutritionSummary(
                user_id=user_id,
                summary_date=summary_date
            )
            db.session.add(summary)
        
        # Reset values
        summary.planned_calories = 0
        summary.planned_protein = 0
        summary.planned_carbs = 0
        summary.planned_fat = 0
        summary.planned_fiber = 0
        summary.planned_sodium = 0
        summary.planned_sugar = 0
        
        summary.actual_calories = 0
        summary.actual_protein = 0
        summary.actual_carbs = 0
        summary.actual_fat = 0
        summary.actual_fiber = 0
        summary.actual_sodium = 0
        summary.actual_sugar = 0
        
        summary.meals_planned = 0
        summary.meals_consumed = 0
        summary.meals_skipped = 0
        summary.meals_replaced = 0
        summary.meals_modified = 0
        summary.on_time_meals = 0
        
        # Set user targets
        targets = user.get_daily_targets()
        summary.target_calories = targets['calories']
        summary.target_protein = targets['protein']
        summary.target_carbs = targets['carbs']
        summary.target_fat = targets['fat']
        summary.target_fiber = targets['fiber']
        summary.target_sodium = targets['sodium']
        summary.target_sugar = targets['sugar']
        
        # Set week and month context
        days_since_monday = summary_date.weekday()
        summary.week_start = summary_date - timedelta(days=days_since_monday)
        summary.month_year = summary_date.strftime('%Y-%m')
        
        # Aggregate data from trackings
        timing_variances = []
        satisfaction_ratings = []
        difficulty_ratings = []
        
        for tracking in meal_trackings:
            # Planned nutrition
            summary.planned_calories += tracking.planned_calories
            summary.planned_protein += tracking.planned_protein
            summary.planned_carbs += tracking.planned_carbs
            summary.planned_fat += tracking.planned_fat
            summary.planned_fiber += tracking.planned_fiber
            summary.planned_sodium += tracking.planned_sodium
            summary.planned_sugar += tracking.planned_sugar
            
            # Actual nutrition (effective values)
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
                summary.meals_consumed += 1
            elif tracking.status == MealStatus.MODIFIED:
                summary.meals_modified += 1
                summary.meals_consumed += 1
            
            # Timing analysis
            if tracking.timing_variance_minutes is not None:
                timing_variances.append(tracking.timing_variance_minutes)
                if abs(tracking.timing_variance_minutes) <= 15:
                    summary.on_time_meals += 1
            
            # Quality ratings
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
        
        # Update metadata
        summary.last_calculated = datetime.utcnow()
        summary.needs_recalculation = False
        summary.calculation_version = 1
        
        db.session.commit()
        return summary
    
    @staticmethod
    def invalidate_daily_summary(user_id: int, target_date: date) -> None:
        """
        Mark a daily summary as needing recalculation
        
        Args:
            user_id: User ID
            target_date: Date of summary to invalidate
        """
        summary = DailyNutritionSummary.query.filter_by(
            user_id=user_id,
            summary_date=target_date
        ).first()
        
        if summary:
            summary.needs_recalculation = True
            db.session.commit()
    
    @staticmethod
    def get_weekly_summary(user_id: int, week_start: date) -> Dict[str, Any]:
        """
        Get weekly aggregated summary
        
        Args:
            user_id: User ID
            week_start: Monday of the week
            
        Returns:
            Dictionary with weekly summary data
        """
        week_end = week_start + timedelta(days=6)
        
        daily_summaries = DailyNutritionSummary.query.filter(
            and_(
                DailyNutritionSummary.user_id == user_id,
                DailyNutritionSummary.summary_date >= week_start,
                DailyNutritionSummary.summary_date <= week_end
            )
        ).order_by(DailyNutritionSummary.summary_date).all()
        
        if not daily_summaries:
            return {
                'week_start': week_start.isoformat(),
                'week_end': week_end.isoformat(),
                'days_tracked': 0,
                'summary': {}
            }
        
        # Aggregate weekly data
        total_days = len(daily_summaries)
        weekly_data = {
            'week_start': week_start.isoformat(),
            'week_end': week_end.isoformat(),
            'days_tracked': total_days,
            'avg_calories': sum(s.actual_calories for s in daily_summaries) / total_days,
            'avg_protein': sum(s.actual_protein for s in daily_summaries) / total_days,
            'avg_plan_adherence': sum(s.plan_adherence_score for s in daily_summaries) / total_days,
            'avg_target_adherence': sum(s.target_adherence_score for s in daily_summaries) / total_days,
            'total_meals_planned': sum(s.meals_planned for s in daily_summaries),
            'total_meals_consumed': sum(s.meals_consumed for s in daily_summaries),
            'total_meals_skipped': sum(s.meals_skipped for s in daily_summaries),
            'weekly_completion_rate': 0,
            'days_hit_calorie_target': sum(1 for s in daily_summaries if s.hit_calorie_target),
            'days_hit_protein_target': sum(1 for s in daily_summaries if s.hit_protein_target),
            'avg_satisfaction': None,
            'daily_summaries': [s.to_dict() for s in daily_summaries]
        }
        
        # Calculate completion rate
        if weekly_data['total_meals_planned'] > 0:
            weekly_data['weekly_completion_rate'] = (
                weekly_data['total_meals_consumed'] / weekly_data['total_meals_planned']
            ) * 100
        
        # Calculate average satisfaction
        satisfaction_ratings = [s.avg_satisfaction_rating for s in daily_summaries if s.avg_satisfaction_rating]
        if satisfaction_ratings:
            weekly_data['avg_satisfaction'] = sum(satisfaction_ratings) / len(satisfaction_ratings)
        
        return weekly_data
    
    @staticmethod
    def get_monthly_summary(user_id: int, year: int, month: int) -> Dict[str, Any]:
        """
        Get monthly aggregated summary
        
        Args:
            user_id: User ID
            year: Year
            month: Month (1-12)
            
        Returns:
            Dictionary with monthly summary data
        """
        month_str = f"{year:04d}-{month:02d}"
        
        daily_summaries = DailyNutritionSummary.query.filter_by(
            user_id=user_id,
            month_year=month_str
        ).order_by(DailyNutritionSummary.summary_date).all()
        
        if not daily_summaries:
            return {
                'year': year,
                'month': month,
                'month_year': month_str,
                'days_tracked': 0,
                'summary': {}
            }
        
        # Aggregate monthly data
        total_days = len(daily_summaries)
        monthly_data = {
            'year': year,
            'month': month,
            'month_year': month_str,
            'days_tracked': total_days,
            'avg_daily_calories': sum(s.actual_calories for s in daily_summaries) / total_days,
            'avg_daily_protein': sum(s.actual_protein for s in daily_summaries) / total_days,
            'avg_plan_adherence': sum(s.plan_adherence_score for s in daily_summaries) / total_days,
            'avg_target_adherence': sum(s.target_adherence_score for s in daily_summaries) / total_days,
            'total_meals_planned': sum(s.meals_planned for s in daily_summaries),
            'total_meals_consumed': sum(s.meals_consumed for s in daily_summaries),
            'monthly_completion_rate': 0,
            'days_hit_calorie_target': sum(1 for s in daily_summaries if s.hit_calorie_target),
            'days_hit_protein_target': sum(1 for s in daily_summaries if s.hit_protein_target),
            'calorie_target_success_rate': 0,
            'protein_target_success_rate': 0,
            'best_day': None,
            'worst_day': None
        }
        
        # Calculate rates
        if monthly_data['total_meals_planned'] > 0:
            monthly_data['monthly_completion_rate'] = (
                monthly_data['total_meals_consumed'] / monthly_data['total_meals_planned']
            ) * 100
        
        if total_days > 0:
            monthly_data['calorie_target_success_rate'] = (
                monthly_data['days_hit_calorie_target'] / total_days
            ) * 100
            monthly_data['protein_target_success_rate'] = (
                monthly_data['days_hit_protein_target'] / total_days
            ) * 100
        
        # Find best and worst days by overall nutrition score
        if daily_summaries:
            best_summary = max(daily_summaries, key=lambda s: s.overall_nutrition_score)
            worst_summary = min(daily_summaries, key=lambda s: s.overall_nutrition_score)
            
            monthly_data['best_day'] = {
                'date': best_summary.summary_date.isoformat(),
                'score': best_summary.overall_nutrition_score,
                'adherence': best_summary.target_adherence_score
            }
            
            monthly_data['worst_day'] = {
                'date': worst_summary.summary_date.isoformat(),
                'score': worst_summary.overall_nutrition_score,
                'adherence': worst_summary.target_adherence_score
            }
        
        return monthly_data
    
    @staticmethod
    def get_adherence_trends(user_id: int, days: int = 30) -> Dict[str, Any]:
        """
        Get adherence trends over specified days
        
        Args:
            user_id: User ID
            days: Number of days to analyze
            
        Returns:
            Dictionary with trend analysis
        """
        start_date = date.today() - timedelta(days=days)
        
        summaries = DailyNutritionSummary.query.filter(
            and_(
                DailyNutritionSummary.user_id == user_id,
                DailyNutritionSummary.summary_date >= start_date
            )
        ).order_by(DailyNutritionSummary.summary_date).all()
        
        if len(summaries) < 2:
            return {'error': 'Insufficient data for trend analysis'}
        
        # Calculate trends
        plan_adherence_scores = [s.plan_adherence_score for s in summaries]
        target_adherence_scores = [s.target_adherence_score for s in summaries]
        completion_rates = [s.completion_rate for s in summaries]
        
        def calculate_trend(values: List[float]) -> str:
            if len(values) < 2:
                return 'stable'
            
            recent_avg = sum(values[-7:]) / min(7, len(values))
            earlier_avg = sum(values[:-7]) / max(1, len(values) - 7) if len(values) > 7 else sum(values[:7]) / min(7, len(values))
            
            if recent_avg > earlier_avg + 5:
                return 'improving'
            elif recent_avg < earlier_avg - 5:
                return 'declining'
            else:
                return 'stable'
        
        return {
            'period_days': days,
            'data_points': len(summaries),
            'avg_plan_adherence': sum(plan_adherence_scores) / len(plan_adherence_scores),
            'avg_target_adherence': sum(target_adherence_scores) / len(target_adherence_scores),
            'avg_completion_rate': sum(completion_rates) / len(completion_rates),
            'plan_adherence_trend': calculate_trend(plan_adherence_scores),
            'target_adherence_trend': calculate_trend(target_adherence_scores),
            'completion_trend': calculate_trend(completion_rates),
            'recent_7_day_avg': {
                'plan_adherence': sum(plan_adherence_scores[-7:]) / min(7, len(plan_adherence_scores)),
                'target_adherence': sum(target_adherence_scores[-7:]) / min(7, len(target_adherence_scores)),
                'completion_rate': sum(completion_rates[-7:]) / min(7, len(completion_rates))
            }
        }