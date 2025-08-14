#!/usr/bin/env python3
"""
Script final pour corriger les recettes avec les quantités exactes du programme
"""

import sys
import os
sys.path.append('src/backend')

from main import create_app
from models.recipe import Recipe
from models.ingredient import Ingredient
from database import db

app = create_app()

with app.app_context():
    print("🔧 Correction finale des recettes avec les bonnes quantités...")
    
    # Créer un mapping des ingrédients
    ingredients = Ingredient.query.all()
    ing_map = {ing.name.lower(): ing.id for ing in ingredients}
    
    # Définir les quantités exactes selon le programme
    # REPAS 1 : 3 blancs d'œufs (99g), 40g noix de cajou/amandes
    # COLLATION 1 : 200ml lait d'amande, 60g avoine, 50g fruits
    # REPAS 2 : 180g viande blanche, 150g légume vert, 5g huile d'olive  
    # COLLATION 2 : 2 blancs d'œufs (66g), 40g amandes, 50g fruits rouges
    # REPAS 3 : 200g poisson blanc, salade verte, 5g huile d'olive
    
    recipes = Recipe.query.all()
    
    for recipe in recipes:
        name_lower = recipe.name.lower()
        new_ingredients = []
        
        # REPAS 1 - Petit-déjeuner (Omelettes et blancs d'œufs)
        if recipe.id <= 15:  
            # Base : 3 blancs d'œufs + 40g noix
            new_ingredients.append({
                "ingredient_id": ing_map.get("blanc d'œuf", 1),
                "quantity": 99,  # 3 blancs = 99g
                "unit": "g"
            })
            
            # Alterner entre noix de cajou et amandes
            if recipe.id % 2 == 1:
                new_ingredients.append({
                    "ingredient_id": ing_map.get("noix de cajou", 6),
                    "quantity": 40,
                    "unit": "g"
                })
            else:
                new_ingredients.append({
                    "ingredient_id": ing_map.get("amandes", 7),
                    "quantity": 40,
                    "unit": "g"
                })
            
            # Ajouter le légume spécifique si mentionné
            if "épinards" in name_lower:
                new_ingredients.append({
                    "ingredient_id": ing_map.get("épinards frais", 9),
                    "quantity": 50,
                    "unit": "g"
                })
            elif "champignons" in name_lower:
                new_ingredients.append({
                    "ingredient_id": ing_map.get("champignons", 20),
                    "quantity": 50,
                    "unit": "g"
                })
            elif "tomates" in name_lower:
                new_ingredients.append({
                    "ingredient_id": ing_map.get("tomates cerises", 19),
                    "quantity": 50,
                    "unit": "g"
                })
            elif "courgettes" in name_lower:
                new_ingredients.append({
                    "ingredient_id": ing_map.get("courgettes", 18),
                    "quantity": 50,
                    "unit": "g"
                })
            elif "poivrons" in name_lower:
                new_ingredients.append({
                    "ingredient_id": ing_map.get("poivrons", 21),
                    "quantity": 50,
                    "unit": "g"
                })
            elif "brocolis" in name_lower:
                new_ingredients.append({
                    "ingredient_id": ing_map.get("brocolis", 8),
                    "quantity": 50,
                    "unit": "g"
                })
            elif "roquette" in name_lower:
                new_ingredients.append({
                    "ingredient_id": ing_map.get("roquette", 23),
                    "quantity": 30,
                    "unit": "g"
                })
                
        # COLLATION 1 - Smoothies (recettes 16-25)
        elif 16 <= recipe.id <= 25:
            # Base du smoothie
            new_ingredients.extend([
                {
                    "ingredient_id": ing_map.get("lait d'amande", 16),
                    "quantity": 200,
                    "unit": "ml"
                },
                {
                    "ingredient_id": ing_map.get("flocons d'avoine", 15),
                    "quantity": 60,
                    "unit": "g"
                }
            ])
            
            # Ajouter les fruits/saveurs spécifiques
            if "tropical" in name_lower or "ananas" in name_lower:
                new_ingredients.append({
                    "ingredient_id": ing_map.get("ananas frais", 12),
                    "quantity": 50,
                    "unit": "g"
                })
            elif "chocolat" in name_lower and "banane" in name_lower:
                new_ingredients.extend([
                    {
                        "ingredient_id": ing_map.get("banane", 32),
                        "quantity": 60,  # 1/2 banane
                        "unit": "g"
                    },
                    {
                        "ingredient_id": ing_map.get("chocolat noir 70%", 18),
                        "quantity": 10,  # 1 carré
                        "unit": "g"
                    }
                ])
            elif "vert" in name_lower:
                new_ingredients.extend([
                    {
                        "ingredient_id": ing_map.get("épinards frais", 9),
                        "quantity": 50,
                        "unit": "g"
                    },
                    {
                        "ingredient_id": ing_map.get("ananas frais", 12),
                        "quantity": 50,
                        "unit": "g"
                    }
                ])
            elif "fruits rouges" in name_lower or "rouge" in name_lower:
                new_ingredients.append({
                    "ingredient_id": ing_map.get("fruits rouges", 25),
                    "quantity": 50,
                    "unit": "g"
                })
            elif "pêche" in name_lower:
                new_ingredients.extend([
                    {
                        "ingredient_id": ing_map.get("pêche", 33),
                        "quantity": 50,
                        "unit": "g"
                    },
                    {
                        "ingredient_id": ing_map.get("chocolat noir 70%", 18),
                        "quantity": 10,
                        "unit": "g"
                    }
                ])
            else:
                # Smoothie classique avec ananas et chocolat
                new_ingredients.extend([
                    {
                        "ingredient_id": ing_map.get("ananas frais", 12),
                        "quantity": 50,
                        "unit": "g"
                    },
                    {
                        "ingredient_id": ing_map.get("chocolat noir 70%", 18),
                        "quantity": 10,
                        "unit": "g"
                    }
                ])
                
        # REPAS 2 - Déjeuner (recettes 26-40)
        elif 26 <= recipe.id <= 40:
            # Viande : 180g
            if "poulet" in name_lower:
                new_ingredients.append({
                    "ingredient_id": ing_map.get("blanc de poulet", 2),
                    "quantity": 180,
                    "unit": "g"
                })
            else:  # dinde
                new_ingredients.append({
                    "ingredient_id": ing_map.get("escalope de dinde", 3),
                    "quantity": 180,
                    "unit": "g"
                })
            
            # Légume vert : 150g
            if "brocolis" in name_lower:
                new_ingredients.append({
                    "ingredient_id": ing_map.get("brocolis", 8),
                    "quantity": 150,
                    "unit": "g"
                })
            elif "épinards" in name_lower:
                new_ingredients.append({
                    "ingredient_id": ing_map.get("épinards frais", 9),
                    "quantity": 150,
                    "unit": "g"
                })
            elif "haricots" in name_lower:
                new_ingredients.append({
                    "ingredient_id": ing_map.get("haricots verts", 10),
                    "quantity": 150,
                    "unit": "g"
                })
            elif "courgettes" in name_lower:
                new_ingredients.append({
                    "ingredient_id": ing_map.get("courgettes", 18),
                    "quantity": 150,
                    "unit": "g"
                })
            elif "champignons" in name_lower:
                new_ingredients.append({
                    "ingredient_id": ing_map.get("champignons", 20),
                    "quantity": 150,
                    "unit": "g"
                })
            elif "asperges" in name_lower:
                new_ingredients.append({
                    "ingredient_id": ing_map.get("asperges", 22),
                    "quantity": 150,
                    "unit": "g"
                })
            elif "poivrons" in name_lower:
                new_ingredients.append({
                    "ingredient_id": ing_map.get("poivrons", 21),
                    "quantity": 150,
                    "unit": "g"
                })
            else:
                # Par défaut : brocolis
                new_ingredients.append({
                    "ingredient_id": ing_map.get("brocolis", 8),
                    "quantity": 150,
                    "unit": "g"
                })
            
            # Huile d'olive
            new_ingredients.append({
                "ingredient_id": ing_map.get("huile d'olive", 17),
                "quantity": 5,
                "unit": "ml"
            })
            
        # COLLATION 2 - Blancs d'œufs et noix (recettes 41-50)
        elif 41 <= recipe.id <= 50:
            # Base : 2 blancs d'œufs
            new_ingredients.append({
                "ingredient_id": ing_map.get("blanc d'œuf", 1),
                "quantity": 66,  # 2 blancs = 66g
                "unit": "g"
            })
            
            # 40g de noix variées
            if "cajou" in name_lower:
                new_ingredients.append({
                    "ingredient_id": ing_map.get("noix de cajou", 6),
                    "quantity": 40,
                    "unit": "g"
                })
            elif "noisettes" in name_lower:
                new_ingredients.append({
                    "ingredient_id": ing_map.get("noisettes", 27),
                    "quantity": 40,
                    "unit": "g"
                })
            elif "pistaches" in name_lower:
                new_ingredients.append({
                    "ingredient_id": ing_map.get("pistaches", 28),
                    "quantity": 40,
                    "unit": "g"
                })
            elif "pécan" in name_lower:
                new_ingredients.append({
                    "ingredient_id": ing_map.get("noix de pécan", 29),
                    "quantity": 40,
                    "unit": "g"
                })
            elif "noix" in name_lower and "cajou" not in name_lower:
                new_ingredients.append({
                    "ingredient_id": ing_map.get("noix", 26),
                    "quantity": 40,
                    "unit": "g"
                })
            else:
                new_ingredients.append({
                    "ingredient_id": ing_map.get("amandes", 7),
                    "quantity": 40,
                    "unit": "g"
                })
            
            # 50g de fruits rouges
            if "myrtilles" in name_lower:
                new_ingredients.append({
                    "ingredient_id": ing_map.get("myrtilles", 30),
                    "quantity": 50,
                    "unit": "g"
                })
            elif "framboises" in name_lower:
                new_ingredients.append({
                    "ingredient_id": ing_map.get("framboises", 31),
                    "quantity": 50,
                    "unit": "g"
                })
            elif "fraises" in name_lower:
                new_ingredients.append({
                    "ingredient_id": ing_map.get("fraises", 32),
                    "quantity": 50,
                    "unit": "g"
                })
            elif "mûres" in name_lower:
                new_ingredients.append({
                    "ingredient_id": ing_map.get("mûres", 33),
                    "quantity": 50,
                    "unit": "g"
                })
            else:
                new_ingredients.append({
                    "ingredient_id": ing_map.get("fruits rouges", 25),
                    "quantity": 50,
                    "unit": "g"
                })
                
        # REPAS 3 - Dîner (recettes 51-65)
        elif recipe.id >= 51:
            # Poisson : 200g
            if "cabillaud" in name_lower:
                new_ingredients.append({
                    "ingredient_id": ing_map.get("filet de cabillaud", 4),
                    "quantity": 200,
                    "unit": "g"
                })
            else:  # sole
                new_ingredients.append({
                    "ingredient_id": ing_map.get("filet de sole", 5),
                    "quantity": 200,
                    "unit": "g"
                })
            
            # Salade ou légume
            if "épinards" in name_lower:
                new_ingredients.append({
                    "ingredient_id": ing_map.get("épinards frais", 9),
                    "quantity": 100,
                    "unit": "g"
                })
            elif "courgettes" in name_lower:
                new_ingredients.append({
                    "ingredient_id": ing_map.get("courgettes", 18),
                    "quantity": 100,
                    "unit": "g"
                })
            elif "tomates" in name_lower:
                new_ingredients.append({
                    "ingredient_id": ing_map.get("tomates cerises", 19),
                    "quantity": 100,
                    "unit": "g"
                })
            elif "haricots" in name_lower:
                new_ingredients.append({
                    "ingredient_id": ing_map.get("haricots verts", 10),
                    "quantity": 100,
                    "unit": "g"
                })
            elif "brocolis" in name_lower:
                new_ingredients.append({
                    "ingredient_id": ing_map.get("brocolis", 8),
                    "quantity": 100,
                    "unit": "g"
                })
            elif "champignons" in name_lower:
                new_ingredients.append({
                    "ingredient_id": ing_map.get("champignons", 20),
                    "quantity": 100,
                    "unit": "g"
                })
            elif "poivrons" in name_lower:
                new_ingredients.append({
                    "ingredient_id": ing_map.get("poivrons", 21),
                    "quantity": 100,
                    "unit": "g"
                })
            else:
                # Par défaut : salade verte
                new_ingredients.append({
                    "ingredient_id": ing_map.get("salade verte", 11),
                    "quantity": 100,
                    "unit": "g"
                })
            
            # Huile d'olive
            new_ingredients.append({
                "ingredient_id": ing_map.get("huile d'olive", 17),
                "quantity": 5,
                "unit": "ml"
            })
        
        # Mettre à jour la recette
        if new_ingredients:
            recipe.ingredients = new_ingredients
            print(f"  ✓ {recipe.name} - {len(new_ingredients)} ingrédients")
    
    db.session.commit()
    print("\n✅ Toutes les recettes ont été mises à jour avec les quantités exactes du programme!")