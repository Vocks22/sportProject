from database import db
from datetime import datetime, date, timedelta
from sqlalchemy.orm import relationship
from typing import Dict, Any, Optional, List
import json

class User(db.Model):
    __tablename__ = 'users'
    
    # Identification
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    
    # Informations personnelles pour la diète
    current_weight = db.Column(db.Float, nullable=True)
    target_weight = db.Column(db.Float, nullable=True)
    height = db.Column(db.Float, nullable=True)
    age = db.Column(db.Integer, nullable=True)
    gender = db.Column(db.String(10), nullable=True)
    activity_level = db.Column(db.String(20), nullable=True)
    
    # Nouvelles informations personnelles étendues (US1.7)
    birth_date = db.Column(db.Date, nullable=True)
    goals = db.Column(db.Text, nullable=True)
    medical_conditions = db.Column(db.Text, nullable=True)
    dietary_restrictions = db.Column(db.Text, nullable=True)
    preferred_cuisine_types = db.Column(db.Text, nullable=True)
    
    # Métriques de santé avancées
    body_fat_percentage = db.Column(db.Float, nullable=True)
    muscle_mass_percentage = db.Column(db.Float, nullable=True)
    water_percentage = db.Column(db.Float, nullable=True)
    bone_density = db.Column(db.Float, nullable=True)
    metabolic_age = db.Column(db.Integer, nullable=True)
    
    # Objectifs nutritionnels de base
    daily_calories_target = db.Column(db.Float, default=1500)
    daily_protein_target = db.Column(db.Float, default=150)
    daily_carbs_target = db.Column(db.Float, default=85)
    daily_fat_target = db.Column(db.Float, default=75)
    
    # Objectifs nutritionnels étendus (US1.7)
    daily_fiber_target = db.Column(db.Float, default=25.0)
    daily_sodium_target = db.Column(db.Float, default=2300.0)
    daily_sugar_target = db.Column(db.Float, default=50.0)
    daily_water_target = db.Column(db.Float, default=2000.0)
    
    # Préférences et paramètres
    timezone = db.Column(db.String(50), default='UTC')
    language = db.Column(db.String(10), default='fr')
    units_system = db.Column(db.String(10), default='metric')
    notification_preferences = db.Column(db.Text, nullable=True)
    
    # Cache pour performances (BMR/TDEE)
    cached_bmr = db.Column(db.Float, nullable=True)
    cached_tdee = db.Column(db.Float, nullable=True)
    cache_last_updated = db.Column(db.DateTime, nullable=True)
    
    # Statut et validation du profil
    profile_completed = db.Column(db.Boolean, default=False, nullable=False)
    profile_validated = db.Column(db.Boolean, default=False, nullable=False)
    last_profile_update = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Sécurité et audit
    last_login = db.Column(db.DateTime, nullable=True)
    login_count = db.Column(db.Integer, default=0, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    deactivated_at = db.Column(db.DateTime, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    weight_history = relationship('WeightHistory', back_populates='user', cascade='all, delete-orphan')
    goals_history = relationship('UserGoalsHistory', back_populates='user', cascade='all, delete-orphan')
    # measurements = relationship('UserMeasurement', back_populates='user', cascade='all, delete-orphan')  # Défini dans measurements.py
    meal_plans = relationship('MealPlan', backref='user', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.username} (ID: {self.id})>'
    
    # Propriétés calculées
    @property
    def calculated_age(self) -> Optional[int]:
        """Calcule l'âge à partir de la date de naissance, sinon utilise l'âge stocké"""
        if self.birth_date:
            today = date.today()
            return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
        return self.age
    
    @property
    def bmi(self) -> Optional[float]:
        """Calcule l'IMC (BMI) si poids et taille sont disponibles"""
        if self.current_weight and self.height:
            height_m = self.height / 100  # Conversion cm -> m
            return round(self.current_weight / (height_m ** 2), 1)
        return None
    
    @property
    def bmi_category(self) -> Optional[str]:
        """Retourne la catégorie IMC"""
        bmi = self.bmi
        if bmi is None:
            return None
        
        if bmi < 18.5:
            return 'underweight'
        elif bmi < 25:
            return 'normal'
        elif bmi < 30:
            return 'overweight'
        else:
            return 'obese'
    
    @property
    def bmr(self) -> Optional[float]:
        """Retourne le BMR (métabolisme de base) calculé ou en cache"""
        # Si le cache est valide (moins de 7 jours)
        if (self.cached_bmr and self.cache_last_updated and 
            (datetime.utcnow() - self.cache_last_updated).days < 7):
            return self.cached_bmr
        
        # Calcul du BMR avec la formule de Harris-Benedict révisée
        if self.current_weight and self.height and self.calculated_age and self.gender:
            if self.gender.lower() == 'male':
                bmr = 88.362 + (13.397 * self.current_weight) + (4.799 * self.height) - (5.677 * self.calculated_age)
            elif self.gender.lower() == 'female':
                bmr = 447.593 + (9.247 * self.current_weight) + (3.098 * self.height) - (4.330 * self.calculated_age)
            else:
                return None
            
            # Mettre à jour le cache
            self.cached_bmr = round(bmr, 1)
            self.cache_last_updated = datetime.utcnow()
            return self.cached_bmr
        
        return None
    
    @property
    def tdee(self) -> Optional[float]:
        """Retourne le TDEE (dépense énergétique totale) calculé ou en cache"""
        # Si le cache est valide (moins de 7 jours)
        if (self.cached_tdee and self.cache_last_updated and 
            (datetime.utcnow() - self.cache_last_updated).days < 7):
            return self.cached_tdee
        
        bmr = self.bmr
        if bmr and self.activity_level:
            activity_multipliers = {
                'sedentary': 1.2,
                'lightly_active': 1.375,
                'moderately_active': 1.55,
                'very_active': 1.725,
                'extremely_active': 1.9
            }
            
            multiplier = activity_multipliers.get(self.activity_level, 1.2)
            tdee = bmr * multiplier
            
            # Mettre à jour le cache
            self.cached_tdee = round(tdee, 1)
            self.cache_last_updated = datetime.utcnow()
            return self.cached_tdee
        
        return None
    
    @property
    def goals_list(self) -> List[str]:
        """Retourne la liste des objectifs depuis le JSON stocké"""
        if self.goals:
            try:
                return json.loads(self.goals)
            except (json.JSONDecodeError, TypeError):
                return [self.goals] if isinstance(self.goals, str) else []
        return []
    
    @goals_list.setter
    def goals_list(self, value: List[str]):
        """Définit les objectifs en format JSON"""
        if isinstance(value, list):
            self.goals = json.dumps(value)
        elif isinstance(value, str):
            self.goals = value
        else:
            self.goals = None
    
    @property
    def medical_conditions_list(self) -> List[str]:
        """Retourne la liste des conditions médicales depuis le JSON stocké"""
        if self.medical_conditions:
            try:
                return json.loads(self.medical_conditions)
            except (json.JSONDecodeError, TypeError):
                return [self.medical_conditions] if isinstance(self.medical_conditions, str) else []
        return []
    
    @medical_conditions_list.setter
    def medical_conditions_list(self, value: List[str]):
        """Définit les conditions médicales en format JSON"""
        if isinstance(value, list):
            self.medical_conditions = json.dumps(value)
        elif isinstance(value, str):
            self.medical_conditions = value
        else:
            self.medical_conditions = None
    
    @property
    def dietary_restrictions_list(self) -> List[str]:
        """Retourne la liste des restrictions alimentaires depuis le JSON stocké"""
        if self.dietary_restrictions:
            try:
                return json.loads(self.dietary_restrictions)
            except (json.JSONDecodeError, TypeError):
                return [self.dietary_restrictions] if isinstance(self.dietary_restrictions, str) else []
        return []
    
    @dietary_restrictions_list.setter
    def dietary_restrictions_list(self, value: List[str]):
        """Définit les restrictions alimentaires en format JSON"""
        if isinstance(value, list):
            self.dietary_restrictions = json.dumps(value)
        elif isinstance(value, str):
            self.dietary_restrictions = value
        else:
            self.dietary_restrictions = None
    
    @property
    def preferred_cuisine_types_list(self) -> List[str]:
        """Retourne la liste des types de cuisine préférés depuis le JSON stocké"""
        if self.preferred_cuisine_types:
            try:
                return json.loads(self.preferred_cuisine_types)
            except (json.JSONDecodeError, TypeError):
                return [self.preferred_cuisine_types] if isinstance(self.preferred_cuisine_types, str) else []
        return []
    
    @preferred_cuisine_types_list.setter
    def preferred_cuisine_types_list(self, value: List[str]):
        """Définit les types de cuisine préférés en format JSON"""
        if isinstance(value, list):
            self.preferred_cuisine_types = json.dumps(value)
        elif isinstance(value, str):
            self.preferred_cuisine_types = value
        else:
            self.preferred_cuisine_types = None
    
    @property
    def notification_preferences_dict(self) -> Dict[str, Any]:
        """Retourne les préférences de notification depuis le JSON stocké"""
        if self.notification_preferences:
            try:
                return json.loads(self.notification_preferences)
            except (json.JSONDecodeError, TypeError):
                return {}
        return {
            'email_enabled': True,
            'meal_reminders': True,
            'weight_reminders': True,
            'goal_updates': True,
            'weekly_reports': True
        }
    
    @notification_preferences_dict.setter
    def notification_preferences_dict(self, value: Dict[str, Any]):
        """Définit les préférences de notification en format JSON"""
        if isinstance(value, dict):
            self.notification_preferences = json.dumps(value)
        else:
            self.notification_preferences = None
    
    # Méthodes utilitaires
    def invalidate_cache(self):
        """Invalide le cache BMR/TDEE pour forcer le recalcul"""
        self.cached_bmr = None
        self.cached_tdee = None
        self.cache_last_updated = None
    
    def update_profile_status(self):
        """Met à jour le statut de complétion du profil"""
        required_fields = [
            self.current_weight, self.target_weight, self.height,
            self.calculated_age, self.gender, self.activity_level
        ]
        
        self.profile_completed = all(field is not None for field in required_fields)
        self.last_profile_update = datetime.utcnow()
        
        if self.profile_completed:
            # Invalider le cache pour recalculer BMR/TDEE
            self.invalidate_cache()
    
    def get_latest_weight(self) -> Optional[float]:
        """Retourne le dernier poids enregistré dans l'historique"""
        if self.weight_history:
            latest = max(self.weight_history, key=lambda wh: wh.recorded_date)
            return latest.weight
        return self.current_weight
    
    def get_weight_trend(self, days: int = 30) -> Optional[str]:
        """Retourne la tendance du poids sur N jours ('increasing', 'decreasing', 'stable')"""
        if not self.weight_history or len(self.weight_history) < 2:
            return None
        
        recent_date = date.today() - timedelta(days=days)
        recent_weights = [wh for wh in self.weight_history if wh.recorded_date >= recent_date]
        
        if len(recent_weights) < 2:
            return None
        
        recent_weights.sort(key=lambda wh: wh.recorded_date)
        first_weight = recent_weights[0].weight
        last_weight = recent_weights[-1].weight
        
        diff = last_weight - first_weight
        threshold = 0.5  # kg
        
        if diff > threshold:
            return 'increasing'
        elif diff < -threshold:
            return 'decreasing'
        else:
            return 'stable'
    
    def calculate_progress_percentage(self) -> Optional[float]:
        """Calcule le pourcentage de progression vers l'objectif de poids"""
        if not (self.current_weight and self.target_weight):
            return None
        
        initial_weight = self.current_weight
        # Essayer de trouver le poids initial dans l'historique
        if self.weight_history:
            oldest = min(self.weight_history, key=lambda wh: wh.recorded_date)
            initial_weight = oldest.weight
        
        current_weight = self.get_latest_weight() or self.current_weight
        
        if initial_weight == self.target_weight:
            return 100.0 if current_weight == self.target_weight else 0.0
        
        total_change_needed = self.target_weight - initial_weight
        current_change = current_weight - initial_weight
        
        if total_change_needed == 0:
            return 100.0
        
        progress = (current_change / total_change_needed) * 100
        return max(0, min(100, progress))  # Limiter entre 0 et 100%
    
    def to_dict(self, include_sensitive: bool = False, include_extended: bool = True) -> Dict[str, Any]:
        """Convertit l'utilisateur en dictionnaire avec options de personnalisation"""
        base_data = {
            'id': self.id,
            'username': self.username,
            'email': self.email if include_sensitive else None,
            'current_weight': self.current_weight,
            'target_weight': self.target_weight,
            'height': self.height,
            'age': self.calculated_age,
            'gender': self.gender,
            'activity_level': self.activity_level,
            'profile_completed': self.profile_completed,
            'profile_validated': self.profile_validated,
            'is_active': self.is_active,
            'daily_targets': {
                'calories': self.daily_calories_target,
                'protein': self.daily_protein_target,
                'carbs': self.daily_carbs_target,
                'fat': self.daily_fat_target,
                'fiber': self.daily_fiber_target,
                'sodium': self.daily_sodium_target,
                'sugar': self.daily_sugar_target,
                'water': self.daily_water_target
            },
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_extended:
            extended_data = {
                'birth_date': self.birth_date.isoformat() if self.birth_date else None,
                'goals': self.goals_list,
                'medical_conditions': self.medical_conditions_list if include_sensitive else None,
                'dietary_restrictions': self.dietary_restrictions_list,
                'preferred_cuisine_types': self.preferred_cuisine_types_list,
                'health_metrics': {
                    'body_fat_percentage': self.body_fat_percentage,
                    'muscle_mass_percentage': self.muscle_mass_percentage,
                    'water_percentage': self.water_percentage,
                    'bone_density': self.bone_density,
                    'metabolic_age': self.metabolic_age
                },
                'preferences': {
                    'timezone': self.timezone,
                    'language': self.language,
                    'units_system': self.units_system,
                    'notifications': self.notification_preferences_dict
                },
                'calculated_values': {
                    'bmr': self.bmr,
                    'tdee': self.tdee,
                    'bmi': self.bmi,
                    'bmi_category': self.bmi_category
                },
                'last_profile_update': self.last_profile_update.isoformat() if self.last_profile_update else None
            }
            base_data.update(extended_data)
        
        return base_data
    
    def to_summary_dict(self) -> Dict[str, Any]:
        """Retourne un résumé concis pour les listes"""
        return {
            'id': self.id,
            'username': self.username,
            'profile_completed': self.profile_completed,
            'current_weight': self.current_weight,
            'target_weight': self.target_weight,
            'bmi': self.bmi,
            'bmi_category': self.bmi_category,
            'progress_percentage': self.calculate_progress_percentage(),
            'last_profile_update': self.last_profile_update.isoformat() if self.last_profile_update else None,
            'is_active': self.is_active
        }


# Modèles associés pour l'US1.7

class WeightHistory(db.Model):
    """Historique des pesées utilisateur"""
    __tablename__ = 'weight_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    weight = db.Column(db.Float, nullable=False)
    body_fat_percentage = db.Column(db.Float, nullable=True)
    muscle_mass_percentage = db.Column(db.Float, nullable=True)
    water_percentage = db.Column(db.Float, nullable=True)
    recorded_date = db.Column(db.Date, nullable=False, index=True)
    measurement_time = db.Column(db.Time, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    measurement_method = db.Column(db.String(50), default='manual')
    data_source = db.Column(db.String(100), nullable=True)
    is_verified = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relation
    user = relationship('User', back_populates='weight_history')
    
    # Index unique pour éviter doublons
    __table_args__ = (db.UniqueConstraint('user_id', 'recorded_date', name='uq_weight_history_user_date'),)
    
    def __repr__(self):
        return f'<WeightHistory {self.user_id}: {self.weight}kg on {self.recorded_date}>'
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'user_id': self.user_id,
            'weight': self.weight,
            'body_fat_percentage': self.body_fat_percentage,
            'muscle_mass_percentage': self.muscle_mass_percentage,
            'water_percentage': self.water_percentage,
            'recorded_date': self.recorded_date.isoformat(),
            'measurement_time': self.measurement_time.isoformat() if self.measurement_time else None,
            'notes': self.notes,
            'measurement_method': self.measurement_method,
            'data_source': self.data_source,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class UserGoalsHistory(db.Model):
    """Historique des objectifs utilisateur"""
    __tablename__ = 'user_goals_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    goal_type = db.Column(db.String(50), nullable=False)
    target_value = db.Column(db.Float, nullable=True)
    target_date = db.Column(db.Date, nullable=True)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(20), default='active')
    progress_percentage = db.Column(db.Float, default=0.0)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relation
    user = relationship('User', back_populates='goals_history')
    
    def __repr__(self):
        return f'<UserGoalsHistory {self.user_id}: {self.goal_type} ({self.status})>'
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'user_id': self.user_id,
            'goal_type': self.goal_type,
            'target_value': self.target_value,
            'target_date': self.target_date.isoformat() if self.target_date else None,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'status': self.status,
            'progress_percentage': self.progress_percentage,
            'notes': self.notes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


# La classe UserMeasurement a été déplacée dans models/measurements.py

