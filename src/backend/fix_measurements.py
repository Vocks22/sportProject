#!/usr/bin/env python3
"""
Script pour corriger et créer la table des mesures
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from flask import Flask
from database import db
from database.config import get_config

def fix_measurements():
    """Crée la table user_measurements correctement"""
    
    # Configuration Flask
    app = Flask(__name__)
    config = get_config('development')
    app.config.from_object(config)
    db.init_app(app)
    
    with app.app_context():
        # Import les modèles dans le contexte de l'app
        from models.user import User, WeightHistory, UserGoalsHistory
        from models.measurements import UserMeasurement
        from models.recipe import Recipe
        from models.meal_plan import MealPlan
        from models.ingredient import Ingredient
        
        # Créer toutes les tables
        db.create_all()
        
        print("✅ Tables créées/mises à jour avec succès")
        
        # Vérifier que la table existe
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        if 'user_measurements' in tables:
            print("✅ Table user_measurements existe")
            columns = [col['name'] for col in inspector.get_columns('user_measurements')]
            print(f"   Colonnes: {', '.join(columns[:10])}...")  # Afficher les 10 premières colonnes
        else:
            print("❌ Table user_measurements n'existe pas")
            
        # Créer une mesure de test
        from datetime import date
        
        try:
            # Vérifier si une mesure existe déjà
            existing = UserMeasurement.query.filter(
                UserMeasurement.user_id == 1,
                UserMeasurement.date == date.today()
            ).first()
            
            if not existing:
                test_measurement = UserMeasurement(
                    user_id=1,
                    date=date.today(),
                    weight=99.0,
                    notes="Mesure de test",
                    data_source="script",
                    is_verified=True
                )
                db.session.add(test_measurement)
                db.session.commit()
                print("✅ Mesure de test créée")
            else:
                print("ℹ️ Une mesure existe déjà pour aujourd'hui")
                
        except Exception as e:
            print(f"⚠️ Erreur lors de la création de la mesure de test: {e}")
            db.session.rollback()

if __name__ == '__main__':
    try:
        fix_measurements()
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)