"""
Service d'ajustement des portions pour l'US1.7 : Profil Utilisateur Réel
Ajuste automatiquement les portions des recettes selon les besoins nutritionnels individuels
"""

from typing import Dict, List, Any, Optional, Tuple
import logging
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

from models.user import User
from models.recipe import Recipe, RecipeIngredient
from services.nutrition_calculator_service import nutrition_calculator, NutritionCalculationResult

# Configuration du logger
logger = logging.getLogger(__name__)


@dataclass
class PortionAdjustment:
    """Résultat d'ajustement de portions"""
    original_servings: int
    adjusted_servings: float
    multiplier: float
    user_id: int
    recipe_id: int
    nutrition_profile: Dict[str, Any]
    adjusted_ingredients: List[Dict[str, Any]]
    adjusted_nutrition: Dict[str, float]
    rationale: str


class PortionAdjustmentService:
    """Service d'ajustement automatique des portions"""
    
    # Constantes
    MIN_MULTIPLIER = 0.25  # Minimum 25% de la recette originale
    MAX_MULTIPLIER = 4.0   # Maximum 400% de la recette originale
    PRECISION_DIGITS = 2   # Précision des calculs
    
    # Seuils d'ajustement
    CALORIE_TOLERANCE = 0.10  # 10% de tolérance
    MACRO_TOLERANCE = 0.15    # 15% de tolérance pour macros
    
    def __init__(self):
        """Initialise le service"""
        logger.info("PortionAdjustmentService initialisé")
    
    def adjust_recipe_for_user(
        self,
        recipe: Recipe,
        user: User,
        target_meal_type: str = "main",
        nutrition_profile: Optional[NutritionCalculationResult] = None
    ) -> PortionAdjustment:
        """
        Ajuste une recette pour les besoins spécifiques d'un utilisateur
        
        Args:
            recipe: Recette à ajuster
            user: Utilisateur pour qui ajuster
            target_meal_type: Type de repas (main, snack, side)
            nutrition_profile: Profil nutritionnel (optionnel, calculé si absent)
            
        Returns:
            PortionAdjustment: Détails de l'ajustement effectué
        """
        if not nutrition_profile:
            nutrition_profile = nutrition_calculator.calculate_nutrition_profile(user)
        
        # Calculer les besoins caloriques pour ce type de repas
        target_calories = self._calculate_meal_target_calories(
            nutrition_profile.adjusted_calories, 
            target_meal_type
        )
        
        # Calculer le multiplicateur de portions
        multiplier = self._calculate_portion_multiplier(
            recipe, 
            target_calories,
            nutrition_profile
        )
        
        # Ajuster les ingrédients
        adjusted_ingredients = self._adjust_recipe_ingredients(recipe, multiplier)
        
        # Calculer la nutrition ajustée
        adjusted_nutrition = self._calculate_adjusted_nutrition(recipe, multiplier)
        
        # Calculer le nombre de portions ajusté
        adjusted_servings = recipe.servings * multiplier
        
        # Générer la justification
        rationale = self._generate_adjustment_rationale(
            recipe, multiplier, target_calories, nutrition_profile
        )
        
        result = PortionAdjustment(
            original_servings=recipe.servings,
            adjusted_servings=round(adjusted_servings, 1),
            multiplier=multiplier,
            user_id=user.id,
            recipe_id=recipe.id,
            nutrition_profile=nutrition_profile.to_dict(),
            adjusted_ingredients=adjusted_ingredients,
            adjusted_nutrition=adjusted_nutrition,
            rationale=rationale
        )
        
        logger.info(f"Recette {recipe.id} ajustée pour utilisateur {user.id}: "
                   f"multiplier={multiplier}, portions={adjusted_servings}")
        
        return result
    
    def adjust_meal_plan_portions(
        self,
        recipes: List[Recipe],
        user: User,
        meal_distribution: Optional[Dict[str, float]] = None
    ) -> Dict[int, PortionAdjustment]:
        """
        Ajuste les portions d'un plan de repas complet
        
        Args:
            recipes: Liste des recettes du plan
            user: Utilisateur pour qui ajuster
            meal_distribution: Distribution calorique par repas (optionnel)
            
        Returns:
            Dict[int, PortionAdjustment]: Ajustements par recipe_id
        """
        if not meal_distribution:
            meal_distribution = {
                'breakfast': 0.25,   # 25% des calories
                'lunch': 0.35,       # 35% des calories
                'dinner': 0.30,      # 30% des calories
                'snack': 0.10        # 10% des calories
            }
        
        nutrition_profile = nutrition_calculator.calculate_nutrition_profile(user)
        adjustments = {}
        
        # Classifier les recettes par type de repas (basé sur les tags ou nom)
        recipe_types = self._classify_recipes_by_meal_type(recipes)
        
        for recipe in recipes:
            meal_type = recipe_types.get(recipe.id, 'main')
            
            adjustment = self.adjust_recipe_for_user(
                recipe=recipe,
                user=user,
                target_meal_type=meal_type,
                nutrition_profile=nutrition_profile
            )
            
            adjustments[recipe.id] = adjustment
        
        logger.info(f"Plan de repas ajusté pour utilisateur {user.id}: {len(adjustments)} recettes")
        return adjustments
    
    def _calculate_meal_target_calories(self, daily_calories: float, meal_type: str) -> float:
        """Calcule les calories cibles pour un type de repas"""
        
        meal_percentages = {
            'breakfast': 0.25,
            'lunch': 0.35,
            'dinner': 0.30,
            'snack': 0.10,
            'main': 0.35,     # Repas principal
            'side': 0.15,     # Accompagnement
            'dessert': 0.08   # Dessert
        }
        
        percentage = meal_percentages.get(meal_type, 0.25)
        return daily_calories * percentage
    
    def _calculate_portion_multiplier(
        self,
        recipe: Recipe,
        target_calories: float,
        nutrition_profile: NutritionCalculationResult
    ) -> float:
        """Calcule le multiplicateur de portions optimal"""
        
        # Calories par portion de la recette originale
        if recipe.servings <= 0:
            recipe_calories_per_serving = recipe.calories or 400  # Défaut
        else:
            recipe_calories_per_serving = (recipe.calories or 400) / recipe.servings
        
        # Multiplicateur basique basé sur les calories
        base_multiplier = target_calories / recipe_calories_per_serving
        
        # Ajustements basés sur les macros si disponibles
        macro_adjustments = []
        
        if recipe.protein and nutrition_profile.protein_target:
            protein_per_serving = recipe.protein / recipe.servings
            target_protein_per_meal = nutrition_profile.protein_target * 0.25  # 25% par repas
            protein_multiplier = target_protein_per_meal / protein_per_serving
            macro_adjustments.append(protein_multiplier)
        
        if recipe.carbs and nutrition_profile.carbs_target:
            carbs_per_serving = recipe.carbs / recipe.servings
            target_carbs_per_meal = nutrition_profile.carbs_target * 0.25
            carbs_multiplier = target_carbs_per_meal / carbs_per_serving
            macro_adjustments.append(carbs_multiplier)
        
        if recipe.fat and nutrition_profile.fat_target:
            fat_per_serving = recipe.fat / recipe.servings
            target_fat_per_meal = nutrition_profile.fat_target * 0.25
            fat_multiplier = target_fat_per_meal / fat_per_serving
            macro_adjustments.append(fat_multiplier)
        
        # Si on a des données macro, faire une moyenne pondérée
        if macro_adjustments:
            # Privilégier le multiplier calorique mais tenir compte des macros
            avg_macro_multiplier = sum(macro_adjustments) / len(macro_adjustments)
            final_multiplier = (base_multiplier * 0.7) + (avg_macro_multiplier * 0.3)
        else:
            final_multiplier = base_multiplier
        
        # Appliquer les limites
        final_multiplier = max(self.MIN_MULTIPLIER, min(self.MAX_MULTIPLIER, final_multiplier))
        
        # Arrondir à une précision raisonnable
        return round(final_multiplier, 2)
    
    def _adjust_recipe_ingredients(self, recipe: Recipe, multiplier: float) -> List[Dict[str, Any]]:
        """Ajuste les quantités d'ingrédients selon le multiplicateur"""
        
        adjusted_ingredients = []
        
        for ingredient in recipe.ingredients:
            # Calculer la nouvelle quantité
            original_quantity = float(ingredient.quantity)
            adjusted_quantity = original_quantity * multiplier
            
            # Arrondir intelligemment selon le type d'ingrédient
            adjusted_quantity = self._smart_round_quantity(adjusted_quantity, ingredient.unit)
            
            adjusted_ingredient = {
                'ingredient_id': ingredient.ingredient_id,
                'name': ingredient.ingredient.name if ingredient.ingredient else 'Unknown',
                'original_quantity': original_quantity,
                'adjusted_quantity': adjusted_quantity,
                'unit': ingredient.unit,
                'multiplier_applied': multiplier
            }
            
            adjusted_ingredients.append(adjusted_ingredient)
        
        return adjusted_ingredients
    
    def _smart_round_quantity(self, quantity: float, unit: str) -> float:
        """Arrondit les quantités de manière intelligente selon l'unité"""
        
        # Unités liquides - arrondir à 25ml près si > 100ml
        if unit.lower() in ['ml', 'millilitre', 'millilitres']:
            if quantity >= 100:
                return round(quantity / 25) * 25
            elif quantity >= 10:
                return round(quantity, 0)
            else:
                return round(quantity, 1)
        
        # Unités de poids - arrondir selon la taille
        elif unit.lower() in ['g', 'gramme', 'grammes']:
            if quantity >= 100:
                return round(quantity / 5) * 5  # Arrondir à 5g près
            elif quantity >= 10:
                return round(quantity, 0)
            else:
                return round(quantity, 1)
        
        # Kilogrammes
        elif unit.lower() in ['kg', 'kilogramme', 'kilogrammes']:
            return round(quantity, 2)
        
        # Unités de volume sec
        elif unit.lower() in ['l', 'litre', 'litres']:
            if quantity >= 1:
                return round(quantity, 1)
            else:
                return round(quantity, 2)
        
        # Cuillères et tasses
        elif unit.lower() in ['cuillère', 'cuillères', 'c.', 'cs', 'cc', 'tasse', 'tasses']:
            if quantity >= 1:
                return round(quantity * 4) / 4  # Arrondir au 1/4 près
            else:
                return round(quantity, 2)
        
        # Pièces/unités
        elif unit.lower() in ['pièce', 'pièces', 'unité', 'unités', '']:
            if quantity >= 1:
                return round(quantity, 1)
            else:
                return round(quantity, 2)
        
        # Défaut
        else:
            return round(quantity, 2)
    
    def _calculate_adjusted_nutrition(self, recipe: Recipe, multiplier: float) -> Dict[str, float]:
        """Calcule les valeurs nutritionnelles ajustées"""
        
        return {
            'calories': round((recipe.calories or 0) * multiplier, 1),
            'protein': round((recipe.protein or 0) * multiplier, 1),
            'carbs': round((recipe.carbs or 0) * multiplier, 1),
            'fat': round((recipe.fat or 0) * multiplier, 1),
            'fiber': round((recipe.fiber or 0) * multiplier, 1),
            'sodium': round((recipe.sodium or 0) * multiplier, 1),
            'sugar': round((recipe.sugar or 0) * multiplier, 1)
        }
    
    def _classify_recipes_by_meal_type(self, recipes: List[Recipe]) -> Dict[int, str]:
        """Classifie les recettes par type de repas basé sur les indices disponibles"""
        
        classification = {}
        
        for recipe in recipes:
            meal_type = 'main'  # Défaut
            
            # Analyser le nom de la recette
            name_lower = recipe.name.lower()
            
            if any(word in name_lower for word in ['petit-déjeuner', 'breakfast', 'matin']):
                meal_type = 'breakfast'
            elif any(word in name_lower for word in ['collation', 'snack', 'goûter']):
                meal_type = 'snack'
            elif any(word in name_lower for word in ['dessert', 'gâteau', 'mousse', 'crème']):
                meal_type = 'dessert'
            elif any(word in name_lower for word in ['accompagnement', 'garniture', 'side']):
                meal_type = 'side'
            elif any(word in name_lower for word in ['déjeuner', 'lunch', 'midi']):
                meal_type = 'lunch'
            elif any(word in name_lower for word in ['dîner', 'dinner', 'soir']):
                meal_type = 'dinner'
            
            # Analyser les tags si disponibles
            if hasattr(recipe, 'tags') and recipe.tags:
                tags_lower = ' '.join(recipe.tags).lower()
                if 'breakfast' in tags_lower:
                    meal_type = 'breakfast'
                elif 'snack' in tags_lower:
                    meal_type = 'snack'
                elif 'dessert' in tags_lower:
                    meal_type = 'dessert'
                elif 'side' in tags_lower:
                    meal_type = 'side'
            
            classification[recipe.id] = meal_type
        
        return classification
    
    def _generate_adjustment_rationale(
        self,
        recipe: Recipe,
        multiplier: float,
        target_calories: float,
        nutrition_profile: NutritionCalculationResult
    ) -> str:
        """Génère une explication de l'ajustement effectué"""
        
        original_calories_per_serving = (recipe.calories or 0) / (recipe.servings or 1)
        
        if multiplier > 1.2:
            reason = f"Portions augmentées de {int((multiplier - 1) * 100)}% pour atteindre vos besoins caloriques ({target_calories:.0f} cal visées vs {original_calories_per_serving:.0f} cal par portion originale)"
        elif multiplier < 0.8:
            reason = f"Portions réduites de {int((1 - multiplier) * 100)}% pour respecter vos objectifs caloriques ({target_calories:.0f} cal visées vs {original_calories_per_serving:.0f} cal par portion originale)"
        else:
            reason = f"Portions ajustées légèrement ({multiplier:.1f}x) pour optimiser l'équilibre nutritionnel selon votre profil"
        
        # Ajouter des informations sur les objectifs
        goal_info = ""
        if hasattr(nutrition_profile, 'adjusted_calories'):
            daily_calories = nutrition_profile.adjusted_calories
            if daily_calories < 1800:
                goal_info = " (objectif de perte de poids)"
            elif daily_calories > 2500:
                goal_info = " (objectif de prise de masse)"
            else:
                goal_info = " (objectif de maintien)"
        
        return reason + goal_info
    
    def calculate_shopping_list_adjustments(
        self,
        adjustments: Dict[int, PortionAdjustment],
        recipes: List[Recipe]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Calcule les ajustements pour la liste de courses basés sur les portions ajustées
        
        Returns:
            Dict avec les ingrédients et leurs quantités ajustées totales
        """
        
        shopping_adjustments = {}
        
        for recipe in recipes:
            if recipe.id not in adjustments:
                continue
                
            adjustment = adjustments[recipe.id]
            
            for adj_ingredient in adjustment.adjusted_ingredients:
                ingredient_name = adj_ingredient['name']
                unit = adj_ingredient['unit']
                adjusted_quantity = adj_ingredient['adjusted_quantity']
                
                key = f"{ingredient_name}_{unit}"
                
                if key not in shopping_adjustments:
                    shopping_adjustments[key] = {
                        'name': ingredient_name,
                        'unit': unit,
                        'total_quantity': 0,
                        'recipes': []
                    }
                
                shopping_adjustments[key]['total_quantity'] += adjusted_quantity
                shopping_adjustments[key]['recipes'].append({
                    'recipe_id': recipe.id,
                    'recipe_name': recipe.name,
                    'quantity': adjusted_quantity
                })
        
        # Arrondir les totaux
        for key, data in shopping_adjustments.items():
            data['total_quantity'] = self._smart_round_quantity(
                data['total_quantity'], 
                data['unit']
            )
        
        return shopping_adjustments
    
    def get_adjustment_analytics(
        self, 
        adjustments: Dict[int, PortionAdjustment]
    ) -> Dict[str, Any]:
        """Génère des analytics sur les ajustements effectués"""
        
        if not adjustments:
            return {}
        
        multipliers = [adj.multiplier for adj in adjustments.values()]
        
        analytics = {
            'total_recipes_adjusted': len(adjustments),
            'average_multiplier': round(sum(multipliers) / len(multipliers), 2),
            'min_multiplier': min(multipliers),
            'max_multiplier': max(multipliers),
            'recipes_increased': len([m for m in multipliers if m > 1.1]),
            'recipes_decreased': len([m for m in multipliers if m < 0.9]),
            'recipes_unchanged': len([m for m in multipliers if 0.9 <= m <= 1.1]),
            'total_calorie_adjustment': sum([
                adj.adjusted_nutrition['calories'] - 
                (adj.adjusted_nutrition['calories'] / adj.multiplier)
                for adj in adjustments.values()
            ])
        }
        
        return analytics


# Instance globale du service
portion_adjustment = PortionAdjustmentService()