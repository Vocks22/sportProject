#!/usr/bin/env python3
"""
Script pour corriger les ingrédients des recettes dans la base de données
"""

import sys
import os
sys.path.append('src/backend')

from main import create_app
from models.recipe import Recipe
from models.ingredient import Ingredient
from database import db

def create_or_get_ingredient(name, category, calories, protein, carbs, fat, unit='g'):
    """Créer ou récupérer un ingrédient"""
    # Chercher d'abord par nom exact
    ing = Ingredient.query.filter_by(name=name).first()
    if not ing:
        ing = Ingredient(
            name=name,
            category=category,
            calories_per_100g=calories,
            protein_per_100g=protein,
            carbs_per_100g=carbs,
            fat_per_100g=fat,
            unit=unit
        )
        db.session.add(ing)
        db.session.flush()
    return ing.id

app = create_app()

with app.app_context():
    print("🧹 Nettoyage et correction des ingrédients...")
    
    # Supprimer les doublons d'ingrédients
    Ingredient.query.filter(Ingredient.id > 18).delete()
    db.session.commit()
    
    # Créer/vérifier les ingrédients de base
    ingredients_map = {
        # Protéines
        "Blanc d'œuf": create_or_get_ingredient("Blanc d'œuf", "protein", 52, 11, 0.7, 0.2),
        "Blanc de poulet": create_or_get_ingredient("Blanc de poulet", "protein", 165, 31, 0, 3.6),
        "Escalope de dinde": create_or_get_ingredient("Escalope de dinde", "protein", 135, 29, 0, 2.5),
        "Filet de cabillaud": create_or_get_ingredient("Filet de cabillaud", "protein", 82, 18, 0, 0.7),
        "Filet de sole": create_or_get_ingredient("Filet de sole", "protein", 86, 18, 0, 1.2),
        "Thon en conserve": create_or_get_ingredient("Thon en conserve", "protein", 132, 29.9, 0, 0.8),
        "Saumon": create_or_get_ingredient("Saumon", "protein", 208, 20, 0, 13),
        
        # Noix et graines
        "Noix de cajou": create_or_get_ingredient("Noix de cajou", "nuts", 553, 18, 30, 44),
        "Amandes": create_or_get_ingredient("Amandes", "nuts", 579, 21, 22, 50),
        "Noix": create_or_get_ingredient("Noix", "nuts", 654, 15, 14, 65),
        "Noisettes": create_or_get_ingredient("Noisettes", "nuts", 628, 15, 17, 61),
        "Pistaches": create_or_get_ingredient("Pistaches", "nuts", 562, 20, 28, 45),
        "Noix de pécan": create_or_get_ingredient("Noix de pécan", "nuts", 691, 9, 14, 72),
        
        # Légumes
        "Brocolis": create_or_get_ingredient("Brocolis", "vegetable", 34, 2.8, 7, 0.4),
        "Épinards frais": create_or_get_ingredient("Épinards frais", "vegetable", 23, 2.9, 3.6, 0.4),
        "Haricots verts": create_or_get_ingredient("Haricots verts", "vegetable", 31, 1.8, 7, 0.1),
        "Salade verte": create_or_get_ingredient("Salade verte", "vegetable", 15, 1.4, 2.9, 0.2),
        "Courgettes": create_or_get_ingredient("Courgettes", "vegetable", 17, 1.2, 3.1, 0.3),
        "Tomates cerises": create_or_get_ingredient("Tomates cerises", "vegetable", 18, 0.9, 3.9, 0.2),
        "Champignons": create_or_get_ingredient("Champignons", "vegetable", 22, 3.1, 3.3, 0.3),
        "Poivrons": create_or_get_ingredient("Poivrons", "vegetable", 31, 1, 6, 0.3),
        "Asperges": create_or_get_ingredient("Asperges", "vegetable", 20, 2.2, 3.9, 0.1),
        "Roquette": create_or_get_ingredient("Roquette", "vegetable", 25, 2.6, 3.7, 0.7),
        
        # Fruits
        "Ananas frais": create_or_get_ingredient("Ananas frais", "fruit", 50, 0.5, 13, 0.1),
        "Fruits rouges": create_or_get_ingredient("Fruits rouges", "fruit", 43, 0.9, 10, 0.3),
        "Myrtilles": create_or_get_ingredient("Myrtilles", "fruit", 57, 0.7, 14, 0.3),
        "Framboises": create_or_get_ingredient("Framboises", "fruit", 53, 1.2, 12, 0.7),
        "Fraises": create_or_get_ingredient("Fraises", "fruit", 32, 0.7, 7.7, 0.3),
        "Mûres": create_or_get_ingredient("Mûres", "fruit", 43, 1.4, 10, 0.5),
        "Banane": create_or_get_ingredient("Banane", "fruit", 89, 1.1, 23, 0.3),
        "Pêche": create_or_get_ingredient("Pêche", "fruit", 39, 0.9, 10, 0.3),
        
        # Grains et céréales
        "Flocons d'avoine": create_or_get_ingredient("Flocons d'avoine", "grain", 389, 13.2, 67.7, 6.9),
        
        # Liquides et graisses
        "Lait d'amande": create_or_get_ingredient("Lait d'amande", "fat", 17, 0.6, 0.6, 1.5, 'ml'),
        "Huile d'olive": create_or_get_ingredient("Huile d'olive", "fat", 884, 0, 0, 100, 'ml'),
        "Whey protéine": create_or_get_ingredient("Whey protéine", "protein", 352, 80, 7, 3),
        
        # Autres
        "Chocolat noir 70%": create_or_get_ingredient("Chocolat noir 70%", "fat", 579, 5.3, 45.9, 37.3),
        "Miel": create_or_get_ingredient("Miel", "grain", 304, 0.3, 82, 0),
        "Cannelle": create_or_get_ingredient("Cannelle", "grain", 247, 4, 81, 1.2),
        "Vanille": create_or_get_ingredient("Vanille", "grain", 288, 0.1, 13, 0.1),
        "Cacao en poudre": create_or_get_ingredient("Cacao en poudre", "grain", 228, 19.6, 57.9, 13.7),
        "Menthe fraîche": create_or_get_ingredient("Menthe fraîche", "vegetable", 70, 3.8, 14.9, 0.9),
        "Lait de coco": create_or_get_ingredient("Lait de coco", "fat", 230, 2.3, 6, 24, 'ml')
    }
    
    db.session.commit()
    
    print("📝 Correction des recettes...")
    
    # Définir les ingrédients corrects pour chaque type de recette
    recipe_ingredients_mapping = {
        # Omelettes et blancs d'œufs (Petit-déjeuner)
        "omelette": [
            {"name": "Blanc d'œuf", "quantity": 99, "unit": "g"},
            {"name": "Noix de cajou", "quantity": 40, "unit": "g"}
        ],
        "blancs d'œufs": [
            {"name": "Blanc d'œuf", "quantity": 99, "unit": "g"},
            {"name": "Noix de cajou", "quantity": 40, "unit": "g"}
        ],
        "scrambled": [
            {"name": "Blanc d'œuf", "quantity": 99, "unit": "g"},
            {"name": "Amandes", "quantity": 40, "unit": "g"}
        ],
        
        # Smoothies
        "smoothie": [
            {"name": "Whey protéine", "quantity": 30, "unit": "g"},
            {"name": "Lait d'amande", "quantity": 250, "unit": "ml"},
            {"name": "Flocons d'avoine", "quantity": 20, "unit": "g"}
        ],
        
        # Poulet et dinde (Déjeuner)
        "poulet": [
            {"name": "Blanc de poulet", "quantity": 200, "unit": "g"},
            {"name": "Brocolis", "quantity": 150, "unit": "g"},
            {"name": "Huile d'olive", "quantity": 5, "unit": "ml"}
        ],
        "dinde": [
            {"name": "Escalope de dinde", "quantity": 200, "unit": "g"},
            {"name": "Épinards frais", "quantity": 150, "unit": "g"},
            {"name": "Huile d'olive", "quantity": 5, "unit": "ml"}
        ],
        
        # Poissons (Dîner)
        "cabillaud": [
            {"name": "Filet de cabillaud", "quantity": 200, "unit": "g"},
            {"name": "Salade verte", "quantity": 100, "unit": "g"},
            {"name": "Huile d'olive", "quantity": 5, "unit": "ml"}
        ],
        "sole": [
            {"name": "Filet de sole", "quantity": 200, "unit": "g"},
            {"name": "Haricots verts", "quantity": 150, "unit": "g"},
            {"name": "Huile d'olive", "quantity": 5, "unit": "ml"}
        ],
        
        # Collations aux œufs et noix
        "collation": [
            {"name": "Blanc d'œuf", "quantity": 66, "unit": "g"},
            {"name": "Amandes", "quantity": 30, "unit": "g"},
            {"name": "Fruits rouges", "quantity": 50, "unit": "g"}
        ]
    }
    
    # Corriger chaque recette
    recipes = Recipe.query.all()
    
    for recipe in recipes:
        # Déterminer le type de recette basé sur le nom
        recipe_name_lower = recipe.name.lower()
        new_ingredients = []
        
        # Mapping spécifique selon le nom de la recette
        if "omelette" in recipe_name_lower:
            base_ingredients = recipe_ingredients_mapping["omelette"].copy()
            
            # Ajouter des ingrédients spécifiques selon la variante
            if "épinards" in recipe_name_lower:
                base_ingredients.append({"name": "Épinards frais", "quantity": 50, "unit": "g"})
            elif "tomates" in recipe_name_lower:
                base_ingredients.append({"name": "Tomates cerises", "quantity": 50, "unit": "g"})
            elif "champignons" in recipe_name_lower:
                base_ingredients.append({"name": "Champignons", "quantity": 50, "unit": "g"})
            elif "courgettes" in recipe_name_lower:
                base_ingredients.append({"name": "Courgettes", "quantity": 50, "unit": "g"})
            elif "poivrons" in recipe_name_lower:
                base_ingredients.append({"name": "Poivrons", "quantity": 50, "unit": "g"})
            elif "brocolis" in recipe_name_lower:
                base_ingredients.append({"name": "Brocolis", "quantity": 50, "unit": "g"})
            elif "roquette" in recipe_name_lower:
                base_ingredients.append({"name": "Roquette", "quantity": 30, "unit": "g"})
                
        elif "scrambled" in recipe_name_lower or "brouillés" in recipe_name_lower:
            base_ingredients = recipe_ingredients_mapping["scrambled"].copy()
            
            if "champignons" in recipe_name_lower:
                base_ingredients.append({"name": "Champignons", "quantity": 50, "unit": "g"})
                
        elif "smoothie" in recipe_name_lower:
            base_ingredients = recipe_ingredients_mapping["smoothie"].copy()
            
            # Ajouter des fruits selon la variante
            if "tropical" in recipe_name_lower:
                base_ingredients.append({"name": "Ananas frais", "quantity": 100, "unit": "g"})
            elif "chocolat" in recipe_name_lower:
                base_ingredients.append({"name": "Cacao en poudre", "quantity": 10, "unit": "g"})
                base_ingredients.append({"name": "Banane", "quantity": 100, "unit": "g"})
            elif "fruits rouges" in recipe_name_lower or "rouge" in recipe_name_lower:
                base_ingredients.append({"name": "Fruits rouges", "quantity": 100, "unit": "g"})
            elif "vert" in recipe_name_lower:
                base_ingredients.append({"name": "Épinards frais", "quantity": 30, "unit": "g"})
            elif "vanille" in recipe_name_lower:
                base_ingredients.append({"name": "Vanille", "quantity": 1, "unit": "g"})
            elif "cannelle" in recipe_name_lower:
                base_ingredients.append({"name": "Cannelle", "quantity": 2, "unit": "g"})
            elif "coco" in recipe_name_lower:
                base_ingredients.append({"name": "Lait de coco", "quantity": 100, "unit": "ml"})
                base_ingredients.append({"name": "Ananas frais", "quantity": 100, "unit": "g"})
            elif "menthe" in recipe_name_lower:
                base_ingredients.append({"name": "Menthe fraîche", "quantity": 5, "unit": "g"})
                base_ingredients.append({"name": "Chocolat noir 70%", "quantity": 10, "unit": "g"})
            elif "pêche" in recipe_name_lower:
                base_ingredients.append({"name": "Pêche", "quantity": 100, "unit": "g"})
                
        elif "poulet" in recipe_name_lower:
            base_ingredients = recipe_ingredients_mapping["poulet"].copy()
            
            # Varier les légumes
            if "épinards" in recipe_name_lower:
                base_ingredients[1] = {"name": "Épinards frais", "quantity": 150, "unit": "g"}
            elif "courgettes" in recipe_name_lower:
                base_ingredients[1] = {"name": "Courgettes", "quantity": 150, "unit": "g"}
            elif "haricots" in recipe_name_lower:
                base_ingredients[1] = {"name": "Haricots verts", "quantity": 150, "unit": "g"}
            elif "champignons" in recipe_name_lower:
                base_ingredients[1] = {"name": "Champignons", "quantity": 150, "unit": "g"}
            elif "asperges" in recipe_name_lower:
                base_ingredients[1] = {"name": "Asperges", "quantity": 150, "unit": "g"}
                
        elif "dinde" in recipe_name_lower:
            base_ingredients = recipe_ingredients_mapping["dinde"].copy()
            
            # Varier les légumes
            if "haricots" in recipe_name_lower:
                base_ingredients[1] = {"name": "Haricots verts", "quantity": 150, "unit": "g"}
            elif "brocolis" in recipe_name_lower:
                base_ingredients[1] = {"name": "Brocolis", "quantity": 150, "unit": "g"}
            elif "asperges" in recipe_name_lower:
                base_ingredients[1] = {"name": "Asperges", "quantity": 150, "unit": "g"}
            elif "poivrons" in recipe_name_lower:
                base_ingredients[1] = {"name": "Poivrons", "quantity": 150, "unit": "g"}
                
        elif "cabillaud" in recipe_name_lower:
            base_ingredients = recipe_ingredients_mapping["cabillaud"].copy()
            
            # Varier les accompagnements
            if "épinards" in recipe_name_lower:
                base_ingredients[1] = {"name": "Épinards frais", "quantity": 150, "unit": "g"}
            elif "courgettes" in recipe_name_lower:
                base_ingredients[1] = {"name": "Courgettes", "quantity": 150, "unit": "g"}
            elif "tomates" in recipe_name_lower:
                base_ingredients[1] = {"name": "Tomates cerises", "quantity": 100, "unit": "g"}
            elif "brocolis" in recipe_name_lower:
                base_ingredients[1] = {"name": "Brocolis", "quantity": 150, "unit": "g"}
            elif "poivrons" in recipe_name_lower:
                base_ingredients[1] = {"name": "Poivrons", "quantity": 150, "unit": "g"}
                
        elif "sole" in recipe_name_lower:
            base_ingredients = recipe_ingredients_mapping["sole"].copy()
            
            # Varier les accompagnements
            if "courgettes" in recipe_name_lower:
                base_ingredients[1] = {"name": "Courgettes", "quantity": 150, "unit": "g"}
            elif "champignons" in recipe_name_lower:
                base_ingredients[1] = {"name": "Champignons", "quantity": 150, "unit": "g"}
            elif "épinards" in recipe_name_lower:
                base_ingredients[1] = {"name": "Épinards frais", "quantity": 150, "unit": "g"}
                
        elif "collation" in recipe.category or "snack" in recipe.category:
            base_ingredients = recipe_ingredients_mapping["collation"].copy()
            
            # Varier les noix et fruits
            if "cajou" in recipe_name_lower:
                base_ingredients[1] = {"name": "Noix de cajou", "quantity": 30, "unit": "g"}
            elif "noix" in recipe_name_lower and "cajou" not in recipe_name_lower:
                base_ingredients[1] = {"name": "Noix", "quantity": 30, "unit": "g"}
            elif "noisettes" in recipe_name_lower:
                base_ingredients[1] = {"name": "Noisettes", "quantity": 30, "unit": "g"}
            elif "pistaches" in recipe_name_lower:
                base_ingredients[1] = {"name": "Pistaches", "quantity": 30, "unit": "g"}
            elif "pécan" in recipe_name_lower:
                base_ingredients[1] = {"name": "Noix de pécan", "quantity": 30, "unit": "g"}
                
            if "myrtilles" in recipe_name_lower:
                base_ingredients[2] = {"name": "Myrtilles", "quantity": 50, "unit": "g"}
            elif "framboises" in recipe_name_lower:
                base_ingredients[2] = {"name": "Framboises", "quantity": 50, "unit": "g"}
            elif "fraises" in recipe_name_lower:
                base_ingredients[2] = {"name": "Fraises", "quantity": 50, "unit": "g"}
            elif "mûres" in recipe_name_lower:
                base_ingredients[2] = {"name": "Mûres", "quantity": 50, "unit": "g"}
        else:
            # Recette par défaut
            base_ingredients = recipe_ingredients_mapping["omelette"].copy()
        
        # Convertir en format pour la DB
        for ing in base_ingredients:
            ing_id = ingredients_map.get(ing["name"])
            if ing_id:
                new_ingredients.append({
                    "ingredient_id": ing_id,
                    "quantity": ing["quantity"],
                    "unit": ing["unit"]
                })
        
        # Mettre à jour la recette
        recipe.ingredients = new_ingredients
        
        print(f"  ✓ {recipe.name}")
    
    db.session.commit()
    
    print("\n✅ Correction terminée!")
    print("   Toutes les recettes ont maintenant des ingrédients cohérents.")