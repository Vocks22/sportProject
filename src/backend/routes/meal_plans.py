from flask import Blueprint, request, jsonify
from database import db
from models.meal_plan import MealPlan, ShoppingList
from models.recipe import Recipe
from models.ingredient import Ingredient
from models.user import User
from schemas.meal_plan import (
    meal_plan_schema, meal_plans_schema, meal_plan_update_schema,
    meal_plan_generation_schema, meal_plan_query_schema,
    shopping_list_schema, shopping_lists_schema, shopping_list_update_schema,
    # Nouveaux schémas US1.5
    optimized_shopping_list_schema, optimized_shopping_lists_schema,
    item_toggle_schema, bulk_toggle_schema, regenerate_list_schema,
    aggregation_preferences_schema, shopping_list_export_schema,
    shopping_list_statistics_schema, shopping_list_history_schema,
    shopping_list_histories_schema
)
from services.shopping_service import ShoppingService
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
    """Générer une liste de courses optimisée pour un plan de repas (US1.5)"""
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
        
        # Récupérer les préférences d'agrégation depuis le body de la requête
        request_data = request.get_json() or {}
        aggregation_preferences = request_data.get('aggregation_preferences', {})
        
        # Générer la liste optimisée avec le nouveau service
        optimized_data = ShoppingService.generate_optimized_shopping_list(
            meal_plan, 
            aggregation_preferences
        )
        
        # Créer la liste de courses avec les nouvelles données
        shopping_list_data = {
            'meal_plan_id': plan_id,
            'week_start': meal_plan.week_start.isoformat(),
            'items': optimized_data['items'],
            'category_grouping': optimized_data['category_grouping'],
            'estimated_budget': optimized_data['estimated_budget'],
            'aggregation_rules': optimized_data['aggregation_rules']
        }
        
        shopping_list = ShoppingList.create_from_dict(shopping_list_data)
        db.session.add(shopping_list)
        db.session.commit()
        
        return jsonify({
            'shopping_list': optimized_shopping_list_schema.dump(shopping_list),
            'generation_info': optimized_data['statistics']
        }), 201
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
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

# ===== NOUVEAUX ENDPOINTS US1.5 - LISTE DE COURSES INTERACTIVE =====

@meal_plans_bp.route('/shopping-lists/<int:list_id>/items/<item_id>/toggle', methods=['PATCH'])
def toggle_shopping_item(list_id, item_id):
    """Cocher/décocher un article de la liste de courses"""
    try:
        # Validation de l'ID
        if list_id <= 0:
            return jsonify({'error': 'ID de liste invalide'}), 400
        
        shopping_list = ShoppingList.query.get(list_id)
        if not shopping_list:
            return jsonify({'error': 'Liste de courses non trouvée'}), 404
        
        # Récupérer les données de la requête
        data = request.get_json() or {}
        checked = data.get('checked', False)
        user_id = data.get('user_id')
        
        # Utiliser le service pour mettre à jour l'état
        success = ShoppingService.update_item_status(
            shopping_list, 
            item_id, 
            checked, 
            user_id
        )
        
        if success:
            return jsonify({
                'success': True,
                'shopping_list': optimized_shopping_list_schema.dump(shopping_list)
            })
        else:
            return jsonify({'error': 'Échec de la mise à jour de l\'article'}), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@meal_plans_bp.route('/shopping-lists/<int:list_id>/regenerate', methods=['POST'])
