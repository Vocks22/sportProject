#!/usr/bin/env python3
"""
Script pour créer la table user_measurements dans la base de données
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from flask import Flask
from database import db
from database.config import get_config
from models.user import User, WeightHistory
from models.measurements import UserMeasurement
# Import tous les modèles pour éviter les erreurs de relation
from models.recipe import Recipe
from models.meal_plan import MealPlan
from models.ingredient import Ingredient

def create_measurements_table():
    """Crée la table user_measurements si elle n'existe pas"""
    
    # Configuration Flask
    app = Flask(__name__)
    config = get_config('development')
    app.config.from_object(config)
    db.init_app(app)
    
    with app.app_context():
        # Créer toutes les tables (y compris user_measurements)
        db.create_all()
        
        print("✅ Table user_measurements créée avec succès")
        
        # Vérifier que l'utilisateur existe
        user = User.query.get(1)
        if user:
            # Créer une première mesure avec le poids actuel
            from datetime import date
            
            existing = UserMeasurement.query.filter(
                UserMeasurement.user_id == 1,
                UserMeasurement.date == date.today()
            ).first()
            
            if not existing:
                first_measurement = UserMeasurement(
                    user_id=1,
                    date=date.today(),
                    weight=99.0,  # Ton poids actuel
                    notes="Première mesure - Début du suivi complet",
                    data_source="initialization",
                    is_verified=True
                )
                db.session.add(first_measurement)
                db.session.commit()
                print(f"✅ Première mesure créée : 99.0 kg pour aujourd'hui")
            else:
                print(f"ℹ️ Une mesure existe déjà pour aujourd'hui")
        else:
            print("❌ Utilisateur non trouvé")

if __name__ == '__main__':
    try:
        create_measurements_table()
    except Exception as e:
        print(f"❌ Erreur: {e}")
        sys.exit(1)