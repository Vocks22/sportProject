from flask import Blueprint, request, jsonify
from database import db
from models.meal_plan import MealPlan, ShoppingList
from models.recipe import Recipe
from models.ingredient import Ingredient
from models.user import User
from schemas.meal_plan import (
    meal_plan_schema, meal_plans_schema, meal_plan_update_schema,
    meal_plan_generation_schema, meal_plan_query_schema,
    shopping_list_schema, shopping_lists_schema, shopping_list_update_schema
)
from datetime import datetime, date, timedelta
from collections import defaultdict
from marshmallow import ValidationError
import random

meal_plans_bp = Blueprint('meal_plans', __name__)

@meal_plans_bp.route('/meal-plans', methods=['GET'])
def get_meal_plans():
    """Récupérer tous les plans de repas avec pagination"""
    try:
        # Validation des paramètres de requête
        try:
            query_params = meal_plan_query_schema.load(request.args)
        except ValidationError as e:
            return jsonify({'error': 'Paramètres de requête invalides', 'details': e.messages}), 400
        
        # Construction de la requête
        query = MealPlan.query
        
        # Filtres
        if query_params.get('user_id'):
            query = query.filter(MealPlan.user_id == query_params['user_id'])
        if query_params.get('week_start'):
            query = query.filter(MealPlan.week_start == query_params['week_start'])
        if query_params.get('is_active') is not None:
            query = query.filter(MealPlan.is_active == query_params['is_active'])
        
        # Tri
        sort_column = getattr(MealPlan, query_params['sort_by'])
        if query_params['order'] == 'desc':
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())
        
        # Pagination
        page = query_params['page']
        per_page = query_params['per_page']
        paginated = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        return jsonify({
            'meal_plans': meal_plans_schema.dump(paginated.items),
            'pagination': {
                'page': paginated.page,
                'pages': paginated.pages,
                'per_page': paginated.per_page,
                'total': paginated.total,
                'has_next': paginated.has_next,
                'has_prev': paginated.has_prev
            }
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@meal_plans_bp.route('/meal-plans/<int:plan_id>', methods=['GET'])
def get_meal_plan(plan_id):
    """Récupérer un plan de repas spécifique"""
    try:
        # Validation de l'ID
        if plan_id <= 0:
            return jsonify({'error': 'ID de plan invalide'}), 400
        
        meal_plan = MealPlan.query.get(plan_id)
        if not meal_plan:
            return jsonify({'error': 'Plan de repas non trouvé'}), 404
        
        return jsonify(meal_plan_schema.dump(meal_plan))
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@meal_plans_bp.route('/meal-plans', methods=['POST'])
def create_meal_plan():
    """Créer un nouveau plan de repas"""
    try:
        # Validation du Content-Type
        if not request.is_json:
            return jsonify({'error': 'Content-Type doit être application/json'}), 400
        
        # Validation des données avec Marshmallow
        try:
            data = meal_plan_schema.load(request.get_json())
        except ValidationError as e:
            return jsonify({'error': 'Données invalides', 'details': e.messages}), 400
        
        # Calculer le résumé nutritionnel
        nutrition_summary = calculate_meal_plan_nutrition(data.get('meals', {}))
        data['nutrition_summary'] = nutrition_summary
        
        meal_plan = MealPlan.create_from_dict(data)
        db.session.add(meal_plan)
        db.session.commit()
        
        return jsonify(meal_plan_schema.dump(meal_plan)), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@meal_plans_bp.route('/meal-plans/<int:plan_id>', methods=['PUT'])
def update_meal_plan(plan_id):
    """Mettre à jour un plan de repas"""
    try:
        # Validation de l'ID
        if plan_id <= 0:
            return jsonify({'error': 'ID de plan invalide'}), 400
        
        meal_plan = MealPlan.query.get(plan_id)
        if not meal_plan:
            return jsonify({'error': 'Plan de repas non trouvé'}), 404
        
        # Validation du Content-Type
        if not request.is_json:
            return jsonify({'error': 'Content-Type doit être application/json'}), 400
        
        # Validation des données avec Marshmallow
        try:
            data = meal_plan_update_schema.load(request.get_json())
        except ValidationError as e:
            return jsonify({'error': 'Données invalides', 'details': e.messages}), 400
        
        # Mise à jour des champs
        if 'meals' in data:
            meal_plan.meals = data['meals']
            # Recalculer la nutrition
            nutrition_summary = calculate_meal_plan_nutrition(data['meals'])
            meal_plan.daily_calories = nutrition_summary['daily_calories']
            meal_plan.daily_protein = nutrition_summary['daily_protein']
            meal_plan.daily_carbs = nutrition_summary['daily_carbs']
            meal_plan.daily_fat = nutrition_summary['daily_fat']
        
        if 'week_start' in data:
            meal_plan.week_start = data['week_start']
        
        if 'is_active' in data:
            meal_plan.is_active = data['is_active']
        
        meal_plan.updated_at = datetime.utcnow()
        
        db.session.commit()
        return jsonify(meal_plan_schema.dump(meal_plan))
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@meal_plans_bp.route('/meal-plans/<int:plan_id>', methods=['DELETE'])
def delete_meal_plan(plan_id):
    """Supprimer un plan de repas"""
    try:
        # Validation de l'ID
        if plan_id <= 0:
            return jsonify({'error': 'ID de plan invalide'}), 400
        
        meal_plan = MealPlan.query.get(plan_id)
        if not meal_plan:
            return jsonify({'error': 'Plan de repas non trouvé'}), 404
        
        db.session.delete(meal_plan)
        db.session.commit()
        
        return jsonify({'message': 'Plan de repas supprimé avec succès'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@meal_plans_bp.route('/meal-plans/generate', methods=['POST'])
def generate_meal_plan():
    """Générer automatiquement un plan de repas avec objectifs nutritionnels"""
    try:
        # Validation du Content-Type
        if not request.is_json:
            return jsonify({'error': 'Content-Type doit être application/json'}), 400
        
        # Validation des données avec Marshmallow
        try:
            data = meal_plan_generation_schema.load(request.get_json() or {})
        except ValidationError as e:
            return jsonify({'error': 'Données invalides', 'details': e.messages}), 400
        
        user_id = data.get('user_id')
        week_start = data['week_start']
        
        # Récupérer les objectifs nutritionnels de l'utilisateur si disponible
        nutritional_goals = {
            'target_calories': data['target_calories'],
            'target_protein': data['target_protein'],
            'target_carbs': data['target_carbs'],
            'target_fat': data['target_fat']
        }
        
        # Si user_id est fourni, essayer de récupérer ses objectifs personnalisés
        if user_id:
            user = User.query.filter_by(id=user_id).first()
            if user:
                nutritional_goals = {
                    'target_calories': user.daily_calories_target or data['target_calories'],
                    'target_protein': user.daily_protein_target or data['target_protein'],
                    'target_carbs': user.daily_carbs_target or data['target_carbs'],
                    'target_fat': user.daily_fat_target or data['target_fat']
                }
        
        # Générer le plan de repas optimisé
        meals = generate_optimized_meal_plan(
            nutritional_goals=nutritional_goals,
            meal_types_to_include=data['meal_types_to_include'],
            max_repeats=data['max_repeats'],
            preferred_categories=data.get('preferred_categories')
        )
        
        if not meals:
            return jsonify({'error': 'Impossible de générer un plan de repas avec les critères donnés'}), 400
        
        # Calculer la nutrition
        nutrition_summary = calculate_meal_plan_nutrition(meals)
        
        # Créer le plan de repas
        meal_plan_data = {
            'user_id': user_id,
            'week_start': week_start,
            'meals': meals,
            'nutrition_summary': nutrition_summary
        }
        
        meal_plan = MealPlan.create_from_dict(meal_plan_data)
        db.session.add(meal_plan)
        db.session.commit()
        
        return jsonify({
            'meal_plan': meal_plan_schema.dump(meal_plan),
            'generation_info': {
                'target_nutrition': nutritional_goals,
                'actual_nutrition': nutrition_summary,
                'accuracy': calculate_nutrition_accuracy(nutritional_goals, nutrition_summary)
            }
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@meal_plans_bp.route('/meal-plans/<int:plan_id>/shopping-list', methods=['POST'])
def generate_shopping_list(plan_id):
    """Générer une liste de courses pour un plan de repas"""
    try:
        # Validation de l'ID
        if plan_id <= 0:
            return jsonify({'error': 'ID de plan invalide'}), 400
        
        meal_plan = MealPlan.query.get(plan_id)
        if not meal_plan:
            return jsonify({'error': 'Plan de repas non trouvé'}), 404
        
        # Vérifier s'il y a déjà une liste de courses pour ce plan
        existing_list = ShoppingList.query.filter_by(meal_plan_id=plan_id).first()
        if existing_list:
            return jsonify({'error': 'Une liste de courses existe déjà pour ce plan de repas'}), 409
        
        # Collecter tous les ingrédients nécessaires
        ingredient_quantities = defaultdict(float)
        
        for day, meals in meal_plan.meals.items():
            for meal_type, recipe_id in meals.items():
                if recipe_id:
                    recipe = Recipe.query.get(recipe_id)
                    if recipe:
                        for ingredient_data in recipe.ingredients:
                            ingredient_id = ingredient_data.get('ingredient_id')
                            quantity = ingredient_data.get('quantity', 0)
                            
                            if ingredient_id:
                                ingredient_quantities[ingredient_id] += quantity
        
        if not ingredient_quantities:
            return jsonify({'error': 'Aucun ingrédient trouvé dans le plan de repas'}), 400
        
        # Créer la liste d'articles
        items = []
        for ingredient_id, total_quantity in ingredient_quantities.items():
            ingredient = Ingredient.query.get(ingredient_id)
            if ingredient:
                items.append({
                    'ingredient_id': ingredient_id,
                    'name': ingredient.name,
                    'quantity': round(total_quantity, 2),
                    'unit': ingredient.unit,
                    'category': ingredient.category or 'other',
                    'checked': False
                })
        
        # Trier par catégorie
        items.sort(key=lambda x: (x['category'], x['name']))
        
        # Créer la liste de courses
        shopping_list_data = {
            'meal_plan_id': plan_id,
            'week_start': meal_plan.week_start.isoformat(),
            'items': items
        }
        
        shopping_list = ShoppingList.create_from_dict(shopping_list_data)
        db.session.add(shopping_list)
        db.session.commit()
        
        return jsonify(shopping_list_schema.dump(shopping_list)), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@meal_plans_bp.route('/shopping-lists', methods=['GET'])
def get_shopping_lists():
    """Récupérer toutes les listes de courses"""
    try:
        meal_plan_id = request.args.get('meal_plan_id', type=int)
        
        # Validation du meal_plan_id si fourni
        if meal_plan_id is not None and meal_plan_id <= 0:
            return jsonify({'error': 'ID de plan de repas invalide'}), 400
        
        query = ShoppingList.query
        if meal_plan_id:
            # Vérifier que le plan de repas existe
            meal_plan = MealPlan.query.get(meal_plan_id)
            if not meal_plan:
                return jsonify({'error': 'Plan de repas non trouvé'}), 404
            query = query.filter(ShoppingList.meal_plan_id == meal_plan_id)
        
        shopping_lists = query.order_by(ShoppingList.generated_date.desc()).all()
        return jsonify(shopping_lists_schema.dump(shopping_lists))
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@meal_plans_bp.route('/shopping-lists/<int:list_id>', methods=['PUT'])
def update_shopping_list(list_id):
    """Mettre à jour une liste de courses"""
    try:
        # Validation de l'ID
        if list_id <= 0:
            return jsonify({'error': 'ID de liste invalide'}), 400
        
        shopping_list = ShoppingList.query.get(list_id)
        if not shopping_list:
            return jsonify({'error': 'Liste de courses non trouvée'}), 404
        
        # Validation du Content-Type
        if not request.is_json:
            return jsonify({'error': 'Content-Type doit être application/json'}), 400
        
        # Validation des données avec Marshmallow
        try:
            data = shopping_list_update_schema.load(request.get_json())
        except ValidationError as e:
            return jsonify({'error': 'Données invalides', 'details': e.messages}), 400
        
        if 'items' in data:
            shopping_list.items = data['items']
        if 'is_completed' in data:
            shopping_list.is_completed = data['is_completed']
        
        db.session.commit()
        return jsonify(shopping_list_schema.dump(shopping_list))
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

def calculate_meal_plan_nutrition(meals):
    """Calculer les valeurs nutritionnelles moyennes d'un plan de repas"""
    total_calories = 0
    total_protein = 0
    total_carbs = 0
    total_fat = 0
    day_count = 0
    
    for day, day_meals in meals.items():
        day_calories = 0
        day_protein = 0
        day_carbs = 0
        day_fat = 0
        
        for meal_type, recipe_id in day_meals.items():
            if recipe_id:
                recipe = Recipe.query.get(recipe_id)
                if recipe:
                    day_calories += recipe.total_calories or 0
                    day_protein += recipe.total_protein or 0
                    day_carbs += recipe.total_carbs or 0
                    day_fat += recipe.total_fat or 0
        
        if day_calories > 0:  # Jour avec au moins un repas
            total_calories += day_calories
            total_protein += day_protein
            total_carbs += day_carbs
            total_fat += day_fat
            day_count += 1
    
    if day_count > 0:
        return {
            'daily_calories': round(total_calories / day_count, 1),
            'daily_protein': round(total_protein / day_count, 1),
            'daily_carbs': round(total_carbs / day_count, 1),
            'daily_fat': round(total_fat / day_count, 1)
        }
    else:
        return {
            'daily_calories': 0,
            'daily_protein': 0,
            'daily_carbs': 0,
            'daily_fat': 0
        }

def generate_optimized_meal_plan(nutritional_goals, meal_types_to_include, max_repeats=2, preferred_categories=None):
    """Générer un plan de repas optimisé selon les objectifs nutritionnels"""
    try:
        # Récupérer toutes les recettes disponibles
        recipes_query = Recipe.query
        
        # Filtrer par catégories préférées si spécifiées
        if preferred_categories:
            recipes_query = recipes_query.filter(Recipe.category.in_(preferred_categories))
        
        all_recipes = recipes_query.all()
        
        if not all_recipes:
            return None
        
        # Organiser les recettes par type de repas
        recipes_by_type = defaultdict(list)
        for recipe in all_recipes:
            if recipe.meal_type in meal_types_to_include:
                recipes_by_type[recipe.meal_type].append(recipe)
        
        # Vérifier qu'on a des recettes pour chaque type demandé
        for meal_type in meal_types_to_include:
            if not recipes_by_type[meal_type]:
                # Si aucune recette pour un type, utiliser toutes les recettes
                recipes_by_type[meal_type] = all_recipes
        
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        
        # Algorithme génétique simple pour l'optimisation
        best_plan = None
        best_score = float('inf')
        
        # Essayer plusieurs générations
        for attempt in range(50):  # 50 tentatives pour trouver un bon plan
            meals = {}
            recipe_usage = defaultdict(int)
            
            # Générer les repas pour chaque jour
            for day in days:
                meals[day] = {}
                for meal_type in meal_types_to_include:
                    available_recipes = [
                        recipe for recipe in recipes_by_type[meal_type]
                        if recipe_usage[recipe.id] < max_repeats
                    ]
                    
                    if not available_recipes:
                        # Si toutes les recettes ont été utilisées max_repeats fois,
                        # réinitialiser et permettre une utilisation supplémentaire
                        available_recipes = recipes_by_type[meal_type]
                    
                    if available_recipes:
                        selected_recipe = random.choice(available_recipes)
                        meals[day][meal_type] = selected_recipe.id
                        recipe_usage[selected_recipe.id] += 1
            
            # Évaluer ce plan
            nutrition = calculate_meal_plan_nutrition(meals)
            score = calculate_nutrition_score(nutritional_goals, nutrition)
            
            if score < best_score:
                best_score = score
                best_plan = meals.copy()
                
                # Si le score est très bon, on peut s'arrêter
                if score < 0.1:  # Moins de 10% d'écart
                    break
        
        return best_plan
    
    except Exception as e:
        print(f"Erreur lors de la génération du plan optimisé: {e}")
        return None

def calculate_nutrition_score(target, actual):
    """Calculer un score d'écart entre les objectifs et les valeurs actuelles"""
    try:
        # Calculer l'écart relatif pour chaque nutriment
        calories_diff = abs(target['target_calories'] - actual['daily_calories']) / target['target_calories']
        protein_diff = abs(target['target_protein'] - actual['daily_protein']) / target['target_protein']
        carbs_diff = abs(target['target_carbs'] - actual['daily_carbs']) / target['target_carbs']
        fat_diff = abs(target['target_fat'] - actual['daily_fat']) / target['target_fat']
        
        # Score pondéré (les calories ont plus d'importance)
        score = (calories_diff * 0.4 + protein_diff * 0.25 + carbs_diff * 0.2 + fat_diff * 0.15)
        return score
    except (ZeroDivisionError, KeyError):
        return float('inf')

def calculate_nutrition_accuracy(target, actual):
    """Calculer la précision nutritionnelle en pourcentage"""
    try:
        accuracies = {}
        
        for nutrient in ['calories', 'protein', 'carbs', 'fat']:
            target_key = f'target_{nutrient}'
            actual_key = f'daily_{nutrient}'
            
            if target[target_key] > 0:
                diff = abs(target[target_key] - actual[actual_key]) / target[target_key]
                accuracy = max(0, (1 - diff) * 100)
                accuracies[nutrient] = round(accuracy, 1)
            else:
                accuracies[nutrient] = 0
        
        # Précision globale
        overall = sum(accuracies.values()) / len(accuracies)
        accuracies['overall'] = round(overall, 1)
        
        return accuracies
    except (ZeroDivisionError, KeyError):
        return {
            'calories': 0,
            'protein': 0,
            'carbs': 0,
            'fat': 0,
            'overall': 0
        }

