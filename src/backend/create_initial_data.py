"""
Script pour créer les données initiales dans la base de données
À exécuter une seule fois après le déploiement
"""

import os
import sys
from pathlib import Path

# Force production environment
os.environ['FLASK_ENV'] = 'production'
os.environ['RENDER'] = 'true'

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from flask import Flask
from database import db
from database.config import ProductionConfig
from models.user import User
from models.recipe import Recipe
from models.ingredient import Ingredient
from models.meal_plan import MealPlan
from models.measurements import UserMeasurement
from datetime import datetime, date, timedelta

def create_initial_data():
    """Crée les données initiales dans la base de données de production"""
    
    app = Flask(__name__)
    
    # Use production config
    app.config.from_object(ProductionConfig)
    
    db.init_app(app)
    
    with app.app_context():
        print("🔄 Création des tables...")
        try:
            db.create_all()
            print("✅ Tables créées/vérifiées")
        except Exception as e:
            print(f"❌ Erreur création tables: {e}")
            return False
        
        # Vérifier si l'utilisateur existe déjà
        try:
            existing_user = User.query.filter_by(id=1).first()
            if existing_user:
                print(f"✅ L'utilisateur ID=1 existe déjà: {existing_user.username}")
            else:
                print("📝 Création de l'utilisateur test ID=1...")
                
                # Créer l'utilisateur test avec ID=1
                test_user = User(
                    id=1,
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
                    target_fat=65,
                    profile_completed=True
                )
                
                db.session.add(test_user)
                db.session.commit()
                print(f"✅ Utilisateur test créé avec ID: 1")
                
                # Ajouter quelques mesures de poids
                print("📊 Ajout de l'historique de poids...")
                base_date = date.today() - timedelta(days=30)
                weights = [75.0, 74.8, 74.5, 74.3, 74.0, 73.8, 73.5, 73.3, 73.0, 72.8]
                
                for i, weight in enumerate(weights):
                    measurement_date = base_date + timedelta(days=i*3)
                    measurement = UserMeasurement(
                        user_id=1,
                        date=measurement_date,
                        weight=weight,
                        unit='kg'
                    )
                    db.session.add(measurement)
                
                db.session.commit()
                print(f"✅ {len(weights)} mesures de poids ajoutées")
            
        except Exception as e:
            print(f"❌ Erreur création utilisateur: {e}")
            db.session.rollback()
            return False
        
        # Créer quelques ingrédients de base
        try:
            existing_ingredients = Ingredient.query.count()
            if existing_ingredients == 0:
                print("🥗 Création des ingrédients de base...")
                
                ingredients_data = [
                    {"name": "Poulet", "category": "Protéines", "calories_per_100g": 165, "protein": 31, "carbs": 0, "fat": 3.6},
                    {"name": "Riz blanc", "category": "Glucides", "calories_per_100g": 130, "protein": 2.7, "carbs": 28, "fat": 0.3},
                    {"name": "Brocoli", "category": "Légumes", "calories_per_100g": 34, "protein": 2.8, "carbs": 7, "fat": 0.4},
                    {"name": "Huile d'olive", "category": "Graisses", "calories_per_100g": 884, "protein": 0, "carbs": 0, "fat": 100},
                    {"name": "Œufs", "category": "Protéines", "calories_per_100g": 155, "protein": 13, "carbs": 1.1, "fat": 11},
                    {"name": "Saumon", "category": "Protéines", "calories_per_100g": 208, "protein": 20, "carbs": 0, "fat": 13},
                    {"name": "Pâtes", "category": "Glucides", "calories_per_100g": 131, "protein": 5, "carbs": 25, "fat": 1.1},
                    {"name": "Tomate", "category": "Légumes", "calories_per_100g": 18, "protein": 0.9, "carbs": 3.9, "fat": 0.2}
                ]
                
                for data in ingredients_data:
                    ingredient = Ingredient(**data)
                    db.session.add(ingredient)
                
                db.session.commit()
                print(f"✅ {len(ingredients_data)} ingrédients créés")
            else:
                print(f"✅ {existing_ingredients} ingrédients existent déjà")
                
        except Exception as e:
            print(f"❌ Erreur création ingrédients: {e}")
            db.session.rollback()
        
        # Créer quelques recettes
        try:
            existing_recipes = Recipe.query.count()
            if existing_recipes == 0:
                print("🍳 Création de recettes test...")
                
                recipes_data = [
                    {
                        "name": "Poulet au riz et brocoli",
                        "category": "lunch",
                        "meal_type": "repas2",
                        "prep_time": 15,
                        "cook_time": 25,
                        "servings": 2,
                        "difficulty_level": "beginner",
                        "has_chef_mode": False,
                        "instructions": ["Cuire le riz", "Griller le poulet", "Cuire le brocoli à la vapeur", "Servir ensemble"],
                        "total_calories": 450,
                        "total_protein": 35,
                        "total_carbs": 45,
                        "total_fat": 10
                    },
                    {
                        "name": "Omelette aux légumes",
                        "category": "breakfast",
                        "meal_type": "repas1",
                        "prep_time": 5,
                        "cook_time": 10,
                        "servings": 1,
                        "difficulty_level": "beginner",
                        "has_chef_mode": True,
                        "instructions": ["Battre les œufs", "Couper les légumes", "Cuire l'omelette"],
                        "total_calories": 250,
                        "total_protein": 18,
                        "total_carbs": 8,
                        "total_fat": 15
                    }
                ]
                
                for data in recipes_data:
                    recipe = Recipe(**data)
                    db.session.add(recipe)
                
                db.session.commit()
                print(f"✅ {len(recipes_data)} recettes créées")
            else:
                print(f"✅ {existing_recipes} recettes existent déjà")
                
        except Exception as e:
            print(f"❌ Erreur création recettes: {e}")
            db.session.rollback()
        
        print("\n🎉 Base de données initialisée avec succès!")
        print("\nRésumé:")
        print(f"  - Utilisateurs: {User.query.count()}")
        print(f"  - Mesures: {UserMeasurement.query.count()}")
        print(f"  - Ingrédients: {Ingredient.query.count()}")
        print(f"  - Recettes: {Recipe.query.count()}")
        
        return True

if __name__ == "__main__":
    # Vérifier que DATABASE_URL est définie
    if not os.environ.get('DATABASE_URL'):
        print("❌ DATABASE_URL n'est pas définie!")
        print("Définissez DATABASE_URL avec l'URL de votre base PostgreSQL")
        sys.exit(1)
    
    print(f"📊 Connexion à: {os.environ.get('DATABASE_URL')[:50]}...")
    
    success = create_initial_data()
    
    if success:
        print("\n✅ Script terminé avec succès")
    else:
        print("\n❌ Le script a rencontré des erreurs")
        sys.exit(1)