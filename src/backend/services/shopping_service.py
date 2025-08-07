"""
Service pour la gestion avancée des listes de courses (US1.5)
Gère l'agrégation, le groupement et les calculs d'optimisation
"""

from collections import defaultdict
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Tuple, Optional, Any
import json
from datetime import datetime

from models.recipe import Recipe
from models.ingredient import Ingredient
from models.meal_plan import MealPlan, ShoppingList
from database import db

class ShoppingService:
    """Service principal pour la gestion des listes de courses interactives"""
    
    # Configuration des conversions d'unités
    UNIT_CONVERSIONS = {
        'g': {'kg': 0.001, 'mg': 1000},
        'ml': {'l': 0.001, 'cl': 0.1},
        'unités': {'douzaine': 1/12, 'pièce': 1}
    }
    
    # Seuils pour l'agrégation automatique
    AGGREGATION_THRESHOLDS = {
        'g': 1000,    # 1000g → 1kg
        'ml': 1000,   # 1000ml → 1l
        'unités': 12  # 12 unités → 1 douzaine
    }
    
    # Mapping des catégories d'ingrédients vers les rayons magasin
    CATEGORY_TO_STORE_SECTION = {
        'protein': 'protein',
        'vegetable': 'vegetable',
        'fruit': 'fruit',
        'dairy': 'dairy',
        'grain': 'grain',
        'nuts': 'nuts',
        'oil': 'condiment',
        'spice': 'condiment',
        'herb': 'condiment',
        'supplement': 'supplement',
        'frozen': 'frozen',
        'bakery': 'bakery',
        'beverage': 'beverages'
    }

    @classmethod
    def generate_optimized_shopping_list(
        cls, 
        meal_plan: MealPlan, 
        aggregation_preferences: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Génère une liste de courses optimisée avec agrégation intelligente
        
        Args:
            meal_plan: Plan de repas source
            aggregation_preferences: Préférences d'agrégation utilisateur
        
        Returns:
            Dict contenant la liste optimisée avec métadonnées
        """
        
        # Étape 1: Collecter tous les ingrédients nécessaires
        raw_ingredients = cls._collect_ingredients_from_meal_plan(meal_plan)
        
        if not raw_ingredients:
            raise ValueError("Aucun ingrédient trouvé dans le plan de repas")
        
        # Étape 2: Agréger les quantités par ingrédient
        aggregated_ingredients = cls._aggregate_ingredient_quantities(raw_ingredients)
        
        # Étape 3: Appliquer les règles d'optimisation d'unités
        optimized_ingredients = cls._optimize_units_and_quantities(
            aggregated_ingredients, 
            aggregation_preferences
        )
        
        # Étape 4: Grouper par rayons de magasin
        categorized_items = cls._group_by_store_categories(optimized_ingredients)
        
        # Étape 5: Calculer le budget estimé
        estimated_budget = cls._calculate_estimated_budget(optimized_ingredients)
        
        # Étape 6: Générer les métadonnées et règles d'agrégation
        aggregation_rules = cls._generate_aggregation_rules(raw_ingredients, optimized_ingredients)
        
        return {
            'items': optimized_ingredients,
            'category_grouping': categorized_items,
            'estimated_budget': estimated_budget,
            'aggregation_rules': aggregation_rules,
            'statistics': {
                'total_items': len(optimized_ingredients),
                'total_categories': len(categorized_items),
                'aggregation_savings': cls._calculate_aggregation_savings(
                    raw_ingredients, optimized_ingredients
                )
            }
        }

    @classmethod
    def _collect_ingredients_from_meal_plan(cls, meal_plan: MealPlan) -> List[Dict]:
        """Collecte tous les ingrédients nécessaires depuis le plan de repas"""
        ingredients_list = []
        
        for day, meals in meal_plan.meals.items():
            for meal_type, recipe_id in meals.items():
                if recipe_id:
                    recipe = Recipe.query.get(recipe_id)
                    if recipe and recipe.ingredients:
                        for ingredient_data in recipe.ingredients:
                            ingredient_entry = {
                                'recipe_id': recipe_id,
                                'recipe_name': recipe.name,
                                'day': day,
                                'meal_type': meal_type,
                                'ingredient_id': ingredient_data.get('ingredient_id'),
                                'quantity': float(ingredient_data.get('quantity', 0)),
                                'unit': ingredient_data.get('unit', 'unités'),
                                'original_ingredient_data': ingredient_data
                            }
                            ingredients_list.append(ingredient_entry)
        
        return ingredients_list

    @classmethod
    def _aggregate_ingredient_quantities(cls, raw_ingredients: List[Dict]) -> List[Dict]:
        """Agrège les quantités des mêmes ingrédients"""
        ingredient_totals = defaultdict(lambda: {
            'total_quantity': 0,
            'unit': 'unités',
            'sources': [],
            'ingredient_id': None,
            'ingredient_info': None
        })
        
        for item in raw_ingredients:
            ingredient_id = item['ingredient_id']
            if not ingredient_id:
                continue
                
            key = f"{ingredient_id}_{item['unit']}"
            
            ingredient_totals[key]['total_quantity'] += item['quantity']
            ingredient_totals[key]['unit'] = item['unit']
            ingredient_totals[key]['ingredient_id'] = ingredient_id
            ingredient_totals[key]['sources'].append({
                'recipe_name': item['recipe_name'],
                'day': item['day'],
                'meal_type': item['meal_type'],
                'quantity': item['quantity']
            })
            
            # Récupérer les informations de l'ingrédient si pas encore fait
            if not ingredient_totals[key]['ingredient_info']:
                ingredient = Ingredient.query.get(ingredient_id)
                if ingredient:
                    ingredient_totals[key]['ingredient_info'] = {
                        'name': ingredient.name,
                        'category': getattr(ingredient, 'category', 'other'),
                        'unit_price': getattr(ingredient, 'unit_price', None),
                        'preferred_brand': getattr(ingredient, 'preferred_brand', None)
                    }
        
        # Convertir en liste avec IDs uniques
        aggregated_list = []
        for idx, (key, data) in enumerate(ingredient_totals.items()):
            if data['ingredient_info']:  # Ne garder que les ingrédients valides
                aggregated_list.append({
                    'id': f"agg_{idx + 1}",
                    'ingredient_id': data['ingredient_id'],
                    'name': data['ingredient_info']['name'],
                    'quantity': data['total_quantity'],
                    'unit': data['unit'],
                    'category': data['ingredient_info']['category'],
                    'sources': data['sources'],
                    'unit_price': data['ingredient_info'].get('unit_price'),
                    'preferred_brand': data['ingredient_info'].get('preferred_brand'),
                    'checked': False
                })
        
        return aggregated_list

    @classmethod
    def _optimize_units_and_quantities(
        cls, 
        ingredients: List[Dict], 
        preferences: Optional[Dict] = None
    ) -> List[Dict]:
        """Optimise les unités et quantités selon les seuils définis"""
        optimized = []
        preferences = preferences or {}
        
        for item in ingredients:
            quantity = item['quantity']
            unit = item['unit']
            
            # Arrondir les quantités à 2 décimales
            quantity = float(Decimal(str(quantity)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
            
            # Appliquer les conversions d'unités si nécessaire
            optimized_quantity, optimized_unit, conversion_note = cls._apply_unit_conversion(
                quantity, unit, preferences.get('unit_preferences', {})
            )
            
            optimized_item = item.copy()
            optimized_item.update({
                'quantity': optimized_quantity,
                'unit': optimized_unit,
                'original_quantity': quantity,
                'original_unit': unit,
                'conversion_applied': conversion_note
            })
            
            # Ajouter note explicative pour l'utilisateur
            if conversion_note:
                source_details = cls._generate_source_note(item['sources'])
                optimized_item['note'] = f"{conversion_note} ({source_details})"
            else:
                optimized_item['note'] = cls._generate_source_note(item['sources'])
            
            optimized.append(optimized_item)
        
        return optimized

    @classmethod
    def _apply_unit_conversion(
        cls, 
        quantity: float, 
        unit: str, 
        unit_preferences: Dict
    ) -> Tuple[float, str, Optional[str]]:
        """Applique les conversions d'unités selon les seuils et préférences"""
        
        # Vérifier si une conversion est nécessaire selon les seuils
        if unit in cls.AGGREGATION_THRESHOLDS:
            threshold = cls.AGGREGATION_THRESHOLDS[unit]
            
            if quantity >= threshold:
                # Déterminer l'unité cible
                if unit == 'g' and quantity >= 1000:
                    new_quantity = quantity / 1000
                    new_unit = 'kg'
                    conversion_note = f"Converti de {quantity}g en {new_quantity}kg"
                    return new_quantity, new_unit, conversion_note
                
                elif unit == 'ml' and quantity >= 1000:
                    new_quantity = quantity / 1000
                    new_unit = 'L'
                    conversion_note = f"Converti de {quantity}ml en {new_quantity}L"
                    return new_quantity, new_unit, conversion_note
                
                elif unit == 'unités' and quantity >= 12 and quantity % 12 == 0:
                    new_quantity = quantity / 12
                    new_unit = 'douzaine'
                    conversion_note = f"Converti de {int(quantity)} unités en {int(new_quantity)} douzaine(s)"
                    return new_quantity, new_unit, conversion_note
        
        return quantity, unit, None

    @classmethod
    def _generate_source_note(cls, sources: List[Dict]) -> str:
        """Génère une note explicative sur les sources de l'ingrédient"""
        if len(sources) == 1:
            source = sources[0]
            return f"{source['recipe_name']} - {source['day']}"
        
        total_portions = len(sources)
        recipes = list(set(source['recipe_name'] for source in sources))
        
        if len(recipes) == 1:
            return f"{total_portions} portions de {recipes[0]}"
        else:
            return f"{total_portions} portions dans {len(recipes)} recettes"

    @classmethod
    def _group_by_store_categories(cls, ingredients: List[Dict]) -> Dict[str, List[Dict]]:
        """Groupe les ingrédients par rayons de magasin"""
        categorized = defaultdict(list)
        
        for item in ingredients:
            category = item.get('category', 'other')
            store_section = cls.CATEGORY_TO_STORE_SECTION.get(category, 'other')
            categorized[store_section].append(item)
        
        # Trier chaque catégorie par nom d'ingrédient
        for section in categorized:
            categorized[section].sort(key=lambda x: x['name'])
        
        return dict(categorized)

    @classmethod
    def _calculate_estimated_budget(cls, ingredients: List[Dict]) -> Optional[float]:
        """Calcule le budget estimé basé sur les prix unitaires"""
        total_cost = 0
        items_with_price = 0
        
        for item in ingredients:
            unit_price = item.get('unit_price')
            if unit_price:
                total_cost += unit_price * item['quantity']
                items_with_price += 1
        
        if items_with_price > 0:
            # Ajouter une marge pour les articles sans prix (estimation)
            coverage_ratio = items_with_price / len(ingredients)
            if coverage_ratio < 1.0:
                # Extrapoler le coût total
                total_cost = total_cost / coverage_ratio
            
            return round(total_cost, 2)
        
        return None

    @classmethod
    def _generate_aggregation_rules(
        cls, 
        raw_ingredients: List[Dict], 
        optimized_ingredients: List[Dict]
    ) -> Dict[str, Any]:
        """Génère les règles d'agrégation appliquées pour traçabilité"""
        return {
            'total_raw_items': len(raw_ingredients),
            'total_optimized_items': len(optimized_ingredients),
            'conversion_rules_applied': [
                rule for rule in cls.AGGREGATION_THRESHOLDS.keys()
            ],
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0'
        }

    @classmethod
    def _calculate_aggregation_savings(
        cls, 
        raw_ingredients: List[Dict], 
        optimized_ingredients: List[Dict]
    ) -> Dict[str, int]:
        """Calcule les économies réalisées par l'agrégation"""
        return {
            'items_reduced': len(raw_ingredients) - len(optimized_ingredients),
            'aggregation_percentage': round(
                (1 - len(optimized_ingredients) / len(raw_ingredients)) * 100, 1
            ) if raw_ingredients else 0
        }

    @classmethod
    def update_item_status(
        cls,
        shopping_list: ShoppingList,
        item_id: str,
        checked: bool,
        user_id: Optional[str] = None
    ) -> bool:
        """
        Met à jour le statut coché/décoché d'un article
        
        Args:
            shopping_list: Liste de courses à modifier
            item_id: ID de l'article à modifier
            checked: Nouveau statut
            user_id: ID utilisateur pour l'historique
            
        Returns:
            bool: Succès de l'opération
        """
        try:
            checked_items = shopping_list.checked_items.copy()
            old_status = checked_items.get(item_id, False)
            checked_items[item_id] = checked
            
            shopping_list.checked_items = checked_items
            shopping_list.version += 1
            shopping_list.last_updated = datetime.utcnow()
            
            # Enregistrer dans l'historique
            cls._record_shopping_list_change(
                shopping_list.id,
                'item_checked' if checked else 'item_unchecked',
                item_id,
                {'checked': old_status},
                {'checked': checked},
                user_id
            )
            
            # Vérifier si la liste est complète
            items = shopping_list.items
            all_checked = all(
                checked_items.get(str(item.get('id', '')), False) 
                for item in items
            )
            
            if all_checked and not shopping_list.is_completed:
                shopping_list.is_completed = True
                shopping_list.completion_date = datetime.utcnow()
            elif not all_checked and shopping_list.is_completed:
                shopping_list.is_completed = False
                shopping_list.completion_date = None
            
            db.session.commit()
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"Erreur lors de la mise à jour de l'article {item_id}: {e}")
            return False

    @classmethod
    def _record_shopping_list_change(
        cls,
        shopping_list_id: int,
        action: str,
        item_id: Optional[str],
        old_value: Dict,
        new_value: Dict,
        user_id: Optional[str]
    ) -> None:
        """Enregistre une modification dans l'historique"""
        try:
            from models.shopping_history import ShoppingListHistory
            
            ShoppingListHistory.record_action(
                shopping_list_id=shopping_list_id,
                action=action,
                item_id=item_id,
                old_value=old_value,
                new_value=new_value,
                user_id=user_id,
                metadata={'timestamp': datetime.utcnow().isoformat()}
            )
        except Exception as e:
            # Ne pas interrompre le processus principal si l'historique échoue
            print(f"Erreur lors de l'enregistrement de l'historique: {e}")

    @classmethod
    def regenerate_shopping_list(
        cls,
        shopping_list: ShoppingList,
        preserve_checked_items: bool = True
    ) -> Dict[str, Any]:
        """
        Régénère une liste de courses en préservant optionnellement les cases cochées
        
        Args:
            shopping_list: Liste existante à régénérer
            preserve_checked_items: Conserver les cases cochées
            
        Returns:
            Dict: Nouvelle liste générée avec métadonnées
        """
        try:
            # Récupérer le plan de repas associé
            meal_plan = shopping_list.meal_plan
            
            # Sauvegarder l'ancien état si nécessaire
            old_checked_items = shopping_list.checked_items.copy() if preserve_checked_items else {}
            
            # Régénérer la liste
            new_list_data = cls.generate_optimized_shopping_list(meal_plan)
            
            # Restaurer les cases cochées si demandé
            if preserve_checked_items:
                for item in new_list_data['items']:
                    item_id = str(item['id'])
                    if item_id in old_checked_items:
                        item['checked'] = old_checked_items[item_id]
            
            # Mettre à jour la liste existante
            shopping_list.items = new_list_data['items']
            shopping_list.category_grouping = new_list_data['category_grouping']
            shopping_list.estimated_budget = new_list_data['estimated_budget']
            shopping_list.aggregation_rules = new_list_data['aggregation_rules']
            shopping_list.version += 1
            shopping_list.last_updated = datetime.utcnow()
            
            if preserve_checked_items:
                # Reconstruire l'état des cases cochées pour les nouveaux IDs
                new_checked_items = {}
                for item in new_list_data['items']:
                    item_id = str(item['id'])
                    new_checked_items[item_id] = item.get('checked', False)
                shopping_list.checked_items = new_checked_items
            else:
                shopping_list.checked_items = {}
            
            db.session.commit()
            
            return {
                'success': True,
                'shopping_list': shopping_list.to_dict(),
                'statistics': new_list_data['statistics']
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': str(e)
            }

    @classmethod
    def get_shopping_list_statistics(cls, shopping_list: ShoppingList) -> Dict[str, Any]:
        """
        Calcule les statistiques détaillées d'une liste de courses
        
        Args:
            shopping_list: La liste de courses à analyser
            
        Returns:
            Dict: Statistiques complètes de la liste
        """
        try:
            items = shopping_list.items or []
            checked_items = shopping_list.checked_items or {}
            
            total_items = len(items)
            completed_items = sum(1 for item_id, is_checked in checked_items.items() if is_checked)
            
            # Statistiques par catégorie
            category_stats = defaultdict(lambda: {
                'total': 0, 
                'completed': 0, 
                'estimated_cost': 0,
                'items': []
            })
            
            total_estimated_cost = 0
            
            for item in items:
                category = item.get('category', 'other')
                item_id = str(item.get('id', ''))
                
                category_stats[category]['total'] += 1
                category_stats[category]['items'].append(item)
                
                if checked_items.get(item_id, False):
                    category_stats[category]['completed'] += 1
                
                # Coût estimé
                unit_price = item.get('unit_price', 0) or 0
                quantity = item.get('quantity', 0)
                item_cost = unit_price * quantity
                category_stats[category]['estimated_cost'] += item_cost
                total_estimated_cost += item_cost
            
            # Calcul des pourcentages de completion par catégorie
            for category_data in category_stats.values():
                total_cat = category_data['total']
                completed_cat = category_data['completed']
                category_data['completion_percentage'] = (
                    round((completed_cat / total_cat * 100) if total_cat > 0 else 0, 1)
                )
            
            # Statistiques sur les agrégations
            aggregation_info = shopping_list.aggregation_rules or {}
            
            # Informations sur le plan de repas associé
            meal_plan_info = {}
            if shopping_list.meal_plan:
                meal_plan_meals = shopping_list.meal_plan.meals or {}
                total_recipes = len([
                    recipe_id for day_meals in meal_plan_meals.values()
                    for recipe_id in day_meals.values() if recipe_id
                ])
                
                meal_plan_info = {
                    'id': shopping_list.meal_plan_id,
                    'week_start': shopping_list.week_start.isoformat(),
                    'total_recipes': total_recipes,
                    'daily_calories': shopping_list.meal_plan.daily_calories,
                    'daily_protein': shopping_list.meal_plan.daily_protein
                }
            
            # Temps estimé pour faire les courses (basé sur le nombre d'articles et catégories)
            estimated_shopping_time = cls._calculate_estimated_shopping_time(
                total_items, len(category_stats)
            )
            
            return {
                'overview': {
                    'total_items': total_items,
                    'completed_items': completed_items,
                    'completion_percentage': round(
                        (completed_items / total_items * 100) if total_items > 0 else 0, 1
                    ),
                    'estimated_budget': shopping_list.estimated_budget or total_estimated_cost,
                    'calculated_cost': total_estimated_cost,
                    'is_completed': shopping_list.is_completed,
                    'estimated_shopping_time_minutes': estimated_shopping_time,
                    'last_updated': shopping_list.last_updated.isoformat() if shopping_list.last_updated else None,
                    'version': shopping_list.version or 1
                },
                'by_category': dict(category_stats),
                'aggregation_info': aggregation_info,
                'meal_plan_info': meal_plan_info,
                'efficiency_metrics': {
                    'aggregation_reduction': aggregation_info.get('aggregation_savings', {}).get('items_reduced', 0),
                    'items_per_category': round(total_items / len(category_stats) if category_stats else 0, 1),
                    'completion_rate_trend': cls._calculate_completion_trend(shopping_list),
                    'cost_per_item': round(total_estimated_cost / total_items if total_items > 0 else 0, 2)
                }
            }
            
        except Exception as e:
            print(f"Erreur lors du calcul des statistiques: {e}")
            return {
                'overview': {
                    'total_items': 0,
                    'completed_items': 0,
                    'completion_percentage': 0,
                    'estimated_budget': 0,
                    'is_completed': False,
                    'error': str(e)
                }
            }

    @classmethod
    def _calculate_estimated_shopping_time(cls, total_items: int, total_categories: int) -> int:
        """
        Calcule le temps estimé pour faire les courses
        
        Args:
            total_items: Nombre total d'articles
            total_categories: Nombre de rayons différents
            
        Returns:
            int: Temps estimé en minutes
        """
        # Formule basée sur:
        # - 2 minutes par rayon pour se déplacer
        # - 30 secondes par article pour chercher et sélectionner
        # - 5 minutes de temps fixe (parking, caisse, etc.)
        
        travel_time = total_categories * 2  # 2 min par rayon
        selection_time = total_items * 0.5  # 30 sec par article
        fixed_time = 5  # 5 min fixes
        
        return int(travel_time + selection_time + fixed_time)

    @classmethod
    def _calculate_completion_trend(cls, shopping_list: ShoppingList) -> str:
        """
        Calcule la tendance de completion basée sur l'historique
        
        Args:
            shopping_list: La liste de courses
            
        Returns:
            str: 'improving', 'stable', 'declining', 'unknown'
        """
        try:
            from models.shopping_history import ShoppingListHistory
            
            # Récupérer les 10 dernières actions de type check/uncheck
            recent_actions = ShoppingListHistory.query.filter(
                ShoppingListHistory.shopping_list_id == shopping_list.id,
                ShoppingListHistory.action.in_(['item_checked', 'item_unchecked'])
            ).order_by(ShoppingListHistory.timestamp.desc()).limit(10).all()
            
            if len(recent_actions) < 5:
                return 'unknown'
            
            # Calculer le ratio check vs uncheck dans les actions récentes
            checks = sum(1 for action in recent_actions if action.action == 'item_checked')
            unchecks = len(recent_actions) - checks
            
            if checks > unchecks * 2:
                return 'improving'  # Plus de checks que d'unchecks
            elif unchecks > checks * 2:
                return 'declining'  # Plus d'unchecks que de checks
            else:
                return 'stable'
                
        except:
            return 'unknown'

    @classmethod
    def export_shopping_list_data(
        cls,
        shopping_list: ShoppingList,
        export_format: str = 'json',
        include_metadata: bool = True,
        include_checked_items: bool = True
    ) -> Dict[str, Any]:
        """
        Prépare les données d'export pour une liste de courses
        
        Args:
            shopping_list: Liste à exporter
            export_format: Format d'export ('json', 'pdf', 'txt', 'email')
            include_metadata: Inclure les métadonnées
            include_checked_items: Inclure l'état des cases cochées
            
        Returns:
            Dict: Données formatées pour l'export
        """
        try:
            # Données de base
            export_data = {
                'shopping_list': {
                    'id': shopping_list.id,
                    'week_start': shopping_list.week_start.isoformat(),
                    'items': shopping_list.items or [],
                    'is_completed': shopping_list.is_completed,
                    'estimated_budget': shopping_list.estimated_budget
                }
            }
            
            # Ajouter les cases cochées si demandé
            if include_checked_items:
                export_data['shopping_list']['checked_items'] = shopping_list.checked_items or {}
            
            # Ajouter les métadonnées si demandé
            if include_metadata:
                export_data['metadata'] = {
                    'generated_at': datetime.utcnow().isoformat(),
                    'export_format': export_format,
                    'total_items': len(shopping_list.items or []),
                    'completed_items': len([
                        item_id for item_id, is_checked in (shopping_list.checked_items or {}).items()
                        if is_checked
                    ]),
                    'category_grouping': shopping_list.category_grouping or {},
                    'aggregation_rules': shopping_list.aggregation_rules or {},
                    'version': shopping_list.version or 1
                }
                
                # Ajouter les infos du plan de repas
                if shopping_list.meal_plan:
                    export_data['meal_plan'] = {
                        'id': shopping_list.meal_plan_id,
                        'week_start': shopping_list.week_start.isoformat(),
                        'meals': shopping_list.meal_plan.meals or {},
                        'daily_calories': shopping_list.meal_plan.daily_calories,
                        'daily_protein': shopping_list.meal_plan.daily_protein
                    }
            
            # Formatage spécifique selon le type d'export
            if export_format == 'txt' or export_format == 'email':
                export_data['formatted_text'] = cls._format_list_as_text(shopping_list)
            elif export_format == 'pdf':
                export_data['pdf_metadata'] = {
                    'title': f"Liste de courses - Semaine du {shopping_list.week_start.strftime('%d/%m/%Y')}",
                    'author': 'DietTracker',
                    'subject': 'Liste de courses hebdomadaire',
                    'creator': 'DietTracker - Application de planification nutritionnelle'
                }
            
            return {
                'success': True,
                'export_data': export_data,
                'download_info': {
                    'filename': f"liste_courses_{shopping_list.week_start.strftime('%Y%m%d')}.{export_format}",
                    'mime_type': cls._get_mime_type(export_format),
                    'size_estimate': len(str(export_data))
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Erreur lors de la préparation de l'export: {str(e)}"
            }

    @classmethod
    def _format_list_as_text(cls, shopping_list: ShoppingList) -> str:
        """Formate la liste de courses en texte plain"""
        try:
            text_lines = []
            text_lines.append(f"LISTE DE COURSES - Semaine du {shopping_list.week_start.strftime('%d/%m/%Y')}")
            text_lines.append("=" * 60)
            text_lines.append("")
            
            if shopping_list.estimated_budget:
                text_lines.append(f"Budget estimé: {shopping_list.estimated_budget}€")
                text_lines.append("")
            
            # Grouper par catégorie
            categorized = cls._group_by_store_categories(shopping_list.items or [])
            checked_items = shopping_list.checked_items or {}
            
            category_names = {
                'protein': '🥩 PROTÉINES',
                'nuts': '🥜 OLÉAGINEUX',
                'vegetable': '🥬 LÉGUMES FRAIS',
                'fruit': '🍓 FRUITS',
                'dairy': '🥛 PRODUITS LAITIERS',
                'grain': '🌾 CÉRÉALES',
                'condiment': '🫒 CONDIMENTS & ÉPICES',
                'supplement': '💊 COMPLÉMENTS',
                'other': '📦 AUTRES'
            }
            
            for category, items in categorized.items():
                if items:
                    category_name = category_names.get(category, category.upper())
                    text_lines.append(category_name)
                    text_lines.append("-" * len(category_name))
                    
                    for item in items:
                        item_id = str(item.get('id', ''))
                        status = '✓' if checked_items.get(item_id, False) else '☐'
                        name = item.get('name', '')
                        quantity = item.get('quantity', 0)
                        unit = item.get('unit', '')
                        note = item.get('note', '')
                        
                        line = f"{status} {name} - {quantity} {unit}"
                        if note:
                            line += f" ({note})"
                        text_lines.append(line)
                    
                    text_lines.append("")
            
            text_lines.append("=" * 60)
            text_lines.append(f"Généré le {datetime.utcnow().strftime('%d/%m/%Y à %H:%M')}")
            text_lines.append("DietTracker - Application de planification nutritionnelle")
            
            return "\n".join(text_lines)
            
        except Exception as e:
            return f"Erreur lors du formatage: {str(e)}"

    @classmethod
    def _get_mime_type(cls, export_format: str) -> str:
        """Retourne le type MIME pour un format d'export"""
        mime_types = {
            'json': 'application/json',
            'pdf': 'application/pdf',
            'txt': 'text/plain',
            'email': 'text/plain'
        }
        return mime_types.get(export_format, 'application/octet-stream')