from database import db
from datetime import datetime
import json

class Recipe(db.Model):
    __tablename__ = 'recipes'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # breakfast, lunch, dinner, snack
    meal_type = db.Column(db.String(20), nullable=False)  # repas1, repas2, repas3, collation
    
    # Stockage JSON des ingrédients
    ingredients_json = db.Column(db.Text, nullable=False)
    
    # Instructions de préparation
    instructions_json = db.Column(db.Text, nullable=False)
    
    # Temps de préparation et cuisson (en minutes)
    prep_time = db.Column(db.Integer, default=0)
    cook_time = db.Column(db.Integer, default=0)
    servings = db.Column(db.Integer, default=1)
    
    # Valeurs nutritionnelles totales
    total_calories = db.Column(db.Float, default=0)
    total_protein = db.Column(db.Float, default=0)
    total_carbs = db.Column(db.Float, default=0)
    total_fat = db.Column(db.Float, default=0)
    
    # Ustensiles nécessaires
    utensils_json = db.Column(db.Text, nullable=True)
    
    # Tags pour filtrage
    tags_json = db.Column(db.Text, nullable=True)
    
    # Métadonnées
    rating = db.Column(db.Float, default=0)
    is_favorite = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @property
    def ingredients(self):
        return json.loads(self.ingredients_json) if self.ingredients_json else []
    
    @ingredients.setter
    def ingredients(self, value):
        self.ingredients_json = json.dumps(value)
    
    @property
    def instructions(self):
        return json.loads(self.instructions_json) if self.instructions_json else []
    
    @instructions.setter
    def instructions(self, value):
        self.instructions_json = json.dumps(value)
    
    @property
    def utensils(self):
        return json.loads(self.utensils_json) if self.utensils_json else []
    
    @utensils.setter
    def utensils(self, value):
        self.utensils_json = json.dumps(value)
    
    @property
    def tags(self):
        return json.loads(self.tags_json) if self.tags_json else []
    
    @tags.setter
    def tags(self, value):
        self.tags_json = json.dumps(value)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'meal_type': self.meal_type,
            'ingredients': self.ingredients,
            'instructions': self.instructions,
            'prep_time': self.prep_time,
            'cook_time': self.cook_time,
            'servings': self.servings,
            'nutrition_total': {
                'calories': self.total_calories,
                'protein': self.total_protein,
                'carbs': self.total_carbs,
                'fat': self.total_fat
            },
            'utensils': self.utensils,
            'tags': self.tags,
            'rating': self.rating,
            'is_favorite': self.is_favorite,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @staticmethod
    def create_from_dict(data):
        nutrition = data.get('nutrition_total', {})
        recipe = Recipe(
            name=data['name'],
            category=data['category'],
            meal_type=data['meal_type'],
            prep_time=data.get('prep_time', 0),
            cook_time=data.get('cook_time', 0),
            servings=data.get('servings', 1),
            total_calories=nutrition.get('calories', 0),
            total_protein=nutrition.get('protein', 0),
            total_carbs=nutrition.get('carbs', 0),
            total_fat=nutrition.get('fat', 0),
            rating=data.get('rating', 0),
            is_favorite=data.get('is_favorite', False)
        )
        
        recipe.ingredients = data.get('ingredients', [])
        recipe.instructions = data.get('instructions', [])
        recipe.utensils = data.get('utensils', [])
        recipe.tags = data.get('tags', [])
        
        return recipe