def regenerate_shopping_list(list_id):
    """Régénérer une liste de courses existante"""
    try:
        # Validation de l'ID
        if list_id <= 0:
            return jsonify({'error': 'ID de liste invalide'}), 400
        
        shopping_list = ShoppingList.query.get(list_id)
        if not shopping_list:
            return jsonify({'error': 'Liste de courses non trouvée'}), 404
        
        # Récupérer les options de régénération
        data = request.get_json() or {}
        preserve_checked = data.get('preserve_checked_items', True)
        
        # Régénérer avec le service
        result = ShoppingService.regenerate_shopping_list(
            shopping_list, 
            preserve_checked
        )
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify({'error': result['error']}), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@meal_plans_bp.route('/shopping-lists/<int:list_id>/export', methods=['POST'])
def export_shopping_list(list_id):
    """Exporter une liste de courses (prépare les données pour l'export côté client)"""
    try:
        # Validation de l'ID
        if list_id <= 0:
            return jsonify({'error': 'ID de liste invalide'}), 400
        
        shopping_list = ShoppingList.query.get(list_id)
        if not shopping_list:
            return jsonify({'error': 'Liste de courses non trouvée'}), 404
        
        # Récupérer le format d'export demandé
        data = request.get_json() or {}
        export_format = data.get('format', 'json')  # json, pdf, txt, email
        
        # Préparer les données d'export
        export_data = {
            'shopping_list': shopping_list.to_dict(),
            'meal_plan': shopping_list.meal_plan.to_dict(),
            'export_metadata': {
                'generated_at': datetime.utcnow().isoformat(),
                'format': export_format,
                'total_items': len(shopping_list.items),
                'completed_items': len([
                    item for item_id, item in shopping_list.checked_items.items() 
                    if item
                ]),
                'estimated_budget': shopping_list.estimated_budget
            }
        }
        
        return jsonify({
            'success': True,
            'export_data': export_data,
            'download_url': f'/api/shopping-lists/{list_id}/download/{export_format}'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@meal_plans_bp.route('/shopping-lists/<int:list_id>/statistics', methods=['GET'])
def get_shopping_list_statistics(list_id):
    """Récupérer les statistiques détaillées d'une liste de courses (US1.5)"""
    try:
        # Validation de l'ID
        if list_id <= 0:
            return jsonify({'error': 'ID de liste invalide'}), 400
        
        shopping_list = ShoppingList.query.get(list_id)
        if not shopping_list:
            return jsonify({'error': 'Liste de courses non trouvée'}), 404
        
        # Utiliser le service pour calculer les statistiques
        statistics = ShoppingService.get_shopping_list_statistics(shopping_list)
        
        return jsonify(statistics)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@meal_plans_bp.route('/shopping-lists/<int:list_id>/bulk-toggle', methods=['PATCH'])
def bulk_toggle_items(list_id):
    """Cocher/décocher plusieurs articles en une fois"""
    try:
        # Validation de l'ID
        if list_id <= 0:
            return jsonify({'error': 'ID de liste invalide'}), 400
        
        shopping_list = ShoppingList.query.get(list_id)
        if not shopping_list:
            return jsonify({'error': 'Liste de courses non trouvée'}), 404
        
        # Récupérer les données de la requête
        data = request.get_json() or {}
        items_to_update = data.get('items', [])  # [{'item_id': 'id', 'checked': bool}]
        user_id = data.get('user_id')
        
        if not items_to_update:
            return jsonify({'error': 'Aucun article à mettre à jour'}), 400
        
        # Mettre à jour en batch
        success_count = 0
        for item_update in items_to_update:
            item_id = item_update.get('item_id')
            checked = item_update.get('checked', False)
            
            if item_id:
                success = ShoppingService.update_item_status(
                    shopping_list, 
                    item_id, 
                    checked, 
                    user_id
                )
                if success:
                    success_count += 1
        
        return jsonify({
            'success': True,
            'updated_items': success_count,
            'total_items': len(items_to_update),
            'shopping_list': optimized_shopping_list_schema.dump(shopping_list)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ===== NOUVEAUX ENDPOINTS US1.5 - FONCTIONNALITÉS AVANCÉES =====

@meal_plans_bp.route('/shopping-lists/<int:list_id>/history', methods=['GET'])
def get_shopping_list_history(list_id):
    """Récupérer l'historique des modifications d'une liste de courses"""
    try:
        # Validation de l'ID
        if list_id <= 0:
            return jsonify({'error': 'ID de liste invalide'}), 400
        
        shopping_list = ShoppingList.query.get(list_id)
        if not shopping_list:
            return jsonify({'error': 'Liste de courses non trouvée'}), 404
        
        # Paramètres de pagination
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        # Récupérer l'historique
        from models.shopping_history import ShoppingListHistory
        
        history_query = ShoppingListHistory.query.filter_by(
            shopping_list_id=list_id
        ).order_by(ShoppingListHistory.timestamp.desc())
        
        paginated_history = history_query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        return jsonify({
            'history': shopping_list_histories_schema.dump(paginated_history.items),
            'pagination': {
                'page': paginated_history.page,
                'pages': paginated_history.pages,
                'per_page': paginated_history.per_page,
                'total': paginated_history.total,
                'has_next': paginated_history.has_next,
                'has_prev': paginated_history.has_prev
            }
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@meal_plans_bp.route('/shopping-lists/<int:list_id>/export-data', methods=['POST'])
def prepare_shopping_list_export(list_id):
    """Préparer les données d'export d'une liste de courses (version améliorée US1.5)"""
    try:
        # Validation de l'ID
        if list_id <= 0:
            return jsonify({'error': 'ID de liste invalide'}), 400
        
        shopping_list = ShoppingList.query.get(list_id)
        if not shopping_list:
            return jsonify({'error': 'Liste de courses non trouvée'}), 404
        
        # Validation des données de requête
        try:
            data = shopping_list_export_schema.load(request.get_json() or {})
        except ValidationError as e:
            return jsonify({'error': 'Données invalides', 'details': e.messages}), 400
        
        # Utiliser le service pour préparer l'export
        export_result = ShoppingService.export_shopping_list_data(
            shopping_list=shopping_list,
            export_format=data['format'],
            include_metadata=data['include_metadata'],
            include_checked_items=data['include_checked_items']
        )
        
        if export_result['success']:
            return jsonify(export_result)
        else:
            return jsonify({'error': export_result['error']}), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@meal_plans_bp.route('/shopping-lists/categories', methods=['GET'])
def get_store_categories():
    """Récupérer les catégories de rayons de magasin disponibles"""
    try:
        from models.shopping_history import StoreCategory
        
        # Récupérer les catégories pour l'utilisateur (ou globales)
        user_id = request.args.get('user_id')
        categories = StoreCategory.get_user_categories(user_id)
        
        # Convertir en dictionnaire
        categories_data = [category.to_dict() for category in categories]
        
        return jsonify({
            'categories': categories_data,
            'total': len(categories_data)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

