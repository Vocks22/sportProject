#!/usr/bin/env python3
"""
Script d'initialisation de la base de données DietTracker
Crée les tables et insère les données initiales (ingrédients, recettes)
"""

import sys
import os
from pathlib import Path
from datetime import datetime, date

# Add backend to path
backend_path = Path(__file__).resolve().parents[1] / 'src' / 'backend'
sys.path.insert(0, str(backend_path))

from flask import Flask
from models.user import db, User
from models.ingredient import Ingredient
from models.recipe import Recipe
from models.meal_plan import MealPlan, ShoppingList
from database.config import get_config

def init_ingredients():
    """Initialiser les ingrédients de base"""
    ingredients_data = [
        # Protéines
        {
            "name": "Blanc d'œuf",
            "category": "protein",
            "nutrition_per_100g": {
                "calories": 47,
                "protein": 10.3,
                "carbs": 0.7,
                "fat": 0.2
            },
            "unit": "g"
        },
        {
            "name": "Blanc de poulet",
            "category": "protein",
            "nutrition_per_100g": {
                "calories": 121,
                "protein": 26.2,
                "carbs": 0,
                "fat": 1.8
            },
            "unit": "g"
        },
        {
            "name": "Escalope de dinde",
            "category": "protein",
            "nutrition_per_100g": {
                "calories": 109,
                "protein": 22,
                "carbs": 0,
                "fat": 2.5
            },
            "unit": "g"
        },
        {
            "name": "Filet de cabillaud",
            "category": "protein",
            "nutrition_per_100g": {
                "calories": 105,
                "protein": 22.8,
                "carbs": 0,
                "fat": 1.5
            },
            "unit": "g"
        },
        {
            "name": "Filet de sole",
            "category": "protein",
            "nutrition_per_100g": {
                "calories": 85,
                "protein": 18,
                "carbs": 0,
                "fat": 1.2
            },
            "unit": "g"
        },
        # Oléagineux
        {
            "name": "Noix de cajou",
            "category": "nuts",
            "nutrition_per_100g": {
                "calories": 550,
                "protein": 17.5,
                "carbs": 30,
                "fat": 45
            },
            "unit": "g"
        },
        {
            "name": "Amandes",
            "category": "nuts",
            "nutrition_per_100g": {
                "calories": 575,
                "protein": 20,
                "carbs": 20,
                "fat": 50
            },
            "unit": "g"
        },
        # Légumes
        {
            "name": "Brocolis",
            "category": "vegetable",
            "nutrition_per_100g": {
                "calories": 25,
                "protein": 2.6,
                "carbs": 5,
                "fat": 0.3
            },
            "unit": "g"
        },
        {
            "name": "Épinards frais",
            "category": "vegetable",
            "nutrition_per_100g": {
                "calories": 23,
                "protein": 2.9,
                "carbs": 3.6,
                "fat": 0.4
            },
            "unit": "g"
        },
        {
            "name": "Haricots verts",
            "category": "vegetable",
            "nutrition_per_100g": {
                "calories": 30,
                "protein": 2,
                "carbs": 5.5,
                "fat": 0.2
            },
            "unit": "g"
        },
        {
            "name": "Salade verte",
            "category": "vegetable",
            "nutrition_per_100g": {
                "calories": 12,
                "protein": 1.2,
                "carbs": 2.3,
                "fat": 0.1
            },
            "unit": "g"
        },
        # Fruits
        {
            "name": "Ananas frais",
            "category": "fruit",
            "nutrition_per_100g": {
                "calories": 50,
                "protein": 0.5,
                "carbs": 12,
                "fat": 0.1
            },
            "unit": "g"
        },
        {
            "name": "Fruits rouges mélangés",
            "category": "fruit",
            "nutrition_per_100g": {
                "calories": 40,
                "protein": 1,
                "carbs": 8,
                "fat": 0.2
            },
            "unit": "g"
        },
        {
            "name": "Jus de pamplemousse",
            "category": "fruit",
            "nutrition_per_100g": {
                "calories": 40,
                "protein": 0.5,
                "carbs": 9,
                "fat": 0.1
            },
            "unit": "ml"
        },
        # Céréales
        {
            "name": "Flocons d'avoine",
            "category": "grain",
            "nutrition_per_100g": {
                "calories": 367,
                "protein": 13.2,
                "carbs": 67,
                "fat": 6.5
            },
            "unit": "g"
        },
        # Produits laitiers
        {
            "name": "Lait d'amande",
            "category": "fat",
            "nutrition_per_100g": {
                "calories": 15,
                "protein": 0.5,
                "carbs": 0.3,
                "fat": 1.1
            },
            "unit": "ml"
        },
        # Matières grasses
        {
            "name": "Huile d'olive",
            "category": "fat",
            "nutrition_per_100g": {
                "calories": 900,
                "protein": 0,
                "carbs": 0,
                "fat": 100
            },
            "unit": "ml"
        },
        # Autres
        {
            "name": "Chocolat noir 70%",
            "category": "fat",
            "nutrition_per_100g": {
                "calories": 500,
                "protein": 7,
                "carbs": 45,
                "fat": 35
            },
            "unit": "g"
        }
    ]
    
    for ingredient_data in ingredients_data:
        existing = Ingredient.query.filter_by(name=ingredient_data['name']).first()
        if not existing:
            ingredient = Ingredient.create_from_dict(ingredient_data)
            db.session.add(ingredient)
    
    db.session.commit()
    print(f"✅ {len(ingredients_data)} ingrédients initialisés")

