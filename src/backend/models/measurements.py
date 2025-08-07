"""
Modèle pour stocker TOUTES les mesures de l'utilisateur
Chaque mesure est sauvegardée de manière permanente dans la base de données
"""

from datetime import datetime, date
from database import db

class UserMeasurement(db.Model):
    """
    Table pour stocker TOUTES les mesures quotidiennes de l'utilisateur
    Chaque ligne = une journée de mesures
    """
    __tablename__ = 'user_measurements'
    __table_args__ = (
        db.Index('idx_user_date', 'user_id', 'date'),
        db.UniqueConstraint('user_id', 'date', name='unique_user_date'),
        {'extend_existing': True}
    )
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)
    
    # === POIDS ET COMPOSITION CORPORELLE ===
    weight = db.Column(db.Float)  # Poids en kg
    body_fat = db.Column(db.Float)  # Pourcentage de masse grasse
    muscle_mass = db.Column(db.Float)  # Pourcentage de masse musculaire
    water_percentage = db.Column(db.Float)  # Pourcentage d'eau corporelle
    bone_mass = db.Column(db.Float)  # Masse osseuse en kg
    visceral_fat = db.Column(db.Integer)  # Graisse viscérale (score 1-59)
    metabolic_age = db.Column(db.Integer)  # Âge métabolique
    
    # === ACTIVITÉ PHYSIQUE ===
    calories_burned = db.Column(db.Integer)  # Calories dépensées dans la journée
    steps = db.Column(db.Integer)  # Nombre de pas
    exercise_hours = db.Column(db.Float)  # Heures d'exercice
    exercise_type = db.Column(db.String(200))  # Type d'exercice (musculation, cardio, etc.)
    exercise_intensity = db.Column(db.String(50))  # Intensité (léger, modéré, intense)
    distance_walked = db.Column(db.Float)  # Distance parcourue en km
    floors_climbed = db.Column(db.Integer)  # Étages montés
    active_minutes = db.Column(db.Integer)  # Minutes actives
    
    # === NUTRITION ===
    calories_consumed = db.Column(db.Integer)  # Calories consommées
    protein = db.Column(db.Float)  # Protéines en grammes
    carbs = db.Column(db.Float)  # Glucides en grammes
    fat = db.Column(db.Float)  # Lipides en grammes
    fiber = db.Column(db.Float)  # Fibres en grammes
    sugar = db.Column(db.Float)  # Sucre en grammes
    sodium = db.Column(db.Float)  # Sodium en mg
    water_intake = db.Column(db.Integer)  # Eau bue en ml
    alcohol = db.Column(db.Float)  # Alcool en unités
    
    # === SANTÉ ET BIEN-ÊTRE ===
    sleep_hours = db.Column(db.Float)  # Heures de sommeil
    sleep_quality = db.Column(db.Integer)  # Qualité du sommeil (1-10)
    heart_rate_rest = db.Column(db.Integer)  # Fréquence cardiaque au repos
    heart_rate_max = db.Column(db.Integer)  # Fréquence cardiaque max
    blood_pressure_sys = db.Column(db.Integer)  # Tension systolique
    blood_pressure_dia = db.Column(db.Integer)  # Tension diastolique
    blood_sugar = db.Column(db.Float)  # Glycémie
    stress_level = db.Column(db.Integer)  # Niveau de stress (1-10)
    energy_level = db.Column(db.Integer)  # Niveau d'énergie (1-10)
    mood = db.Column(db.String(50))  # Humeur
    
    # === MESURES CORPORELLES ===
    waist = db.Column(db.Float)  # Tour de taille en cm
    hips = db.Column(db.Float)  # Tour de hanches en cm
    chest = db.Column(db.Float)  # Tour de poitrine en cm
    arms = db.Column(db.Float)  # Tour de bras en cm
    thighs = db.Column(db.Float)  # Tour de cuisses en cm
    neck = db.Column(db.Float)  # Tour de cou en cm
    
    # === MÉTA-DONNÉES ===
    notes = db.Column(db.Text)  # Notes personnelles
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    data_source = db.Column(db.String(50))  # Source des données (manuel, fitbit, etc.)
    is_verified = db.Column(db.Boolean, default=True)
    
    # Relations
    user = db.relationship('User', backref='measurements')
    
    def to_dict(self):
        """Convertit l'objet en dictionnaire pour l'API"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'date': self.date.isoformat() if self.date else None,
            
            # Poids et composition
            'weight': self.weight,
            'body_fat': self.body_fat,
            'muscle_mass': self.muscle_mass,
            'water_percentage': self.water_percentage,
            'bone_mass': self.bone_mass,
            'visceral_fat': self.visceral_fat,
            'metabolic_age': self.metabolic_age,
            
            # Activité
            'calories_burned': self.calories_burned,
            'steps': self.steps,
            'exercise_hours': self.exercise_hours,
            'exercise_type': self.exercise_type,
            'exercise_intensity': self.exercise_intensity,
            'distance_walked': self.distance_walked,
            'floors_climbed': self.floors_climbed,
            'active_minutes': self.active_minutes,
            
            # Nutrition
            'calories_consumed': self.calories_consumed,
            'protein': self.protein,
            'carbs': self.carbs,
            'fat': self.fat,
            'fiber': self.fiber,
            'sugar': self.sugar,
            'sodium': self.sodium,
            'water_intake': self.water_intake,
            'alcohol': self.alcohol,
            
            # Santé
            'sleep_hours': self.sleep_hours,
            'sleep_quality': self.sleep_quality,
            'heart_rate_rest': self.heart_rate_rest,
            'heart_rate_max': self.heart_rate_max,
            'blood_pressure_sys': self.blood_pressure_sys,
            'blood_pressure_dia': self.blood_pressure_dia,
            'blood_sugar': self.blood_sugar,
            'stress_level': self.stress_level,
            'energy_level': self.energy_level,
            'mood': self.mood,
            
            # Mesures corporelles
            'waist': self.waist,
            'hips': self.hips,
            'chest': self.chest,
            'arms': self.arms,
            'thighs': self.thighs,
            'neck': self.neck,
            
            # Méta
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'data_source': self.data_source,
            'is_verified': self.is_verified
        }
    
    @classmethod
    def get_latest_for_user(cls, user_id, days=30):
        """Récupère les dernières mesures d'un utilisateur"""
        from datetime import timedelta
        cutoff_date = date.today() - timedelta(days=days)
        return cls.query.filter(
            cls.user_id == user_id,
            cls.date >= cutoff_date
        ).order_by(cls.date.desc()).all()
    
    @classmethod
    def get_by_date_range(cls, user_id, start_date, end_date):
        """Récupère les mesures sur une période donnée"""
        return cls.query.filter(
            cls.user_id == user_id,
            cls.date >= start_date,
            cls.date <= end_date
        ).order_by(cls.date.desc()).all()
    
    def __repr__(self):
        return f'<UserMeasurement {self.user_id} - {self.date}>'