#!/usr/bin/env python3
"""
Script pour peupler la base de données avec des recettes ayant le mode chef
"""

import requests
import json

BASE_URL = "http://localhost:5000/api"

def create_chef_recipe(recipe_data):
    """Créer une recette avec mode chef"""
    try:
        response = requests.post(f"{BASE_URL}/recipes", json=recipe_data)
        if response.status_code == 201:
            recipe = response.json()
            print(f"✅ Recette '{recipe['name']}' créée avec ID {recipe['id']}")
            return recipe['id']
        else:
            print(f"❌ Erreur création '{recipe_data['name']}': {response.status_code}")
            print(f"   Détail: {response.text}")
            return None
    except requests.exceptions.ConnectionError:
        print("❌ Serveur non disponible")
        return None

def populate_recipes():
    """Peupler avec des recettes de démonstration"""
    recipes = [
        {
            "name": "Omelette aux Blancs d'Œufs - Mode Chef",
            "category": "breakfast", 
            "meal_type": "repas1",
            "ingredients": [
                {"ingredient_id": 1, "name": "Blancs d'œufs", "quantity": 3, "unit": "pièces"},
                {"ingredient_id": 2, "name": "Noix de cajou", "quantity": 40, "unit": "g"}
            ],
            "instructions": [
                {"step": 1, "description": "Séparer les blancs des jaunes"},
                {"step": 2, "description": "Battre légèrement les blancs"},
                {"step": 3, "description": "Cuire à feu moyen dans une poêle antiadhésive"}
            ],
            "prep_time": 5,
            "cook_time": 10,
            "servings": 1,
            "has_chef_mode": True,
            "difficulty_level": "beginner",
            "chef_instructions": [
                "Assurez-vous que les blancs d'œufs sont à température ambiante pour une meilleure texture",
                "Préchauffez la poêle avant d'ajouter les œufs pour éviter qu'ils collent",
                "N'ajoutez pas de sel avant la cuisson, cela durcirait les blancs"
            ],
            "cooking_steps": [
                {
                    "step": 1,
                    "title": "Préparation des blancs",
                    "description": "Séparer soigneusement les blancs des jaunes. Aucune trace de jaune ne doit rester.",
                    "duration_minutes": 2,
                    "temperature": "Température ambiante",
                    "technique": "Séparation manuelle"
                },
                {
                    "step": 2,
                    "title": "Battage léger",
                    "description": "Battre les blancs juste assez pour les homogénéiser, sans les monter en neige.",
                    "duration_minutes": 1,
                    "temperature": "Température ambiante", 
                    "technique": "Battage à la fourchette"
                },
                {
                    "step": 3,
                    "title": "Cuisson de l'omelette",
                    "description": "Verser les blancs dans la poêle chaude et cuire en remuant délicatement les bords.",
                    "duration_minutes": 7,
                    "temperature": "Feu moyen (5/10)",
                    "technique": "Cuisson à la poêle"
                }
            ],
            "chef_tips": [
                {
                    "id": "tip1",
                    "type": "tip", 
                    "title": "Température parfaite",
                    "description": "La poêle doit être chaude mais pas fumante. Testez avec une goutte d'eau qui doit grésiller doucement.",
                    "importance": "high"
                },
                {
                    "id": "tip2",
                    "type": "secret",
                    "title": "Secret du chef",
                    "description": "Ajoutez une pincée d'eau aux blancs d'œufs (1 cuillère à café) pour une texture plus moelleuse.",
                    "importance": "medium"
                },
                {
                    "id": "tip3",
                    "type": "warning",
                    "title": "Attention !",
                    "description": "Ne retournez jamais l'omelette avec une spatule métallique sur une poêle antiadhésive.",
                    "importance": "high"
                }
            ],
            "visual_cues": [
                {
                    "step_number": 3,
                    "description": "Les bords commencent à se solidifier",
                    "what_to_look_for": "Une bordure blanche opaque se forme autour de l'omelette, le centre reste encore légèrement liquide"
                },
                {
                    "step_number": 3,
                    "description": "Fin de cuisson",
                    "what_to_look_for": "L'omelette ne colle plus à la poêle quand on la secoue légèrement"
                }
            ],
            "timing_details": {
                "total_time": 15,
                "prep_time": 5,
                "cook_time": 10,
                "rest_time": 0
            },
            "media_references": []
        },
        
        {
            "name": "Poulet Grillé Parfait - Mode Chef",
            "category": "lunch",
            "meal_type": "repas2", 
            "ingredients": [
                {"ingredient_id": 3, "name": "Blanc de poulet", "quantity": 180, "unit": "g"},
                {"ingredient_id": 4, "name": "Brocolis", "quantity": 150, "unit": "g"},
                {"ingredient_id": 5, "name": "Huile d'olive", "quantity": 5, "unit": "g"}
            ],
            "instructions": [
                {"step": 1, "description": "Préparer le poulet"},
                {"step": 2, "description": "Cuire les brocolis à la vapeur"},
                {"step": 3, "description": "Griller le poulet"}
            ],
            "prep_time": 10,
            "cook_time": 20,
            "servings": 1,
            "has_chef_mode": True,
            "difficulty_level": "intermediate",
            "chef_instructions": [
                "Sortez le poulet du réfrigérateur 20 minutes avant la cuisson",
                "Utilisez un thermomètre à viande pour vérifier la cuisson interne",
                "Laissez reposer le poulet 5 minutes après cuisson"
            ],
            "cooking_steps": [
                {
                    "step": 1,
                    "title": "Préparation du poulet", 
                    "description": "Aplatir légèrement le blanc de poulet pour une cuisson uniforme. Assaisonner.",
                    "duration_minutes": 5,
                    "temperature": "Température ambiante",
                    "technique": "Attendrissage au maillet"
                },
                {
                    "step": 2,
                    "title": "Cuisson vapeur des brocolis",
                    "description": "Cuire les brocolis à la vapeur jusqu'à ce qu'ils soient tendres mais encore croquants.",
                    "duration_minutes": 8,
                    "temperature": "Vapeur 100°C",
                    "technique": "Cuisson vapeur"
                },
                {
                    "step": 3,
                    "title": "Grillage du poulet",
                    "description": "Griller le poulet 6-7 minutes de chaque côté jusqu'à ce que la température interne atteigne 74°C.",
                    "duration_minutes": 12,
                    "temperature": "Feu moyen-fort",
                    "technique": "Grillage à la poêle"
                }
            ],
            "chef_tips": [
                {
                    "id": "tip1",
                    "type": "tip",
                    "title": "Test de cuisson",
                    "description": "Le poulet est cuit quand les jus qui s'en échappent sont clairs, pas roses.",
                    "importance": "high"
                },
                {
                    "id": "tip2",
                    "type": "warning", 
                    "title": "Sécurité alimentaire",
                    "description": "La température interne doit absolument atteindre 74°C pour éliminer les bactéries.",
                    "importance": "high"
                },
                {
                    "id": "tip3",
                    "type": "secret",
                    "title": "Jutosité garantie",
                    "description": "Ne piquez jamais le poulet pendant la cuisson, les jus s'échapperaient.",
                    "importance": "medium"
                }
            ],
            "visual_cues": [
                {
                    "step_number": 3,
                    "description": "Croûte dorée formée",
                    "what_to_look_for": "Une belle coloration dorée sur la surface du poulet"
                },
                {
                    "step_number": 3,
                    "description": "Fermeté au toucher", 
                    "what_to_look_for": "Le poulet devient ferme sous la pression du doigt"
                }
            ],
            "timing_details": {
                "total_time": 30,
                "prep_time": 10,
                "cook_time": 20,
                "rest_time": 5
            },
            "media_references": []
        }
    ]
    
    print("🚀 Création de recettes de démonstration avec mode chef...")
    print("=" * 60)
    
    created_count = 0
    for recipe in recipes:
        if create_chef_recipe(recipe):
            created_count += 1
    
    print("=" * 60)
    print(f"✅ {created_count}/{len(recipes)} recettes créées avec succès!")
    print("\nCes recettes incluent:")
    print("- Instructions détaillées du chef")
    print("- Étapes de cuisson avec timing précis")
    print("- Conseils et astuces professionnelles") 
    print("- Indices visuels pour réussir la cuisson")
    print("- Niveaux de difficulté différents")

if __name__ == "__main__":
    populate_recipes()