def init_recipes():
    """Initialiser les recettes de base"""
    
    # Récupérer les IDs des ingrédients
    ingredients = {ing.name: ing.id for ing in Ingredient.query.all()}
    
    recipes_data = [
        # Repas 1 (Petit-déjeuner)
        {
            "name": "Omelette aux blancs d'œufs",
            "category": "breakfast",
            "meal_type": "repas1",
            "ingredients": [
                {"ingredient_id": ingredients["Blanc d'œuf"], "quantity": 99, "unit": "g"},
                {"ingredient_id": ingredients["Noix de cajou"], "quantity": 40, "unit": "g"}
            ],
            "instructions": [
                "Séparer les blancs des jaunes d'œufs",
                "Battre les blancs d'œufs dans un bol",
                "Assaisonner avec les épices et le sel",
                "Chauffer une poêle antiadhésive à feu moyen",
                "Verser les blancs battus dans la poêle",
                "Cuire 3-4 minutes de chaque côté",
                "Servir avec les noix de cajou"
            ],
            "prep_time": 5,
            "cook_time": 10,
            "servings": 1,
            "utensils": ["Poêle antiadhésive", "Fouet", "Bol de préparation", "Balance de cuisine"],
            "tags": ["protéiné", "rapide", "sans gluten"]
        },
        # Collation 1
        {
            "name": "Smoothie protéiné",
            "category": "snack",
            "meal_type": "collation1",
            "ingredients": [
                {"ingredient_id": ingredients["Lait d'amande"], "quantity": 200, "unit": "ml"},
                {"ingredient_id": ingredients["Flocons d'avoine"], "quantity": 60, "unit": "g"},
                {"ingredient_id": ingredients["Ananas frais"], "quantity": 50, "unit": "g"},
                {"ingredient_id": ingredients["Chocolat noir 70%"], "quantity": 5, "unit": "g"}
            ],
            "instructions": [
                "Verser le lait d'amande dans le blender",
                "Ajouter les flocons d'avoine",
                "Ajouter l'ananas et le chocolat noir fondu",
                "Mixer jusqu'à obtenir une consistance lisse",
                "Ajouter des glaçons si désiré",
                "Servir immédiatement"
            ],
            "prep_time": 5,
            "cook_time": 0,
            "servings": 1,
            "utensils": ["Blender", "Verre", "Balance de cuisine"],
            "tags": ["smoothie", "énergisant", "rapide"]
        },
        # Repas 2 (Déjeuner) - Poulet
        {
            "name": "Poulet grillé aux brocolis",
            "category": "lunch",
            "meal_type": "repas2",
            "ingredients": [
                {"ingredient_id": ingredients["Blanc de poulet"], "quantity": 180, "unit": "g"},
                {"ingredient_id": ingredients["Brocolis"], "quantity": 150, "unit": "g"},
                {"ingredient_id": ingredients["Huile d'olive"], "quantity": 5, "unit": "ml"}
            ],
            "instructions": [
                "Assaisonner le poulet avec les épices et le sel",
                "Chauffer une poêle antiadhésive",
                "Griller le poulet 6-8 minutes de chaque côté",
                "Cuire les brocolis à la vapeur 8-10 minutes",
                "Arroser les légumes d'huile d'olive",
                "Servir chaud"
            ],
            "prep_time": 10,
            "cook_time": 15,
            "servings": 1,
            "utensils": ["Poêle antiadhésive", "Cuit-vapeur", "Assiette"],
            "tags": ["protéiné", "équilibré", "sain"]
        },
        # Repas 2 (Déjeuner) - Dinde
        {
            "name": "Dinde sautée aux épinards",
            "category": "lunch",
            "meal_type": "repas2",
            "ingredients": [
                {"ingredient_id": ingredients["Escalope de dinde"], "quantity": 180, "unit": "g"},
                {"ingredient_id": ingredients["Épinards frais"], "quantity": 150, "unit": "g"},
                {"ingredient_id": ingredients["Huile d'olive"], "quantity": 5, "unit": "ml"}
            ],
            "instructions": [
                "Couper la dinde en lamelles",
                "Chauffer l'huile d'olive dans une poêle",
                "Faire revenir la dinde 5-6 minutes",
                "Ajouter les épinards et cuire 2-3 minutes",
                "Assaisonner avec les épices",
                "Servir immédiatement"
            ],
            "prep_time": 8,
            "cook_time": 12,
            "servings": 1,
            "utensils": ["Poêle", "Planche à découper", "Couteau"],
            "tags": ["protéiné", "rapide", "léger"]
        },
        # Collation 2
        {
            "name": "Blancs d'œufs aux amandes",
            "category": "snack",
            "meal_type": "collation2",
            "ingredients": [
                {"ingredient_id": ingredients["Blanc d'œuf"], "quantity": 99, "unit": "g"},
                {"ingredient_id": ingredients["Amandes"], "quantity": 40, "unit": "g"},
                {"ingredient_id": ingredients["Fruits rouges mélangés"], "quantity": 50, "unit": "g"}
            ],
            "instructions": [
                "Cuire les blancs d'œufs à la poêle",
                "Servir avec les amandes",
                "Accompagner de fruits rouges frais"
            ],
            "prep_time": 3,
            "cook_time": 5,
            "servings": 1,
            "utensils": ["Poêle antiadhésive", "Assiette"],
            "tags": ["protéiné", "antioxydant", "simple"]
        },
        # Repas 3 (Dîner) - Cabillaud
        {
            "name": "Cabillaud en papillote",
            "category": "dinner",
            "meal_type": "repas3",
            "ingredients": [
                {"ingredient_id": ingredients["Filet de cabillaud"], "quantity": 200, "unit": "g"},
                {"ingredient_id": ingredients["Salade verte"], "quantity": 100, "unit": "g"},
                {"ingredient_id": ingredients["Huile d'olive"], "quantity": 5, "unit": "ml"}
            ],
            "instructions": [
                "Préchauffer le four à 180°C",
                "Placer le poisson sur du papier sulfurisé",
                "Assaisonner avec citron, herbes et sel",
                "Fermer la papillote",
                "Cuire au four 15-20 minutes",
                "Préparer la salade avec l'huile d'olive",
                "Servir le poisson avec la salade"
            ],
            "prep_time": 10,
            "cook_time": 20,
            "servings": 1,
            "utensils": ["Four", "Papier sulfurisé", "Saladier"],
            "tags": ["léger", "savoureux", "sain"]
        },
        # Repas 3 (Dîner) - Sole
        {
            "name": "Sole grillée à la salade",
            "category": "dinner",
            "meal_type": "repas3",
            "ingredients": [
                {"ingredient_id": ingredients["Filet de sole"], "quantity": 200, "unit": "g"},
                {"ingredient_id": ingredients["Salade verte"], "quantity": 100, "unit": "g"},
                {"ingredient_id": ingredients["Huile d'olive"], "quantity": 5, "unit": "ml"}
            ],
            "instructions": [
                "Assaisonner la sole avec les épices",
                "Griller la sole dans une poêle 3-4 minutes par côté",
                "Préparer une vinaigrette avec l'huile d'olive",
                "Assaisonner la salade",
                "Servir le poisson sur lit de salade"
            ],
            "prep_time": 8,
            "cook_time": 8,
            "servings": 1,
            "utensils": ["Poêle antiadhésive", "Saladier", "Fouet"],
            "tags": ["rapide", "léger", "délicieux"]
        }
    ]
    
    for recipe_data in recipes_data:
        existing = Recipe.query.filter_by(name=recipe_data['name']).first()
        if not existing:
            # Calculer la nutrition
            from src.routes.recipes import calculate_recipe_nutrition
            nutrition = calculate_recipe_nutrition(recipe_data['ingredients'])
            recipe_data['nutrition_total'] = nutrition
            
            recipe = Recipe.create_from_dict(recipe_data)
            db.session.add(recipe)
    
    db.session.commit()
    print(f"✅ {len(recipes_data)} recettes initialisées")

