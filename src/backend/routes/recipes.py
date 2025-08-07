from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from sqlalchemy import or_, asc, desc
from database import db
from models.recipe import Recipe
from models.ingredient import Ingredient
from models.user import User
from schemas.recipe import (
    recipe_schema, recipes_schema, recipe_update_schema, 
    recipe_query_schema
)
from services.nutrition_calculator_service import nutrition_calculator
from services.portion_adjustment_service import portion_adjustment
import logging

logger = logging.getLogger(__name__)

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


# ===== ROUTES US1.7 : AJUSTEMENT AUTOMATIQUE DES PORTIONS =====

@recipes_bp.route('/recipes/<int:recipe_id>/adjust-for-user/<int:user_id>', methods=['GET'])
def get_recipe_adjusted_for_user(recipe_id, user_id):
    """Récupère une recette avec portions ajustées pour un utilisateur spécifique"""
    try:
        recipe = Recipe.query.get_or_404(recipe_id)
        user = User.query.get_or_404(user_id)
        
        # Paramètres optionnels
        meal_type = request.args.get('meal_type', 'main')
        force_recalculate = request.args.get('force_recalculate', 'false').lower() == 'true'
        
        # Calcul du profil nutritionnel si nécessaire
        nutrition_profile = nutrition_calculator.calculate_nutrition_profile(
            user, 
            force_recalculate=force_recalculate
        )
        
        # Ajustement de la recette
        adjustment = portion_adjustment.adjust_recipe_for_user(
            recipe=recipe,
            user=user,
            target_meal_type=meal_type,
            nutrition_profile=nutrition_profile
        )
        
        # Données de base de la recette
        recipe_data = recipe_schema.dump(recipe)
        
        # Ajouter les données d'ajustement
        recipe_data['portion_adjustment'] = {
            'original_servings': adjustment.original_servings,
            'adjusted_servings': adjustment.adjusted_servings,
            'multiplier': adjustment.multiplier,
            'rationale': adjustment.rationale,
            'adjusted_ingredients': adjustment.adjusted_ingredients,
            'adjusted_nutrition': adjustment.adjusted_nutrition,
            'nutrition_profile': adjustment.nutrition_profile
        }
        
        # Informations utilisateur contextuelles
        recipe_data['user_context'] = {
            'user_id': user.id,
            'username': user.username,
            'current_weight': user.current_weight,
            'target_weight': user.target_weight,
            'bmi': user.bmi,
            'bmi_category': user.bmi_category,
            'meal_type': meal_type
        }
        
        logger.info(f"Recette {recipe_id} ajustée pour utilisateur {user_id} avec multiplicateur {adjustment.multiplier}")
        
        return jsonify(recipe_data)
        
    except Exception as e:
        logger.error(f"Erreur ajustement recette {recipe_id} pour utilisateur {user_id}: {e}")
        return jsonify({'error': str(e)}), 500


@recipes_bp.route('/recipes/batch-adjust-for-user/<int:user_id>', methods=['POST'])
def batch_adjust_recipes_for_user(user_id):
    """Ajuste plusieurs recettes pour un utilisateur (pour plan de repas)"""
    try:
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        
        if not data or 'recipe_ids' not in data:
            return jsonify({'error': 'Liste des IDs de recettes requise'}), 400
        
        recipe_ids = data['recipe_ids']
        meal_distribution = data.get('meal_distribution', {})
        force_recalculate = data.get('force_recalculate', False)
        
        # Récupération des recettes
        recipes = Recipe.query.filter(Recipe.id.in_(recipe_ids)).all()
        
        if len(recipes) != len(recipe_ids):
            found_ids = [r.id for r in recipes]
            missing_ids = [rid for rid in recipe_ids if rid not in found_ids]
            return jsonify({
                'error': f'Recettes non trouvées: {missing_ids}'
            }), 404
        
        # Calcul du profil nutritionnel
        nutrition_profile = nutrition_calculator.calculate_nutrition_profile(
            user, 
            force_recalculate=force_recalculate
        )
        
        # Ajustement des portions pour toutes les recettes
        adjustments = portion_adjustment.adjust_meal_plan_portions(
            recipes=recipes,
            user=user,
            meal_distribution=meal_distribution
        )
        
        # Calcul des ajustements pour la liste de courses
        shopping_adjustments = portion_adjustment.calculate_shopping_list_adjustments(
            adjustments, recipes
        )
        
        # Analytics des ajustements
        analytics = portion_adjustment.get_adjustment_analytics(adjustments)
        
        # Préparation de la réponse
        result = {
            'user_info': {
                'id': user.id,
                'username': user.username,
                'nutrition_profile': nutrition_profile.to_dict()
            },
            'recipe_adjustments': {},
            'shopping_list_adjustments': shopping_adjustments,
            'adjustment_analytics': analytics,
            'meal_distribution': meal_distribution
        }
        
        # Détails par recette
        for recipe in recipes:
            if recipe.id in adjustments:
                adjustment = adjustments[recipe.id]
                recipe_data = recipe_schema.dump(recipe)
                
                recipe_data['portion_adjustment'] = {
                    'original_servings': adjustment.original_servings,
                    'adjusted_servings': adjustment.adjusted_servings,
                    'multiplier': adjustment.multiplier,
                    'rationale': adjustment.rationale,
                    'adjusted_ingredients': adjustment.adjusted_ingredients,
                    'adjusted_nutrition': adjustment.adjusted_nutrition
                }
                
                result['recipe_adjustments'][recipe.id] = recipe_data
        
        logger.info(f"Ajustement de {len(recipes)} recettes pour utilisateur {user_id}")
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Erreur ajustement batch recettes pour utilisateur {user_id}: {e}")
        return jsonify({'error': str(e)}), 500


