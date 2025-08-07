#!/usr/bin/env python3
"""
Script pour créer un utilisateur de test avec des données pour l'US1.7
"""

import sys
import os
from pathlib import Path
from datetime import datetime, date, timedelta

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from flask import Flask
from database import db
from database.config import get_config

# Importer tous les modèles pour éviter les erreurs de relations
from models.user import User, WeightHistory
from models.meal_plan import MealPlan
from models.recipe import Recipe
from models.ingredient import Ingredient

def create_test_user():
    """Crée un utilisateur de test avec des données complètes"""
    
    # Configuration Flask
    app = Flask(__name__)
    config = get_config('development')
    app.config.from_object(config)
    db.init_app(app)
    
    with app.app_context():
        # Vérifier si l'utilisateur existe déjà
        existing_user = User.query.filter_by(id=1).first()
        if existing_user:
            print("ℹ️ Utilisateur de test déjà existant, mise à jour...")
            user = existing_user
        else:
            print("✨ Création d'un nouvel utilisateur de test...")
            user = User(id=1)
            db.session.add(user)
        
        # Mettre à jour les données de l'utilisateur
        user.username = "test_user"
        user.email = "test@diettracker.com"
        user.current_weight = 75.0
        user.target_weight = 70.0
        user.height = 175.0
        user.age = 30
        user.gender = "male"
        user.activity_level = "moderately_active"
        
        # Nouvelles données US1.7
        user.birth_date = date(1994, 5, 15)
        user.goals = "Perdre 5kg et améliorer ma condition physique"
        user.dietary_restrictions = "Sans lactose"
        user.preferred_cuisine_types = "Méditerranéenne, Asiatique"
        
        # Métriques de santé
        user.body_fat_percentage = 18.5
        user.muscle_mass_percentage = 42.0
        user.water_percentage = 60.0
        
        # Objectifs nutritionnels
        user.daily_calories_target = 2200
        user.daily_protein_target = 150
        user.daily_carbs_target = 250
        user.daily_fat_target = 70
        user.daily_fiber_target = 30
        user.daily_water_target = 2500
        
        # Préférences
        user.timezone = "Europe/Paris"
        user.language = "fr"
        user.units_system = "metric"
        
        # Statuts
        user.profile_completed = True
        user.profile_validated = True
        user.last_profile_update = datetime.utcnow()
        user.is_active = True
        user.created_at = datetime.utcnow()
        
        # Sauvegarder l'utilisateur
        db.session.commit()
        print(f"✅ Utilisateur créé/mis à jour: {user.username} (ID: {user.id})")
        
        # Créer un historique de poids
        print("📊 Création de l'historique de poids...")
        
        # Supprimer l'ancien historique s'il existe
        WeightHistory.query.filter_by(user_id=1).delete()
        
        # Créer 30 jours d'historique
        weights = [
            (30, 78.0), (28, 77.8), (26, 77.5), (24, 77.3), (22, 77.0),
            (20, 76.8), (18, 76.5), (16, 76.3), (14, 76.0), (12, 75.8),
            (10, 75.5), (8, 75.3), (6, 75.2), (4, 75.1), (2, 75.0),
            (0, 75.0)  # Aujourd'hui
        ]
        
        for days_ago, weight in weights:
            entry = WeightHistory(
                user_id=1,
                weight=weight,
                recorded_date=date.today() - timedelta(days=days_ago),
                body_fat_percentage=18.5 + (days_ago * 0.1),  # Simulation
                notes=f"Pesée il y a {days_ago} jours" if days_ago > 0 else "Pesée du jour"
            )
            db.session.add(entry)
        
        db.session.commit()
        print(f"✅ {len(weights)} entrées d'historique créées")
        
        # Afficher les informations de l'utilisateur
        print("\n📋 Profil utilisateur créé:")
        print(f"  - Username: {user.username}")
        print(f"  - Email: {user.email}")
        print(f"  - Poids: {user.current_weight} kg")
        print(f"  - Objectif: {user.target_weight} kg")
        print(f"  - Taille: {user.height} cm")
        print(f"  - Âge: {user.age} ans")
        print(f"  - Niveau d'activité: {user.activity_level}")
        print(f"  - Objectifs caloriques: {user.daily_calories_target} kcal/jour")
        
        print("\n🎉 Configuration terminée avec succès!")
        print("Vous pouvez maintenant accéder au profil sur http://localhost:5173/profile")
        
        return user

if __name__ == '__main__':
    try:
        create_test_user()
    except Exception as e:
        print(f"❌ Erreur: {e}")
        sys.exit(1)