def create_app():
    """Create Flask application with configuration"""
    app = Flask(__name__)
    config = get_config('development')
    app.config.from_object(config)
    
    # Initialize database
    db.init_app(app)
    
    return app

def init_database():
    """Initialize database with tables"""
    app = create_app()
    
    with app.app_context():
        # Create all tables
        db.create_all()
        print("✅ Tables créées avec succès")
        
        # Check if data already exists
        if Ingredient.query.first():
            print("⚠️  Des données existent déjà. Utilisez --force pour réinitialiser.")
            return
        
        # Initialize ingredients
        init_ingredients()
        
        # Initialize recipes
        init_recipes()
        
        # Create default user
        init_default_user()
        
        print("\n🎉 Base de données initialisée avec succès!")
        print(f"📊 {Ingredient.query.count()} ingrédients créés")
        print(f"🍽️  {Recipe.query.count()} recettes créées")
        print(f"👤 {User.query.count()} utilisateur(s) créé(s)")

def init_default_user():
    """Create default user for testing"""
    user = User(
        username='fabien',
        email='fabien@diettracker.com',
        current_weight=75.0,
        target_weight=70.0,
        height=175.0,
        age=30,
        gender='male',
        activity_level='moderate',
        daily_calories_target=1500,
        daily_protein_target=150,
        daily_carbs_target=85,
        daily_fat_target=75
    )
    
    db.session.add(user)
    db.session.commit()
    print("✅ Utilisateur par défaut créé (fabien@diettracker.com)")

def reset_database():
    """Reset database - drop all tables and recreate"""
    app = create_app()
    
    with app.app_context():
        # Drop all tables
        db.drop_all()
        print("🗑️  Tables supprimées")
        
        # Recreate all tables
        db.create_all()
        print("✅ Tables recréées")
        
        # Initialize data
        init_ingredients()
        init_recipes()
        init_default_user()
        
        print("\n🎉 Base de données réinitialisée avec succès!")

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Initialize DietTracker database')
    parser.add_argument('--reset', action='store_true', help='Reset database (drop and recreate all tables)')
    parser.add_argument('--force', action='store_true', help='Force initialization even if data exists')
    
    args = parser.parse_args()
    
    if args.reset or args.force:
        reset_database()
    else:
        init_database()