@recipes_bp.route('/recipes/<int:recipe_id>/portion-calculator', methods=['POST'])
def calculate_recipe_portions(recipe_id):
    """Calcule les portions optimales pour une recette selon différents profils utilisateur"""
    try:
        recipe = Recipe.query.get_or_404(recipe_id)
        data = request.get_json()
        
        # Paramètres de calcul
        target_calories = data.get('target_calories', 2000)
        meal_type = data.get('meal_type', 'main')
        user_profiles = data.get('user_profiles', [])
        
        results = {
            'recipe_info': recipe_schema.dump(recipe),
            'calculations': []
        }
        
        # Calcul basé sur calories cibles si pas de profils utilisateur
        if not user_profiles:
            multiplier = portion_adjustment._calculate_portion_multiplier(
                recipe, 
                portion_adjustment._calculate_meal_target_calories(target_calories, meal_type),
                None  # Pas de profil nutritionnel
            )
            
            adjusted_servings = recipe.servings * multiplier
            adjusted_ingredients = portion_adjustment._adjust_recipe_ingredients(recipe, multiplier)
            adjusted_nutrition = portion_adjustment._calculate_adjusted_nutrition(recipe, multiplier)
            
            results['calculations'].append({
                'type': 'calorie_based',
                'target_calories': target_calories,
                'meal_type': meal_type,
                'multiplier': multiplier,
                'adjusted_servings': adjusted_servings,
                'adjusted_ingredients': adjusted_ingredients,
                'adjusted_nutrition': adjusted_nutrition
            })
        
        # Calculs pour chaque profil utilisateur
        for profile in user_profiles:
            user_id = profile.get('user_id')
            if not user_id:
                continue
                
            user = User.query.get(user_id)
            if not user:
                continue
            
            # Ajustement pour cet utilisateur
            adjustment = portion_adjustment.adjust_recipe_for_user(
                recipe=recipe,
                user=user,
                target_meal_type=profile.get('meal_type', meal_type)
            )
            
            results['calculations'].append({
                'type': 'user_based',
                'user_id': user.id,
                'username': user.username,
                'meal_type': profile.get('meal_type', meal_type),
                'multiplier': adjustment.multiplier,
                'adjusted_servings': adjustment.adjusted_servings,
                'adjusted_ingredients': adjustment.adjusted_ingredients,
                'adjusted_nutrition': adjustment.adjusted_nutrition,
                'rationale': adjustment.rationale
            })
        
        return jsonify(results)
        
    except Exception as e:
        logger.error(f"Erreur calcul portions recette {recipe_id}: {e}")
        return jsonify({'error': str(e)}), 500


@recipes_bp.route('/users/<int:user_id>/nutrition-adjusted-recipes', methods=['GET'])
def get_nutrition_adjusted_recipes(user_id):
    """Récupère des recettes recommandées avec portions ajustées pour un utilisateur"""
    try:
        user = User.query.get_or_404(user_id)
        
        # Paramètres de requête
        limit = request.args.get('limit', 10, type=int)
        meal_type = request.args.get('meal_type', 'main')
        category = request.args.get('category')
        max_prep_time = request.args.get('max_prep_time', type=int)
        
        # Construction de la requête
        query = Recipe.query
        
        if category:
            query = query.filter(Recipe.category == category)
        if max_prep_time:
            query = query.filter(Recipe.prep_time <= max_prep_time)
        
        # Récupération des recettes
        recipes = query.limit(limit * 2).all()  # Plus de recettes pour avoir du choix
        
        # Calcul du profil nutritionnel utilisateur
        nutrition_profile = nutrition_calculator.calculate_nutrition_profile(user)
        
        # Ajustement et scoring des recettes
        scored_recipes = []
        
        for recipe in recipes:
            try:
                # Ajustement de la recette
                adjustment = portion_adjustment.adjust_recipe_for_user(
                    recipe=recipe,
                    user=user,
                    target_meal_type=meal_type,
                    nutrition_profile=nutrition_profile
                )
                
                # Calcul d'un score de pertinence
                score = calculate_recipe_relevance_score(
                    recipe, user, adjustment, nutrition_profile, meal_type
                )
                
                recipe_data = recipe_schema.dump(recipe)
                recipe_data['portion_adjustment'] = {
                    'multiplier': adjustment.multiplier,
                    'adjusted_servings': adjustment.adjusted_servings,
                    'adjusted_nutrition': adjustment.adjusted_nutrition,
                    'rationale': adjustment.rationale
                }
                recipe_data['relevance_score'] = score
                
                scored_recipes.append((score, recipe_data))
                
            except Exception as e:
                logger.warning(f"Erreur ajustement recette {recipe.id} pour utilisateur {user_id}: {e}")
                continue
        
        # Tri par score et limitation
        scored_recipes.sort(key=lambda x: x[0], reverse=True)
        final_recipes = [recipe_data for score, recipe_data in scored_recipes[:limit]]
        
        return jsonify({
            'user_info': {
                'id': user.id,
                'username': user.username,
                'nutrition_profile': nutrition_profile.to_dict()
            },
            'meal_type': meal_type,
            'recipes': final_recipes,
            'total_found': len(final_recipes)
        })
        
    except Exception as e:
        logger.error(f"Erreur récupération recettes ajustées utilisateur {user_id}: {e}")
        return jsonify({'error': str(e)}), 500


