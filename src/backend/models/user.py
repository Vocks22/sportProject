from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    
    # Informations personnelles pour la diète
    current_weight = db.Column(db.Float, nullable=True)
    target_weight = db.Column(db.Float, nullable=True)
    height = db.Column(db.Float, nullable=True)
    age = db.Column(db.Integer, nullable=True)
    gender = db.Column(db.String(10), nullable=True)
    activity_level = db.Column(db.String(20), nullable=True)
    
    # Objectifs nutritionnels
    daily_calories_target = db.Column(db.Float, default=1500)
    daily_protein_target = db.Column(db.Float, default=150)
    daily_carbs_target = db.Column(db.Float, default=85)
    daily_fat_target = db.Column(db.Float, default=75)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'current_weight': self.current_weight,
            'target_weight': self.target_weight,
            'height': self.height,
            'age': self.age,
            'gender': self.gender,
            'activity_level': self.activity_level,
            'daily_targets': {
                'calories': self.daily_calories_target,
                'protein': self.daily_protein_target,
                'carbs': self.daily_carbs_target,
                'fat': self.daily_fat_target
            },
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

