"""
Service de calcul nutritionnel pour l'US1.7 : Profil Utilisateur Réel
Implémente les calculs BMR/TDEE avec cache multi-niveau et optimisations performances
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple
import math
import logging
from dataclasses import dataclass, asdict
from enum import Enum

from models.user import User, db
from services.cache_service import CacheService

# Configuration du logger
logger = logging.getLogger(__name__)


class ActivityLevel(Enum):
    """Niveaux d'activité physique avec multiplicateurs TDEE"""
    SEDENTARY = ("sedentary", 1.2, "Sédentaire - Travail de bureau, pas d'exercice")
    LIGHTLY_ACTIVE = ("lightly_active", 1.375, "Légèrement actif - Exercice léger 1-3 jours/semaine")
    MODERATELY_ACTIVE = ("moderately_active", 1.55, "Modérément actif - Exercice modéré 3-5 jours/semaine")
    VERY_ACTIVE = ("very_active", 1.725, "Très actif - Exercice intensif 6-7 jours/semaine")
    EXTREMELY_ACTIVE = ("extremely_active", 1.9, "Extrêmement actif - Exercice très intensif, sport professionnel")
    
    def __init__(self, code: str, multiplier: float, description: str):
        self.code = code
        self.multiplier = multiplier
        self.description = description


class GoalType(Enum):
    """Types d'objectifs de poids avec ajustements caloriques"""
    MAINTENANCE = ("maintenance", 0, "Maintenir le poids actuel")
    WEIGHT_LOSS_SLOW = ("weight_loss_slow", -250, "Perte de poids lente (0.25 kg/semaine)")
    WEIGHT_LOSS_MODERATE = ("weight_loss_moderate", -500, "Perte de poids modérée (0.5 kg/semaine)")
    WEIGHT_LOSS_FAST = ("weight_loss_fast", -750, "Perte de poids rapide (0.75 kg/semaine)")
    WEIGHT_GAIN_SLOW = ("weight_gain_slow", 250, "Prise de poids lente (0.25 kg/semaine)")
    WEIGHT_GAIN_MODERATE = ("weight_gain_moderate", 500, "Prise de poids modérée (0.5 kg/semaine)")
    MUSCLE_GAIN = ("muscle_gain", 300, "Prise de masse musculaire")
    
    def __init__(self, code: str, calorie_adjustment: int, description: str):
        self.code = code
        self.calorie_adjustment = calorie_adjustment
        self.description = description


