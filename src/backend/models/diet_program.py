"""
Modèle pour le programme de diète fixe de Fabien
"""
from database import db
from datetime import datetime

class DietProgram(db.Model):
    """Programme alimentaire fixe avec 5 repas par jour"""
    __tablename__ = 'diet_program'
    
    id = db.Column(db.Integer, primary_key=True)
    meal_type = db.Column(db.String(50), nullable=False)  # repas1, collation1, repas2, collation2, repas3
    meal_name = db.Column(db.String(100), nullable=False)  # Nom du repas (ex: "Petit-déjeuner")
    time_slot = db.Column(db.String(20), nullable=False)  # Heure recommandée (ex: "6h-9h")
    foods = db.Column(db.JSON, nullable=False)  # Liste des aliments avec quantités
    order_index = db.Column(db.Integer, nullable=False)  # Ordre d'affichage (1-5)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relations
    trackings = db.relationship('DietTracking', back_populates='meal', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'meal_type': self.meal_type,
            'meal_name': self.meal_name,
            'time_slot': self.time_slot,
            'foods': self.foods,
            'order_index': self.order_index
        }


class DietTracking(db.Model):
    """Suivi quotidien de chaque repas"""
    __tablename__ = 'diet_tracking'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    meal_id = db.Column(db.Integer, db.ForeignKey('diet_program.id'), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    notes = db.Column(db.Text, nullable=True)  # Notes optionnelles
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    meal = db.relationship('DietProgram', back_populates='trackings')
    
    # Index unique pour éviter les doublons
    __table_args__ = (
        db.UniqueConstraint('date', 'meal_id', name='unique_date_meal'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.isoformat(),
            'meal_id': self.meal_id,
            'meal': self.meal.to_dict() if self.meal else None,
            'completed': self.completed,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'notes': self.notes
        }


class DietStreak(db.Model):
    """Statistiques de suivi (streak, taux de respect, etc.)"""
    __tablename__ = 'diet_streak'
    
    id = db.Column(db.Integer, primary_key=True)
    current_streak = db.Column(db.Integer, default=0)  # Jours consécutifs
    longest_streak = db.Column(db.Integer, default=0)  # Record
    total_days_tracked = db.Column(db.Integer, default=0)
    total_meals_completed = db.Column(db.Integer, default=0)
    last_tracked_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'current_streak': self.current_streak,
            'longest_streak': self.longest_streak,
            'total_days_tracked': self.total_days_tracked,
            'total_meals_completed': self.total_meals_completed,
            'last_tracked_date': self.last_tracked_date.isoformat() if self.last_tracked_date else None
        }