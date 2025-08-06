from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.ingredient import Ingredient

ingredients_bp = Blueprint('ingredients', __name__)

@ingredients_bp.route('/ingredients', methods=['GET'])
def get_ingredients():
    """Récupérer tous les ingrédients avec filtres optionnels"""
    try:
        # Paramètres de filtrage
        category = request.args.get('category')
        search = request.args.get('search')
        
        # Construction de la requête
        query = Ingredient.query
        
        if category:
            query = query.filter(Ingredient.category == category)
        if search:
            query = query.filter(Ingredient.name.contains(search))
        
        ingredients = query.order_by(Ingredient.name).all()
        return jsonify([ingredient.to_dict() for ingredient in ingredients])
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ingredients_bp.route('/ingredients/<int:ingredient_id>', methods=['GET'])
def get_ingredient(ingredient_id):
    """Récupérer un ingrédient spécifique"""
    try:
        ingredient = Ingredient.query.get_or_404(ingredient_id)
        return jsonify(ingredient.to_dict())
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ingredients_bp.route('/ingredients', methods=['POST'])
def create_ingredient():
    """Créer un nouvel ingrédient"""
    try:
        data = request.get_json()
        
        # Validation des données requises
        required_fields = ['name', 'category', 'nutrition_per_100g']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Champ requis manquant: {field}'}), 400
        
        # Vérifier que l'ingrédient n'existe pas déjà
        existing = Ingredient.query.filter_by(name=data['name']).first()
        if existing:
            return jsonify({'error': 'Un ingrédient avec ce nom existe déjà'}), 400
        
        ingredient = Ingredient.create_from_dict(data)
        db.session.add(ingredient)
        db.session.commit()
        
        return jsonify(ingredient.to_dict()), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@ingredients_bp.route('/ingredients/<int:ingredient_id>', methods=['PUT'])
def update_ingredient(ingredient_id):
    """Mettre à jour un ingrédient"""
    try:
        ingredient = Ingredient.query.get_or_404(ingredient_id)
        data = request.get_json()
        
        # Mise à jour des champs
        if 'name' in data:
            ingredient.name = data['name']
        if 'category' in data:
            ingredient.category = data['category']
        if 'unit' in data:
            ingredient.unit = data['unit']
        
        # Mise à jour des valeurs nutritionnelles
        if 'nutrition_per_100g' in data:
            nutrition = data['nutrition_per_100g']
            ingredient.calories_per_100g = nutrition.get('calories', ingredient.calories_per_100g)
            ingredient.protein_per_100g = nutrition.get('protein', ingredient.protein_per_100g)
            ingredient.carbs_per_100g = nutrition.get('carbs', ingredient.carbs_per_100g)
            ingredient.fat_per_100g = nutrition.get('fat', ingredient.fat_per_100g)
        
        db.session.commit()
        return jsonify(ingredient.to_dict())
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@ingredients_bp.route('/ingredients/<int:ingredient_id>', methods=['DELETE'])
def delete_ingredient(ingredient_id):
    """Supprimer un ingrédient"""
    try:
        ingredient = Ingredient.query.get_or_404(ingredient_id)
        db.session.delete(ingredient)
        db.session.commit()
        
        return jsonify({'message': 'Ingrédient supprimé avec succès'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@ingredients_bp.route('/ingredients/categories', methods=['GET'])
def get_categories():
    """Récupérer toutes les catégories d'ingrédients"""
    try:
        categories = db.session.query(Ingredient.category).distinct().all()
        return jsonify([cat[0] for cat in categories])
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ingredients_bp.route('/ingredients/bulk', methods=['POST'])
def create_bulk_ingredients():
    """Créer plusieurs ingrédients en une fois"""
    try:
        data = request.get_json()
        ingredients_data = data.get('ingredients', [])
        
        created_ingredients = []
        
        for ingredient_data in ingredients_data:
            # Vérifier que l'ingrédient n'existe pas déjà
            existing = Ingredient.query.filter_by(name=ingredient_data['name']).first()
            if not existing:
                ingredient = Ingredient.create_from_dict(ingredient_data)
                db.session.add(ingredient)
                created_ingredients.append(ingredient)
        
        db.session.commit()
        
        return jsonify({
            'message': f'{len(created_ingredients)} ingrédients créés avec succès',
            'ingredients': [ing.to_dict() for ing in created_ingredients]
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

