"""
Utilitaires de validation pour l'US1.7 : Profil Utilisateur Réel
Validations côté backend pour les données utilisateur et nutritionnelles
"""

import re
from datetime import datetime, date
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass


@dataclass
class ValidationError:
    """Représente une erreur de validation"""
    field: str
    message: str
    code: str
    value: Any = None


@dataclass
class ValidationResult:
    """Résultat de validation"""
    is_valid: bool
    errors: List[ValidationError]
    warnings: List[ValidationError]
    
    def add_error(self, field: str, message: str, code: str, value: Any = None):
        """Ajoute une erreur de validation"""
        self.errors.append(ValidationError(field, message, code, value))
        self.is_valid = False
    
    def add_warning(self, field: str, message: str, code: str, value: Any = None):
        """Ajoute un avertissement"""
        self.warnings.append(ValidationError(field, message, code, value))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire"""
        return {
            'is_valid': self.is_valid,
            'errors': [
                {
                    'field': e.field,
                    'message': e.message,
                    'code': e.code,
                    'value': e.value
                }
                for e in self.errors
            ],
            'warnings': [
                {
                    'field': w.field,
                    'message': w.message,
                    'code': w.code,
                    'value': w.value
                }
                for w in self.warnings
            ]
        }


class ProfileValidator:
    """Validateur pour les données de profil utilisateur"""
    
    # Constantes de validation
    MIN_WEIGHT = 20.0
    MAX_WEIGHT = 500.0
    MIN_HEIGHT = 50.0
    MAX_HEIGHT = 300.0
    MIN_AGE = 10
    MAX_AGE = 120
    MIN_BODY_FAT = 0.0
    MAX_BODY_FAT = 100.0
    
    # Regex pour email
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    
    @classmethod
    def validate_profile_data(cls, data: Dict[str, Any]) -> ValidationResult:
        """Valide les données complètes d'un profil utilisateur"""
        result = ValidationResult(is_valid=True, errors=[], warnings=[])
        
        # Validation du poids actuel
        if 'current_weight' in data:
            cls._validate_weight(data['current_weight'], 'current_weight', result)
        
        # Validation du poids cible
        if 'target_weight' in data:
            cls._validate_weight(data['target_weight'], 'target_weight', result)
        
        # Validation de la taille
        if 'height' in data:
            cls._validate_height(data['height'], result)
        
        # Validation de l'âge
        if 'age' in data:
            cls._validate_age(data['age'], result)
        
        # Validation de la date de naissance
        if 'birth_date' in data:
            cls._validate_birth_date(data['birth_date'], result)
        
        # Validation du genre
        if 'gender' in data:
            cls._validate_gender(data['gender'], result)
        
        # Validation du niveau d'activité
        if 'activity_level' in data:
            cls._validate_activity_level(data['activity_level'], result)
        
        # Validation de l'email
        if 'email' in data:
            cls._validate_email(data['email'], result)
        
        # Validation des métriques corporelles
        body_metrics = ['body_fat_percentage', 'muscle_mass_percentage', 'water_percentage']
        for metric in body_metrics:
            if metric in data and data[metric] is not None:
                cls._validate_body_percentage(data[metric], metric, result)
        
        # Validation de la cohérence des objectifs
        if 'current_weight' in data and 'target_weight' in data:
            cls._validate_weight_goals(data['current_weight'], data['target_weight'], result)
        
        # Validation des objectifs nutritionnels
        nutrition_fields = [
            'daily_calories_target', 'daily_protein_target', 'daily_carbs_target',
            'daily_fat_target', 'daily_fiber_target', 'daily_sodium_target',
            'daily_sugar_target', 'daily_water_target'
        ]
        for field in nutrition_fields:
            if field in data and data[field] is not None:
                cls._validate_nutrition_target(data[field], field, result)
        
        return result
    
    @classmethod
    def _validate_weight(cls, weight: Any, field: str, result: ValidationResult):
        """Valide un poids (actuel ou cible)"""
        if weight is None:
            return
        
        try:
            weight_float = float(weight)
            if weight_float < cls.MIN_WEIGHT:
                result.add_error(field, f"Le poids doit être supérieur à {cls.MIN_WEIGHT} kg", "weight_too_low", weight)
            elif weight_float > cls.MAX_WEIGHT:
                result.add_error(field, f"Le poids doit être inférieur à {cls.MAX_WEIGHT} kg", "weight_too_high", weight)
            elif weight_float < 30 or weight_float > 200:
                result.add_warning(field, "Poids inhabituel - vérifiez la valeur", "weight_unusual", weight)
        except (TypeError, ValueError):
            result.add_error(field, "Le poids doit être un nombre valide", "weight_invalid_format", weight)
    
    @classmethod
    def _validate_height(cls, height: Any, result: ValidationResult):
        """Valide la taille"""
        if height is None:
            return
        
        try:
            height_float = float(height)
            if height_float < cls.MIN_HEIGHT:
                result.add_error('height', f"La taille doit être supérieure à {cls.MIN_HEIGHT} cm", "height_too_low", height)
            elif height_float > cls.MAX_HEIGHT:
                result.add_error('height', f"La taille doit être inférieure à {cls.MAX_HEIGHT} cm", "height_too_high", height)
            elif height_float < 120 or height_float > 220:
                result.add_warning('height', "Taille inhabituelle - vérifiez la valeur", "height_unusual", height)
        except (TypeError, ValueError):
            result.add_error('height', "La taille doit être un nombre valide", "height_invalid_format", height)
    
    @classmethod
    def _validate_age(cls, age: Any, result: ValidationResult):
        """Valide l'âge"""
        if age is None:
            return
        
        try:
            age_int = int(age)
            if age_int < cls.MIN_AGE:
                result.add_error('age', f"L'âge doit être supérieur à {cls.MIN_AGE} ans", "age_too_low", age)
            elif age_int > cls.MAX_AGE:
                result.add_error('age', f"L'âge doit être inférieur à {cls.MAX_AGE} ans", "age_too_high", age)
        except (TypeError, ValueError):
            result.add_error('age', "L'âge doit être un nombre entier valide", "age_invalid_format", age)
    
    @classmethod
    def _validate_birth_date(cls, birth_date: Any, result: ValidationResult):
        """Valide la date de naissance"""
        if birth_date is None:
            return
        
        try:
            if isinstance(birth_date, str):
                parsed_date = datetime.fromisoformat(birth_date).date()
            elif isinstance(birth_date, date):
                parsed_date = birth_date
            else:
                raise ValueError("Format de date invalide")
            
            today = date.today()
            if parsed_date > today:
                result.add_error('birth_date', "La date de naissance ne peut pas être dans le futur", "birth_date_future", birth_date)
            
            age = today.year - parsed_date.year - ((today.month, today.day) < (parsed_date.month, parsed_date.day))
            if age < cls.MIN_AGE:
                result.add_error('birth_date', f"L'âge calculé est trop faible ({age} ans)", "birth_date_too_young", birth_date)
            elif age > cls.MAX_AGE:
                result.add_error('birth_date', f"L'âge calculé est trop élevé ({age} ans)", "birth_date_too_old", birth_date)
                
        except (ValueError, AttributeError):
            result.add_error('birth_date', "Format de date de naissance invalide", "birth_date_invalid_format", birth_date)
    
    @classmethod
    def _validate_gender(cls, gender: Any, result: ValidationResult):
        """Valide le genre"""
        if gender is None:
            return
        
        valid_genders = ['male', 'female', 'other', 'prefer_not_to_say']
        if gender not in valid_genders:
            result.add_error('gender', f"Genre invalide. Valeurs acceptées: {', '.join(valid_genders)}", "gender_invalid", gender)
    
    @classmethod
    def _validate_activity_level(cls, activity_level: Any, result: ValidationResult):
        """Valide le niveau d'activité"""
        if activity_level is None:
            return
        
        valid_levels = [
            'sedentary', 'lightly_active', 'moderately_active', 
            'very_active', 'extremely_active'
        ]
        if activity_level not in valid_levels:
            result.add_error('activity_level', f"Niveau d'activité invalide. Valeurs acceptées: {', '.join(valid_levels)}", "activity_level_invalid", activity_level)
    
    @classmethod
    def _validate_email(cls, email: Any, result: ValidationResult):
        """Valide l'email"""
        if email is None:
            return
        
        if not isinstance(email, str) or not cls.EMAIL_PATTERN.match(email):
            result.add_error('email', "Format d'email invalide", "email_invalid_format", email)
    
    @classmethod
    def _validate_body_percentage(cls, percentage: Any, field: str, result: ValidationResult):
        """Valide un pourcentage corporel (masse grasse, masse musculaire, etc.)"""
        if percentage is None:
            return
        
        try:
            percent_float = float(percentage)
            if percent_float < cls.MIN_BODY_FAT:
                result.add_error(field, f"Le pourcentage doit être supérieur à {cls.MIN_BODY_FAT}%", f"{field}_too_low", percentage)
            elif percent_float > cls.MAX_BODY_FAT:
                result.add_error(field, f"Le pourcentage doit être inférieur à {cls.MAX_BODY_FAT}%", f"{field}_too_high", percentage)
        except (TypeError, ValueError):
            result.add_error(field, "Le pourcentage doit être un nombre valide", f"{field}_invalid_format", percentage)
    
    @classmethod
    def _validate_weight_goals(cls, current_weight: Any, target_weight: Any, result: ValidationResult):
        """Valide la cohérence entre poids actuel et objectif"""
        try:
            current = float(current_weight) if current_weight is not None else None
            target = float(target_weight) if target_weight is not None else None
            
            if current and target:
                difference = abs(current - target)
                
                # Avertir si l'objectif est trop extrême
                if difference > 50:
                    result.add_warning('target_weight', 
                                     f"Différence importante entre poids actuel et objectif ({difference:.1f} kg)", 
                                     "weight_goal_extreme", target)
                
                # Avertir si l'objectif semble peu réaliste
                if target < 40 or target > 200:
                    result.add_warning('target_weight', "Poids objectif inhabituel", "weight_goal_unusual", target)
                    
        except (TypeError, ValueError):
            pass  # Les erreurs individuelles seront gérées par les validateurs de poids
    
    @classmethod
    def _validate_nutrition_target(cls, value: Any, field: str, result: ValidationResult):
        """Valide un objectif nutritionnel"""
        if value is None:
            return
        
        try:
            value_float = float(value)
            
            # Validation par type de champ
            if 'calories' in field:
                if value_float < 800 or value_float > 5000:
                    result.add_warning(field, f"Objectif calorique inhabituel ({value_float} kcal)", f"{field}_unusual", value)
            
            elif 'protein' in field:
                if value_float < 10 or value_float > 300:
                    result.add_warning(field, f"Objectif protéines inhabituel ({value_float}g)", f"{field}_unusual", value)
            
            elif 'carbs' in field:
                if value_float < 20 or value_float > 500:
                    result.add_warning(field, f"Objectif glucides inhabituel ({value_float}g)", f"{field}_unusual", value)
            
            elif 'fat' in field:
                if value_float < 10 or value_float > 200:
                    result.add_warning(field, f"Objectif lipides inhabituel ({value_float}g)", f"{field}_unusual", value)
            
            elif 'water' in field:
                if value_float < 1000 or value_float > 5000:
                    result.add_warning(field, f"Objectif eau inhabituel ({value_float}ml)", f"{field}_unusual", value)
            
            if value_float < 0:
                result.add_error(field, "Les objectifs nutritionnels doivent être positifs", f"{field}_negative", value)
                
        except (TypeError, ValueError):
            result.add_error(field, f"Objectif {field} doit être un nombre valide", f"{field}_invalid_format", value)


