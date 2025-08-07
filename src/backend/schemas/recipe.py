from marshmallow import Schema, fields, validate, ValidationError, post_load, pre_dump
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from models.recipe import Recipe

class IngredientSchema(Schema):
    """Schéma pour un ingrédient dans une recette"""
    ingredient_id = fields.Integer(required=True, validate=validate.Range(min=1))
    name = fields.String(required=True, validate=validate.Length(min=1, max=200))
    quantity = fields.Float(required=True, validate=validate.Range(min=0.1))
    unit = fields.String(required=True, validate=validate.Length(min=1, max=20))

class InstructionSchema(Schema):
    """Schéma pour une instruction de préparation"""
    step = fields.Integer(required=True, validate=validate.Range(min=1))
    description = fields.String(required=True, validate=validate.Length(min=1, max=500))

class NutritionSchema(Schema):
    """Schéma pour les valeurs nutritionnelles"""
    calories = fields.Float(validate=validate.Range(min=0), allow_none=True)
    protein = fields.Float(validate=validate.Range(min=0), allow_none=True)
    carbs = fields.Float(validate=validate.Range(min=0), allow_none=True)
    fat = fields.Float(validate=validate.Range(min=0), allow_none=True)

# Schemas pour les conseils de chef (US1.4)
class CookingStepSchema(Schema):
    """Schéma pour une étape de cuisson détaillée"""
    step = fields.Integer(required=True, validate=validate.Range(min=1))
    title = fields.String(required=True, validate=validate.Length(min=1, max=100))
    description = fields.String(required=True, validate=validate.Length(min=1, max=1000))
    duration_minutes = fields.Integer(validate=validate.Range(min=0))
    temperature = fields.String(validate=validate.Length(max=50))
    technique = fields.String(validate=validate.Length(max=100))

class ChefTipSchema(Schema):
    """Schéma pour un conseil de chef"""
    id = fields.String(required=True)
    type = fields.String(validate=validate.OneOf(['tip', 'warning', 'secret', 'alternative']))
    title = fields.String(required=True, validate=validate.Length(min=1, max=100))
    description = fields.String(required=True, validate=validate.Length(min=1, max=500))
    importance = fields.String(validate=validate.OneOf(['low', 'medium', 'high']))

class VisualCueSchema(Schema):
    """Schéma pour un indice visuel"""
    step_number = fields.Integer(required=True, validate=validate.Range(min=1))
    description = fields.String(required=True, validate=validate.Length(min=1, max=200))
    what_to_look_for = fields.String(required=True, validate=validate.Length(min=1, max=300))

class MediaReferenceSchema(Schema):
    """Schéma pour les références média"""
    id = fields.String(required=True)
    type = fields.String(validate=validate.OneOf(['photo', 'video', 'animation']))
    url = fields.String(validate=validate.Length(max=500))
    step_number = fields.Integer(validate=validate.Range(min=1))
    description = fields.String(validate=validate.Length(max=200))
    alt_text = fields.String(validate=validate.Length(max=100))