@dataclass
class NutritionCalculationResult:
    """Résultat des calculs nutritionnels"""
    bmr: float
    tdee: float
    adjusted_calories: float
    protein_target: float
    carbs_target: float
    fat_target: float
    fiber_target: float
    water_target: float
    calculation_method: str
    cache_used: bool
    calculated_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire"""
        result = asdict(self)
        result['calculated_at'] = self.calculated_at.isoformat()
        return result


class NutritionCalculatorService:
    """Service de calcul nutritionnel avec cache multi-niveau"""
    
    # Constantes de calcul
    CACHE_TTL_HOURS = 168  # 7 jours
    MIN_BMR = 800  # BMR minimum sécuritaire
    MAX_BMR = 4000  # BMR maximum réaliste
    MIN_CALORIES = 1000  # Calories minimum par jour
    MAX_CALORIES = 5000  # Calories maximum par jour
    
    # Ratios macro-nutriments par défaut
    DEFAULT_PROTEIN_RATIO = 0.25  # 25% des calories
    DEFAULT_CARBS_RATIO = 0.45   # 45% des calories
    DEFAULT_FAT_RATIO = 0.30     # 30% des calories
    
    # Besoins minimums par kg de poids corporel
    MIN_PROTEIN_PER_KG = 0.8    # g/kg minimum
    ACTIVE_PROTEIN_PER_KG = 1.2  # g/kg pour personnes actives
    MAX_PROTEIN_PER_KG = 2.0    # g/kg maximum
    
    def __init__(self):
        """Initialise le service avec cache"""
        self.cache = CacheService()
        logger.info("NutritionCalculatorService initialisé")
    
    def calculate_nutrition_profile(
        self, 
        user: User, 
        goal_type: Optional[str] = None,
        force_recalculate: bool = False
    ) -> NutritionCalculationResult:
        """
        Calcule le profil nutritionnel complet d'un utilisateur
        
        Args:
            user: Utilisateur pour qui calculer
            goal_type: Type d'objectif (optionnel, sinon détecté automatiquement)
            force_recalculate: Force le recalcul même si cache valide
            
        Returns:
            NutritionCalculationResult: Profil nutritionnel complet
        """
        cache_key = f"nutrition_profile:{user.id}:{goal_type or 'auto'}"
        
        # Vérifier le cache si pas de recalcul forcé
        if not force_recalculate:
            cached_result = self._get_cached_result(user, cache_key)
            if cached_result:
                logger.info(f"Profil nutritionnel trouvé en cache pour utilisateur {user.id}")
                return cached_result
        
        # Validation des données utilisateur
        self._validate_user_data(user)
        
        # Calcul BMR avec formule Mifflin-St Jeor
        bmr = self._calculate_bmr_mifflin_st_jeor(user)
        
        # Calcul TDEE
        tdee = self._calculate_tdee(bmr, user.activity_level)
        
        # Ajustement selon objectif
        goal = self._determine_goal_type(user, goal_type)
        adjusted_calories = self._adjust_calories_for_goal(tdee, goal)
        
        # Calcul des macro-nutriments
        macros = self._calculate_macronutrients(adjusted_calories, user)
        
        # Calcul besoins en eau
        water_target = self._calculate_water_needs(user)
        
        # Création du résultat
        result = NutritionCalculationResult(
            bmr=bmr,
            tdee=tdee,
            adjusted_calories=adjusted_calories,
            protein_target=macros['protein'],
            carbs_target=macros['carbs'],
            fat_target=macros['fat'],
            fiber_target=macros['fiber'],
            water_target=water_target,
            calculation_method="mifflin_st_jeor",
            cache_used=False,
            calculated_at=datetime.utcnow()
        )
        
        # Mettre à jour le cache utilisateur et service
        self._update_user_cache(user, result)
        self.cache.set(cache_key, result.to_dict(), ttl_hours=self.CACHE_TTL_HOURS)
        
        logger.info(f"Profil nutritionnel calculé pour utilisateur {user.id}: BMR={bmr}, TDEE={tdee}")
        return result
    
    def _calculate_bmr_mifflin_st_jeor(self, user: User) -> float:
        """
        Calcule le BMR avec la formule de Mifflin-St Jeor (plus précise que Harris-Benedict)
        
        Formules:
        - Hommes: BMR = 10 × poids(kg) + 6.25 × taille(cm) - 5 × âge(années) + 5
        - Femmes: BMR = 10 × poids(kg) + 6.25 × taille(cm) - 5 × âge(années) - 161
        """
        weight = user.current_weight
        height = user.height
        age = user.calculated_age
        gender = user.gender.lower() if user.gender else None
        
        if gender == 'male':
            bmr = 10 * weight + 6.25 * height - 5 * age + 5
        elif gender == 'female':
            bmr = 10 * weight + 6.25 * height - 5 * age - 161
        else:
            # Valeur moyenne si genre non spécifié
            bmr_male = 10 * weight + 6.25 * height - 5 * age + 5
            bmr_female = 10 * weight + 6.25 * height - 5 * age - 161
            bmr = (bmr_male + bmr_female) / 2
            logger.warning(f"Genre non spécifié pour utilisateur {user.id}, utilisation moyenne")
        
        # Validation et limites de sécurité
        bmr = max(self.MIN_BMR, min(self.MAX_BMR, bmr))
        
        return round(bmr, 1)
    
    def _calculate_tdee(self, bmr: float, activity_level: Optional[str]) -> float:
        """Calcule la dépense énergétique totale (TDEE)"""
        if not activity_level:
            activity_level = 'sedentary'  # Par défaut
        
        # Trouver le multiplicateur d'activité
        multiplier = 1.2  # Défaut sédentaire
        for level in ActivityLevel:
            if level.code == activity_level:
                multiplier = level.multiplier
                break
        
        tdee = bmr * multiplier
        return round(tdee, 1)
    
    def _determine_goal_type(self, user: User, goal_type: Optional[str]) -> GoalType:
        """Détermine le type d'objectif de l'utilisateur"""
        if goal_type:
            # Objectif explicitement fourni
            for goal in GoalType:
                if goal.code == goal_type:
                    return goal
        
        # Auto-détection basée sur poids actuel vs cible
        if user.current_weight and user.target_weight:
            diff = user.target_weight - user.current_weight
            
            if abs(diff) <= 0.5:  # Différence négligeable
                return GoalType.MAINTENANCE
            elif diff < -5:  # Perte importante
                return GoalType.WEIGHT_LOSS_MODERATE
            elif diff < 0:  # Perte légère
                return GoalType.WEIGHT_LOSS_SLOW
            elif diff > 5:  # Gain important
                return GoalType.WEIGHT_GAIN_MODERATE
            else:  # Gain léger
                return GoalType.WEIGHT_GAIN_SLOW
        
        # Défaut : maintenance
        return GoalType.MAINTENANCE
    
    def _adjust_calories_for_goal(self, tdee: float, goal: GoalType) -> float:
        """Ajuste les calories selon l'objectif"""
        adjusted = tdee + goal.calorie_adjustment
        
        # Limites de sécurité
        adjusted = max(self.MIN_CALORIES, min(self.MAX_CALORIES, adjusted))
        
        return round(adjusted, 0)
    
    def _calculate_macronutrients(self, calories: float, user: User) -> Dict[str, float]:
        """Calcule les besoins en macro-nutriments"""
        
        # Calcul des protéines (priorité)
        protein_per_kg = self.MIN_PROTEIN_PER_KG
        if user.activity_level in ['moderately_active', 'very_active', 'extremely_active']:
            protein_per_kg = self.ACTIVE_PROTEIN_PER_KG
        
        protein_grams = min(
            user.current_weight * protein_per_kg,
            user.current_weight * self.MAX_PROTEIN_PER_KG
        )
        
        # Ajustement si objectif spécifique détecté dans les goals
        if user.goals_list:
            goals_str = ' '.join(user.goals_list).lower()
            if 'muscle' in goals_str or 'masse' in goals_str:
                protein_grams = user.current_weight * 1.6  # Plus de protéines pour prise de masse
        
        protein_calories = protein_grams * 4  # 4 cal/g
        
        # Calcul des lipides (minimum 20% des calories)
        min_fat_calories = calories * 0.20
        target_fat_calories = calories * self.DEFAULT_FAT_RATIO
        fat_calories = max(min_fat_calories, target_fat_calories)
        fat_grams = fat_calories / 9  # 9 cal/g
        
        # Glucides avec le reste des calories
        remaining_calories = calories - protein_calories - fat_calories
        carbs_grams = max(0, remaining_calories / 4)  # 4 cal/g
        
        # Fibres basées sur les calories (14g pour 1000 cal selon recommandations)
        fiber_grams = (calories / 1000) * 14
        fiber_grams = max(25, min(50, fiber_grams))  # Entre 25 et 50g
        
        return {
            'protein': round(protein_grams, 1),
            'carbs': round(carbs_grams, 1),
            'fat': round(fat_grams, 1),
            'fiber': round(fiber_grams, 1)
        }
    
    def _calculate_water_needs(self, user: User) -> float:
        """Calcule les besoins en eau (ml/jour)"""
        if not user.current_weight:
            return 2000  # Défaut 2L
        
        # Formule de base : 35ml par kg de poids
        base_water = user.current_weight * 35
        
        # Ajustement selon activité
        activity_bonus = 0
        if user.activity_level in ['moderately_active', 'very_active']:
            activity_bonus = 500
        elif user.activity_level == 'extremely_active':
            activity_bonus = 1000
        
        total_water = base_water + activity_bonus
        
        # Limites (1.5L à 4L)
        total_water = max(1500, min(4000, total_water))
        
        return round(total_water, 0)
    
    def _validate_user_data(self, user: User) -> None:
        """Valide les données utilisateur pour les calculs"""
        errors = []
        
        if not user.current_weight or user.current_weight <= 0:
            errors.append("Poids actuel requis et doit être positif")
        
        if not user.height or user.height <= 0:
            errors.append("Taille requise et doit être positive")
        
        if not user.calculated_age or user.calculated_age <= 0:
            errors.append("Âge requis et doit être positif")
        
        if user.current_weight and (user.current_weight < 20 or user.current_weight > 300):
            errors.append("Poids doit être entre 20 et 300 kg")
        
        if user.height and (user.height < 50 or user.height > 250):
            errors.append("Taille doit être entre 50 et 250 cm")
        
        if user.calculated_age and (user.calculated_age < 10 or user.calculated_age > 120):
            errors.append("Âge doit être entre 10 et 120 ans")
        
        if errors:
            raise ValueError(f"Données utilisateur invalides: {'; '.join(errors)}")
    
    def _get_cached_result(self, user: User, cache_key: str) -> Optional[NutritionCalculationResult]:
        """Récupère un résultat depuis le cache multi-niveau"""
        
        # 1. Cache en mémoire (utilisateur)
        if (user.cached_bmr and user.cached_tdee and user.cache_last_updated and
            (datetime.utcnow() - user.cache_last_updated).total_seconds() < self.CACHE_TTL_HOURS * 3600):
            
            return NutritionCalculationResult(
                bmr=user.cached_bmr,
                tdee=user.cached_tdee,
                adjusted_calories=user.cached_tdee,  # Approximation
                protein_target=user.daily_protein_target or 100,
                carbs_target=user.daily_carbs_target or 200,
                fat_target=user.daily_fat_target or 80,
                fiber_target=user.daily_fiber_target or 25,
                water_target=user.daily_water_target or 2000,
                calculation_method="cached_user",
                cache_used=True,
                calculated_at=user.cache_last_updated
            )
        
        # 2. Cache service (Redis/mémoire)
        cached_data = self.cache.get(cache_key)
        if cached_data:
            cached_data['cache_used'] = True
            cached_data['calculated_at'] = datetime.fromisoformat(cached_data['calculated_at'])
            return NutritionCalculationResult(**cached_data)
        
        return None
    
    def _update_user_cache(self, user: User, result: NutritionCalculationResult) -> None:
        """Met à jour le cache au niveau utilisateur"""
        user.cached_bmr = result.bmr
        user.cached_tdee = result.tdee
        user.cache_last_updated = result.calculated_at
        
        # Mise à jour des objectifs nutritionnels
        user.daily_calories_target = result.adjusted_calories
        user.daily_protein_target = result.protein_target
        user.daily_carbs_target = result.carbs_target
        user.daily_fat_target = result.fat_target
        user.daily_fiber_target = result.fiber_target
        user.daily_water_target = result.water_target
        
        try:
            db.session.commit()
            logger.info(f"Cache utilisateur mis à jour pour {user.id}")
        except Exception as e:
            logger.error(f"Erreur mise à jour cache utilisateur {user.id}: {e}")
            db.session.rollback()
    
    def get_activity_levels(self) -> List[Dict[str, str]]:
        """Retourne la liste des niveaux d'activité disponibles"""
        return [
            {
                'code': level.code,
                'multiplier': level.multiplier,
                'description': level.description
            }
            for level in ActivityLevel
        ]
    
    def get_goal_types(self) -> List[Dict[str, Any]]:
        """Retourne la liste des types d'objectifs disponibles"""
        return [
            {
                'code': goal.code,
                'calorie_adjustment': goal.calorie_adjustment,
                'description': goal.description
            }
            for goal in GoalType
        ]
    
    def calculate_portion_multiplier(
        self, 
        user: User, 
        base_calories: float,
        nutrition_profile: Optional[NutritionCalculationResult] = None
    ) -> float:
        """
        Calcule le multiplicateur de portions pour ajuster les recettes
        selon les besoins caloriques de l'utilisateur
        """
        if not nutrition_profile:
            nutrition_profile = self.calculate_nutrition_profile(user)
        
        if base_calories <= 0:
            return 1.0
        
        multiplier = nutrition_profile.adjusted_calories / base_calories
        
        # Limites raisonnables (0.5x à 2x)
        multiplier = max(0.5, min(2.0, multiplier))
        
        return round(multiplier, 2)
    
    def validate_nutrition_goals(self, user: User) -> Dict[str, Any]:
        """Valide et analyse les objectifs nutritionnels de l'utilisateur"""
        
        validation = {
            'is_valid': True,
            'warnings': [],
            'errors': [],
            'suggestions': []
        }
        
        try:
            # Calcul du profil actuel
            profile = self.calculate_nutrition_profile(user)
            
            # Vérifications de sécurité
            if profile.adjusted_calories < 1200:
                validation['warnings'].append(
                    "Objectif calorique très bas - risque de carences nutritionnelles"
                )
            
            if profile.adjusted_calories > 3500:
                validation['warnings'].append(
                    "Objectif calorique très élevé - vérifiez vos paramètres d'activité"
                )
            
            # Analyse des ratios
            total_calories = (profile.protein_target * 4 + 
                            profile.carbs_target * 4 + 
                            profile.fat_target * 9)
            
            protein_ratio = (profile.protein_target * 4) / total_calories
            carbs_ratio = (profile.carbs_target * 4) / total_calories
            fat_ratio = (profile.fat_target * 9) / total_calories
            
            if protein_ratio < 0.15:
                validation['suggestions'].append(
                    "Augmentez vos apports en protéines (minimum 15% des calories)"
                )
            
            if fat_ratio < 0.20:
                validation['warnings'].append(
                    "Apport en lipides insuffisant (minimum 20% des calories requis)"
                )
            
            validation['current_profile'] = profile.to_dict()
            validation['ratios'] = {
                'protein': round(protein_ratio * 100, 1),
                'carbs': round(carbs_ratio * 100, 1),
                'fat': round(fat_ratio * 100, 1)
            }
            
        except Exception as e:
            validation['is_valid'] = False
            validation['errors'].append(str(e))
        
        return validation


# Instance globale du service
nutrition_calculator = NutritionCalculatorService()