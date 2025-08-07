from marshmallow import Schema, fields, validate, ValidationError, post_load, pre_dump
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from datetime import datetime, date
import json

class NutritionSummarySchema(Schema):
    """Schéma pour le résumé nutritionnel"""
    daily_calories = fields.Float(validate=validate.Range(min=0), allow_none=True)
    daily_protein = fields.Float(validate=validate.Range(min=0), allow_none=True)
    daily_carbs = fields.Float(validate=validate.Range(min=0), allow_none=True)
    daily_fat = fields.Float(validate=validate.Range(min=0), allow_none=True)

class MealTypeSchema(Schema):
    """Schéma pour un type de repas (repas1, collation1, etc.)"""
    repas1 = fields.Integer(allow_none=True, validate=validate.Range(min=1))
    collation1 = fields.Integer(allow_none=True, validate=validate.Range(min=1))
    repas2 = fields.Integer(allow_none=True, validate=validate.Range(min=1))
    collation2 = fields.Integer(allow_none=True, validate=validate.Range(min=1))
    repas3 = fields.Integer(allow_none=True, validate=validate.Range(min=1))

class DayMealsSchema(Schema):
    """Schéma pour les repas d'une journée"""
    monday = fields.Nested(MealTypeSchema, allow_none=True)
    tuesday = fields.Nested(MealTypeSchema, allow_none=True)
    wednesday = fields.Nested(MealTypeSchema, allow_none=True)
    thursday = fields.Nested(MealTypeSchema, allow_none=True)
    friday = fields.Nested(MealTypeSchema, allow_none=True)
    saturday = fields.Nested(MealTypeSchema, allow_none=True)
    sunday = fields.Nested(MealTypeSchema, allow_none=True)

class MealPlanSchema(Schema):
    """Schéma principal pour les plans de repas"""
    id = fields.Integer(dump_only=True)
    user_id = fields.String(
        validate=validate.Length(min=1, max=50),
        allow_none=True
    )
    week_start = fields.Date(
        required=True,
        error_messages={'required': 'La date de début de semaine est requise'}
    )
    
    # Structure des repas
    meals = fields.Nested(
        DayMealsSchema,
        required=True,
        error_messages={'required': 'Les repas sont requis'}
    )
    
    # Résumé nutritionnel (calculé automatiquement)
    nutrition_summary = fields.Nested(NutritionSummarySchema, dump_only=True)
    
    # Métadonnées
    is_active = fields.Boolean(load_default=True)
    created_at = fields.DateTime(dump_only=True, format='iso8601')
    updated_at = fields.DateTime(dump_only=True, format='iso8601')
    
    @pre_dump
    def prepare_data(self, obj, **kwargs):
        """Préparer les données pour la sérialisation"""
        if hasattr(obj, 'daily_calories'):
            obj.nutrition_summary = {
                'daily_calories': obj.daily_calories,
                'daily_protein': obj.daily_protein,
                'daily_carbs': obj.daily_carbs,
                'daily_fat': obj.daily_fat
            }
        return obj
    
    @post_load
    def validate_meal_structure(self, data, **kwargs):
        """Valider la structure des repas"""
        meals = data.get('meals', {})
        
        # Vérifier qu'au moins un jour a des repas
        has_meals = False
        for day_name, day_meals in meals.items():
            if day_meals:
                for meal_type, recipe_id in day_meals.items():
                    if recipe_id:
                        has_meals = True
                        break
                if has_meals:
                    break
        
        if not has_meals:
            raise ValidationError('Au moins un repas doit être planifié')
        
        return data

class MealPlanUpdateSchema(MealPlanSchema):
    """Schéma pour la mise à jour d'un plan de repas (tous les champs optionnels sauf meals)"""
    week_start = fields.Date()
    meals = fields.Nested(DayMealsSchema)

