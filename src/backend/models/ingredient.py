from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Ingredient(db.Model):
    __tablename__ = 'ingredients'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # protein, vegetable, fruit, nuts, grain, fat
    
    # Valeurs nutritionnelles pour 100g
    calories_per_100g = db.Column(db.Float, nullable=False)
    protein_per_100g = db.Column(db.Float, nullable=False)
    carbs_per_100g = db.Column(db.Float, nullable=False)
    fat_per_100g = db.Column(db.Float, nullable=False)
    
    unit = db.Column(db.String(10), nullable=False, default='g')  # g, ml, piece
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'nutrition_per_100g': {
                'calories': self.calories_per_100g,
                'protein': self.protein_per_100g,
                'carbs': self.carbs_per_100g,
                'fat': self.fat_per_100g
            },
            'unit': self.unit,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @staticmethod
    def create_from_dict(data):
        nutrition = data.get('nutrition_per_100g', {})
        return Ingredient(
            name=data['name'],
            category=data['category'],
            calories_per_100g=nutrition.get('calories', 0),
            protein_per_100g=nutrition.get('protein', 0),
            carbs_per_100g=nutrition.get('carbs', 0),
            fat_per_100g=nutrition.get('fat', 0),
            unit=data.get('unit', 'g')
        )

