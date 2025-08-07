from flask import Blueprint, jsonify, request
from datetime import datetime, date, timedelta
from database import db
from models.user import User, WeightHistory, UserGoalsHistory
from models.measurements import UserMeasurement
# Import des modèles pour les relations SQLAlchemy
from models.meal_plan import MealPlan
from models.recipe import Recipe
from models.ingredient import Ingredient
from services.nutrition_calculator_service import nutrition_calculator
from services.portion_adjustment_service import portion_adjustment
import logging

logger = logging.getLogger(__name__)

user_bp = Blueprint('user', __name__)

@user_bp.route('/users', methods=['GET'])
def get_users():
    try:
        users = User.query.all()
        return jsonify([user.to_dict() for user in users])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    try:
        user = User.query.get_or_404(user_id)
        return jsonify(user.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    user = User(
        username=data['username'],
        email=data['email'],
        current_weight=data.get('current_weight'),
        target_weight=data.get('target_weight'),
        height=data.get('height'),
        age=data.get('age'),
        gender=data.get('gender'),
        activity_level=data.get('activity_level', 'moderate'),
        daily_calories_target=data.get('daily_calories_target', 2000),
        daily_protein_target=data.get('daily_protein_target', 100),
        daily_carbs_target=data.get('daily_carbs_target', 250),
        daily_fat_target=data.get('daily_fat_target', 65)
    )
    db.session.add(user)
    db.session.commit()
    return jsonify(user.to_dict()), 201

@user_bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    for key, value in data.items():
        if hasattr(user, key):
            setattr(user, key, value)
    
    db.session.commit()
    return jsonify(user.to_dict())


# ===== ROUTES US1.7 : PROFIL UTILISATEUR RÉEL =====

@user_bp.route('/users/<int:user_id>/profile', methods=['GET'])
def get_user_profile(user_id):
    """Récupère le profil utilisateur complet avec calculs nutritionnels"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': f'User {user_id} not found'}), 404
        
        # Calculs nutritionnels
        nutrition_profile = nutrition_calculator.calculate_nutrition_profile(user)
        
        # Données de base du profil
        profile_data = user.to_dict(include_sensitive=False, include_extended=True)
        
        # Ajouter les calculs nutritionnels
        profile_data['nutrition_profile'] = nutrition_profile.to_dict()
        
        # Historique récent du poids (30 derniers jours)
        recent_weights = WeightHistory.query.filter(
            WeightHistory.user_id == user_id,
            WeightHistory.recorded_date >= date.today() - timedelta(days=30)
        ).order_by(WeightHistory.recorded_date.desc()).limit(30).all()
        
        profile_data['recent_weight_history'] = [wh.to_dict() for wh in recent_weights]
        
        # Objectifs actifs
        active_goals = UserGoalsHistory.query.filter(
            UserGoalsHistory.user_id == user_id,
            UserGoalsHistory.status == 'active'
        ).order_by(UserGoalsHistory.start_date.desc()).all()
        
        profile_data['active_goals'] = [goal.to_dict() for goal in active_goals]
        
        # Progression vers l'objectif
        profile_data['progress'] = {
            'weight_trend': user.get_weight_trend(30),
            'progress_percentage': user.calculate_progress_percentage(),
            'days_since_last_weigh_in': None
        }
        
        if recent_weights:
            last_weigh_in = recent_weights[0].recorded_date
            days_diff = (date.today() - last_weigh_in).days
            profile_data['progress']['days_since_last_weigh_in'] = days_diff
        
        logger.info(f"Profil complet récupéré pour utilisateur {user_id}")
        return jsonify(profile_data)
        
    except Exception as e:
        logger.error(f"Erreur récupération profil utilisateur {user_id}: {e}")
        return jsonify({'error': str(e)}), 500


@user_bp.route('/users/<int:user_id>/profile', methods=['PUT'])
def update_user_profile(user_id):
    """Met à jour le profil utilisateur avec validation et recalculs automatiques"""
    try:
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        
        # Validation des données
        validation_errors = []
        
        # Validation du poids
        if 'current_weight' in data:
            weight = data['current_weight']
            if not weight or weight <= 0 or weight > 500:
                validation_errors.append("Le poids doit être entre 1 et 500 kg")
        
        # Validation de la taille
        if 'height' in data:
            height = data['height']
            if not height or height <= 0 or height > 300:
                validation_errors.append("La taille doit être entre 1 et 300 cm")
        
        # Validation de l'âge ou date de naissance
        if 'birth_date' in data and data['birth_date']:
            try:
                birth_date = datetime.fromisoformat(data['birth_date']).date()
                if birth_date > date.today():
                    validation_errors.append("La date de naissance ne peut pas être dans le futur")
                age = (date.today() - birth_date).days // 365
                if age < 10 or age > 120:
                    validation_errors.append("L'âge doit être entre 10 et 120 ans")
            except ValueError:
                validation_errors.append("Format de date de naissance invalide")
        
        if validation_errors:
            return jsonify({'errors': validation_errors}), 400
        
        # Mettre à jour les champs du profil
        old_weight = user.current_weight
        
        # Mise à jour des champs simples
        simple_fields = [
            'current_weight', 'target_weight', 'height', 'age', 'gender', 'activity_level',
            'goals', 'medical_conditions', 'dietary_restrictions', 'preferred_cuisine_types',
            'body_fat_percentage', 'muscle_mass_percentage', 'water_percentage',
            'bone_density', 'metabolic_age', 'timezone', 'language', 'units_system'
        ]
        
        for field in simple_fields:
            if field in data:
                setattr(user, field, data[field])
        
        # Traitement spécial pour la date de naissance
        if 'birth_date' in data and data['birth_date']:
            user.birth_date = datetime.fromisoformat(data['birth_date']).date()
        
        # Traitement des listes JSON
        list_fields = {
            'goals_list': 'goals',
            'medical_conditions_list': 'medical_conditions',
            'dietary_restrictions_list': 'dietary_restrictions',
            'preferred_cuisine_types_list': 'preferred_cuisine_types'
        }
        
        for list_field, db_field in list_fields.items():
            if list_field in data:
                setattr(user, list_field, data[list_field])
        
        # Traitement des préférences de notification
        if 'notification_preferences' in data:
            user.notification_preferences_dict = data['notification_preferences']
        
        # Mise à jour des objectifs nutritionnels si fournis
        nutrition_targets = [
            'daily_calories_target', 'daily_protein_target', 'daily_carbs_target',
            'daily_fat_target', 'daily_fiber_target', 'daily_sodium_target',
            'daily_sugar_target', 'daily_water_target'
        ]
        
        for target in nutrition_targets:
            if target in data:
                setattr(user, target, data[target])
        
        # Mettre à jour le statut du profil
        user.update_profile_status()
        
        # Si le poids a changé, ajouter à l'historique
        if old_weight != user.current_weight and user.current_weight:
            existing_entry = WeightHistory.query.filter(
                WeightHistory.user_id == user_id,
                WeightHistory.recorded_date == date.today()
            ).first()
            
            if existing_entry:
                # Mettre à jour l'entrée existante
                existing_entry.weight = user.current_weight
                existing_entry.body_fat_percentage = user.body_fat_percentage
                existing_entry.muscle_mass_percentage = user.muscle_mass_percentage
                existing_entry.water_percentage = user.water_percentage
                existing_entry.notes = "Mise à jour du profil"
                existing_entry.updated_at = datetime.utcnow()
            else:
                # Créer nouvelle entrée
                weight_entry = WeightHistory(
                    user_id=user_id,
                    weight=user.current_weight,
                    body_fat_percentage=user.body_fat_percentage,
                    muscle_mass_percentage=user.muscle_mass_percentage,
                    water_percentage=user.water_percentage,
                    recorded_date=date.today(),
                    notes="Mise à jour du profil",
                    measurement_method="profile_update",
                    data_source="user_profile"
                )
                db.session.add(weight_entry)
        
        db.session.commit()
        
        # Recalculer le profil nutritionnel avec les nouvelles données
        nutrition_profile = nutrition_calculator.calculate_nutrition_profile(user, force_recalculate=True)
        
        # Retourner le profil mis à jour
        profile_data = user.to_dict(include_sensitive=False, include_extended=True)
        profile_data['nutrition_profile'] = nutrition_profile.to_dict()
        
        logger.info(f"Profil utilisateur {user_id} mis à jour avec succès")
        return jsonify(profile_data)
        
    except Exception as e:
        logger.error(f"Erreur mise à jour profil utilisateur {user_id}: {e}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@user_bp.route('/users/<int:user_id>/weight-history', methods=['GET'])
def get_weight_history(user_id):
    """Récupère l'historique des pesées d'un utilisateur"""
    try:
        # Paramètres de requête
        days = request.args.get('days', 365, type=int)  # 365 jours par défaut pour tout récupérer
        limit = request.args.get('limit', 500, type=int)  # Limite augmentée
        
        # Calculer la date de début pour les stats
        start_date = date.today() - timedelta(days=days)
        
        # Si days >= 365, récupérer TOUT l'historique
        if days >= 365:
            # Récupérer TOUT sans limite de date
            weight_entries = WeightHistory.query.filter(
                WeightHistory.user_id == user_id
            ).order_by(WeightHistory.recorded_date.desc()).limit(limit).all()
            # Pour les stats, utiliser la date la plus ancienne disponible
            if weight_entries:
                start_date = min(entry.recorded_date for entry in weight_entries)
        else:
            # Sinon, filtrer par date
            weight_entries = WeightHistory.query.filter(
                WeightHistory.user_id == user_id,
                WeightHistory.recorded_date >= start_date
            ).order_by(WeightHistory.recorded_date.desc()).limit(limit).all()
        
        # Statistiques sur la période
        if weight_entries:
            weights = [entry.weight for entry in weight_entries]
            stats = {
                'count': len(weight_entries),
                'min_weight': min(weights),
                'max_weight': max(weights),
                'avg_weight': round(sum(weights) / len(weights), 1),
                'latest_weight': weights[0] if weights else None,
                'weight_change': weights[0] - weights[-1] if len(weights) > 1 else 0,
                'period_days': days
            }
        else:
            stats = {
                'count': 0,
                'min_weight': None,
                'max_weight': None,
                'avg_weight': None,
                'latest_weight': None,
                'weight_change': 0,
                'period_days': days
            }
        
        response_data = {
            'weight_history': [entry.to_dict() for entry in weight_entries],
            'statistics': stats,
            'period_info': {
                'start_date': start_date.isoformat(),
                'end_date': date.today().isoformat(),
                'requested_days': days,
                'actual_entries': len(weight_entries)
            }
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Erreur récupération historique poids utilisateur {user_id}: {e}")
        return jsonify({'error': str(e)}), 500


@user_bp.route('/users/<int:user_id>/weight-history', methods=['POST'])
def add_weight_entry(user_id):
    """Ajoute une nouvelle pesée à l'historique"""
    try:
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        
        # Validation des données requises
        if 'weight' not in data or not data['weight']:
            return jsonify({'error': 'Le poids est requis'}), 400
        
        weight = float(data['weight'])
        if weight <= 0 or weight > 500:
            return jsonify({'error': 'Le poids doit être entre 1 et 500 kg'}), 400
        
        # Date d'enregistrement
        recorded_date = date.today()
        if 'recorded_date' in data and data['recorded_date']:
            try:
                recorded_date = datetime.fromisoformat(data['recorded_date']).date()
            except ValueError:
                return jsonify({'error': 'Format de date invalide'}), 400
        
        # Vérifier si une entrée existe déjà pour cette date
        existing_entry = WeightHistory.query.filter(
            WeightHistory.user_id == user_id,
            WeightHistory.recorded_date == recorded_date
        ).first()
        
        if existing_entry:
            # Mettre à jour l'entrée existante
            existing_entry.weight = weight
            existing_entry.body_fat_percentage = data.get('body_fat_percentage')
            existing_entry.muscle_mass_percentage = data.get('muscle_mass_percentage')
            existing_entry.water_percentage = data.get('water_percentage')
            existing_entry.notes = data.get('notes', existing_entry.notes)
            existing_entry.measurement_method = data.get('measurement_method', 'manual')
            existing_entry.updated_at = datetime.utcnow()
            
            weight_entry = existing_entry
            created = False
        else:
            # Créer nouvelle entrée
            weight_entry = WeightHistory(
                user_id=user_id,
                weight=weight,
                body_fat_percentage=data.get('body_fat_percentage'),
                muscle_mass_percentage=data.get('muscle_mass_percentage'),
                water_percentage=data.get('water_percentage'),
                recorded_date=recorded_date,
                measurement_time=datetime.fromisoformat(data['measurement_time']).time() if data.get('measurement_time') else None,
                notes=data.get('notes'),
                measurement_method=data.get('measurement_method', 'manual'),
                data_source=data.get('data_source', 'mobile_app')
            )
            db.session.add(weight_entry)
            created = True
        
        # Mettre à jour le poids actuel de l'utilisateur si c'est la pesée la plus récente
        if recorded_date >= date.today():
            user.current_weight = weight
            if data.get('body_fat_percentage'):
                user.body_fat_percentage = data.get('body_fat_percentage')
            if data.get('muscle_mass_percentage'):
                user.muscle_mass_percentage = data.get('muscle_mass_percentage')
            if data.get('water_percentage'):
                user.water_percentage = data.get('water_percentage')
            
            # Invalider le cache nutritionnel pour forcer le recalcul
            user.invalidate_cache()
        
        db.session.commit()
        
        logger.info(f"Pesée {'mise à jour' if not created else 'ajoutée'} pour utilisateur {user_id}: {weight}kg le {recorded_date}")
        
        return jsonify({
            'weight_entry': weight_entry.to_dict(),
            'created': created,
            'message': f'Pesée {"mise à jour" if not created else "enregistrée"} avec succès'
        }), 201 if created else 200
        
    except Exception as e:
        logger.error(f"Erreur ajout pesée utilisateur {user_id}: {e}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@user_bp.route('/users/<int:user_id>/weight-history/<int:entry_id>', methods=['DELETE'])
def delete_weight_entry(user_id, entry_id):
    """Supprime une pesée de l'historique"""
    try:
        weight_entry = WeightHistory.query.filter(
            WeightHistory.id == entry_id,
            WeightHistory.user_id == user_id
        ).first_or_404()
        
        db.session.delete(weight_entry)
        db.session.commit()
        
        logger.info(f"Pesée {entry_id} supprimée pour utilisateur {user_id}")
        return jsonify({'message': 'Pesée supprimée avec succès'}), 200
        
    except Exception as e:
        logger.error(f"Erreur suppression pesée {entry_id} utilisateur {user_id}: {e}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@user_bp.route('/users/<int:user_id>/nutrition-profile', methods=['GET'])
def get_nutrition_profile(user_id):
    """Récupère uniquement le profil nutritionnel calculé"""
    try:
        user = User.query.get_or_404(user_id)
        
        # Paramètres optionnels
        goal_type = request.args.get('goal_type')
        force_recalculate = request.args.get('force_recalculate', 'false').lower() == 'true'
        
        # Calcul du profil nutritionnel
        nutrition_profile = nutrition_calculator.calculate_nutrition_profile(
            user, 
            goal_type=goal_type,
            force_recalculate=force_recalculate
        )
        
        # Ajouter des informations contextuelles
        response_data = nutrition_profile.to_dict()
        response_data['user_info'] = {
            'id': user.id,
            'username': user.username,
            'current_weight': user.current_weight,
            'target_weight': user.target_weight,
            'bmi': user.bmi,
            'bmi_category': user.bmi_category
        }
        
        # Niveaux d'activité et types d'objectifs disponibles
        response_data['available_options'] = {
            'activity_levels': nutrition_calculator.get_activity_levels(),
            'goal_types': nutrition_calculator.get_goal_types()
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Erreur récupération profil nutritionnel utilisateur {user_id}: {e}")
        return jsonify({'error': str(e)}), 500


@user_bp.route('/users/<int:user_id>/nutrition-validation', methods=['POST'])
def validate_nutrition_goals(user_id):
    """Valide les objectifs nutritionnels d'un utilisateur"""
    try:
        user = User.query.get_or_404(user_id)
        
        validation_result = nutrition_calculator.validate_nutrition_goals(user)
        
        return jsonify(validation_result)
        
    except Exception as e:
        logger.error(f"Erreur validation objectifs nutritionnels utilisateur {user_id}: {e}")
        return jsonify({'error': str(e)}), 500


@user_bp.route('/users/<int:user_id>/goals', methods=['GET'])
def get_user_goals(user_id):
    """Récupère l'historique des objectifs d'un utilisateur"""
    try:
        status_filter = request.args.get('status', 'all')
        limit = request.args.get('limit', 50, type=int)
        
        query = UserGoalsHistory.query.filter(UserGoalsHistory.user_id == user_id)
        
        if status_filter != 'all':
            query = query.filter(UserGoalsHistory.status == status_filter)
        
        goals = query.order_by(UserGoalsHistory.start_date.desc()).limit(limit).all()
        
        return jsonify({
            'goals': [goal.to_dict() for goal in goals],
            'count': len(goals),
            'status_filter': status_filter
        })
        
    except Exception as e:
        logger.error(f"Erreur récupération objectifs utilisateur {user_id}: {e}")
        return jsonify({'error': str(e)}), 500


@user_bp.route('/users/<int:user_id>/goals', methods=['POST'])
def create_user_goal(user_id):
    """Crée un nouvel objectif pour l'utilisateur"""
    try:
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        
        # Validation des données requises
        if 'goal_type' not in data:
            return jsonify({'error': 'Le type d\'objectif est requis'}), 400
        
        # Désactiver les objectifs actifs du même type
        existing_goals = UserGoalsHistory.query.filter(
            UserGoalsHistory.user_id == user_id,
            UserGoalsHistory.goal_type == data['goal_type'],
            UserGoalsHistory.status == 'active'
        ).all()
        
        for goal in existing_goals:
            goal.status = 'replaced'
            goal.end_date = date.today()
        
        # Créer le nouvel objectif
        new_goal = UserGoalsHistory(
            user_id=user_id,
            goal_type=data['goal_type'],
            target_value=data.get('target_value'),
            target_date=datetime.fromisoformat(data['target_date']).date() if data.get('target_date') else None,
            start_date=date.today(),
            status='active',
            notes=data.get('notes')
        )
        
        db.session.add(new_goal)
        db.session.commit()
        
        logger.info(f"Nouvel objectif {data['goal_type']} créé pour utilisateur {user_id}")
        return jsonify(new_goal.to_dict()), 201
        
    except Exception as e:
        logger.error(f"Erreur création objectif utilisateur {user_id}: {e}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ===== ROUTES POUR LES MESURES COMPLÈTES =====

@user_bp.route('/users/<int:user_id>/measurements', methods=['GET'])
def get_user_measurements(user_id):
    """Récupère toutes les mesures de l'utilisateur"""
    try:
        # Paramètres de requête
        limit = request.args.get('limit', 100, type=int)  # Augmenté à 100
        days = request.args.get('days', 365, type=int)  # Augmenté à 365 jours par défaut
        
        # Récupérer TOUTES les mesures si days est très grand
        if days >= 365:
            # Récupérer toutes les mesures sans limite de date
            measurements = UserMeasurement.query.filter(
                UserMeasurement.user_id == user_id
            ).order_by(UserMeasurement.date.desc()).limit(limit).all()
        else:
            # Récupérer les mesures des X derniers jours
            from datetime import date, timedelta
            cutoff_date = date.today() - timedelta(days=days)
            measurements = UserMeasurement.query.filter(
                UserMeasurement.user_id == user_id,
                UserMeasurement.date >= cutoff_date
            ).order_by(UserMeasurement.date.desc()).limit(limit).all()
        
        # Retourner les données
        return jsonify([
            measurement.to_dict() for measurement in measurements
        ])
        
    except Exception as e:
        logger.error(f"Erreur récupération mesures utilisateur {user_id}: {e}")
        return jsonify({'error': str(e)}), 500


@user_bp.route('/users/<int:user_id>/measurements', methods=['POST'])
def add_user_measurement(user_id):
    """Ajoute une nouvelle mesure pour l'utilisateur"""
    try:
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        
        # Date de la mesure
        measurement_date = date.today()
        if 'date' in data and data['date']:
            try:
                measurement_date = datetime.fromisoformat(data['date']).date()
            except ValueError:
                return jsonify({'error': 'Format de date invalide'}), 400
        
        # Vérifier si une mesure existe déjà pour cette date
        existing = UserMeasurement.query.filter(
            UserMeasurement.user_id == user_id,
            UserMeasurement.date == measurement_date
        ).first()
        
        if existing:
            # Mettre à jour la mesure existante
            for key, value in data.items():
                if key != 'date' and hasattr(existing, key):
                    setattr(existing, key, value)
            existing.updated_at = datetime.utcnow()
            measurement = existing
            created = False
        else:
            # Créer une nouvelle mesure
            measurement = UserMeasurement(
                user_id=user_id,
                date=measurement_date,
                data_source='mobile_app',
                is_verified=True
            )
            
            # Ajouter tous les champs fournis
            for key, value in data.items():
                if key != 'date' and hasattr(measurement, key):
                    setattr(measurement, key, value)
            
            db.session.add(measurement)
            created = True
        
        # Si le poids est fourni et que c'est la mesure du jour, mettre à jour le profil
        if 'weight' in data and measurement_date == date.today():
            user.current_weight = data['weight']
            
            # Ajouter aussi à l'historique de poids
            weight_entry = WeightHistory.query.filter(
                WeightHistory.user_id == user_id,
                WeightHistory.recorded_date == measurement_date
            ).first()
            
            if weight_entry:
                weight_entry.weight = data['weight']
                weight_entry.body_fat_percentage = data.get('body_fat')
                weight_entry.muscle_mass_percentage = data.get('muscle_mass')
                weight_entry.water_percentage = data.get('water_percentage')
                weight_entry.updated_at = datetime.utcnow()
            else:
                weight_entry = WeightHistory(
                    user_id=user_id,
                    weight=data['weight'],
                    body_fat_percentage=data.get('body_fat'),
                    muscle_mass_percentage=data.get('muscle_mass'),
                    water_percentage=data.get('water_percentage'),
                    recorded_date=measurement_date,
                    notes="Enregistré via la page Mesures",
                    measurement_method="manual",
                    data_source="measurements_page"
                )
                db.session.add(weight_entry)
        
        db.session.commit()
        
        logger.info(f"Mesure {'mise à jour' if not created else 'ajoutée'} pour utilisateur {user_id} le {measurement_date}")
        
        return jsonify({
            'measurement': measurement.to_dict(),
            'created': created,
            'message': f'Mesure {"mise à jour" if not created else "enregistrée"} avec succès'
        }), 201 if created else 200
        
    except Exception as e:
        logger.error(f"Erreur ajout mesure utilisateur {user_id}: {e}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@user_bp.route('/users/<int:user_id>/measurements/<measurement_date>', methods=['GET'])
def get_measurement_by_date(user_id, measurement_date):
    """Récupère une mesure spécifique par date"""
    try:
        # Parser la date
        try:
            date_obj = datetime.fromisoformat(measurement_date).date()
        except ValueError:
            return jsonify({'error': 'Format de date invalide'}), 400
        
        # Récupérer la mesure
        measurement = UserMeasurement.query.filter(
            UserMeasurement.user_id == user_id,
            UserMeasurement.date == date_obj
        ).first()
        
        if not measurement:
            return jsonify({'error': 'Mesure non trouvée'}), 404
        
        return jsonify(measurement.to_dict())
        
    except Exception as e:
        logger.error(f"Erreur récupération mesure utilisateur {user_id} date {measurement_date}: {e}")
        return jsonify({'error': str(e)}), 500


@user_bp.route('/users/<int:user_id>/measurements/<measurement_date>', methods=['DELETE'])
def delete_measurement(user_id, measurement_date):
    """Supprime une mesure spécifique"""
    try:
        # Parser la date
        try:
            date_obj = datetime.fromisoformat(measurement_date).date()
        except ValueError:
            return jsonify({'error': 'Format de date invalide'}), 400
        
        # Récupérer et supprimer la mesure
        measurement = UserMeasurement.query.filter(
            UserMeasurement.user_id == user_id,
            UserMeasurement.date == date_obj
        ).first()
        
        if not measurement:
            return jsonify({'error': 'Mesure non trouvée'}), 404
        
        db.session.delete(measurement)
        db.session.commit()
        
        logger.info(f"Mesure supprimée pour utilisateur {user_id} date {measurement_date}")
        return jsonify({'message': 'Mesure supprimée avec succès'}), 200
        
    except Exception as e:
        logger.error(f"Erreur suppression mesure utilisateur {user_id} date {measurement_date}: {e}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500