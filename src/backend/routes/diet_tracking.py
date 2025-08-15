"""
API Routes pour le suivi quotidien de la diète
"""
from flask import Blueprint, jsonify, request
from datetime import datetime, date, timedelta
from database import db
from models.diet_program import DietProgram, DietTracking, DietStreak
from sqlalchemy import and_

diet_tracking_bp = Blueprint('diet_tracking', __name__)

@diet_tracking_bp.route('/api/diet/program', methods=['GET'])
def get_diet_program():
    """Récupère le programme alimentaire complet"""
    try:
        meals = DietProgram.query.order_by(DietProgram.order_index).all()
        return jsonify({
            'success': True,
            'program': [meal.to_dict() for meal in meals]
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@diet_tracking_bp.route('/api/diet/today', methods=['GET'])
def get_today_diet():
    """Récupère le statut de la diète du jour avec le repas actuel"""
    try:
        today = date.today()
        now = datetime.now()
        current_hour = now.hour
        current_minute = now.minute
        
        # Déterminer le repas actuel selon l'heure et les minutes
        current_meal_type = get_current_meal_type(current_hour, current_minute)
        
        # Récupérer tous les repas du programme
        meals = DietProgram.query.order_by(DietProgram.order_index).all()
        
        # Récupérer le tracking du jour
        today_trackings = DietTracking.query.filter_by(date=today).all()
        tracking_dict = {t.meal_id: t for t in today_trackings}
        
        # Créer les entrées de tracking si elles n'existent pas
        for meal in meals:
            if meal.id not in tracking_dict:
                new_tracking = DietTracking(
                    date=today,
                    meal_id=meal.id,
                    completed=False
                )
                db.session.add(new_tracking)
                tracking_dict[meal.id] = new_tracking
        
        db.session.commit()
        
        # Préparer la réponse
        meals_status = []
        current_meal = None
        next_meal = None
        
        for meal in meals:
            tracking = tracking_dict.get(meal.id)
            meal_data = {
                'id': meal.id,
                'meal_type': meal.meal_type,
                'meal_name': meal.meal_name,
                'time_slot': meal.time_slot,
                'order_index': meal.order_index,  # Ajout de l'ordre
                'foods': meal.foods,
                'completed': tracking.completed if tracking else False,
                'completed_at': tracking.completed_at.isoformat() if tracking and tracking.completed_at else None
            }
            meals_status.append(meal_data)
            
            # Identifier le repas actuel et le prochain
            if meal.meal_type == current_meal_type:
                current_meal = meal_data
            elif not next_meal and not (tracking and tracking.completed):
                next_meal = meal_data
        
        # Calculer les statistiques du jour
        completed_count = sum(1 for m in meals_status if m['completed'])
        completion_percentage = (completed_count / len(meals)) * 100 if meals else 0
        
        return jsonify({
            'success': True,
            'date': today.isoformat(),
            'current_meal_type': current_meal_type,
            'current_meal': current_meal,
            'next_meal': next_meal,
            'meals': meals_status,
            'stats': {
                'completed': completed_count,
                'total': len(meals),
                'percentage': round(completion_percentage, 1)
            }
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@diet_tracking_bp.route('/api/diet/validate', methods=['POST'])
def validate_meal():
    """Valide qu'un repas a été consommé"""
    try:
        data = request.get_json()
        meal_id = data.get('meal_id')
        completed = data.get('completed', True)
        notes = data.get('notes', '')
        tracking_date = data.get('date', date.today().isoformat())
        
        # Convertir la date si fournie
        if isinstance(tracking_date, str):
            tracking_date = date.fromisoformat(tracking_date)
        
        # Trouver ou créer le tracking
        tracking = DietTracking.query.filter(
            and_(
                DietTracking.date == tracking_date,
                DietTracking.meal_id == meal_id
            )
        ).first()
        
        if not tracking:
            tracking = DietTracking(
                date=tracking_date,
                meal_id=meal_id
            )
            db.session.add(tracking)
        
        # Mettre à jour le statut
        tracking.completed = completed
        tracking.completed_at = datetime.now() if completed else None
        tracking.notes = notes
        
        db.session.commit()
        
        # Mettre à jour les statistiques de streak seulement pour aujourd'hui
        if tracking_date == date.today():
            update_streak_stats()
        
        return jsonify({
            'success': True,
            'tracking': tracking.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        print(f"Erreur dans validate_meal: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@diet_tracking_bp.route('/api/diet/stats', methods=['GET'])
def get_diet_stats():
    """Récupère les statistiques de suivi (streak, taux de respect, etc.)"""
    try:
        # Récupérer ou créer les stats
        stats = DietStreak.query.first()
        if not stats:
            stats = DietStreak()
            db.session.add(stats)
            db.session.commit()
        
        # Calculer les stats de la semaine
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        
        week_trackings = DietTracking.query.filter(
            DietTracking.date >= week_start,
            DietTracking.date <= today
        ).all()
        
        # Calculer le taux de respect de la semaine
        total_meals = len(week_trackings)
        completed_meals = sum(1 for t in week_trackings if t.completed)
        week_percentage = (completed_meals / total_meals * 100) if total_meals > 0 else 0
        
        # Récupérer l'historique des 30 derniers jours pour le calendrier
        month_ago = today - timedelta(days=30)
        month_trackings = db.session.query(
            DietTracking.date,
            db.func.count(DietTracking.id).label('total'),
            db.func.sum(db.cast(DietTracking.completed, db.Integer)).label('completed')
        ).filter(
            DietTracking.date >= month_ago
        ).group_by(DietTracking.date).all()
        
        calendar_data = {}
        for tracking in month_trackings:
            calendar_data[tracking.date.isoformat()] = {
                'total': tracking.total,
                'completed': tracking.completed or 0,
                'success': tracking.completed == tracking.total and tracking.total == 5
            }
        
        return jsonify({
            'success': True,
            'streak': stats.to_dict(),
            'week_stats': {
                'percentage': round(week_percentage, 1),
                'completed_meals': completed_meals,
                'total_meals': total_meals
            },
            'calendar': calendar_data
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@diet_tracking_bp.route('/api/diet/history/<date_str>', methods=['GET'])
def get_diet_history(date_str):
    """Récupère l'historique d'une date spécifique"""
    try:
        target_date = date.fromisoformat(date_str)
        
        trackings = DietTracking.query.filter_by(date=target_date).all()
        
        return jsonify({
            'success': True,
            'date': date_str,
            'trackings': [t.to_dict() for t in trackings]
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@diet_tracking_bp.route('/api/diet/week/<int:week_number>/<int:year>', methods=['GET'])
def get_week_diet(week_number, year):
    """Récupère les repas validés pour une semaine spécifique"""
    try:
        # Calculer les dates de début et fin de semaine
        jan1 = date(year, 1, 1)
        week_start = jan1 + timedelta(days=(week_number - 1) * 7 - jan1.weekday())
        week_end = week_start + timedelta(days=6)
        
        # Récupérer tous les trackings de la semaine
        trackings = DietTracking.query.filter(
            DietTracking.date >= week_start,
            DietTracking.date <= week_end
        ).all()
        
        # Organiser par jour
        week_data = {}
        for tracking in trackings:
            # Obtenir le nom du jour en anglais
            day_name = tracking.date.strftime('%A').lower()
            
            if day_name not in week_data:
                week_data[day_name] = {}
            
            # Récupérer le meal pour avoir le meal_type
            meal = DietProgram.query.get(tracking.meal_id)
            if meal:
                week_data[day_name][meal.meal_type] = tracking.completed
        
        return jsonify({
            'success': True,
            'week_number': week_number,
            'year': year,
            'week_start': week_start.isoformat(),
            'week_end': week_end.isoformat(),
            'meals': week_data
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


def get_current_meal_type(hour, minute=0):
    """Détermine le type de repas selon l'heure actuelle en utilisant les vrais horaires"""
    from models.diet_program import DietProgram
    import re
    
    # Récupérer tous les repas avec leurs horaires
    meals = DietProgram.query.order_by(DietProgram.order_index).all()
    
    current_time = hour * 60 + minute  # Convertir en minutes pour faciliter la comparaison
    
    for meal in meals:
        # Parser le time_slot (format: "6h-9h" ou "19h30-23h00")
        time_slot = meal.time_slot
        match = re.match(r'(\d+)h?(\d*)-(\d+)h?(\d*)', time_slot)
        
        if match:
            start_hour = int(match.group(1))
            start_min = int(match.group(2)) if match.group(2) else 0
            end_hour = int(match.group(3))
            end_min = int(match.group(4)) if match.group(4) else 0
            
            start_time = start_hour * 60 + start_min
            end_time = end_hour * 60 + end_min
            
            # Gérer le cas où la fin est le lendemain (ex: 23h-2h)
            if end_time < start_time:
                # Si on est après minuit mais avant la fin
                if current_time < end_time:
                    return meal.meal_type
                # Si on est après le début le soir
                elif current_time >= start_time:
                    return meal.meal_type
            else:
                # Cas normal
                if start_time <= current_time < end_time:
                    return meal.meal_type
    
    # Si aucun repas ne correspond, retourner le premier repas
    if meals:
        return meals[0].meal_type
    
    return 'repas1'  # Fallback


def update_streak_stats():
    """Met à jour les statistiques de streak"""
    stats = DietStreak.query.first()
    if not stats:
        stats = DietStreak()
        db.session.add(stats)
    
    today = date.today()
    
    # Vérifier si tous les repas du jour sont complétés
    today_trackings = DietTracking.query.filter_by(date=today).all()
    all_completed = all(t.completed for t in today_trackings) and len(today_trackings) == 5
    
    if all_completed:
        # Si c'est un nouveau jour complet
        if stats.last_tracked_date != today:
            # Vérifier si c'est consécutif
            if stats.last_tracked_date == today - timedelta(days=1):
                stats.current_streak += 1
            else:
                stats.current_streak = 1
            
            stats.last_tracked_date = today
            stats.total_days_tracked += 1
            
            # Mettre à jour le record
            if stats.current_streak > stats.longest_streak:
                stats.longest_streak = stats.current_streak
    
    # Compter le total de repas complétés
    all_completed_meals = DietTracking.query.filter_by(completed=True).count()
    stats.total_meals_completed = all_completed_meals
    
    db.session.commit()