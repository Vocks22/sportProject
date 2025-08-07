#!/usr/bin/env python3
"""
Test script pour vérifier le fonctionnement du mode Chef (US1.4)
"""

import requests
import json
import sys

BASE_URL = "http://localhost:5000/api"

def test_recipe_creation_with_chef_mode():
    """Test la création d'une recette avec mode chef"""
    recipe_data = {
        "name": "Test Omelette Mode Chef",
        "category": "breakfast",
        "meal_type": "repas1",
        "ingredients": [
            {"ingredient_id": 1, "name": "Blancs d'œufs", "quantity": 3, "unit": "pièces"}
        ],
        "instructions": [
            {"step": 1, "description": "Battre les blancs d'œufs"}
        ],
        "prep_time": 5,
        "cook_time": 10,
        "servings": 1,
        "has_chef_mode": True,
        "difficulty_level": "beginner",
        "chef_instructions": [
            "Assurez-vous que les blancs d'œufs sont à température ambiante",
            "Utilisez une poêle antiadhésive bien chaude"
        ],
        "cooking_steps": [
            {
                "step": 1,
                "title": "Préparation des blancs",
                "description": "Séparer les blancs des jaunes et les battre légèrement",
                "duration_minutes": 2,
                "temperature": "Température ambiante",
                "technique": "Battage léger"
            },
            {
                "step": 2,
                "title": "Cuisson",
                "description": "Verser dans la poêle chaude et cuire à feu moyen",
                "duration_minutes": 8,
                "temperature": "Feu moyen",
                "technique": "Cuisson à la poêle"
            }
        ],
        "chef_tips": [
            {
                "id": "tip1",
                "type": "tip",
                "title": "Température parfaite",
                "description": "La poêle doit être chaude mais pas fumante",
                "importance": "high"
            },
            {
                "id": "tip2",
                "type": "secret",
                "title": "Secret du chef",
                "description": "Ajouter une goutte d'huile d'olive pour plus de saveur",
                "importance": "medium"
            }
        ],
        "visual_cues": [
            {
                "step_number": 2,
                "description": "Les bords commencent à se solidifier",
                "what_to_look_for": "Bordure blanche qui se forme autour de l'omelette"
            }
        ],
        "timing_details": {
            "total_time": 10,
            "active_time": 8,
            "passive_time": 2
        },
        "media_references": [
            {
                "id": "media1",
                "type": "photo",
                "step_number": 2,
                "description": "Aspect de l'omelette parfaitement cuite",
                "alt_text": "Omelette dorée dans la poêle"
            }
        ]
    }
    
    print("🧪 Test création d'une recette avec mode chef...")
    try:
        response = requests.post(f"{BASE_URL}/recipes", json=recipe_data)
        if response.status_code == 201:
            recipe = response.json()
            print("✅ Recette créée avec succès!")
            print(f"   ID: {recipe['id']}")
            print(f"   Nom: {recipe['name']}")
            print(f"   Mode chef: {recipe['has_chef_mode']}")
            print(f"   Difficulté: {recipe['difficulty_level']}")
            return recipe['id']
        else:
            print(f"❌ Erreur lors de la création: {response.status_code}")
            print(f"   Détail: {response.text}")
            return None
    except requests.exceptions.ConnectionError:
        print("❌ Impossible de se connecter au serveur. Assurez-vous que l'API est démarrée.")
        return None

def test_cooking_guide_endpoint(recipe_id):
    """Test l'endpoint du guide de cuisson"""
    print(f"\n🧪 Test récupération du guide de cuisson pour la recette {recipe_id}...")
    try:
        response = requests.get(f"{BASE_URL}/recipes/{recipe_id}/cooking-guide")
        if response.status_code == 200:
            guide = response.json()
            print("✅ Guide de cuisson récupéré avec succès!")
            print(f"   Recette: {guide['recipe_name']}")
            print(f"   Difficulté: {guide['difficulty_level']}")
            print(f"   Nombre d'étapes: {len(guide['cooking_steps'])}")
            print(f"   Nombre de conseils: {len(guide['chef_tips'])}")
            print(f"   Indices visuels: {len(guide['visual_cues'])}")
            return True
        else:
            print(f"❌ Erreur lors de la récupération: {response.status_code}")
            print(f"   Détail: {response.text}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Impossible de se connecter au serveur.")
        return False

def test_recipe_filtering():
    """Test le filtrage des recettes avec mode chef"""
    print(f"\n🧪 Test filtrage des recettes avec mode chef...")
    try:
        # Test filtre par has_chef_mode
        response = requests.get(f"{BASE_URL}/recipes?has_chef_mode=true")
        if response.status_code == 200:
            data = response.json()
            recipes_with_chef = data['recipes']
            print(f"✅ Filtrage par mode chef réussi! {len(recipes_with_chef)} recettes trouvées")
            
            # Vérifier que toutes les recettes ont le mode chef
            all_have_chef_mode = all(recipe.get('has_chef_mode', False) for recipe in recipes_with_chef)
            if all_have_chef_mode:
                print("✅ Toutes les recettes retournées ont bien le mode chef activé")
            else:
                print("❌ Certaines recettes sans mode chef ont été retournées")
        else:
            print(f"❌ Erreur lors du filtrage: {response.status_code}")
            
        # Test filtre par difficulty_level
        response = requests.get(f"{BASE_URL}/recipes?difficulty_level=beginner")
        if response.status_code == 200:
            data = response.json()
            beginner_recipes = data['recipes']
            print(f"✅ Filtrage par difficulté réussi! {len(beginner_recipes)} recettes débutant trouvées")
        else:
            print(f"❌ Erreur lors du filtrage par difficulté: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Impossible de se connecter au serveur.")

def main():
    print("🚀 Test des fonctionnalités Mode Chef (US1.4)")
    print("=" * 50)
    
    # Test création de recette avec mode chef
    recipe_id = test_recipe_creation_with_chef_mode()
    if not recipe_id:
        print("\n❌ Les tests ne peuvent pas continuer sans recette de test.")
        return
    
    # Test guide de cuisson
    test_cooking_guide_endpoint(recipe_id)
    
    # Test filtrage
    test_recipe_filtering()
    
    print("\n" + "=" * 50)
    print("✅ Tests terminés! Vérifiez les résultats ci-dessus.")
    print("\nPour tester l'interface utilisateur:")
    print("1. Démarrez le serveur frontend (npm run dev)")
    print("2. Allez sur la page Recettes")
    print("3. Utilisez les filtres 'Mode Chef uniquement' et 'Difficulté'")
    print("4. Cliquez sur 'Mode Chef' sur une recette compatible")

if __name__ == "__main__":
    main()