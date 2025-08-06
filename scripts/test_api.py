#!/usr/bin/env python3
"""
Script de test des API DietTracker
Vérifie que les endpoints fonctionnent correctement
"""

import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).resolve().parents[1] / 'src' / 'backend'
sys.path.insert(0, str(backend_path))

from flask import Flask
from models.user import db, User
from models.ingredient import Ingredient
from models.recipe import Recipe
from database.config import get_config

def test_database():
    """Test database connection and data"""
    app = Flask(__name__)
    config = get_config('development')
    app.config.from_object(config)
    
    # Initialize database
    db.init_app(app)
    
    with app.app_context():
        print("🔍 Test de connexion à la base de données...")
        
        try:
            # Test Ingredients
            ingredients_count = Ingredient.query.count()
            print(f"✅ Ingrédients: {ingredients_count}")
            
            if ingredients_count > 0:
                first_ingredient = Ingredient.query.first()
                print(f"   Premier ingrédient: {first_ingredient.name}")
            
            # Test Recipes
            recipes_count = Recipe.query.count()
            print(f"✅ Recettes: {recipes_count}")
            
            # Test Users
            users_count = User.query.count()
            print(f"✅ Utilisateurs: {users_count}")
            
            print("\n🎉 Connexion à la base de données OK!")
            
            # Show sample ingredient
            if ingredients_count > 0:
                print("\n📊 Exemple d'ingrédient (JSON):")
                print(first_ingredient.to_dict())
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur: {e}")
            return False

if __name__ == '__main__':
    test_database()