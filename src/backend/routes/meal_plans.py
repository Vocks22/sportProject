from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.meal_plan import MealPlan, ShoppingList
from src.models.recipe import Recipe
from src.models.ingredient import Ingredient
from datetime import datetime, date, timedelta
from collections import defaultdict

meal_plans_bp = Blueprint('meal_plans', __name__)

@meal_plans_bp.route('/meal-plans', methods=['GET'])
def get_meal_plans():
    """Récupérer tous les plans de repas"""
    try:
        user_id = request.args.get('user_id')
        week_start = request.args.get('week_start')
        
        query = MealPlan.query
        
        if user_id:
            query = query.filter(MealPlan.user_id == user_id)
        if week_start:
            week_date = datetime.fromisoformat(week_start).date()
            query = query.filter(MealPlan.week_start == week_date)
        
        meal_plans = query.order_by(MealPlan.week_start.desc()).all()
        return jsonify([plan.to_dict() for plan in meal_plans])
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@meal_plans_bp.route('/meal-plans/<int:plan_id>', methods=['GET'])
def get_meal_plan(plan_id):
    """Récupérer un plan de repas spécifique"""
    try:
        meal_plan = MealPlan.query.get_or_404(plan_id)
        return jsonify(meal_plan.to_dict())
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@meal_plans_bp.route('/meal-plans', methods=['POST'])
def create_meal_plan():
    """Créer un nouveau plan de repas"""
    try:
        data = request.get_json()
        
        # Validation des données requises
        if 'week_start' not in data:
            return jsonify({'error': 'Date de début de semaine requise'}), 400
        
        # Calculer le résumé nutritionnel
        nutrition_summary = calculate_meal_plan_nutrition(data.get('meals', {}))
        data['nutrition_summary'] = nutrition_summary
        
        meal_plan = MealPlan.create_from_dict(data)
        db.session.add(meal_plan)
        db.session.commit()
        
        return jsonify(meal_plan.to_dict()), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@meal_plans_bp.route('/meal-plans/<int:plan_id>', methods=['PUT'])
def update_meal_plan(plan_id):
    """Mettre à jour un plan de repas"""
    try:
        meal_plan = MealPlan.query.get_or_404(plan_id)
        data = request.get_json()
        
        # Mise à jour des champs
        if 'meals' in data:
            meal_plan.meals = data['meals']
            # Recalculer la nutrition
            nutrition_summary = calculate_meal_plan_nutrition(data['meals'])
            meal_plan.daily_calories = nutrition_summary['daily_calories']
            meal_plan.daily_protein = nutrition_summary['daily_protein']
            meal_plan.daily_carbs = nutrition_summary['daily_carbs']
            meal_plan.daily_fat = nutrition_summary['daily_fat']
        
        if 'is_active' in data:
            meal_plan.is_active = data['is_active']
        
        db.session.commit()
        return jsonify(meal_plan.to_dict())
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@meal_plans_bp.route('/meal-plans/<int:plan_id>', methods=['DELETE'])
def delete_meal_plan(plan_id):
    """Supprimer un plan de repas"""
    try:
        meal_plan = MealPlan.query.get_or_404(plan_id)
        db.session.delete(meal_plan)
        db.session.commit()
        
        return jsonify({'message': 'Plan de repas supprimé avec succès'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@meal_plans_bp.route('/meal-plans/generate', methods=['POST'])
def generate_meal_plan():
    """Générer automatiquement un plan de repas"""
    try:
        data = request.get_json()
        week_start = data.get('week_start', date.today().isoformat())
        user_id = data.get('user_id')
        
        # Récupérer toutes les recettes disponibles
        recipes = Recipe.query.all()
        
        # Organiser les recettes par type de repas
        recipes_by_type = defaultdict(list)
        for recipe in recipes:
            recipes_by_type[recipe.meal_type].append(recipe)
        
        # Générer le plan pour 7 jours
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        meal_types = ['repas1', 'collation1', 'repas2', 'collation2', 'repas3']
        
        meals = {}
        for day in days:
            meals[day] = {}
            for meal_type in meal_types:
                available_recipes = recipes_by_type.get(meal_type, [])
                if available_recipes:
                    # Sélectionner une recette aléatoirement
                    import random
                    selected_recipe = random.choice(available_recipes)
                    meals[day][meal_type] = selected_recipe.id
        
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
        
        return jsonify(meal_plan.to_dict()), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@meal_plans_bp.route('/meal-plans/<int:plan_id>/shopping-list', methods=['POST'])
def generate_shopping_list(plan_id):
    """Générer une liste de courses pour un plan de repas"""
    try:
        meal_plan = MealPlan.query.get_or_404(plan_id)
        
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
        
        # Créer la liste d'articles
        items = []
        for ingredient_id, total_quantity in ingredient_quantities.items():
            ingredient = Ingredient.query.get(ingredient_id)
            if ingredient:
                items.append({
                    'ingredient_id': ingredient_id,
                    'name': ingredient.name,
                    'quantity': total_quantity,
                    'unit': ingredient.unit,
                    'category': ingredient.category,
                    'checked': False
                })
        
        # Trier par catégorie
        items.sort(key=lambda x: x['category'])
        
        # Créer la liste de courses
        shopping_list_data = {
            'meal_plan_id': plan_id,
            'week_start': meal_plan.week_start.isoformat(),
            'items': items
        }
        
        shopping_list = ShoppingList.create_from_dict(shopping_list_data)
        db.session.add(shopping_list)
        db.session.commit()
        
        return jsonify(shopping_list.to_dict()), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@meal_plans_bp.route('/shopping-lists', methods=['GET'])
def get_shopping_lists():
    """Récupérer toutes les listes de courses"""
    try:
        meal_plan_id = request.args.get('meal_plan_id', type=int)
        
        query = ShoppingList.query
        if meal_plan_id:
            query = query.filter(ShoppingList.meal_plan_id == meal_plan_id)
        
        shopping_lists = query.order_by(ShoppingList.generated_date.desc()).all()
        return jsonify([sl.to_dict() for sl in shopping_lists])
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@meal_plans_bp.route('/shopping-lists/<int:list_id>', methods=['PUT'])
def update_shopping_list(list_id):
    """Mettre à jour une liste de courses"""
    try:
        shopping_list = ShoppingList.query.get_or_404(list_id)
        data = request.get_json()
        
        if 'items' in data:
            shopping_list.items = data['items']
        if 'is_completed' in data:
            shopping_list.is_completed = data['is_completed']
        
        db.session.commit()
        return jsonify(shopping_list.to_dict())
    
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
                    day_calories += recipe.total_calories
                    day_protein += recipe.total_protein
                    day_carbs += recipe.total_carbs
                    day_fat += recipe.total_fat
        
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

