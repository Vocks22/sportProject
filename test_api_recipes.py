#!/usr/bin/env python3
"""
Script de test simple pour démontrer l'API des recettes
"""

import requests
import json
import sys
import os

# Ajouter le chemin src/backend au path pour les imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src/backend'))

def test_api():
    """Tester les endpoints de l'API des recettes"""
    
    base_url = "http://localhost:5000/api"
    
    # Données de test
    recipe_data = {
        "name": "Crêpes Test",
        "category": "breakfast",
        "meal_type": "repas1",
        "ingredients": [
            {
                "ingredient_id": 1,
                "name": "Farine",
                "quantity": 200,
                "unit": "g"
            },
            {
                "ingredient_id": 2,
                "name": "Lait",
                "quantity": 300,
                "unit": "ml"
            }
        ],
        "instructions": [
            {
                "step": 1,
                "description": "Mélanger la farine avec le lait"
            },
            {
                "step": 2,
                "description": "Cuire dans une poêle chaude"
            }
        ],
        "prep_time": 10,
        "cook_time": 15,
        "servings": 4,
        "utensils": ["poêle", "fouet", "bol"],
        "tags": ["facile", "rapide"]
    }
    
    print("🧪 Test de l'API des recettes")
    print("=" * 50)
    
    try:
        # Test 1: GET /recipes (vide)
        print("\n1. Récupération de toutes les recettes (liste vide)")
        response = requests.get(f"{base_url}/recipes")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Succès: {len(data['recipes'])} recettes trouvées")
            print(f"   Pagination: page {data['pagination']['page']}, total {data['pagination']['total']}")
        else:
            print(f"❌ Erreur {response.status_code}: {response.text}")
        
        # Test 2: POST /recipes (création)
        print("\n2. Création d'une nouvelle recette")
        response = requests.post(
            f"{base_url}/recipes",
            json=recipe_data,
            headers={'Content-Type': 'application/json'}
        )
        if response.status_code == 201:
            created_recipe = response.json()
            recipe_id = created_recipe['id']
            print(f"✅ Succès: Recette créée avec ID {recipe_id}")
            print(f"   Nom: {created_recipe['name']}")
            print(f"   Calories totales: {created_recipe.get('nutrition_total', {}).get('calories', 0)}")
        else:
            print(f"❌ Erreur {response.status_code}: {response.text}")
            return
        
        # Test 3: GET /recipes/:id
        print(f"\n3. Récupération de la recette ID {recipe_id}")
        response = requests.get(f"{base_url}/recipes/{recipe_id}")
        if response.status_code == 200:
            recipe = response.json()
            print(f"✅ Succès: Recette '{recipe['name']}' récupérée")
            print(f"   Ingrédients: {len(recipe['ingredients'])}")
            print(f"   Instructions: {len(recipe['instructions'])}")
        else:
            print(f"❌ Erreur {response.status_code}: {response.text}")
        
        # Test 4: PUT /recipes/:id
        print(f"\n4. Mise à jour de la recette ID {recipe_id}")
        update_data = {
            "name": "Crêpes Test Modifiées",
            "rating": 4.5,
            "is_favorite": True
        }
        response = requests.put(
            f"{base_url}/recipes/{recipe_id}",
            json=update_data,
            headers={'Content-Type': 'application/json'}
        )
        if response.status_code == 200:
            updated_recipe = response.json()
            print(f"✅ Succès: Recette mise à jour")
            print(f"   Nouveau nom: {updated_recipe['name']}")
            print(f"   Note: {updated_recipe['rating']}/5")
            print(f"   Favori: {updated_recipe['is_favorite']}")
        else:
            print(f"❌ Erreur {response.status_code}: {response.text}")
        
        # Test 5: POST /recipes/:id/favorite
        print(f"\n5. Basculement du statut favori")
        response = requests.post(f"{base_url}/recipes/{recipe_id}/favorite")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Succès: Statut favori basculé")
            print(f"   Favori: {data['is_favorite']}")
        else:
            print(f"❌ Erreur {response.status_code}: {response.text}")
        
        # Test 6: GET /recipes avec filtres et pagination
        print(f"\n6. Récupération avec filtres")
        response = requests.get(f"{base_url}/recipes?category=breakfast&page=1&per_page=5")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Succès: {len(data['recipes'])} recettes trouvées")
            print(f"   Filtre catégorie: breakfast")
            print(f"   Pagination: page {data['pagination']['page']}")
        else:
            print(f"❌ Erreur {response.status_code}: {response.text}")
        
        # Test 7: DELETE /recipes/:id
        print(f"\n7. Suppression de la recette ID {recipe_id}")
        response = requests.delete(f"{base_url}/recipes/{recipe_id}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Succès: {data['message']}")
        else:
            print(f"❌ Erreur {response.status_code}: {response.text}")
        
        # Test 8: Vérification de la suppression
        print(f"\n8. Vérification de la suppression")
        response = requests.get(f"{base_url}/recipes/{recipe_id}")
        if response.status_code == 404:
            print(f"✅ Succès: Recette bien supprimée (404 attendu)")
        else:
            print(f"❌ Erreur: La recette devrait être supprimée")
        
        print("\n" + "=" * 50)
        print("🎉 Tests de l'API terminés avec succès!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Erreur: Impossible de se connecter au serveur")
        print("   Assurez-vous que le serveur Flask est lancé sur http://localhost:5000")
        print("   Commande: python src/backend/main.py")
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")

if __name__ == "__main__":
    test_api()