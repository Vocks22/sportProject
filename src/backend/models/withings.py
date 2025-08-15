"""
Modèles pour l'intégration Withings
"""
from database import db
from datetime import datetime


class WithingsAuth(db.Model):
    """Stockage des tokens OAuth2 Withings pour chaque utilisateur"""
    __tablename__ = 'withings_auth'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    withings_user_id = db.Column(db.String(100), nullable=False)
    access_token = db.Column(db.Text, nullable=False)
    refresh_token = db.Column(db.Text, nullable=False)
    token_expiry = db.Column(db.DateTime, nullable=False)
    scope = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relation avec l'utilisateur
    user = db.relationship('User', backref='withings_auth', uselist=False)
    
    def is_token_expired(self):
        """Vérifie si le token est expiré"""
        return datetime.utcnow() >= self.token_expiry
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'withings_user_id': self.withings_user_id,
            'connected': True,
            'token_valid': not self.is_token_expired(),
            'connected_at': self.created_at.isoformat() if self.created_at else None,
            'scope': self.scope
        }


class WithingsMeasurement(db.Model):
    """Stockage des mesures récupérées depuis Withings"""
    __tablename__ = 'withings_measurements'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Données de base
    weight = db.Column(db.Float)  # kg
    height = db.Column(db.Float)  # cm
    
    # Composition corporelle
    fat_mass = db.Column(db.Float)  # kg
    fat_ratio = db.Column(db.Float)  # %
    muscle_mass = db.Column(db.Float)  # kg
    muscle_ratio = db.Column(db.Float)  # %
    hydration = db.Column(db.Float)  # kg
    hydration_ratio = db.Column(db.Float)  # %
    bone_mass = db.Column(db.Float)  # kg
    
    # Métriques avancées
    pulse_wave_velocity = db.Column(db.Float)  # m/s
    heart_rate = db.Column(db.Integer)  # bpm
    temperature = db.Column(db.Float)  # °C
    skin_temperature = db.Column(db.Float)  # °C
    
    # Métadonnées
    withings_measure_id = db.Column(db.String(100), unique=True)
    measured_at = db.Column(db.DateTime, nullable=False)
    device_id = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relation avec l'utilisateur
    user = db.relationship('User', backref='withings_measurements')
    
    def to_dict(self):
        return {
            'id': self.id,
            'weight': self.weight,
            'fat_mass': self.fat_mass,
            'fat_ratio': self.fat_ratio,
            'muscle_mass': self.muscle_mass,
            'muscle_ratio': self.muscle_ratio,
            'hydration': self.hydration,
            'hydration_ratio': self.hydration_ratio,
            'bone_mass': self.bone_mass,
            'heart_rate': self.heart_rate,
            'measured_at': self.measured_at.isoformat() if self.measured_at else None
        }