#!/usr/bin/env python3
"""
Script pour nettoyer les données de test et mettre les vraies données
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
# Import tous les modèles pour éviter les erreurs de relation
from models.recipe import Recipe
from models.meal_plan import MealPlan
from models.ingredient import Ingredient

def clean_and_setup_real_data():
    """Nettoie les données de test et met les vraies données"""
    
    # Configuration Flask
    app = Flask(__name__)
    config = get_config('development')
    app.config.from_object(config)
    db.init_app(app)
    
    with app.app_context():
        # Récupérer l'utilisateur
        user = User.query.get(1)
        if not user:
            print("❌ Aucun utilisateur trouvé")
            return
        
        print("🧹 Nettoyage des données de test...")
        
        # Supprimer tout l'historique de poids de test
        WeightHistory.query.filter_by(user_id=1).delete()
        print("✅ Historique de poids supprimé")
        
        # Mettre à jour le profil avec les vraies données
        user.current_weight = 99.0  # Ton poids actuel
        user.target_weight = 70.0   # Garder l'objectif ou le modifier si tu veux
        user.height = user.height or 175.0  # Ta taille (à modifier si nécessaire)
        
        # Créer une seule entrée de poids pour aujourd'hui
        today_weight = WeightHistory(
            user_id=1,
            weight=99.0,
            recorded_date=date.today(),
            notes="Début de la diète - Poids de départ",
            measurement_method="manual",
            is_verified=True
        )
        db.session.add(today_weight)
        
        db.session.commit()
        
        print("\n✅ Données mises à jour :")
        print(f"  - Poids actuel : {user.current_weight} kg")
        print(f"  - Objectif : {user.target_weight} kg")
        print(f"  - Historique : 1 mesure (aujourd'hui)")
        print("\n🎯 Prêt pour commencer le suivi réel !")
        
        return user

if __name__ == '__main__':
    try:
        clean_and_setup_real_data()
    except Exception as e:
        print(f"❌ Erreur: {e}")
        sys.exit(1)