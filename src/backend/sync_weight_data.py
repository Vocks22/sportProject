#!/usr/bin/env python3
"""
Script pour synchroniser les données de poids entre UserMeasurement et WeightHistory
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
from models.recipe import Recipe
from models.meal_plan import MealPlan
from models.ingredient import Ingredient

def sync_weight_data():
    """Synchronise les données de poids entre les deux tables"""
    
    # Configuration Flask
    app = Flask(__name__)
    config = get_config('development')
    app.config.from_object(config)
    db.init_app(app)
    
    with app.app_context():
        print("🔄 Synchronisation des données de poids...")
        
        # Récupérer toutes les mesures avec un poids
        measurements = UserMeasurement.query.filter(
            UserMeasurement.user_id == 1,
            UserMeasurement.weight.isnot(None)
        ).order_by(UserMeasurement.date).all()
        
        print(f"📊 {len(measurements)} mesures trouvées avec un poids")
        
        synced = 0
        for measurement in measurements:
            # Vérifier si une entrée existe dans WeightHistory
            existing = WeightHistory.query.filter(
                WeightHistory.user_id == 1,
                WeightHistory.recorded_date == measurement.date
            ).first()
            
            if not existing:
                # Créer l'entrée manquante
                weight_entry = WeightHistory(
                    user_id=1,
                    weight=measurement.weight,
                    body_fat_percentage=measurement.body_fat,
                    muscle_mass_percentage=measurement.muscle_mass,
                    water_percentage=measurement.water_percentage,
                    recorded_date=measurement.date,
                    notes=f"Synchronisé depuis UserMeasurement",
                    measurement_method="scale",
                    data_source="sync_script"
                )
                db.session.add(weight_entry)
                synced += 1
                print(f"  ➕ Ajout: {measurement.date} - {measurement.weight}kg")
            else:
                # Mettre à jour si le poids est différent
                if existing.weight != measurement.weight:
                    existing.weight = measurement.weight
                    existing.body_fat_percentage = measurement.body_fat
                    existing.muscle_mass_percentage = measurement.muscle_mass
                    existing.water_percentage = measurement.water_percentage
                    existing.updated_at = measurement.updated_at
                    synced += 1
                    print(f"  🔄 Mise à jour: {measurement.date} - {measurement.weight}kg")
        
        db.session.commit()
        
        print(f"\n✅ Synchronisation terminée: {synced} entrées synchronisées")
        
        # Afficher le résumé
        weight_count = WeightHistory.query.filter_by(user_id=1).count()
        print(f"📈 Total dans WeightHistory: {weight_count} entrées")

if __name__ == '__main__':
    try:
        sync_weight_data()
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)