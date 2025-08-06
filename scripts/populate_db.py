#!/usr/bin/env python3
"""
Script pour peupler la base de données avec des données complètes
"""

import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).resolve().parents[1] / 'src' / 'backend'
sys.path.insert(0, str(backend_path))

from flask import Flask
from database import db
from models.user import User
from models.ingredient import Ingredient
from models.recipe import Recipe
from database.config import get_config

def create_app():
    """Create Flask application with configuration"""
    app = Flask(__name__)
    config = get_config('development')
    app.config.from_object(config)
    
    # Initialize database
    db.init_app(app)
    
    return app

def add_recipes():
    """Ajouter les recettes avec les ingrédients existants"""
    
    # Récupérer les IDs des ingrédients
    ingredients = {ing.name: ing.id for ing in Ingredient.query.all()}
    
    recipes_data = [
        {
            "name": "Omelette aux blancs d'œufs",
            "category": "breakfast",
            "meal_type": "repas1",
            "ingredients": [
                {"ingredient_id": ingredients.get("Blanc d'œuf"), "quantity": 99, "unit": "g"},
                {"ingredient_id": ingredients.get("Noix de cajou"), "quantity": 40, "unit": "g"}
            ],
            "instructions": [
                "Séparer les blancs des jaunes d'œufs",
                "Battre les blancs d'œufs",
                "Cuire dans une poêle antiadhésive"
            ],
            "prep_time": 5,
            "cook_time": 10,
            "servings": 1
        },
        {
            "name": "Poulet grillé aux brocolis",
            "category": "lunch",
            "meal_type": "repas2",
            "ingredients": [
                {"ingredient_id": ingredients.get("Blanc de poulet"), "quantity": 180, "unit": "g"},
                {"ingredient_id": ingredients.get("Brocolis"), "quantity": 150, "unit": "g"},
                {"ingredient_id": ingredients.get("Huile d'olive"), "quantity": 5, "unit": "ml"}
            ],
            "instructions": [
                "Assaisonner le poulet",
                "Griller 6-8 minutes par côté",
                "Cuire les brocolis à la vapeur"
            ],
            "prep_time": 10,
            "cook_time": 15,
            "servings": 1
        },
        {
            "name": "Smoothie protéiné",
            "category": "snack",
            "meal_type": "collation1",
            "ingredients": [
                {"ingredient_id": ingredients.get("Lait d'amande"), "quantity": 200, "unit": "ml"},
                {"ingredient_id": ingredients.get("Flocons d'avoine"), "quantity": 60, "unit": "g"}
            ],
            "instructions": [
                "Mixer tous les ingrédients",
                "Servir frais"
            ],
            "prep_time": 5,
            "cook_time": 0,
            "servings": 1
        }
    ]
    
    created_recipes = []
    for recipe_data in recipes_data:
        # Remove None ingredient_ids
        recipe_data['ingredients'] = [
            ing for ing in recipe_data['ingredients'] 
            if ing.get('ingredient_id') is not None
        ]
        
        if recipe_data['ingredients']:  # Only create if has valid ingredients
            # Calculate nutrition
            total_calories = 0
            total_protein = 0
            total_carbs = 0
            total_fat = 0
            
            for ing_data in recipe_data['ingredients']:
                ingredient = Ingredient.query.get(ing_data['ingredient_id'])
                if ingredient:
                    quantity = ing_data['quantity']
                    factor = quantity / 100.0
                    total_calories += ingredient.calories_per_100g * factor
                    total_protein += ingredient.protein_per_100g * factor
                    total_carbs += ingredient.carbs_per_100g * factor
                    total_fat += ingredient.fat_per_100g * factor
            
            recipe = Recipe(
                name=recipe_data['name'],
                category=recipe_data['category'],
                meal_type=recipe_data['meal_type'],
                ingredients=recipe_data['ingredients'],
                instructions=recipe_data['instructions'],
                prep_time=recipe_data['prep_time'],
                cook_time=recipe_data['cook_time'],
                servings=recipe_data['servings'],
                total_calories=total_calories,
                total_protein=total_protein,
                total_carbs=total_carbs,
                total_fat=total_fat
            )
            
            db.session.add(recipe)
            created_recipes.append(recipe_data['name'])
    
    db.session.commit()
    return created_recipes

def add_user():
    """Ajouter un utilisateur par défaut"""
    # Check if user already exists
    existing_user = User.query.filter_by(email='fabien@diettracker.com').first()
    if existing_user:
        return False
    
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
    return True

def main():
    """Fonction principale"""
    app = create_app()
    
    with app.app_context():
        print("🔍 Vérification de la base de données...")
        
        # Check current state
        ingredients_count = Ingredient.query.count()
        recipes_count = Recipe.query.count()
        users_count = User.query.count()
        
        print(f"📊 État actuel:")
        print(f"   - Ingrédients: {ingredients_count}")
        print(f"   - Recettes: {recipes_count}")
        print(f"   - Utilisateurs: {users_count}")
        
        # Add recipes if needed
        if recipes_count == 0:
            print("\n📝 Ajout des recettes...")
            created_recipes = add_recipes()
            print(f"✅ {len(created_recipes)} recettes créées:")
            for recipe_name in created_recipes:
                print(f"   - {recipe_name}")
        
        # Add user if needed
        if users_count == 0:
            print("\n👤 Ajout de l'utilisateur par défaut...")
            if add_user():
                print("✅ Utilisateur 'fabien' créé")
        
        # Final state
        print("\n📊 État final:")
        print(f"   - Ingrédients: {Ingredient.query.count()}")
        print(f"   - Recettes: {Recipe.query.count()}")
        print(f"   - Utilisateurs: {User.query.count()}")
        
        print("\n🎉 Base de données prête!")

if __name__ == '__main__':
    main()