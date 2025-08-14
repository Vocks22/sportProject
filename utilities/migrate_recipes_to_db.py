#!/usr/bin/env python3
"""
Script pour migrer les 65 recettes du frontend vers la base de données
avec activation du mode chef et données détaillées
"""

import re
import json
from datetime import datetime

# D'abord, lire et parser les recettes depuis Recipes.jsx
def extract_recipes_from_jsx():
    with open('src/frontend/components/Recipes.jsx', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extraire le tableau des recettes
    recipes_match = re.search(r'const recipes = \[(.*?)\n  \]', content, re.DOTALL)
    if not recipes_match:
        print("Erreur: Impossible de trouver le tableau des recettes")
        return []
    
    recipes_str = recipes_match.group(1)
    
    # Parser chaque recette
    recipes = []
    recipe_blocks = re.findall(r'\{([^}]+(?:\{[^}]*\}[^}]*)*)\}', recipes_str)
    
    for block in recipe_blocks:
        recipe = {}
        
        # Extraire les champs simples
        id_match = re.search(r'id:\s*(\d+)', block)
        if id_match:
            recipe['id'] = int(id_match.group(1))
        
        name_match = re.search(r'name:\s*"([^"]+)"', block)
        if name_match:
            recipe['name'] = name_match.group(1)
        
        category_match = re.search(r'category:\s*"([^"]+)"', block)
        if category_match:
            recipe['category'] = category_match.group(1)
        
        emoji_match = re.search(r'emoji:\s*"([^"]+)"', block)
        if emoji_match:
            recipe['emoji'] = emoji_match.group(1)
        
        time_match = re.search(r'time:\s*"([^"]+)"', block)
        if time_match:
            recipe['time'] = time_match.group(1)
        
        calories_match = re.search(r'calories:\s*(\d+)', block)
        if calories_match:
            recipe['calories'] = int(calories_match.group(1))
        
        protein_match = re.search(r'protein:\s*(\d+)', block)
        if protein_match:
            recipe['protein'] = int(protein_match.group(1))
        
        description_match = re.search(r'description:\s*"([^"]+)"', block)
        if description_match:
            recipe['description'] = description_match.group(1)
        
        # Extraire les tableaux
        ingredients_match = re.search(r'ingredients:\s*\[([^\]]+)\]', block)
        if ingredients_match:
            ingredients_str = ingredients_match.group(1)
            recipe['ingredients'] = [ing.strip().strip('"') for ing in ingredients_str.split(',')]
        
        ustensils_match = re.search(r'ustensils:\s*\[([^\]]+)\]', block)
        if ustensils_match:
            ustensils_str = ustensils_match.group(1)
            recipe['ustensils'] = [u.strip().strip('"') for u in ustensils_str.split(',')]
        
        if recipe.get('id'):
            recipes.append(recipe)
    
    return sorted(recipes, key=lambda x: x.get('id', 0))

def get_meal_type(category):
    """Convertir category en meal_type"""
    mapping = {
        'repas1': 'breakfast',
        'collation1': 'snack',
        'repas2': 'lunch',
        'collation2': 'snack',
        'repas3': 'dinner'
    }
    return mapping.get(category, 'lunch')

def get_difficulty(time_str):
    """Déterminer la difficulté selon le temps"""
    try:
        minutes = int(re.search(r'\d+', time_str).group())
        if minutes <= 10:
            return "beginner"
        elif minutes <= 20:
            return "intermediate"
        else:
            return "advanced"
    except:
        return "intermediate"

def generate_chef_data(recipe):
    """Générer des données chef détaillées pour chaque recette"""
    time_minutes = int(re.search(r'\d+', recipe.get('time', '15 min')).group())
    difficulty = get_difficulty(recipe.get('time', '15 min'))
    
    # Instructions du chef basées sur la catégorie
    chef_instructions = []
    if 'repas1' in recipe.get('category', ''):
        chef_instructions.extend([
            "Préparez tous les ingrédients avant de commencer",
            "Utilisez une poêle bien chaude mais pas fumante",
            "Travaillez rapidement pour un petit-déjeuner frais"
        ])
    elif 'collation' in recipe.get('category', ''):
        chef_instructions.extend([
            "Mesurez précisément les portions",
            "Peut être préparé à l'avance",
            "Conservez au frais si nécessaire"
        ])
    else:
        chef_instructions.extend([
            "Préchauffez votre matériel de cuisson",
            "Assaisonnez progressivement et goûtez",
            "Laissez reposer avant de servir"
        ])
    
    # Étapes de cuisson
    cooking_steps = []
    
    # Étape 1: Préparation
    cooking_steps.append({
        "step": 1,
        "title": "Mise en place",
        "description": f"Préparer et mesurer tous les ingrédients: {', '.join(recipe.get('ingredients', [])[:3])}",
        "duration_minutes": max(2, time_minutes // 4),
        "temperature": "Température ambiante",
        "technique": "Organisation"
    })
    
    # Étape 2: Cuisson/Préparation principale
    cooking_steps.append({
        "step": 2,
        "title": "Préparation principale",
        "description": f"Préparer {recipe.get('name', 'le plat')} selon la méthode classique",
        "duration_minutes": time_minutes // 2,
        "temperature": "Selon recette",
        "technique": "Cuisson maîtrisée"
    })
    
    # Étape 3: Finition
    cooking_steps.append({
        "step": 3,
        "title": "Finition et présentation",
        "description": "Ajuster l'assaisonnement et dresser avec soin",
        "duration_minutes": max(2, time_minutes // 4),
        "temperature": "Service optimal",
        "technique": "Présentation"
    })
    
    # Conseils du chef
    chef_tips = [
        {
            "type": "tip",
            "title": "Qualité des ingrédients",
            "description": "Utilisez toujours des ingrédients frais pour un résultat optimal",
            "importance": "high"
        },
        {
            "type": "secret",
            "title": "Astuce du chef",
            "description": f"Pour {recipe.get('name', 'cette recette')}, le secret est dans le timing parfait",
            "importance": "medium"
        }
    ]
    
    # Ajouter un conseil spécifique selon la catégorie
    if recipe.get('protein', 0) > 30:
        chef_tips.append({
            "type": "tip",
            "title": "Apport protéique",
            "description": "Cette recette est excellente pour la récupération musculaire",
            "importance": "high"
        })
    
    # Indices visuels
    visual_cues = [
        {
            "step_number": 2,
            "description": "Texture et couleur",
            "what_to_look_for": "La préparation doit avoir une belle couleur dorée"
        }
    ]
    
    # Détails de timing
    timing_details = {
        "total_time": time_minutes,
        "active_time": int(time_minutes * 0.7),
        "passive_time": int(time_minutes * 0.3)
    }
    
    # Références média
    media_references = [
        {
            "type": "photo",
            "step_number": 3,
            "description": "Présentation finale du plat"
        }
    ]
    
    return {
        "chef_instructions": chef_instructions,
        "cooking_steps": cooking_steps,
        "chef_tips": chef_tips,
        "visual_cues": visual_cues,
        "timing_details": timing_details,
        "media_references": media_references,
        "difficulty_level": difficulty,
        "has_chef_mode": True
    }

# Script principal pour insérer dans la DB
if __name__ == "__main__":
    import sys
    import os
    sys.path.append('src/backend')
    
    from main import create_app
    from models.recipe import Recipe
    from models.ingredient import Ingredient
    from database import db
    
    # Extraire les recettes du JSX
    print("📖 Extraction des recettes depuis Recipes.jsx...")
    jsx_recipes = extract_recipes_from_jsx()
    print(f"✅ {len(jsx_recipes)} recettes extraites")
    
    # Créer l'application Flask
    app = create_app()
    
    with app.app_context():
        # Supprimer les recettes existantes (optionnel)
        print("\n🗑️  Suppression des anciennes recettes...")
        Recipe.query.delete()
        db.session.commit()
        
        # Créer des ingrédients de base si nécessaire
        print("\n🥚 Vérification des ingrédients de base...")
        base_ingredients = {
            "blancs d'œufs": {"category": "protein", "calories": 52, "protein": 11, "carbs": 0.7, "fat": 0.2},
            "œufs": {"category": "protein", "calories": 155, "protein": 13, "carbs": 1.1, "fat": 11},
            "poulet": {"category": "protein", "calories": 165, "protein": 31, "carbs": 0, "fat": 3.6},
            "thon": {"category": "protein", "calories": 132, "protein": 29.9, "carbs": 0, "fat": 0.8},
            "saumon": {"category": "protein", "calories": 208, "protein": 20, "carbs": 0, "fat": 13},
            "cabillaud": {"category": "protein", "calories": 82, "protein": 18, "carbs": 0, "fat": 0.7},
            "noix de cajou": {"category": "nuts", "calories": 553, "protein": 18, "carbs": 30, "fat": 44},
            "amandes": {"category": "nuts", "calories": 579, "protein": 21, "carbs": 22, "fat": 50},
            "brocoli": {"category": "vegetable", "calories": 34, "protein": 2.8, "carbs": 7, "fat": 0.4},
            "épinards": {"category": "vegetable", "calories": 23, "protein": 2.9, "carbs": 3.6, "fat": 0.4},
            "tomates": {"category": "vegetable", "calories": 18, "protein": 0.9, "carbs": 3.9, "fat": 0.2},
            "salade": {"category": "vegetable", "calories": 15, "protein": 1.4, "carbs": 2.9, "fat": 0.2}
        }
        
        ingredient_map = {}
        for name, nutrition in base_ingredients.items():
            ing = Ingredient.query.filter_by(name=name).first()
            if not ing:
                ing = Ingredient(
                    name=name,
                    category=nutrition["category"],
                    calories_per_100g=nutrition["calories"],
                    protein_per_100g=nutrition["protein"],
                    carbs_per_100g=nutrition["carbs"],
                    fat_per_100g=nutrition["fat"],
                    unit='g'
                )
                db.session.add(ing)
                db.session.flush()
            ingredient_map[name] = ing.id
        
        # Insérer les recettes
        print(f"\n🍳 Insertion de {len(jsx_recipes)} recettes dans la base de données...")
        
        for jsx_recipe in jsx_recipes:
            print(f"  • Recette {jsx_recipe.get('id')}: {jsx_recipe.get('name')}")
            
            # Générer les données chef
            chef_data = generate_chef_data(jsx_recipe)
            
            # Préparer les ingrédients (simplifiés pour cet exemple)
            ingredients_list = []
            for ing_str in jsx_recipe.get('ingredients', []):
                # Essayer d'extraire la quantité et le nom
                quantity_match = re.search(r'(\d+)g?\s+(.+)', ing_str)
                if quantity_match:
                    quantity = int(quantity_match.group(1))
                    ing_name = quantity_match.group(2)
                else:
                    quantity = 100
                    ing_name = ing_str
                
                # Trouver l'ID de l'ingrédient le plus proche
                ingredient_id = 1  # ID par défaut
                for base_name, ing_id in ingredient_map.items():
                    if base_name in ing_name.lower():
                        ingredient_id = ing_id
                        break
                
                ingredients_list.append({
                    "ingredient_id": ingredient_id,
                    "quantity": quantity,
                    "unit": "g"
                })
            
            # Parser le temps
            time_match = re.search(r'(\d+)', jsx_recipe.get('time', '15'))
            prep_time = int(time_match.group(1)) if time_match else 15
            
            # Créer la recette
            recipe = Recipe(
                name=jsx_recipe.get('name'),
                category=jsx_recipe.get('category', 'lunch').replace('repas', 'meal').replace('collation', 'snack'),
                meal_type=get_meal_type(jsx_recipe.get('category', 'repas2')),
                prep_time=min(prep_time // 2, 10),
                cook_time=prep_time,
                servings=1,
                ingredients=ingredients_list,
                instructions=[
                    {"step": 1, "description": f"Préparer {jsx_recipe.get('name')}"},
                    {"step": 2, "description": jsx_recipe.get('description', 'Suivre la recette')}
                ],
                utensils=jsx_recipe.get('ustensils', []),
                total_calories=jsx_recipe.get('calories', 300),
                total_protein=jsx_recipe.get('protein', 25),
                total_carbs=jsx_recipe.get('calories', 300) * 0.2 / 4,  # Estimation
                total_fat=jsx_recipe.get('calories', 300) * 0.3 / 9,  # Estimation
                # Données chef
                chef_instructions=chef_data['chef_instructions'],
                cooking_steps=chef_data['cooking_steps'],
                chef_tips=chef_data['chef_tips'],
                visual_cues=chef_data['visual_cues'],
                timing_details=chef_data['timing_details'],
                media_references=chef_data['media_references'],
                difficulty_level=chef_data['difficulty_level'],
                has_chef_mode=True
            )
            
            db.session.add(recipe)
        
        # Commit final
        db.session.commit()
        
        # Vérification
        total_recipes = Recipe.query.count()
        chef_recipes = Recipe.query.filter_by(has_chef_mode=True).count()
        
        print(f"\n✅ Migration terminée!")
        print(f"   • Total de recettes: {total_recipes}")
        print(f"   • Recettes avec mode chef: {chef_recipes}")
        print(f"\n🎉 Toutes les recettes sont maintenant dans la base de données avec le mode chef activé!")