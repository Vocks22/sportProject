"""
Script d'initialisation de la base de données en production
À exécuter une fois après le déploiement sur Render
"""

import os
import sys
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent))

from flask import Flask
from database import db
from database.config import ProductionConfig
from models.user import User
from models.recipe import Recipe
from models.ingredient import Ingredient
from models.meal_plan import MealPlan
from datetime import datetime, date

def init_production_database():
    """Initialise la base de données de production avec des données de test"""
    
    app = Flask(__name__)
    app.config.from_object(ProductionConfig)
    
    db.init_app(app)
    
    with app.app_context():
        print("🔄 Création des tables...")
        db.create_all()
        
        # Vérifier si l'utilisateur test existe déjà
        existing_user = User.query.filter_by(username="testuser").first()
        if existing_user:
            print("✅ L'utilisateur test existe déjà")
            return
        
        print("📝 Création de l'utilisateur test...")
        
        # Créer un utilisateur test
        test_user = User(
            username="testuser",
            email="test@diettracker.com",
            age=30,
            gender="male",
            height=175,
            current_weight=75.0,
            target_weight=70.0,
            activity_level="moderate",
            dietary_restrictions=[],
            fitness_goal="weight_loss",
            target_calories=2000,
            target_protein=150,
            target_carbs=200,
            target_fat=65
        )
        
        db.session.add(test_user)
        db.session.commit()
        
        print(f"✅ Utilisateur test créé avec ID: {test_user.id}")
        
        # Créer quelques ingrédients de base
        print("🥗 Création des ingrédients de base...")
        
        ingredients_data = [
            {"name": "Poulet", "category": "Protéines", "calories_per_100g": 165, "protein": 31, "carbs": 0, "fat": 3.6},
            {"name": "Riz blanc", "category": "Glucides", "calories_per_100g": 130, "protein": 2.7, "carbs": 28, "fat": 0.3},
            {"name": "Brocoli", "category": "Légumes", "calories_per_100g": 34, "protein": 2.8, "carbs": 7, "fat": 0.4},
            {"name": "Huile d'olive", "category": "Graisses", "calories_per_100g": 884, "protein": 0, "carbs": 0, "fat": 100},
            {"name": "Œufs", "category": "Protéines", "calories_per_100g": 155, "protein": 13, "carbs": 1.1, "fat": 11}
        ]
        
        for data in ingredients_data:
            ingredient = Ingredient(**data)
            db.session.add(ingredient)
        
        db.session.commit()
        print("✅ Ingrédients créés")
        
        # Créer une recette simple
        print("🍳 Création d'une recette test...")
        
        test_recipe = Recipe(
            name="Poulet au riz et brocoli",
            category="lunch",
            meal_type="repas2",
            prep_time=15,
            cook_time=25,
            servings=2,
            difficulty_level="beginner",
            has_chef_mode=False
        )
        
        db.session.add(test_recipe)
        db.session.commit()
        
        print(f"✅ Recette test créée avec ID: {test_recipe.id}")
        
        print("\n🎉 Base de données de production initialisée avec succès!")
        print(f"   - Utilisateur test: ID={test_user.id}, username=testuser")
        print(f"   - Recette test: ID={test_recipe.id}")
        print(f"   - {len(ingredients_data)} ingrédients créés")
        
        return test_user.id

if __name__ == "__main__":
    # Forcer l'environnement de production
    os.environ['FLASK_ENV'] = 'production'
    init_production_database()