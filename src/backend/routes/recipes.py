from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from sqlalchemy import or_, asc, desc
from database import db
from models.recipe import Recipe
from models.ingredient import Ingredient
from schemas.recipe import (
    recipe_schema, recipes_schema, recipe_update_schema, 
    recipe_query_schema
)

recipes_bp = Blueprint('recipes', __name__)

@recipes_bp.route('/recipes', methods=['GET'])
def get_recipes():
    """Récupérer toutes les recettes avec filtres optionnels et pagination"""
    try:
        # Validation des paramètres de requête
        try:
            args = recipe_query_schema.load(request.args)
        except ValidationError as err:
            return jsonify({'error': 'Paramètres de requête invalides', 'messages': err.messages}), 400
        
        # Construction de la requête de base
        query = Recipe.query
        
        # Filtres
        if args.get('category'):
            query = query.filter(Recipe.category == args['category'])
        if args.get('meal_type'):
            query = query.filter(Recipe.meal_type == args['meal_type'])
        if args.get('search'):
            search_term = f"%{args['search']}%"
            query = query.filter(Recipe.name.ilike(search_term))
        if args.get('max_calories'):
            query = query.filter(Recipe.total_calories <= args['max_calories'])
        if args.get('max_time'):
            query = query.filter((Recipe.prep_time + Recipe.cook_time) <= args['max_time'])
        if args.get('is_favorite') is not None:
            query = query.filter(Recipe.is_favorite == args['is_favorite'])
        if args.get('tags'):
            # Filtrer par tags (recherche partielle dans le JSON)
            tags = [tag.strip() for tag in args['tags'].split(',')]
            for tag in tags:
                query = query.filter(Recipe.tags_json.contains(tag))
        if args.get('difficulty_level'):
            query = query.filter(Recipe.difficulty_level == args['difficulty_level'])
        if args.get('has_chef_mode') is not None:
            query = query.filter(Recipe.has_chef_mode == args['has_chef_mode'])
        
        # Tri
        sort_field = getattr(Recipe, args.get('sort_by', 'created_at'))
        if args.get('order', 'desc') == 'desc':
            query = query.order_by(desc(sort_field))
        else:
            query = query.order_by(asc(sort_field))
        
        # Pagination
        page = args.get('page', 1)
        per_page = args.get('per_page', 20)
        
        paginated_recipes = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        # Sérialisation des résultats
        recipes_data = recipes_schema.dump(paginated_recipes.items)
        
        return jsonify({
            'recipes': recipes_data,
            'pagination': {
                'page': paginated_recipes.page,
                'per_page': paginated_recipes.per_page,
                'total': paginated_recipes.total,
                'pages': paginated_recipes.pages,
                'has_prev': paginated_recipes.has_prev,
                'has_next': paginated_recipes.has_next,
                'prev_num': paginated_recipes.prev_num,
                'next_num': paginated_recipes.next_num
            }
        })
    
    except Exception as e:
        return jsonify({'error': 'Erreur interne du serveur', 'message': str(e)}), 500

@recipes_bp.route('/recipes/<int:recipe_id>', methods=['GET'])
def get_recipe(recipe_id):
    """Récupérer une recette spécifique"""
    try:
        recipe = Recipe.query.get(recipe_id)
        if not recipe:
            return jsonify({'error': 'Recette non trouvée'}), 404
        
        return jsonify(recipe_schema.dump(recipe))
    
    except Exception as e:
        return jsonify({'error': 'Erreur interne du serveur', 'message': str(e)}), 500

@recipes_bp.route('/recipes', methods=['POST'])
def create_recipe():
    """Créer une nouvelle recette"""
    try:
        # Vérification du Content-Type
        if not request.is_json:
            return jsonify({'error': 'Content-Type doit être application/json'}), 400
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Données JSON requises'}), 400
        
        # Validation avec Marshmallow
        try:
            validated_data = recipe_schema.load(data)
        except ValidationError as err:
            return jsonify({'error': 'Données invalides', 'messages': err.messages}), 400
        
        # Calcul des valeurs nutritionnelles
        nutrition = calculate_recipe_nutrition(validated_data['ingredients'])
        validated_data['nutrition_total'] = nutrition
        
        # Création de la recette
        recipe = Recipe.create_from_dict(validated_data)
        db.session.add(recipe)
        db.session.commit()
        
        return jsonify(recipe_schema.dump(recipe)), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erreur interne du serveur', 'message': str(e)}), 500

