#!/usr/bin/env python3
"""
Script pour mettre à jour les dates de 2024 en 2025 de manière sécurisée
"""

import sys
import os
from pathlib import Path
from datetime import datetime, date

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from flask import Flask
from database import db
from database.config import get_config
from models.user import User, WeightHistory
from models.measurements import UserMeasurement
from models.meal_plan import MealPlan
from models.recipe import Recipe
from models.ingredient import Ingredient
from sqlalchemy import text

def update_dates_to_2025():
    """Met à jour toutes les dates de 2024 en 2025"""
    
    # Configuration Flask
    app = Flask(__name__)
    config = get_config('development')
    app.config.from_object(config)
    db.init_app(app)
    
    with app.app_context():
        print("🔄 Mise à jour des dates de 2024 vers 2025...")
        
        # D'abord, supprimer les entrées existantes en 2025 qui pourraient créer des conflits
        print("\n🗑️ Suppression des entrées existantes en 2025 pour éviter les conflits...")
        
        # Supprimer les mesures en conflit
        existing_2025 = UserMeasurement.query.filter(
            UserMeasurement.user_id == 1,
            UserMeasurement.date >= date(2025, 7, 1),
            UserMeasurement.date <= date(2025, 8, 31)
        ).all()
        
        if existing_2025:
            print(f"   Suppression de {len(existing_2025)} mesures existantes en 2025")
            for m in existing_2025:
                db.session.delete(m)
        
        # Supprimer les poids en conflit
        existing_weights_2025 = WeightHistory.query.filter(
            WeightHistory.user_id == 1,
            WeightHistory.recorded_date >= date(2025, 7, 1),
            WeightHistory.recorded_date <= date(2025, 8, 31)
        ).all()
        
        if existing_weights_2025:
            print(f"   Suppression de {len(existing_weights_2025)} poids existants en 2025")
            for w in existing_weights_2025:
                db.session.delete(w)
        
        # Commiter les suppressions
        db.session.commit()
        
        # Maintenant, mettre à jour les dates
        print("\n📊 Mise à jour des mesures (UserMeasurement)...")
        measurements = UserMeasurement.query.filter(
            UserMeasurement.user_id == 1,
            UserMeasurement.date >= date(2024, 7, 1),
            UserMeasurement.date <= date(2024, 8, 31)
        ).all()
        
        print(f"   Trouvé {len(measurements)} mesures en juillet-août 2024")
        
        updated_measurements = 0
        for measurement in measurements:
            old_date = measurement.date
            # Remplacer 2024 par 2025
            new_date = date(2025, old_date.month, old_date.day)
            measurement.date = new_date
            updated_measurements += 1
            if updated_measurements <= 10 or updated_measurements > len(measurements) - 5:
                print(f"   ✏️ {old_date} → {new_date}")
            elif updated_measurements == 11:
                print(f"   ... (mise à jour de {len(measurements)} entrées) ...")
        
        # Mettre à jour WeightHistory
        print("\n⚖️ Mise à jour de l'historique de poids (WeightHistory)...")
        weights = WeightHistory.query.filter(
            WeightHistory.user_id == 1,
            WeightHistory.recorded_date >= date(2024, 7, 1),
            WeightHistory.recorded_date <= date(2024, 8, 31)
        ).all()
        
        print(f"   Trouvé {len(weights)} entrées en juillet-août 2024")
        
        updated_weights = 0
        for weight in weights:
            old_date = weight.recorded_date
            # Remplacer 2024 par 2025
            new_date = date(2025, old_date.month, old_date.day)
            weight.recorded_date = new_date
            updated_weights += 1
            if updated_weights <= 10 or updated_weights > len(weights) - 5:
                print(f"   ✏️ {old_date} → {new_date}")
            elif updated_weights == 11:
                print(f"   ... (mise à jour de {len(weights)} entrées) ...")
        
        # Sauvegarder les changements
        try:
            db.session.commit()
            print("\n✅ Dates mises à jour avec succès!")
            
            # Vérifier les nouvelles dates
            print("\n📅 Vérification des nouvelles dates:")
            
            # Vérifier UserMeasurement
            measurements_2025 = UserMeasurement.query.filter(
                UserMeasurement.user_id == 1,
                UserMeasurement.date >= date(2025, 7, 1),
                UserMeasurement.date <= date(2025, 8, 31)
            ).count()
            
            # Vérifier WeightHistory
            weights_2025 = WeightHistory.query.filter(
                WeightHistory.user_id == 1,
                WeightHistory.recorded_date >= date(2025, 7, 1),
                WeightHistory.recorded_date <= date(2025, 8, 31)
            ).count()
            
            print(f"   📊 UserMeasurement en juillet-août 2025: {measurements_2025}")
            print(f"   ⚖️ WeightHistory en juillet-août 2025: {weights_2025}")
            
            # Afficher un résumé
            all_measurements = UserMeasurement.query.filter(
                UserMeasurement.user_id == 1
            ).order_by(UserMeasurement.date).all()
            
            if all_measurements:
                print(f"\n📈 Résumé des données:")
                print(f"   Première mesure: {all_measurements[0].date}")
                print(f"   Dernière mesure: {all_measurements[-1].date}")
                print(f"   Total: {len(all_measurements)} mesures")
                
                # Compter par mois
                months = {}
                for m in all_measurements:
                    month_key = f"{m.date.year}-{m.date.month:02d}"
                    if month_key not in months:
                        months[month_key] = 0
                    months[month_key] += 1
                
                print(f"\n📅 Distribution par mois:")
                for month in sorted(months.keys()):
                    year_str, month_str = month.split("-")
                    month_names = ["", "Janvier", "Février", "Mars", "Avril", "Mai", "Juin", 
                                 "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
                    month_name = month_names[int(month_str)]
                    print(f"   {month_name} {year_str}: {months[month]} mesures")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Erreur lors de la sauvegarde: {e}")
            return False
        
        return True

if __name__ == '__main__':
    try:
        success = update_dates_to_2025()
        if success:
            print("\n🎉 Toutes les dates ont été mises à jour en 2025!")
            print("   Les données de juillet-août 2024 sont maintenant en juillet-août 2025")
        else:
            print("\n❌ La mise à jour a échoué")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)