def calculate_recipe_relevance_score(recipe, user, adjustment, nutrition_profile, meal_type):
    """Calcule un score de pertinence pour une recette selon le profil utilisateur"""
    score = 100.0
    
    try:
        # Score basé sur l'ajustement des portions (moins d'ajustement = mieux)
        multiplier = adjustment.multiplier
        if 0.8 <= multiplier <= 1.2:  # Ajustement minimal
            score += 20
        elif 0.5 <= multiplier <= 1.5:  # Ajustement modéré
            score += 10
        else:  # Ajustement important
            score -= 10
        
        # Score basé sur l'adéquation nutritionnelle
        target_calories = portion_adjustment._calculate_meal_target_calories(
            nutrition_profile.adjusted_calories, meal_type
        )
        
        recipe_calories = adjustment.adjusted_nutrition['calories']
        calorie_diff_percent = abs(recipe_calories - target_calories) / target_calories
        
        if calorie_diff_percent <= 0.1:  # ±10%
            score += 15
        elif calorie_diff_percent <= 0.2:  # ±20%
            score += 10
        elif calorie_diff_percent <= 0.3:  # ±30%
            score += 5
        else:
            score -= 5
        
        # Score basé sur les préférences utilisateur
        if user.dietary_restrictions_list:
            # TODO: Vérifier compatibilité avec restrictions alimentaires
            pass
        
        if user.preferred_cuisine_types_list and hasattr(recipe, 'cuisine_type'):
            if recipe.cuisine_type in user.preferred_cuisine_types_list:
                score += 10
        
        # Score basé sur la complexité (utilisateur débutant vs expert)
        if hasattr(recipe, 'difficulty_level'):
            if recipe.difficulty_level == 'easy':
                score += 5
            elif recipe.difficulty_level == 'hard':
                score -= 5
        
        # Score basé sur le temps de préparation
        total_time = (recipe.prep_time or 0) + (recipe.cook_time or 0)
        if total_time <= 30:  # Recettes rapides
            score += 10
        elif total_time <= 60:
            score += 5
        elif total_time > 120:  # Recettes longues
            score -= 5
        
        # Score basé sur les favoris
        if hasattr(recipe, 'is_favorite') and recipe.is_favorite:
            score += 15
        
    except Exception as e:
        logger.warning(f"Erreur calcul score pertinence recette {recipe.id}: {e}")
        score = 50.0  # Score neutre en cas d'erreur
    
    return max(0, min(200, score))  # Limiter entre 0 et 200


@recipes_bp.route('/nutrition/portion-adjustment-analytics', methods=['GET'])
def get_portion_adjustment_analytics():
    """Récupère des analytics sur les ajustements de portions"""
    try:
        # Paramètres optionnels
        days = request.args.get('days', 30, type=int)
        user_id = request.args.get('user_id', type=int)
        
        # TODO: Implémenter analytics basées sur les logs d'usage
        # Pour l'instant, retourne des données simulées
        
        analytics = {
            'period_days': days,
            'total_adjustments': 0,
            'average_multiplier': 1.0,
            'most_adjusted_recipes': [],
            'user_stats': {} if not user_id else {
                'user_id': user_id,
                'total_recipe_views': 0,
                'average_portion_multiplier': 1.0,
                'favorite_meal_types': []
            },
            'popular_adjustments': {
                'increased_portions': 0,
                'decreased_portions': 0,
                'no_adjustment_needed': 0
            }
        }
        
        return jsonify(analytics)
        
    except Exception as e:
        logger.error(f"Erreur récupération analytics ajustement portions: {e}")
        return jsonify({'error': str(e)}), 500

