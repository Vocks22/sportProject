from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
import json

db = SQLAlchemy()

class MealPlan(db.Model):
    __tablename__ = 'meal_plans'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), nullable=True)  # Pour future authentification
    week_start = db.Column(db.Date, nullable=False)
    
    # Stockage JSON des repas pour chaque jour
    meals_json = db.Column(db.Text, nullable=False)
    
    # Résumé nutritionnel
    daily_calories = db.Column(db.Float, default=0)
    daily_protein = db.Column(db.Float, default=0)
    daily_carbs = db.Column(db.Float, default=0)
    daily_fat = db.Column(db.Float, default=0)
    
    # Métadonnées
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @property
    def meals(self):
        return json.loads(self.meals_json) if self.meals_json else {}
    
    @meals.setter
    def meals(self, value):
        self.meals_json = json.dumps(value)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'week_start': self.week_start.isoformat() if self.week_start else None,
            'meals': self.meals,
            'nutrition_summary': {
                'daily_calories': self.daily_calories,
                'daily_protein': self.daily_protein,
                'daily_carbs': self.daily_carbs,
                'daily_fat': self.daily_fat
            },
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @staticmethod
    def create_from_dict(data):
        nutrition = data.get('nutrition_summary', {})
        meal_plan = MealPlan(
            user_id=data.get('user_id'),
            week_start=datetime.fromisoformat(data['week_start']).date() if data.get('week_start') else date.today(),
            daily_calories=nutrition.get('daily_calories', 0),
            daily_protein=nutrition.get('daily_protein', 0),
            daily_carbs=nutrition.get('daily_carbs', 0),
            daily_fat=nutrition.get('daily_fat', 0),
            is_active=data.get('is_active', True)
        )
        
        meal_plan.meals = data.get('meals', {})
        return meal_plan


class ShoppingList(db.Model):
    __tablename__ = 'shopping_lists'
    
    id = db.Column(db.Integer, primary_key=True)
    meal_plan_id = db.Column(db.Integer, db.ForeignKey('meal_plans.id'), nullable=False)
    week_start = db.Column(db.Date, nullable=False)
    
    # Stockage JSON des articles
    items_json = db.Column(db.Text, nullable=False)
    
    # Métadonnées
    generated_date = db.Column(db.DateTime, default=datetime.utcnow)
    is_completed = db.Column(db.Boolean, default=False)
    
    # Relation avec MealPlan
    meal_plan = db.relationship('MealPlan', backref=db.backref('shopping_lists', lazy=True))
    
    @property
    def items(self):
        return json.loads(self.items_json) if self.items_json else []
    
    @items.setter
    def items(self, value):
        self.items_json = json.dumps(value)
    
    def to_dict(self):
        return {
            'id': self.id,
            'meal_plan_id': self.meal_plan_id,
            'week_start': self.week_start.isoformat() if self.week_start else None,
            'items': self.items,
            'generated_date': self.generated_date.isoformat() if self.generated_date else None,
            'is_completed': self.is_completed
        }
    
    @staticmethod
    def create_from_dict(data):
        shopping_list = ShoppingList(
            meal_plan_id=data['meal_plan_id'],
            week_start=datetime.fromisoformat(data['week_start']).date() if data.get('week_start') else date.today(),
            is_completed=data.get('is_completed', False)
        )
        
        shopping_list.items = data.get('items', [])
        return shopping_list