class MealPlanGenerationSchema(Schema):
    """Schéma pour la génération automatique d'un plan de repas"""
    user_id = fields.String(validate=validate.Length(min=1, max=50))
    week_start = fields.Date(load_default=date.today)
    
    # Objectifs nutritionnels pour la génération
    target_calories = fields.Float(
        validate=validate.Range(min=800, max=5000),
        load_default=2000
    )
    target_protein = fields.Float(
        validate=validate.Range(min=50, max=300),
        load_default=150
    )
    target_carbs = fields.Float(
        validate=validate.Range(min=50, max=500),
        load_default=200
    )
    target_fat = fields.Float(
        validate=validate.Range(min=30, max=200),
        load_default=75
    )
    
    # Options de génération
    meal_types_to_include = fields.List(
        fields.String(validate=validate.OneOf(['repas1', 'collation1', 'repas2', 'collation2', 'repas3'])),
        load_default=['repas1', 'repas2', 'repas3']
    )
    max_repeats = fields.Integer(
        validate=validate.Range(min=1, max=7),
        load_default=2,
        description="Nombre maximum de fois qu'une recette peut se répéter dans la semaine"
    )
    preferred_categories = fields.List(
        fields.String(validate=validate.OneOf(['breakfast', 'lunch', 'dinner', 'snack'])),
        allow_none=True,
        description="Catégories de recettes préférées"
    )

class MealPlanQuerySchema(Schema):
    """Schéma pour les paramètres de requête des plans de repas"""
    page = fields.Integer(validate=validate.Range(min=1), load_default=1)
    per_page = fields.Integer(validate=validate.Range(min=1, max=100), load_default=20)
    user_id = fields.String(validate=validate.Length(min=1, max=50))
    week_start = fields.Date()
    is_active = fields.Boolean()
    sort_by = fields.String(
        validate=validate.OneOf(['week_start', 'created_at', 'daily_calories']),
        load_default='week_start'
    )
    order = fields.String(
        validate=validate.OneOf(['asc', 'desc']),
        load_default='desc'
    )

class ShoppingListItemSchema(Schema):
    """Schéma pour un article de liste de courses"""
    ingredient_id = fields.Integer(required=True, validate=validate.Range(min=1))
    name = fields.String(required=True, validate=validate.Length(min=1, max=200))
    quantity = fields.Float(required=True, validate=validate.Range(min=0.1))
    unit = fields.String(required=True, validate=validate.Length(min=1, max=20))
    category = fields.String(validate=validate.Length(min=1, max=100))
    checked = fields.Boolean(load_default=False)

class ShoppingListSchema(Schema):
    """Schéma pour les listes de courses"""
    id = fields.Integer(dump_only=True)
    meal_plan_id = fields.Integer(
        required=True,
        validate=validate.Range(min=1),
        error_messages={'required': 'L\'ID du plan de repas est requis'}
    )
    week_start = fields.Date(required=True)
    
    items = fields.List(
        fields.Nested(ShoppingListItemSchema),
        required=True,
        validate=validate.Length(min=1),
        error_messages={'required': 'Au moins un article est requis'}
    )
    
    generated_date = fields.DateTime(dump_only=True, format='iso8601')
    is_completed = fields.Boolean(load_default=False)

class ShoppingListUpdateSchema(Schema):
    """Schéma pour la mise à jour d'une liste de courses"""
    items = fields.List(fields.Nested(ShoppingListItemSchema))
    is_completed = fields.Boolean()

# Instances des schémas
meal_plan_schema = MealPlanSchema()
meal_plans_schema = MealPlanSchema(many=True)
meal_plan_update_schema = MealPlanUpdateSchema()
meal_plan_generation_schema = MealPlanGenerationSchema()
meal_plan_query_schema = MealPlanQuerySchema()

shopping_list_schema = ShoppingListSchema()
shopping_lists_schema = ShoppingListSchema(many=True)
shopping_list_update_schema = ShoppingListUpdateSchema()