class WeightHistoryValidator:
    """Validateur pour l'historique des pesées"""
    
    @classmethod
    def validate_weight_entry(cls, data: Dict[str, Any]) -> ValidationResult:
        """Valide une entrée de pesée"""
        result = ValidationResult(is_valid=True, errors=[], warnings=[])
        
        # Validation du poids (obligatoire)
        if 'weight' not in data or data['weight'] is None:
            result.add_error('weight', "Le poids est obligatoire", "weight_required")
        else:
            ProfileValidator._validate_weight(data['weight'], 'weight', result)
        
        # Validation de la date d'enregistrement
        if 'recorded_date' in data and data['recorded_date']:
            cls._validate_recorded_date(data['recorded_date'], result)
        
        # Validation des métriques corporelles optionnelles
        optional_metrics = ['body_fat_percentage', 'muscle_mass_percentage', 'water_percentage']
        for metric in optional_metrics:
            if metric in data and data[metric] is not None:
                ProfileValidator._validate_body_percentage(data[metric], metric, result)
        
        # Validation des notes (longueur)
        if 'notes' in data and data['notes']:
            if len(data['notes']) > 500:
                result.add_error('notes', "Les notes ne peuvent pas dépasser 500 caractères", "notes_too_long", data['notes'])
        
        return result
    
    @classmethod
    def _validate_recorded_date(cls, recorded_date: Any, result: ValidationResult):
        """Valide la date d'enregistrement"""
        try:
            if isinstance(recorded_date, str):
                parsed_date = datetime.fromisoformat(recorded_date).date()
            elif isinstance(recorded_date, date):
                parsed_date = recorded_date
            else:
                raise ValueError("Format de date invalide")
            
            today = date.today()
            if parsed_date > today:
                result.add_error('recorded_date', "La date de pesée ne peut pas être dans le futur", "recorded_date_future", recorded_date)
            
            # Avertir si la date est très ancienne (plus de 5 ans)
            days_diff = (today - parsed_date).days
            if days_diff > 1825:  # 5 ans
                result.add_warning('recorded_date', "Date de pesée très ancienne", "recorded_date_old", recorded_date)
                
        except (ValueError, AttributeError):
            result.add_error('recorded_date', "Format de date invalide", "recorded_date_invalid_format", recorded_date)


