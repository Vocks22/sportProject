from flask import Blueprint, request, jsonify
from database import db
from models.meal_tracking import MealTracking, DailyNutritionSummary, MealStatus
from models.user import User
from models.meal_plan import MealPlan
from models.recipe import Recipe
from services.meal_tracking_service import MealTrackingService
from utils.date_utils import parse_date, get_week_dates
from datetime import datetime, date, timedelta
from marshmallow import ValidationError, Schema, fields
from typing import List, Dict, Any
import json

meal_tracking_bp = Blueprint('meal_tracking', __name__)

# ===== VALIDATION SCHEMAS =====

class MealTrackingSchema(Schema):
    """Schema for meal tracking data"""
    user_id = fields.Integer(required=True)
    meal_plan_id = fields.Integer(allow_none=True)
    recipe_id = fields.Integer(allow_none=True)
    meal_date = fields.Date(required=True)
    meal_type = fields.String(required=True, validate=lambda x: x in ['repas1', 'repas2', 'repas3', 'collation'])
    meal_name = fields.String(allow_none=True)

class ConsumptionDataSchema(Schema):
    """Schema for meal consumption data"""
    consumption_time = fields.DateTime(allow_none=True, load_default=None)
    nutrition = fields.Dict(load_default=dict)
    portion_size = fields.Float(allow_none=True)
    notes = fields.String(allow_none=True)
    satisfaction_rating = fields.Integer(allow_none=True, validate=lambda x: 1 <= x <= 5)
    difficulty_rating = fields.Integer(allow_none=True, validate=lambda x: 1 <= x <= 5)
    photo_urls = fields.List(fields.String(), load_default=list)
    modifications = fields.Dict(load_default=dict)
    substitutions = fields.Dict(load_default=dict)

class SkipDataSchema(Schema):
    """Schema for meal skip data"""
    reason = fields.String(allow_none=True)

class ReplaceDataSchema(Schema):
    """Schema for meal replacement data"""
    replacement_recipe_id = fields.Integer(allow_none=True)
    replacement_name = fields.String(allow_none=True)
    reason = fields.String(allow_none=True)
    nutrition = fields.Dict(load_default=dict)

class PortionAdjustmentSchema(Schema):
    """Schema for portion adjustments"""
    portion_multiplier = fields.Float(required=True, validate=lambda x: x > 0)
    nutrition = fields.Dict(load_default=dict)

meal_tracking_schema = MealTrackingSchema()
consumption_data_schema = ConsumptionDataSchema()
skip_data_schema = SkipDataSchema()
replace_data_schema = ReplaceDataSchema()
portion_adjustment_schema = PortionAdjustmentSchema()

# ===== API ENDPOINTS =====

