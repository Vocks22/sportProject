#!/usr/bin/env python3
"""
Script pour tester l'API weight-history
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
from models.meal_plan import MealPlan  # Import nécessaire pour les relations
from models.recipe import Recipe  # Import nécessaire pour les relations
from models.ingredient import Ingredient  # Import nécessaire pour les relations
from datetime import date, timedelta
import traceback

def test_weight_history_api():
    """Test l'API weight-history directement"""
    
    # Configuration Flask
    app = Flask(__name__)
    config = get_config('development')
    app.config.from_object(config)
    db.init_app(app)
    
    with app.app_context():
        print("🔍 Test de l'API weight-history")
        
        try:
            # Paramètres de test
            user_id = 1
            days = 365
            limit = 500
            
            print(f"📊 Paramètres: user_id={user_id}, days={days}, limit={limit}")
            
            # Si days >= 365, récupérer TOUT l'historique
            if days >= 365:
                # Récupérer TOUT sans limite de date
                weight_entries = WeightHistory.query.filter(
                    WeightHistory.user_id == user_id
                ).order_by(WeightHistory.recorded_date.desc()).limit(limit).all()
            else:
                # Sinon, filtrer par date
                start_date = date.today() - timedelta(days=days)
                weight_entries = WeightHistory.query.filter(
                    WeightHistory.user_id == user_id,
                    WeightHistory.recorded_date >= start_date
                ).order_by(WeightHistory.recorded_date.desc()).limit(limit).all()
            
            print(f"✅ {len(weight_entries)} entrées trouvées")
            
            # Tester la conversion to_dict sur chaque entrée
            errors = []
            for i, entry in enumerate(weight_entries):
                try:
                    entry_dict = entry.to_dict()
                    if i < 3:  # Afficher les 3 premières
                        print(f"  {i+1}. {entry_dict['recorded_date']} - {entry_dict['weight']}kg ✓")
                except Exception as e:
                    errors.append(f"Entrée {i}: {e}")
            
            if errors:
                print(f"\n❌ {len(errors)} erreurs lors de la conversion to_dict():")
                for error in errors[:5]:  # Afficher max 5 erreurs
                    print(f"   - {error}")
            else:
                print(f"\n✅ Toutes les entrées converties avec succès!")
            
            # Statistiques
            if weight_entries:
                weights = [entry.weight for entry in weight_entries]
                stats = {
                    'count': len(weight_entries),
                    'min_weight': min(weights),
                    'max_weight': max(weights),
                    'avg_weight': round(sum(weights) / len(weights), 1),
                    'latest_weight': weights[0] if weights else None,
                    'weight_change': weights[0] - weights[-1] if len(weights) > 1 else 0,
                    'period_days': days
                }
                
                print(f"\n📈 Statistiques:")
                print(f"   - Nombre d'entrées: {stats['count']}")
                print(f"   - Poids min: {stats['min_weight']}kg")
                print(f"   - Poids max: {stats['max_weight']}kg")
                print(f"   - Poids moyen: {stats['avg_weight']}kg")
                print(f"   - Changement: {stats['weight_change']:.1f}kg")
            
        except Exception as e:
            print(f"\n❌ Erreur lors du test: {e}")
            print("\n📋 Traceback complet:")
            traceback.print_exc()
            
            # Vérifier si la table existe
            print("\n🔍 Vérification de la structure de la base de données...")
            try:
                from sqlalchemy import text
                count = db.session.execute(text("SELECT COUNT(*) FROM weight_history")).scalar()
                print(f"   ✅ Table weight_history existe avec {count} entrées")
            except Exception as db_error:
                print(f"   ❌ Problème avec la table: {db_error}")

if __name__ == '__main__':
    test_weight_history_api()