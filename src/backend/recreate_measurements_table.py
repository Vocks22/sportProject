#!/usr/bin/env python3
"""
Script pour recréer la table user_measurements avec la nouvelle structure
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from flask import Flask
from database import db
from database.config import get_config
from sqlalchemy import text

def recreate_measurements_table():
    """Supprime l'ancienne table et crée la nouvelle"""
    
    # Configuration Flask
    app = Flask(__name__)
    config = get_config('development')
    app.config.from_object(config)
    db.init_app(app)
    
    with app.app_context():
        try:
            # Supprimer l'ancienne table si elle existe
            print("🗑️ Suppression de l'ancienne table user_measurements...")
            db.session.execute(text("DROP TABLE IF EXISTS user_measurements"))
            db.session.commit()
            print("✅ Ancienne table supprimée")
            
        except Exception as e:
            print(f"⚠️ Erreur lors de la suppression: {e}")
            db.session.rollback()
        
        # Import les modèles pour créer les nouvelles tables
        from models.user import User, WeightHistory, UserGoalsHistory
        from models.measurements import UserMeasurement
        from models.recipe import Recipe
        from models.meal_plan import MealPlan
        from models.ingredient import Ingredient
        
        # Créer toutes les tables
        print("🔨 Création de la nouvelle table user_measurements...")
        db.create_all()
        print("✅ Nouvelle table créée avec succès")
        
        # Vérifier la structure
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        
        if 'user_measurements' in inspector.get_table_names():
            columns = [col['name'] for col in inspector.get_columns('user_measurements')]
            print(f"✅ Colonnes créées: {', '.join(columns[:15])}...")
            
            # Créer une première mesure
            from datetime import date
            
            try:
                first_measurement = UserMeasurement(
                    user_id=1,
                    date=date.today(),
                    weight=99.0,
                    calories_burned=0,
                    steps=0,
                    exercise_hours=0,
                    notes="Première mesure - Poids de départ",
                    data_source="initialization",
                    is_verified=True
                )
                db.session.add(first_measurement)
                db.session.commit()
                print("✅ Première mesure créée : 99.0 kg")
                
            except Exception as e:
                print(f"⚠️ Erreur création mesure: {e}")
                db.session.rollback()
        else:
            print("❌ La table n'a pas été créée")

if __name__ == '__main__':
    try:
        recreate_measurements_table()
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)