@recipes_bp.route('/recipes/<int:recipe_id>', methods=['PUT'])
def update_recipe(recipe_id):
    """Mettre à jour une recette"""
    try:
        # Vérification du Content-Type
        if not request.is_json:
            return jsonify({'error': 'Content-Type doit être application/json'}), 400
        
        recipe = Recipe.query.get(recipe_id)
        if not recipe:
            return jsonify({'error': 'Recette non trouvée'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Données JSON requises'}), 400
        
        # Validation avec le schéma de mise à jour
        try:
            validated_data = recipe_update_schema.load(data)
        except ValidationError as err:
            return jsonify({'error': 'Données invalides', 'messages': err.messages}), 400
        
        # Mise à jour des champs
        for field, value in validated_data.items():
            if field == 'ingredients':
                recipe.ingredients = value
                # Recalculer la nutrition si les ingrédients changent
                nutrition = calculate_recipe_nutrition(value)
                recipe.total_calories = nutrition['calories']
                recipe.total_protein = nutrition['protein']
                recipe.total_carbs = nutrition['carbs']
                recipe.total_fat = nutrition['fat']
            elif field == 'instructions':
                recipe.instructions = value
            elif field == 'utensils':
                recipe.utensils = value
            elif field == 'tags':
                recipe.tags = value
            # Gestion des champs de conseils de chef (US1.4)
            elif field == 'chef_instructions':
                recipe.chef_instructions = value
            elif field == 'cooking_steps':
                recipe.cooking_steps = value
            elif field == 'chef_tips':
                recipe.chef_tips = value
            elif field == 'visual_cues':
                recipe.visual_cues = value
            elif field == 'timing_details':
                recipe.timing_details = value
            elif field == 'media_references':
                recipe.media_references = value
            else:
                setattr(recipe, field, value)
        
        db.session.commit()
        return jsonify(recipe_schema.dump(recipe))
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erreur interne du serveur', 'message': str(e)}), 500

@recipes_bp.route('/recipes/<int:recipe_id>', methods=['DELETE'])
def delete_recipe(recipe_id):
    """Supprimer une recette"""
    try:
        recipe = Recipe.query.get(recipe_id)
        if not recipe:
            return jsonify({'error': 'Recette non trouvée'}), 404
        
        db.session.delete(recipe)
        db.session.commit()
        
        return jsonify({'message': 'Recette supprimée avec succès'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erreur interne du serveur', 'message': str(e)}), 500

@recipes_bp.route('/recipes/<int:recipe_id>/favorite', methods=['POST'])
def toggle_favorite(recipe_id):
    """Basculer le statut favori d'une recette"""
    try:
        recipe = Recipe.query.get(recipe_id)
        if not recipe:
            return jsonify({'error': 'Recette non trouvée'}), 404
        
        recipe.is_favorite = not recipe.is_favorite
        db.session.commit()
        
        return jsonify({
            'message': 'Statut favori mis à jour',
            'is_favorite': recipe.is_favorite,
            'recipe_id': recipe.id
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erreur interne du serveur', 'message': str(e)}), 500

@recipes_bp.route('/recipes/<int:recipe_id>/cooking-guide', methods=['GET'])
def get_cooking_guide(recipe_id):
    """Récupérer le guide de cuisson détaillé d'une recette"""
    try:
        recipe = Recipe.query.get(recipe_id)
        if not recipe:
            return jsonify({'error': 'Recette non trouvée'}), 404
        
        if not recipe.has_chef_mode:
            return jsonify({'error': 'Cette recette n\'a pas de mode chef disponible'}), 404
        
        # Enrichir les ingrédients avec leurs noms
        enriched_ingredients = []
        for ing_data in recipe.ingredients:
            ingredient_info = dict(ing_data)  # Copier les données existantes
            ingredient_id = ing_data.get('ingredient_id')
            
            if ingredient_id:
                ingredient = Ingredient.query.get(ingredient_id)
                if ingredient:
                    ingredient_info['name'] = ingredient.name
                else:
                    ingredient_info['name'] = 'Ingrédient inconnu'
            else:
                ingredient_info['name'] = 'Ingrédient non spécifié'
            
            enriched_ingredients.append(ingredient_info)
        
        # Retourner uniquement les données nécessaires pour le mode cuisson
        cooking_guide = {
            'recipe_id': recipe.id,
            'recipe_name': recipe.name,
            'difficulty_level': recipe.difficulty_level,
            'prep_time': recipe.prep_time,
            'cook_time': recipe.cook_time,
            'servings': recipe.servings,
            'ingredients': enriched_ingredients,
            'utensils': recipe.utensils,
            'chef_instructions': recipe.chef_instructions,
            'cooking_steps': recipe.cooking_steps,
            'chef_tips': recipe.chef_tips,
            'visual_cues': recipe.visual_cues,
            'timing_details': recipe.timing_details,
            'media_references': recipe.media_references
        }
        
        return jsonify(cooking_guide)
    
    except Exception as e:
        return jsonify({'error': 'Erreur interne du serveur', 'message': str(e)}), 500

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

