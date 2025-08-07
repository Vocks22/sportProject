from database import db
from datetime import datetime, date
from sqlalchemy.orm import relationship
import json

class MealPlan(db.Model):
    __tablename__ = 'meal_plans'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Pour future authentification
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
        
        # Handle week_start - can be string or date object
        week_start_value = data.get('week_start')
        if week_start_value:
            if isinstance(week_start_value, str):
                week_start_date = datetime.fromisoformat(week_start_value).date()
            elif isinstance(week_start_value, date):
                week_start_date = week_start_value
            else:
                week_start_date = date.today()
        else:
            week_start_date = date.today()
        
        meal_plan = MealPlan(
            user_id=data.get('user_id'),
            week_start=week_start_date,
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
    
    # Stockage JSON des articles avec état persistant (US1.5)
    items_json = db.Column(db.Text, nullable=False)
    
    # Nouveaux champs pour US1.5 - Liste Interactive
    checked_items_json = db.Column(db.Text, default='{}')  # État des cases cochées
    aggregation_rules_json = db.Column(db.Text, nullable=True)  # Règles d'agrégation
    category_grouping_json = db.Column(db.Text, nullable=True)  # Groupement par rayon
    estimated_budget = db.Column(db.Float, nullable=True)  # Budget estimé
    
    # Métadonnées étendues
    generated_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_completed = db.Column(db.Boolean, default=False)
    completion_date = db.Column(db.DateTime, nullable=True)
    
    # Version pour gestion de conflits
    version = db.Column(db.Integer, default=1)
    
    # Relation avec MealPlan
    meal_plan = db.relationship('MealPlan', backref=db.backref('shopping_lists', lazy=True))
    
    @property
    def items(self):
        return json.loads(self.items_json) if self.items_json else []
    
    @items.setter
    def items(self, value):
        self.items_json = json.dumps(value)
    
    # Nouvelles propriétés pour US1.5
    @property
    def checked_items(self):
        return json.loads(self.checked_items_json) if self.checked_items_json else {}
    
    @checked_items.setter
    def checked_items(self, value):
        self.checked_items_json = json.dumps(value)
    
    @property
    def aggregation_rules(self):
        return json.loads(self.aggregation_rules_json) if self.aggregation_rules_json else {}
    
    @aggregation_rules.setter
    def aggregation_rules(self, value):
        self.aggregation_rules_json = json.dumps(value)
    
    @property
    def category_grouping(self):
        return json.loads(self.category_grouping_json) if self.category_grouping_json else {}
    
    @category_grouping.setter
    def category_grouping(self, value):
        self.category_grouping_json = json.dumps(value)
    
    def to_dict(self):
        return {
            'id': self.id,
            'meal_plan_id': self.meal_plan_id,
            'week_start': self.week_start.isoformat() if self.week_start else None,
            'items': self.items,
            # Nouveaux champs US1.5
            'checked_items': self.checked_items,
            'aggregation_rules': self.aggregation_rules,
            'category_grouping': self.category_grouping,
            'estimated_budget': self.estimated_budget,
            # Métadonnées étendues
            'generated_date': self.generated_date.isoformat() if self.generated_date else None,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None,
            'is_completed': self.is_completed,
            'completion_date': self.completion_date.isoformat() if self.completion_date else None,
            'version': self.version
        }
    
    @staticmethod
    def create_from_dict(data):
        # Handle week_start - can be string or date object
        week_start_value = data.get('week_start')
        if week_start_value:
            if isinstance(week_start_value, str):
                week_start_date = datetime.fromisoformat(week_start_value).date()
            elif isinstance(week_start_value, date):
                week_start_date = week_start_value
            else:
                week_start_date = date.today()
        else:
            week_start_date = date.today()
        
        shopping_list = ShoppingList(
            meal_plan_id=data['meal_plan_id'],
            week_start=week_start_date,
            is_completed=data.get('is_completed', False)
        )
        
        shopping_list.items = data.get('items', [])
        return shopping_list