class NutritionValidator:
    """Validateur pour les objectifs et calculs nutritionnels"""
    
    @classmethod
    def validate_nutrition_profile(cls, profile_data: Dict[str, Any]) -> ValidationResult:
        """Valide un profil nutritionnel calculé"""
        result = ValidationResult(is_valid=True, errors=[], warnings=[])
        
        # Validation des valeurs calculées
        required_fields = ['bmr', 'tdee', 'adjusted_calories']
        for field in required_fields:
            if field not in profile_data or profile_data[field] is None:
                result.add_error(field, f"Valeur {field} manquante dans le profil nutritionnel", f"{field}_missing")
            else:
                value = profile_data[field]
                if not isinstance(value, (int, float)) or value <= 0:
                    result.add_error(field, f"Valeur {field} invalide", f"{field}_invalid", value)
        
        # Validation de la cohérence BMR/TDEE
        if 'bmr' in profile_data and 'tdee' in profile_data:
            bmr = profile_data['bmr']
            tdee = profile_data['tdee']
            
            if bmr and tdee and tdee < bmr:
                result.add_error('tdee', "Le TDEE ne peut pas être inférieur au BMR", "tdee_lower_than_bmr", tdee)
            
            if bmr and tdee and (tdee / bmr) > 3:
                result.add_warning('tdee', "Ratio TDEE/BMR très élevé - vérifiez le niveau d'activité", "tdee_ratio_high", tdee / bmr)
        
        # Validation des macronutriments
        macro_fields = ['protein_target', 'carbs_target', 'fat_target']
        for field in macro_fields:
            if field in profile_data and profile_data[field] is not None:
                ProfileValidator._validate_nutrition_target(profile_data[field], field, result)
        
        # Validation de la cohérence des macros avec les calories
        if all(field in profile_data and profile_data[field] for field in ['adjusted_calories'] + macro_fields):
            cls._validate_macro_calorie_consistency(profile_data, result)
        
        return result
    
    @classmethod
    def _validate_macro_calorie_consistency(cls, profile_data: Dict[str, Any], result: ValidationResult):
        """Valide la cohérence entre macronutriments et calories"""
        try:
            calories = profile_data['adjusted_calories']
            protein = profile_data['protein_target']
            carbs = profile_data['carbs_target']
            fat = profile_data['fat_target']
            
            # Calcul des calories provenant des macros
            macro_calories = (protein * 4) + (carbs * 4) + (fat * 9)
            
            # Tolérance de 10%
            tolerance = 0.10
            lower_bound = calories * (1 - tolerance)
            upper_bound = calories * (1 + tolerance)
            
            if macro_calories < lower_bound or macro_calories > upper_bound:
                result.add_warning('macronutrients', 
                                 f"Incohérence entre calories ({calories}) et macronutriments ({macro_calories:.0f} cal calculées)", 
                                 "macro_calorie_mismatch", 
                                 {'target_calories': calories, 'calculated_calories': macro_calories})
                                 
        except (TypeError, ValueError, KeyError):
            # Erreur dans les calculs - probablement des valeurs manquantes ou invalides
            pass