class RecipeSchema(Schema):
    """Schéma principal pour les recettes"""
    id = fields.Integer(dump_only=True)
    name = fields.String(
        required=True, 
        validate=validate.Length(min=1, max=200),
        error_messages={'required': 'Le nom de la recette est requis'}
    )
    category = fields.String(
        required=True,
        validate=validate.OneOf(['breakfast', 'lunch', 'dinner', 'snack']),
        error_messages={'required': 'La catégorie est requise'}
    )
    meal_type = fields.String(
        required=True,
        validate=validate.OneOf(['repas1', 'repas2', 'repas3', 'collation']),
        error_messages={'required': 'Le type de repas est requis'}
    )
    
    # Listes validées
    ingredients = fields.List(
        fields.Nested(IngredientSchema),
        required=True,
        validate=validate.Length(min=1),
        error_messages={'required': 'Au moins un ingrédient est requis'}
    )
    instructions = fields.List(
        fields.Nested(InstructionSchema),
        required=True,
        validate=validate.Length(min=1),
        error_messages={'required': 'Au moins une instruction est requise'}
    )
    utensils = fields.List(
        fields.String(validate=validate.Length(min=1, max=100)),
        load_default=[]
    )
    tags = fields.List(
        fields.String(validate=validate.Length(min=1, max=50)),
        load_default=[]
    )
    
    # Temps et portions
    prep_time = fields.Integer(
        validate=validate.Range(min=0, max=1440),  # Max 24 heures
        load_default=0
    )
    cook_time = fields.Integer(
        validate=validate.Range(min=0, max=1440),  # Max 24 heures
        load_default=0
    )
    servings = fields.Integer(
        validate=validate.Range(min=1, max=50),
        load_default=1
    )
    
    # Nutrition (calculée automatiquement)
    nutrition_total = fields.Nested(NutritionSchema, dump_only=True)
    
    # Conseils de chef détaillés (US1.4)
    chef_instructions = fields.List(
        fields.String(validate=validate.Length(min=1, max=1000)),
        load_default=[]
    )
    cooking_steps = fields.List(
        fields.Nested(CookingStepSchema),
        load_default=[]
    )
    chef_tips = fields.List(
        fields.Nested(ChefTipSchema),
        load_default=[]
    )
    visual_cues = fields.List(
        fields.Nested(VisualCueSchema),
        load_default=[]
    )
    timing_details = fields.Dict(load_default={})  # Structure flexible pour les détails de timing
    media_references = fields.List(
        fields.Nested(MediaReferenceSchema),
        load_default=[]
    )
    difficulty_level = fields.String(
        validate=validate.OneOf(['beginner', 'intermediate', 'advanced']),
        load_default='beginner'
    )
    has_chef_mode = fields.Boolean(load_default=False)
    
    # Métadonnées
    rating = fields.Float(
        validate=validate.Range(min=0, max=5),
        load_default=0
    )
    is_favorite = fields.Boolean(load_default=False)
    
    # Dates (en lecture seule)
    created_at = fields.DateTime(dump_only=True, format='iso8601')
    updated_at = fields.DateTime(dump_only=True, format='iso8601')
    
    @pre_dump
    def prepare_nutrition(self, obj, **kwargs):
        """Préparer les données nutritionnelles pour la sérialisation"""
        if hasattr(obj, 'total_calories'):
            obj.nutrition_total = {
                'calories': obj.total_calories,
                'protein': obj.total_protein,
                'carbs': obj.total_carbs,
                'fat': obj.total_fat
            }
        return obj
    
    @post_load
    def validate_instructions_order(self, data, **kwargs):
        """Valider l'ordre des instructions"""
        if 'instructions' in data:
            steps = [instruction['step'] for instruction in data['instructions']]
            expected_steps = list(range(1, len(steps) + 1))
            if sorted(steps) != expected_steps:
                raise ValidationError('Les étapes d\'instructions doivent être numérotées de 1 à N sans manquer de numéro')
        return data

class RecipeUpdateSchema(RecipeSchema):
    """Schéma pour la mise à jour d'une recette (tous les champs optionnels)"""
    name = fields.String(validate=validate.Length(min=1, max=200))
    category = fields.String(validate=validate.OneOf(['breakfast', 'lunch', 'dinner', 'snack']))
    meal_type = fields.String(validate=validate.OneOf(['repas1', 'repas2', 'repas3', 'collation']))
    ingredients = fields.List(fields.Nested(IngredientSchema), validate=validate.Length(min=1))
    instructions = fields.List(fields.Nested(InstructionSchema), validate=validate.Length(min=1))
    # Champs chef optionnels pour mise à jour
    chef_instructions = fields.List(fields.String(validate=validate.Length(min=1, max=1000)))
    cooking_steps = fields.List(fields.Nested(CookingStepSchema))
    chef_tips = fields.List(fields.Nested(ChefTipSchema))
    visual_cues = fields.List(fields.Nested(VisualCueSchema))
    timing_details = fields.Dict()
    media_references = fields.List(fields.Nested(MediaReferenceSchema))
    difficulty_level = fields.String(validate=validate.OneOf(['beginner', 'intermediate', 'advanced']))
    has_chef_mode = fields.Boolean()

class RecipeQuerySchema(Schema):
    """Schéma pour les paramètres de requête"""
    page = fields.Integer(validate=validate.Range(min=1), load_default=1)
    per_page = fields.Integer(validate=validate.Range(min=1, max=100), load_default=20)
    category = fields.String(validate=validate.OneOf(['breakfast', 'lunch', 'dinner', 'snack']))
    meal_type = fields.String(validate=validate.OneOf(['repas1', 'repas2', 'repas3', 'collation']))
    search = fields.String(validate=validate.Length(min=1, max=200))
    max_calories = fields.Float(validate=validate.Range(min=0))
    max_time = fields.Integer(validate=validate.Range(min=0))
    is_favorite = fields.Boolean()
    tags = fields.String()  # Tags séparés par virgule
    difficulty_level = fields.String(validate=validate.OneOf(['beginner', 'intermediate', 'advanced']))
    has_chef_mode = fields.Boolean()
    sort_by = fields.String(
        validate=validate.OneOf(['name', 'created_at', 'rating', 'prep_time', 'total_calories', 'difficulty_level']),
        load_default='created_at'
    )
    order = fields.String(
        validate=validate.OneOf(['asc', 'desc']),
        load_default='desc'
    )

# Instances des schémas
recipe_schema = RecipeSchema()
recipes_schema = RecipeSchema(many=True)
recipe_update_schema = RecipeUpdateSchema()
recipe_query_schema = RecipeQuerySchema()