"""
Routes d'administration pour la gestion des repas de la diète
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from database import db
from models.diet_program import DietProgram, DietTracking, DietStreak
from models.recipe import Recipe
from models.ingredient import Ingredient
from datetime import datetime
import os
import requests

diet_admin_bp = Blueprint('diet_admin', __name__)

@diet_admin_bp.route('/admin/database-info', methods=['GET'])
@jwt_required()
def get_database_info():
    """Affiche toutes les informations de la base de données pour debug"""
    try:
        # Récupérer tous les repas du programme
        meals = DietProgram.query.order_by(DietProgram.order_index).all()
        meals_data = []
        for meal in meals:
            meals_data.append({
                'id': meal.id,
                'meal_type': meal.meal_type,
                'meal_name': meal.meal_name,
                'time_slot': meal.time_slot,
                'order_index': meal.order_index,
                'foods': meal.foods
            })
        
        # Récupérer les derniers trackings
        recent_trackings = DietTracking.query.order_by(DietTracking.date.desc()).limit(20).all()
        trackings_data = []
        for tracking in recent_trackings:
            trackings_data.append({
                'id': tracking.id,
                'date': tracking.date.isoformat(),
                'meal_id': tracking.meal_id,
                'meal_type': tracking.meal.meal_type if tracking.meal else 'N/A',
                'meal_name': tracking.meal.meal_name if tracking.meal else 'N/A',
                'completed': tracking.completed,
                'completed_at': tracking.completed_at.isoformat() if tracking.completed_at else None
            })
        
        # Récupérer les stats
        stats = DietStreak.query.first()
        stats_data = None
        if stats:
            stats_data = {
                'current_streak': stats.current_streak,
                'longest_streak': stats.longest_streak,
                'total_days_tracked': stats.total_days_tracked,
                'total_meals_completed': stats.total_meals_completed,
                'last_tracked_date': stats.last_tracked_date.isoformat() if stats.last_tracked_date else None
            }
        
        # Compter les recettes
        recipes_count = Recipe.query.count()
        
        # Compter les ingrédients  
        ingredients_count = Ingredient.query.count()
        
        return jsonify({
            'success': True,
            'database_info': {
                'diet_program': {
                    'count': len(meals_data),
                    'meals': meals_data
                },
                'recent_trackings': {
                    'count': len(trackings_data),
                    'trackings': trackings_data
                },
                'stats': stats_data,
                'recipes_count': recipes_count,
                'ingredients_count': ingredients_count,
                'server_time': datetime.now().isoformat()
            }
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@diet_admin_bp.route('/diet/admin/meals', methods=['GET'])
@jwt_required()
def get_all_meals():
    """Récupérer tous les repas configurés"""
    try:
        meals = DietProgram.query.order_by(DietProgram.order_index).all()
        return jsonify({
            'success': True,
            'meals': [meal.to_dict() for meal in meals],
            'count': len(meals)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@diet_admin_bp.route('/diet/admin/meals', methods=['POST'])
@jwt_required()
def create_meal():
    """Créer un nouveau repas"""
    try:
        data = request.json
        
        # Vérifier si le meal_type existe déjà
        existing = DietProgram.query.filter_by(meal_type=data.get('meal_type')).first()
        if existing:
            return jsonify({'success': False, 'error': 'Ce type de repas existe déjà'}), 400
        
        meal = DietProgram(
            meal_type=data.get('meal_type'),
            meal_name=data.get('meal_name'),
            time_slot=data.get('time_slot'),
            order_index=data.get('order_index', 1),
            foods=data.get('foods', [])
        )
        
        db.session.add(meal)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'meal': meal.to_dict(),
            'message': 'Repas créé avec succès'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@diet_admin_bp.route('/diet/admin/meals/<int:meal_id>', methods=['PUT'])
@jwt_required()
def update_meal(meal_id):
    """Modifier un repas existant"""
    try:
        meal = DietProgram.query.get_or_404(meal_id)
        data = request.json
        
        meal.meal_name = data.get('meal_name', meal.meal_name)
        meal.time_slot = data.get('time_slot', meal.time_slot)
        meal.order_index = data.get('order_index', meal.order_index)
        meal.foods = data.get('foods', meal.foods)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'meal': meal.to_dict(),
            'message': 'Repas modifié avec succès'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@diet_admin_bp.route('/diet/admin/meals/<int:meal_id>', methods=['DELETE'])
@jwt_required()
def delete_meal(meal_id):
    """Supprimer un repas"""
    try:
        meal = DietProgram.query.get_or_404(meal_id)
        
        # Supprimer d'abord toutes les entrées de suivi liées à ce repas
        from models.diet_program import DietTracking
        DietTracking.query.filter_by(meal_id=meal_id).delete()
        
        # Ensuite supprimer le repas lui-même
        db.session.delete(meal)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Repas et données de suivi associées supprimés avec succès'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@diet_admin_bp.route('/diet/admin/meals/init', methods=['POST'])
@jwt_required()
def init_default_meals():
    """Initialiser les 5 repas par défaut"""
    try:
        # Vérifier si des repas existent déjà
        if DietProgram.query.count() > 0:
            return jsonify({
                'success': False, 
                'error': 'Des repas existent déjà. Supprimez-les d\'abord.'
            }), 400
        
        default_meals = [
            {
                'meal_type': 'repas1',
                'meal_name': 'Petit-déjeuner',
                'time_slot': '7h00-9h00',
                'order_index': 1,
                'foods': []
            },
            {
                'meal_type': 'collation1',
                'meal_name': 'Collation matin',
                'time_slot': '10h00-11h00',
                'order_index': 2,
                'foods': []
            },
            {
                'meal_type': 'repas2',
                'meal_name': 'Déjeuner',
                'time_slot': '12h00-14h00',
                'order_index': 3,
                'foods': []
            },
            {
                'meal_type': 'collation2',
                'meal_name': 'Collation après-midi',
                'time_slot': '16h00-17h00',
                'order_index': 4,
                'foods': []
            },
            {
                'meal_type': 'repas3',
                'meal_name': 'Dîner',
                'time_slot': '19h00-21h00',
                'order_index': 5,
                'foods': []
            }
        ]
        
        for meal_data in default_meals:
            meal = DietProgram(**meal_data)
            db.session.add(meal)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '5 repas par défaut créés avec succès',
            'count': len(default_meals)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@diet_admin_bp.route('/diet/admin/meals/clear', methods=['DELETE'])
@jwt_required()
def clear_all_meals():
    """Supprimer tous les repas (DANGER!)"""
    try:
        # Demander une confirmation via un paramètre
        confirm = request.args.get('confirm', '').lower()
        if confirm != 'yes':
            return jsonify({
                'success': False,
                'error': 'Ajoutez ?confirm=yes pour confirmer la suppression'
            }), 400
        
        # Supprimer d'abord toutes les entrées de suivi
        from models.diet_program import DietTracking
        DietTracking.query.delete()
        
        # Compter et supprimer tous les repas
        count = DietProgram.query.count()
        DietProgram.query.delete()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'{count} repas supprimés',
            'count': count
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@diet_admin_bp.route('/diet/admin/meals/init-foods', methods=['POST'])
@jwt_required()
def init_default_foods():
    """Initialiser les aliments par défaut pour tous les repas"""
    try:
        # Définir les aliments pour chaque type de repas
        foods_by_type = {
            "repas1": [  # Petit-déjeuner
                {"name": "Blanc d'œuf", "quantity": "150", "unit": "g"},
                {"name": "Flocons d'avoine", "quantity": "80", "unit": "g"},
                {"name": "Myrtilles", "quantity": "100", "unit": "g"},
                {"name": "Amandes", "quantity": "20", "unit": "g"},
                {"name": "Banane", "quantity": "1", "unit": "unité"},
                {"name": "Miel", "quantity": "1", "unit": "c.à.s"}
            ],
            "collation1": [  # Collation matin
                {"name": "Shaker protéiné", "quantity": "30", "unit": "g"},
                {"name": "Pomme", "quantity": "1", "unit": "unité"},
                {"name": "Noix", "quantity": "30", "unit": "g"},
                {"name": "Eau", "quantity": "500", "unit": "ml"}
            ],
            "repas2": [  # Déjeuner
                {"name": "Poulet grillé", "quantity": "200", "unit": "g"},
                {"name": "Riz basmati", "quantity": "150", "unit": "g cuit"},
                {"name": "Brocoli", "quantity": "200", "unit": "g"},
                {"name": "Huile d'olive", "quantity": "1", "unit": "c.à.s"},
                {"name": "Salade verte", "quantity": "100", "unit": "g"}
            ],
            "collation2": [  # Collation après-midi
                {"name": "Yaourt grec", "quantity": "150", "unit": "g"},
                {"name": "Fruits rouges", "quantity": "100", "unit": "g"},
                {"name": "Granola", "quantity": "30", "unit": "g"}
            ],
            "repas3": [  # Dîner
                {"name": "Saumon", "quantity": "180", "unit": "g"},
                {"name": "Patate douce", "quantity": "200", "unit": "g"},
                {"name": "Asperges", "quantity": "150", "unit": "g"},
                {"name": "Avocat", "quantity": "1/2", "unit": "unité"}
            ],
            "en_cas": []  # En-cas vide par défaut
        }
        
        # Récupérer tous les repas
        meals = DietProgram.query.all()
        if not meals:
            return jsonify({
                'success': False,
                'error': 'Aucun repas trouvé. Initialisez d\'abord les repas.'
            }), 400
        
        updated_count = 0
        updated_meals = []
        
        # Mettre à jour chaque repas avec ses aliments
        for meal in meals:
            meal_type = meal.meal_type
            if meal_type in foods_by_type:
                meal.foods = foods_by_type[meal_type]
                updated_count += 1
                updated_meals.append({
                    'name': meal.meal_name,
                    'foods_count': len(meal.foods)
                })
        
        # Sauvegarder les modifications
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'{updated_count} repas mis à jour avec leurs aliments',
            'updated_meals': updated_meals
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@diet_admin_bp.route('/diet/admin/meals/export', methods=['GET'])
@jwt_required()
def export_meals():
    """Exporter tous les repas avec leurs aliments"""
    try:
        meals = DietProgram.query.order_by(DietProgram.order_index).all()
        
        export_data = []
        for meal in meals:
            meal_data = {
                'meal_type': meal.meal_type,
                'meal_name': meal.meal_name,
                'time_slot': meal.time_slot,
                'order_index': meal.order_index,
                'foods': meal.foods if meal.foods else []
            }
            export_data.append(meal_data)
        
        return jsonify({
            'success': True,
            'data': export_data,
            'count': len(export_data)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@diet_admin_bp.route('/diet/admin/meals/sync-to-production', methods=['POST'])
@jwt_required()
def sync_to_production():
    """Synchroniser les repas de préprod vers production"""
    try:
        # Vérifier la clé de sécurité
        secret_key = request.json.get('secret_key')
        if secret_key != 'sync2024-diet-tracker':
            return jsonify({'success': False, 'error': 'Clé de sécurité invalide'}), 403
        
        # URL de production
        production_url = request.json.get('production_url', 'https://diettracker-backend.onrender.com')
        
        # Exporter les données locales
        meals = DietProgram.query.order_by(DietProgram.order_index).all()
        export_data = []
        for meal in meals:
            meal_data = {
                'meal_type': meal.meal_type,
                'meal_name': meal.meal_name,
                'time_slot': meal.time_slot,
                'order_index': meal.order_index,
                'foods': meal.foods if meal.foods else []
            }
            export_data.append(meal_data)
        
        # Envoyer vers production
        response = requests.post(
            f'{production_url}/api/diet/admin/meals/import-from-preprod',
            json={
                'secret_key': secret_key,
                'meals': export_data
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return jsonify({
                'success': True,
                'message': 'Synchronisation réussie',
                'details': result
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Erreur de synchronisation: {response.status_code}',
                'details': response.text
            }), 500
            
    except requests.exceptions.RequestException as e:
        return jsonify({
            'success': False,
            'error': f'Erreur de connexion: {str(e)}'
        }), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@diet_admin_bp.route('/diet/admin/meals/import-from-preprod', methods=['POST'])
@jwt_required()
def import_from_preprod():
    """Importer les repas depuis la préprod (endpoint production)"""
    try:
        # Vérifier la clé de sécurité
        secret_key = request.json.get('secret_key')
        if secret_key != 'sync2024-diet-tracker':
            return jsonify({'success': False, 'error': 'Clé de sécurité invalide'}), 403
        
        meals_data = request.json.get('meals', [])
        
        imported = 0
        updated = 0
        
        for meal_data in meals_data:
            # Chercher si le repas existe déjà
            existing = DietProgram.query.filter_by(meal_type=meal_data['meal_type']).first()
            
            if existing:
                # Mettre à jour le repas existant
                existing.meal_name = meal_data['meal_name']
                existing.time_slot = meal_data['time_slot']
                existing.order_index = meal_data['order_index']
                existing.foods = meal_data['foods']
                updated += 1
            else:
                # Créer un nouveau repas
                new_meal = DietProgram(
                    meal_type=meal_data['meal_type'],
                    meal_name=meal_data['meal_name'],
                    time_slot=meal_data['time_slot'],
                    order_index=meal_data['order_index'],
                    foods=meal_data['foods']
                )
                db.session.add(new_meal)
                imported += 1
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'imported': imported,
            'updated': updated,
            'total': len(meals_data)
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500