# Fonction utilitaire pour validation complète
def validate_user_profile_complete(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fonction de validation complète pour un profil utilisateur
    Combine toutes les validations et retourne un résumé complet
    """
    profile_result = ProfileValidator.validate_profile_data(data)
    
    # Si des données de pesée sont incluses
    weight_result = None
    if any(key in data for key in ['weight_history', 'current_weight_entry']):
        weight_data = data.get('current_weight_entry', {
            'weight': data.get('current_weight'),
            'recorded_date': date.today().isoformat()
        })
        weight_result = WeightHistoryValidator.validate_weight_entry(weight_data)
    
    # Compilation du résultat final
    final_result = {
        'is_valid': profile_result.is_valid and (weight_result is None or weight_result.is_valid),
        'profile_validation': profile_result.to_dict(),
        'overall_errors': profile_result.errors + (weight_result.errors if weight_result else []),
        'overall_warnings': profile_result.warnings + (weight_result.warnings if weight_result else []),
        'validation_summary': {
            'total_errors': len(profile_result.errors) + (len(weight_result.errors) if weight_result else 0),
            'total_warnings': len(profile_result.warnings) + (len(weight_result.warnings) if weight_result else 0),
            'critical_issues': [
                error.message for error in profile_result.errors 
                if error.code in ['weight_too_low', 'weight_too_high', 'height_too_low', 'height_too_high']
            ]
        }
    }
    
    if weight_result:
        final_result['weight_validation'] = weight_result.to_dict()
    
    return final_result