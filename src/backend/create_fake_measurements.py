#!/usr/bin/env python3
"""
Script pour créer des données fictives de mesures entre le 1er et 28 juillet
"""

import sys
import os
from pathlib import Path
from datetime import date, datetime, timedelta
import random

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from flask import Flask
from database import db
from database.config import get_config

def create_fake_measurements():
    """Crée des mesures fictives réalistes entre le 1er et 28 juillet"""
    
    # Configuration Flask
    app = Flask(__name__)
    config = get_config('development')
    app.config.from_object(config)
    db.init_app(app)
    
    with app.app_context():
        # Import les modèles
        from models.user import User, WeightHistory
        from models.measurements import UserMeasurement
        from models.recipe import Recipe
        from models.meal_plan import MealPlan
        from models.ingredient import Ingredient
        
        print("🎲 Création de données fictives de mesures...")
        
        # Dates du 1er au 28 juillet 2024
        start_date = date(2024, 7, 1)
        end_date = date(2024, 7, 28)
        
        # Poids de départ et tendance générale (légère perte)
        base_weight = 101.0
        weight_loss_rate = 0.07  # ~70g par jour en moyenne = ~2kg sur 28 jours
        
        current_date = start_date
        day_count = 0
        created_count = 0
        
        while current_date <= end_date:
            # Vérifier si une mesure existe déjà pour cette date
            existing = UserMeasurement.query.filter(
                UserMeasurement.user_id == 1,
                UserMeasurement.date == current_date
            ).first()
            
            if not existing:
                # Calculer le poids avec variation naturelle
                # Tendance générale de perte + variation quotidienne
                weight_trend = base_weight - (weight_loss_rate * day_count)
                daily_variation = random.uniform(-0.5, 0.3)  # Variation de -500g à +300g
                weight = weight_trend + daily_variation
                
                # S'assurer que le poids reste dans les limites (99-101 kg)
                weight = max(99.0, min(101.0, weight))
                
                # Créer la mesure
                measurement = UserMeasurement(
                    user_id=1,
                    date=current_date,
                    weight=round(weight, 1),
                    
                    # Composition corporelle (variations légères)
                    body_fat=round(25 - (day_count * 0.05) + random.uniform(-0.5, 0.5), 1),  # Diminution progressive
                    muscle_mass=round(35 + (day_count * 0.03) + random.uniform(-0.3, 0.3), 1),  # Augmentation légère
                    water_percentage=round(55 + random.uniform(-1, 1), 1),
                    
                    # Activité physique (variable selon le jour)
                    calories_burned=random.randint(1800, 2800),
                    steps=random.randint(3000, 12000),
                    exercise_hours=round(random.uniform(0, 2), 1),
                    exercise_type=random.choice(['Musculation', 'Course', 'Vélo', 'Marche', 'HIIT', 'Yoga', None]),
                    distance_walked=round(random.uniform(2, 10), 1),
                    active_minutes=random.randint(20, 90),
                    
                    # Nutrition (cohérent avec objectif de perte)
                    calories_consumed=random.randint(1400, 1800),  # Déficit calorique
                    protein=random.randint(100, 150),
                    carbs=random.randint(80, 150),
                    fat=random.randint(50, 80),
                    fiber=random.randint(20, 35),
                    water_intake=random.randint(1500, 3000),
                    
                    # Sommeil et santé
                    sleep_hours=round(random.uniform(6, 9), 1),
                    sleep_quality=random.randint(6, 9),
                    heart_rate_rest=random.randint(55, 70),
                    stress_level=random.randint(3, 7),
                    energy_level=random.randint(5, 9),
                    
                    # Mesures corporelles (changements progressifs)
                    waist=round(105 - (day_count * 0.1) + random.uniform(-0.5, 0.5), 1),  # Diminution
                    
                    notes=f"Mesure du {current_date.strftime('%d/%m')}",
                    data_source="script",
                    is_verified=True
                )
                
                db.session.add(measurement)
                
                # Ajouter aussi à l'historique de poids
                weight_entry = WeightHistory(
                    user_id=1,
                    weight=measurement.weight,
                    body_fat_percentage=measurement.body_fat,
                    muscle_mass_percentage=measurement.muscle_mass,
                    water_percentage=measurement.water_percentage,
                    recorded_date=current_date,
                    notes=f"Importé depuis les mesures",
                    measurement_method="scale",
                    data_source="measurements"
                )
                db.session.add(weight_entry)
                
                created_count += 1
            
            current_date += timedelta(days=1)
            day_count += 1
        
        # Ajouter quelques mesures plus récentes (fin juillet - début août)
        recent_dates = [
            date(2024, 7, 29),
            date(2024, 7, 30),
            date(2024, 7, 31),
            date(2024, 8, 1),
            date(2024, 8, 3),
            date(2024, 8, 5),
            date(2024, 8, 6)
        ]
        
        for idx, measure_date in enumerate(recent_dates):
            existing = UserMeasurement.query.filter(
                UserMeasurement.user_id == 1,
                UserMeasurement.date == measure_date
            ).first()
            
            if not existing:
                # Poids continue à descendre vers 99kg
                weight = 99.5 - (idx * 0.07) + random.uniform(-0.2, 0.2)
                weight = max(99.0, min(99.8, weight))
                
                measurement = UserMeasurement(
                    user_id=1,
                    date=measure_date,
                    weight=round(weight, 1),
                    body_fat=round(24 - (idx * 0.1), 1),
                    muscle_mass=round(36 + (idx * 0.05), 1),
                    water_percentage=round(55.5 + random.uniform(-0.5, 0.5), 1),
                    calories_burned=random.randint(2000, 2600),
                    steps=random.randint(5000, 10000),
                    exercise_hours=round(random.uniform(0.5, 1.5), 1),
                    calories_consumed=random.randint(1500, 1700),
                    protein=random.randint(120, 140),
                    carbs=random.randint(100, 130),
                    fat=random.randint(55, 70),
                    sleep_hours=round(random.uniform(7, 8.5), 1),
                    waist=round(103 - (idx * 0.15), 1),
                    notes=f"Progression constante",
                    data_source="script",
                    is_verified=True
                )
                
                db.session.add(measurement)
                
                # Historique de poids
                weight_entry = WeightHistory(
                    user_id=1,
                    weight=measurement.weight,
                    body_fat_percentage=measurement.body_fat,
                    recorded_date=measure_date,
                    notes=f"Proche de l'objectif",
                    measurement_method="scale",
                    data_source="measurements"
                )
                db.session.add(weight_entry)
                
                created_count += 1
        
        db.session.commit()
        
        print(f"✅ {created_count} mesures créées avec succès")
        
        # Afficher un résumé
        all_measurements = UserMeasurement.query.filter(
            UserMeasurement.user_id == 1
        ).order_by(UserMeasurement.date).all()
        
        if all_measurements:
            print(f"\n📊 Résumé des mesures:")
            print(f"   Première mesure: {all_measurements[0].date} - {all_measurements[0].weight}kg")
            print(f"   Dernière mesure: {all_measurements[-1].date} - {all_measurements[-1].weight}kg")
            print(f"   Perte totale: {round(all_measurements[0].weight - all_measurements[-1].weight, 1)}kg")
            print(f"   Nombre total de mesures: {len(all_measurements)}")

if __name__ == '__main__':
    try:
        create_fake_measurements()
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)