@meal_tracking_bp.route('/meal-tracking/today', methods=['GET'])
def get_today_meal_tracking():
    """Get today's meal tracking for a user (US1.8)"""
    try:
        user_id = request.args.get('user_id', type=int)
        if not user_id:
            return jsonify({'error': 'user_id parameter is required'}), 400
        
        # Verify user exists
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get today's date
        today = date.today()
        
        # Get existing meal trackings for today
        trackings = MealTracking.query.filter_by(
            user_id=user_id,
            meal_date=today
        ).order_by(MealTracking.meal_type).all()
        
        # If no trackings exist, try to create from active meal plan
        if not trackings:
            active_meal_plan = MealPlan.query.filter_by(
                user_id=user_id,
                is_active=True
            ).first()
            
            if active_meal_plan:
                try:
                    trackings = MealTrackingService.create_meal_tracking_from_plan(
                        user_id=user_id,
                        meal_plan_id=active_meal_plan.id,
                        target_date=today
                    )
                except Exception as e:
                    print(f"Error creating trackings from meal plan: {e}")
                    trackings = []
        
        # Convert to dictionaries
        tracking_data = [tracking.to_dict() for tracking in trackings]
        
        # Get daily summary if available
        daily_summary = DailyNutritionSummary.query.filter_by(
            user_id=user_id,
            summary_date=today
        ).first()
        
        summary_data = daily_summary.to_dict() if daily_summary else None
        
        return jsonify({
            'date': today.isoformat(),
            'user_id': user_id,
            'meal_trackings': tracking_data,
            'daily_summary': summary_data,
            'total_trackings': len(tracking_data)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@meal_tracking_bp.route('/meal-tracking/<int:tracking_id>/consume', methods=['POST'])
def mark_meal_consumed(tracking_id):
    """Mark a meal as consumed (US1.8)"""
    try:
        # Get user_id from request body for security
        data = request.get_json() or {}
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'user_id is required in request body'}), 400
        
        # Validate consumption data
        try:
            consumption_data = consumption_data_schema.load(data.get('consumption_data', {}))
        except ValidationError as e:
            return jsonify({'error': 'Invalid consumption data', 'details': e.messages}), 400
        
        # Update meal status using service
        tracking = MealTrackingService.update_meal_status(
            tracking_id=tracking_id,
            user_id=user_id,
            status=MealStatus.CONSUMED,
            consumption_data=consumption_data
        )
        
        return jsonify({
            'success': True,
            'message': 'Meal marked as consumed',
            'meal_tracking': tracking.to_dict()
        })
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@meal_tracking_bp.route('/meal-tracking/<int:tracking_id>/adjust', methods=['PUT'])
def adjust_meal_portions(tracking_id):
    """Adjust meal portions (US1.8)"""
    try:
        # Get user_id from request body for security
        data = request.get_json() or {}
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'user_id is required in request body'}), 400
        
        # Validate portion adjustment data
        try:
            adjustment_data = portion_adjustment_schema.load(data)
        except ValidationError as e:
            return jsonify({'error': 'Invalid adjustment data', 'details': e.messages}), 400
        
        # Get the tracking entry
        tracking = MealTracking.query.filter_by(
            id=tracking_id,
            user_id=user_id
        ).first()
        
        if not tracking:
            return jsonify({'error': 'Meal tracking not found or access denied'}), 404
        
        # Calculate adjusted nutrition values
        multiplier = adjustment_data['portion_multiplier']
        adjusted_nutrition = {
            'calories': tracking.planned_calories * multiplier,
            'protein': tracking.planned_protein * multiplier,
            'carbs': tracking.planned_carbs * multiplier,
            'fat': tracking.planned_fat * multiplier,
            'fiber': tracking.planned_fiber * multiplier,
            'sodium': tracking.planned_sodium * multiplier,
            'sugar': tracking.planned_sugar * multiplier
        }
        
        # Override with any custom nutrition values
        custom_nutrition = adjustment_data.get('nutrition', {})
        adjusted_nutrition.update(custom_nutrition)
        
        # Update the tracking
        consumption_data = {
            'portion_size': multiplier,
            'nutrition': adjusted_nutrition
        }
        
        updated_tracking = MealTrackingService.update_meal_status(
            tracking_id=tracking_id,
            user_id=user_id,
            status=MealStatus.MODIFIED,
            consumption_data=consumption_data
        )
        
        return jsonify({
            'success': True,
            'message': 'Meal portions adjusted',
            'meal_tracking': updated_tracking.to_dict(),
            'adjustments': {
                'portion_multiplier': multiplier,
                'adjusted_nutrition': adjusted_nutrition
            }
        })
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@meal_tracking_bp.route('/meal-tracking/<int:tracking_id>/skip', methods=['POST'])
def skip_meal(tracking_id):
    """Mark a meal as skipped (US1.8)"""
    try:
        # Get user_id from request body for security
        data = request.get_json() or {}
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'user_id is required in request body'}), 400
        
        # Validate skip data
        try:
            skip_data = skip_data_schema.load(data.get('skip_data', {}))
        except ValidationError as e:
            return jsonify({'error': 'Invalid skip data', 'details': e.messages}), 400
        
        # Update meal status using service
        tracking = MealTrackingService.update_meal_status(
            tracking_id=tracking_id,
            user_id=user_id,
            status=MealStatus.SKIPPED,
            consumption_data=skip_data
        )
        
        return jsonify({
            'success': True,
            'message': 'Meal marked as skipped',
            'meal_tracking': tracking.to_dict()
        })
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@meal_tracking_bp.route('/meal-tracking/<int:tracking_id>/replace', methods=['POST'])
def replace_meal(tracking_id):
    """Replace a meal with another recipe/meal (US1.8)"""
    try:
        # Get user_id from request body for security
        data = request.get_json() or {}
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'user_id is required in request body'}), 400
        
        # Validate replacement data
        try:
            replace_data = replace_data_schema.load(data.get('replacement_data', {}))
        except ValidationError as e:
            return jsonify({'error': 'Invalid replacement data', 'details': e.messages}), 400
        
        # If replacement recipe provided, get its nutrition data
        replacement_recipe_id = replace_data.get('replacement_recipe_id')
        if replacement_recipe_id:
            replacement_recipe = Recipe.query.get(replacement_recipe_id)
            if replacement_recipe:
                # Use recipe nutrition if not provided
                if not replace_data.get('nutrition'):
                    replace_data['nutrition'] = {
                        'calories': replacement_recipe.total_calories,
                        'protein': replacement_recipe.total_protein,
                        'carbs': replacement_recipe.total_carbs,
                        'fat': replacement_recipe.total_fat,
                        'fiber': getattr(replacement_recipe, 'total_fiber', 0),
                        'sodium': getattr(replacement_recipe, 'total_sodium', 0),
                        'sugar': getattr(replacement_recipe, 'total_sugar', 0)
                    }
                
                # Set replacement name if not provided
                if not replace_data.get('replacement_name'):
                    replace_data['replacement_name'] = replacement_recipe.name
        
        # Update meal status using service
        tracking = MealTrackingService.update_meal_status(
            tracking_id=tracking_id,
            user_id=user_id,
            status=MealStatus.REPLACED,
            consumption_data=replace_data
        )
        
        return jsonify({
            'success': True,
            'message': 'Meal replaced successfully',
            'meal_tracking': tracking.to_dict()
        })
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@meal_tracking_bp.route('/meal-tracking/summary/<date_str>', methods=['GET'])
def get_daily_summary(date_str):
    """Get daily nutrition summary for a specific date (US1.8)"""
    try:
        user_id = request.args.get('user_id', type=int)
        if not user_id:
            return jsonify({'error': 'user_id parameter is required'}), 400
        
        # Parse date
        try:
            summary_date = parse_date(date_str)
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
        # Get or calculate daily summary
        try:
            summary = MealTrackingService.calculate_daily_summary(
                user_id=user_id,
                summary_date=summary_date,
                force_recalculate=request.args.get('force_recalculate', '').lower() == 'true'
            )
            
            return jsonify({
                'success': True,
                'daily_summary': summary.to_dict(),
                'date': date_str
            })
        
        except ValueError as e:
            return jsonify({'error': str(e)}), 404
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@meal_tracking_bp.route('/meal-tracking/patterns', methods=['GET'])
def analyze_eating_patterns():
    """Analyze eating patterns and adherence trends (US1.8)"""
    try:
        user_id = request.args.get('user_id', type=int)
        days = request.args.get('days', 30, type=int)
        
        if not user_id:
            return jsonify({'error': 'user_id parameter is required'}), 400
        
        # Validate days parameter
        if days < 1 or days > 365:
            return jsonify({'error': 'days must be between 1 and 365'}), 400
        
        # Get adherence trends
        trends = MealTrackingService.get_adherence_trends(user_id, days)
        
        # Get recent meal trackings for pattern analysis
        start_date = date.today() - timedelta(days=days)
        recent_trackings = MealTrackingService.get_user_meal_trackings(
            user_id=user_id,
            start_date=start_date
        )
        
        # Analyze patterns
        patterns = analyze_meal_patterns(recent_trackings)
        
        return jsonify({
            'success': True,
            'user_id': user_id,
            'analysis_period': {
                'days': days,
                'start_date': start_date.isoformat(),
                'end_date': date.today().isoformat()
            },
            'adherence_trends': trends,
            'eating_patterns': patterns,
            'total_meals_analyzed': len(recent_trackings)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@meal_tracking_bp.route('/meal-tracking/report/<month_str>', methods=['GET'])
def get_monthly_report(month_str):
    """Get comprehensive monthly meal tracking report (US1.8)"""
    try:
        user_id = request.args.get('user_id', type=int)
        if not user_id:
            return jsonify({'error': 'user_id parameter is required'}), 400
        
        # Parse month (YYYY-MM format)
        try:
            year, month = map(int, month_str.split('-'))
            if month < 1 or month > 12:
                raise ValueError("Invalid month")
        except (ValueError, AttributeError):
            return jsonify({'error': 'Invalid month format. Use YYYY-MM'}), 400
        
        # Get monthly summary
        monthly_summary = MealTrackingService.get_monthly_summary(user_id, year, month)
        
        # Get weekly summaries for the month
        weekly_summaries = []
        month_start = date(year, month, 1)
        
        # Find all Mondays in the month
        current_date = month_start
        while current_date.month == month:
            # Find Monday of this week
            days_since_monday = current_date.weekday()
            week_monday = current_date - timedelta(days=days_since_monday)
            
            # Get weekly summary
            weekly_data = MealTrackingService.get_weekly_summary(user_id, week_monday)
            if weekly_data.get('days_tracked', 0) > 0:
                weekly_summaries.append(weekly_data)
            
            # Move to next week
            current_date += timedelta(days=7)
        
        # Get all daily summaries for detailed analysis
        daily_summaries = DailyNutritionSummary.query.filter_by(
            user_id=user_id,
            month_year=month_str
        ).order_by(DailyNutritionSummary.summary_date).all()
        
        daily_data = [summary.to_dict() for summary in daily_summaries]
        
        return jsonify({
            'success': True,
            'user_id': user_id,
            'month': month_str,
            'monthly_summary': monthly_summary,
            'weekly_summaries': weekly_summaries,
            'daily_summaries': daily_data,
            'report_metadata': {
                'generated_at': datetime.utcnow().isoformat(),
                'total_days_tracked': len(daily_data),
                'total_weeks_tracked': len(weekly_summaries)
            }
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@meal_tracking_bp.route('/meal-tracking/history', methods=['GET'])
def get_meal_tracking_history():
    """Get meal tracking history with filters (US1.8)"""
    try:
        user_id = request.args.get('user_id', type=int)
        if not user_id:
            return jsonify({'error': 'user_id parameter is required'}), 400
        
        # Parse optional filters
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        status_filter = request.args.getlist('status')
        meal_type_filter = request.args.get('meal_type')
        
        # Parse dates
        start_date = None
        end_date = None
        
        if start_date_str:
            try:
                start_date = parse_date(start_date_str)
            except ValueError:
                return jsonify({'error': 'Invalid start_date format. Use YYYY-MM-DD'}), 400
        
        if end_date_str:
            try:
                end_date = parse_date(end_date_str)
            except ValueError:
                return jsonify({'error': 'Invalid end_date format. Use YYYY-MM-DD'}), 400
        
        # Parse status filter
        parsed_status_filter = None
        if status_filter:
            try:
                parsed_status_filter = [MealStatus(status) for status in status_filter]
            except ValueError as e:
                return jsonify({'error': f'Invalid status filter: {e}'}), 400
        
        # Get meal trackings
        trackings = MealTrackingService.get_user_meal_trackings(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            status_filter=parsed_status_filter
        )
        
        # Apply meal type filter if specified
        if meal_type_filter:
            trackings = [t for t in trackings if t.meal_type == meal_type_filter]
        
        # Convert to dictionaries
        tracking_data = [tracking.to_dict() for tracking in trackings]
        
        # Calculate summary statistics
        stats = calculate_history_stats(trackings)
        
        return jsonify({
            'success': True,
            'user_id': user_id,
            'filters': {
                'start_date': start_date.isoformat() if start_date else None,
                'end_date': end_date.isoformat() if end_date else None,
                'status_filter': status_filter,
                'meal_type_filter': meal_type_filter
            },
            'meal_trackings': tracking_data,
            'statistics': stats,
            'total_results': len(tracking_data)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ===== HELPER FUNCTIONS =====

def analyze_meal_patterns(trackings: List[MealTracking]) -> Dict[str, Any]:
    """Analyze eating patterns from meal trackings"""
    if not trackings:
        return {}
    
    # Group by meal type
    meal_type_stats = {}
    timing_patterns = {}
    satisfaction_patterns = {}
    
    for tracking in trackings:
        meal_type = tracking.meal_type
        
        # Initialize stats for meal type
        if meal_type not in meal_type_stats:
            meal_type_stats[meal_type] = {
                'total': 0,
                'consumed': 0,
                'skipped': 0,
                'replaced': 0,
                'modified': 0,
                'avg_satisfaction': 0,
                'satisfaction_count': 0
            }
        
        stats = meal_type_stats[meal_type]
        stats['total'] += 1
        
        if tracking.status == MealStatus.CONSUMED:
            stats['consumed'] += 1
        elif tracking.status == MealStatus.SKIPPED:
            stats['skipped'] += 1
        elif tracking.status == MealStatus.REPLACED:
            stats['replaced'] += 1
        elif tracking.status == MealStatus.MODIFIED:
            stats['modified'] += 1
        
        # Satisfaction ratings
        if tracking.satisfaction_rating:
            stats['avg_satisfaction'] += tracking.satisfaction_rating
            stats['satisfaction_count'] += 1
        
        # Timing patterns
        if tracking.consumption_time_actual:
            hour = tracking.consumption_time_actual.hour
            if meal_type not in timing_patterns:
                timing_patterns[meal_type] = []
            timing_patterns[meal_type].append(hour)
    
    # Calculate averages and percentages
    for meal_type, stats in meal_type_stats.items():
        if stats['total'] > 0:
            stats['completion_rate'] = (stats['consumed'] / stats['total']) * 100
            stats['skip_rate'] = (stats['skipped'] / stats['total']) * 100
            stats['modification_rate'] = ((stats['replaced'] + stats['modified']) / stats['total']) * 100
        
        if stats['satisfaction_count'] > 0:
            stats['avg_satisfaction'] = stats['avg_satisfaction'] / stats['satisfaction_count']
        else:
            stats['avg_satisfaction'] = None
    
    # Calculate timing patterns
    timing_summary = {}
    for meal_type, hours in timing_patterns.items():
        if hours:
            timing_summary[meal_type] = {
                'avg_hour': sum(hours) / len(hours),
                'earliest_hour': min(hours),
                'latest_hour': max(hours),
                'consistency_score': 100 - (max(hours) - min(hours)) * 2  # Simple consistency metric
            }
    
    return {
        'meal_type_statistics': meal_type_stats,
        'timing_patterns': timing_summary,
        'overall_completion_rate': sum(stats['consumed'] for stats in meal_type_stats.values()) / max(1, sum(stats['total'] for stats in meal_type_stats.values())) * 100,
        'most_consistent_meal': max(timing_summary.keys(), key=lambda k: timing_summary[k]['consistency_score']) if timing_summary else None
    }

def calculate_history_stats(trackings: List[MealTracking]) -> Dict[str, Any]:
    """Calculate summary statistics for meal tracking history"""
    if not trackings:
        return {}
    
    total = len(trackings)
    consumed = sum(1 for t in trackings if t.status == MealStatus.CONSUMED)
    skipped = sum(1 for t in trackings if t.status == MealStatus.SKIPPED)
    replaced = sum(1 for t in trackings if t.status == MealStatus.REPLACED)
    modified = sum(1 for t in trackings if t.status == MealStatus.MODIFIED)
    
    # Calculate nutritional totals
    total_calories = sum(t.effective_calories for t in trackings)
    total_protein = sum(t.effective_protein for t in trackings)
    
    # Calculate satisfaction ratings
    ratings = [t.satisfaction_rating for t in trackings if t.satisfaction_rating]
    avg_satisfaction = sum(ratings) / len(ratings) if ratings else None
    
    return {
        'total_meals': total,
        'completion_stats': {
            'consumed': consumed,
            'skipped': skipped,
            'replaced': replaced,
            'modified': modified,
            'completion_rate': (consumed / total) * 100 if total > 0 else 0,
            'skip_rate': (skipped / total) * 100 if total > 0 else 0
        },
        'nutrition_totals': {
            'total_calories': round(total_calories, 1),
            'total_protein': round(total_protein, 1),
            'avg_calories_per_meal': round(total_calories / total, 1) if total > 0 else 0,
            'avg_protein_per_meal': round(total_protein / total, 1) if total > 0 else 0
        },
        'satisfaction': {
            'avg_rating': round(avg_satisfaction, 1) if avg_satisfaction else None,
            'total_ratings': len(ratings)
        }
    }