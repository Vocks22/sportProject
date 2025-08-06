#!/usr/bin/env python3
"""
Script d'initialisation simplifié de la base de données
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

# Démarrer l'application Flask pour initialiser la base
if __name__ == "__main__":
    from src.main import app
    
    with app.app_context():
        from src.models.user import db
        from src.models.ingredient import Ingredient
        from src.models.recipe import Recipe
        
        print("🚀 Initialisation de la base de données...")
        
        # Créer les tables
        db.create_all()
        print("✅ Tables créées")
        
        # Vérifier si des données existent déjà
        if Ingredient.query.count() > 0:
            print("⚠️ Des données existent déjà dans la base")
            print(f"Ingrédients: {Ingredient.query.count()}")
            print(f"Recettes: {Recipe.query.count()}")
        else:
            print("📝 Base de données vide, prête pour l'initialisation manuelle")
        
        print("\n🎉 Base de données initialisée!")
        print("\nPour démarrer l'application:")
        print("python src/main.py")

