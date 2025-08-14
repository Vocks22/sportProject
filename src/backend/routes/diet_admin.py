"""
Routes d'administration pour la gestion des repas de la diète
"""
from flask import Blueprint, jsonify, request
from database import db
from models.diet_program import DietProgram
from datetime import datetime

diet_admin_bp = Blueprint('diet_admin', __name__)

@diet_admin_bp.route('/diet/admin/meals', methods=['GET'])
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