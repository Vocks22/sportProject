from flask import Blueprint, request, jsonify
from database import db
from models.recipe import Recipe
from models.ingredient import Ingredient

recipes_bp = Blueprint('recipes', __name__)

@recipes_bp.route('/recipes', methods=['GET'])
def get_recipes():
    """Récupérer toutes les recettes avec filtres optionnels"""
    try:
        # Paramètres de filtrage
        category = request.args.get('category')
        meal_type = request.args.get('meal_type')
        search = request.args.get('search')
        max_calories = request.args.get('max_calories', type=float)
        max_time = request.args.get('max_time', type=int)
        
        # Construction de la requête
        query = Recipe.query
        
        if category:
            query = query.filter(Recipe.category == category)
        if meal_type:
            query = query.filter(Recipe.meal_type == meal_type)
        if search:
            query = query.filter(Recipe.name.contains(search))
        if max_calories:
            query = query.filter(Recipe.total_calories <= max_calories)
        if max_time:
            query = query.filter((Recipe.prep_time + Recipe.cook_time) <= max_time)
        
        recipes = query.all()
        return jsonify([recipe.to_dict() for recipe in recipes])
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@recipes_bp.route('/recipes/<int:recipe_id>', methods=['GET'])
def get_recipe(recipe_id):
    """Récupérer une recette spécifique"""
    try:
        recipe = Recipe.query.get_or_404(recipe_id)
        return jsonify(recipe.to_dict())
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@recipes_bp.route('/recipes', methods=['POST'])
def create_recipe():
    """Créer une nouvelle recette"""
    try:
        data = request.get_json()
        
        # Validation des données requises
        required_fields = ['name', 'category', 'meal_type', 'ingredients', 'instructions']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Champ requis manquant: {field}'}), 400
        
        # Calcul des valeurs nutritionnelles
        nutrition = calculate_recipe_nutrition(data['ingredients'])
        data['nutrition_total'] = nutrition
        
        recipe = Recipe.create_from_dict(data)
        db.session.add(recipe)
        db.session.commit()
        
        return jsonify(recipe.to_dict()), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@recipes_bp.route('/recipes/<int:recipe_id>', methods=['PUT'])
def update_recipe(recipe_id):
    """Mettre à jour une recette"""
    try:
        recipe = Recipe.query.get_or_404(recipe_id)
        data = request.get_json()
        
        # Mise à jour des champs
        if 'name' in data:
            recipe.name = data['name']
        if 'category' in data:
            recipe.category = data['category']
        if 'meal_type' in data:
            recipe.meal_type = data['meal_type']
        if 'ingredients' in data:
            recipe.ingredients = data['ingredients']
            # Recalculer la nutrition
            nutrition = calculate_recipe_nutrition(data['ingredients'])
            recipe.total_calories = nutrition['calories']
            recipe.total_protein = nutrition['protein']
            recipe.total_carbs = nutrition['carbs']
            recipe.total_fat = nutrition['fat']
        if 'instructions' in data:
            recipe.instructions = data['instructions']
        if 'prep_time' in data:
            recipe.prep_time = data['prep_time']
        if 'cook_time' in data:
            recipe.cook_time = data['cook_time']
        if 'servings' in data:
            recipe.servings = data['servings']
        if 'utensils' in data:
            recipe.utensils = data['utensils']
        if 'tags' in data:
            recipe.tags = data['tags']
        if 'rating' in data:
            recipe.rating = data['rating']
        if 'is_favorite' in data:
            recipe.is_favorite = data['is_favorite']
        
        db.session.commit()
        return jsonify(recipe.to_dict())
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@recipes_bp.route('/recipes/<int:recipe_id>', methods=['DELETE'])
def delete_recipe(recipe_id):
    """Supprimer une recette"""
    try:
        recipe = Recipe.query.get_or_404(recipe_id)
        db.session.delete(recipe)
        db.session.commit()
        
        return jsonify({'message': 'Recette supprimée avec succès'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@recipes_bp.route('/recipes/<int:recipe_id>/favorite', methods=['POST'])
def toggle_favorite(recipe_id):
    """Basculer le statut favori d'une recette"""
    try:
        recipe = Recipe.query.get_or_404(recipe_id)
        recipe.is_favorite = not recipe.is_favorite
        db.session.commit()
        
        return jsonify({
            'message': 'Statut favori mis à jour',
            'is_favorite': recipe.is_favorite
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

def calculate_recipe_nutrition(ingredients_list):
    """Calculer les valeurs nutritionnelles d'une recette"""
    total_calories = 0
    total_protein = 0
    total_carbs = 0
    total_fat = 0
    
    for ingredient_data in ingredients_list:
        ingredient_id = ingredient_data.get('ingredient_id')
        quantity = ingredient_data.get('quantity', 0)
        
        if ingredient_id:
            ingredient = Ingredient.query.get(ingredient_id)
            if ingredient:
                # Calcul basé sur la quantité (supposée en grammes)
                factor = quantity / 100.0
                total_calories += ingredient.calories_per_100g * factor
                total_protein += ingredient.protein_per_100g * factor
                total_carbs += ingredient.carbs_per_100g * factor
                total_fat += ingredient.fat_per_100g * factor
    
    return {
        'calories': round(total_calories, 1),
        'protein': round(total_protein, 1),
        'carbs': round(total_carbs, 1),
        'fat': round(total_fat, 1)
    }

