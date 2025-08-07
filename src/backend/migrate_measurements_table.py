#!/usr/bin/env python3
"""
Script pour migrer la table user_measurements vers la nouvelle structure
SANS PERDRE LES DONNÉES
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
from datetime import date

def migrate_measurements_table():
    """Migre la table vers la nouvelle structure en préservant les données"""
    
    # Configuration Flask
    app = Flask(__name__)
    config = get_config('development')
    app.config.from_object(config)
    db.init_app(app)
    
    with app.app_context():
        try:
            # 1. Sauvegarder les données existantes
            print("📊 Sauvegarde des données existantes...")
            result = db.session.execute(text("""
                SELECT user_id, measurement_type, value, unit, recorded_date, notes
                FROM user_measurements
            """))
            old_data = result.fetchall()
            print(f"   {len(old_data)} mesures trouvées")
            
            # 2. Renommer l'ancienne table
            print("🔄 Renommage de l'ancienne table...")
            db.session.execute(text("ALTER TABLE user_measurements RENAME TO user_measurements_old"))
            db.session.commit()
            
            # 3. Créer la nouvelle table
            print("🔨 Création de la nouvelle structure...")
            # Importer TOUS les modèles pour que les relations soient correctes
            from models.user import User, WeightHistory, UserGoalsHistory
            from models.recipe import Recipe
            from models.meal_plan import MealPlan
            from models.ingredient import Ingredient
            from models.measurements import UserMeasurement
            
            db.create_all()
            
            # 4. Migrer les données pertinentes
            print("📥 Migration des données...")
            for row in old_data:
                user_id, measure_type, value, unit, recorded_date, notes = row
                
                # Créer une nouvelle entrée pour chaque date unique
                existing = UserMeasurement.query.filter(
                    UserMeasurement.user_id == user_id,
                    UserMeasurement.date == recorded_date
                ).first()
                
                if not existing:
                    new_measurement = UserMeasurement(
                        user_id=user_id,
                        date=recorded_date,
                        notes=notes or "",
                        data_source="migrated",
                        is_verified=True
                    )
                    
                    # Mapper les anciennes mesures vers les nouveaux champs
                    if measure_type == 'weight':
                        new_measurement.weight = value
                    elif measure_type == 'height':
                        continue  # La taille va dans le profil utilisateur
                    elif measure_type == 'waist':
                        new_measurement.waist = value
                    elif measure_type == 'chest':
                        new_measurement.chest = value
                    elif measure_type == 'arms':
                        new_measurement.arms = value
                    elif measure_type == 'thighs':
                        new_measurement.thighs = value
                    elif measure_type == 'hips':
                        new_measurement.hips = value
                    elif measure_type == 'neck':
                        new_measurement.neck = value
                    
                    db.session.add(new_measurement)
                else:
                    # Mettre à jour la mesure existante
                    if measure_type == 'weight':
                        existing.weight = value
                    elif measure_type == 'waist':
                        existing.waist = value
                    elif measure_type == 'chest':
                        existing.chest = value
                    elif measure_type == 'arms':
                        existing.arms = value
                    elif measure_type == 'thighs':
                        existing.thighs = value
                    elif measure_type == 'hips':
                        existing.hips = value
                    elif measure_type == 'neck':
                        existing.neck = value
            
            db.session.commit()
            print("✅ Données migrées avec succès")
            
            # 5. Ajouter la mesure d'aujourd'hui si elle n'existe pas
            today_measurement = UserMeasurement.query.filter(
                UserMeasurement.user_id == 1,
                UserMeasurement.date == date.today()
            ).first()
            
            if not today_measurement:
                new_measurement = UserMeasurement(
                    user_id=1,
                    date=date.today(),
                    weight=99.0,
                    notes="Poids actuel",
                    data_source="manual",
                    is_verified=True
                )
                db.session.add(new_measurement)
                db.session.commit()
                print("✅ Mesure du jour ajoutée : 99.0 kg")
            
            # 6. Optionnel : supprimer l'ancienne table
            print("🗑️ Suppression de l'ancienne table...")
            db.session.execute(text("DROP TABLE IF EXISTS user_measurements_old"))
            db.session.commit()
            print("✅ Migration terminée avec succès !")
            
        except Exception as e:
            print(f"❌ Erreur: {e}")
            db.session.rollback()
            # Restaurer si erreur
            try:
                db.session.execute(text("DROP TABLE IF EXISTS user_measurements"))
                db.session.execute(text("ALTER TABLE user_measurements_old RENAME TO user_measurements"))
                db.session.commit()
                print("⚠️ Restauration effectuée")
            except:
                pass

if __name__ == '__main__':
    try:
        migrate_measurements_table()
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)