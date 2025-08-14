#!/usr/bin/env python3
"""
Test de l'ajout d'aliments aux repas
"""
import requests
import json

API_URL = "http://localhost:5000/api"

def test_add_foods():
    # 1. Récupérer les repas existants
    response = requests.get(f"{API_URL}/diet/admin/meals")
    meals = response.json()['meals']
    
    print(f"📋 {len(meals)} repas trouvés")
    
    # 2. Définir les aliments pour chaque type de repas
    foods_by_type = {
        "repas1": [  # Petit-déjeuner
            {"name": "Blanc d'œuf", "quantity": "150", "unit": "g"},
            {"name": "Flocons d'avoine", "quantity": "80", "unit": "g"},
            {"name": "Myrtilles", "quantity": "100", "unit": "g"},
            {"name": "Amandes", "quantity": "20", "unit": "g"},
            {"name": "Banane", "quantity": "1", "unit": "unité"},
            {"name": "Miel", "quantity": "1", "unit": "c.à.s"}
        ],
        "collation1": [  # Collation matin
            {"name": "Shaker protéiné", "quantity": "30", "unit": "g"},
            {"name": "Pomme", "quantity": "1", "unit": "unité"},
            {"name": "Noix", "quantity": "30", "unit": "g"},
            {"name": "Eau", "quantity": "500", "unit": "ml"}
        ],
        "repas2": [  # Déjeuner
            {"name": "Poulet grillé", "quantity": "200", "unit": "g"},
            {"name": "Riz basmati", "quantity": "150", "unit": "g cuit"},
            {"name": "Brocoli", "quantity": "200", "unit": "g"},
            {"name": "Huile d'olive", "quantity": "1", "unit": "c.à.s"},
            {"name": "Salade verte", "quantity": "100", "unit": "g"}
        ],
        "collation2": [  # Collation après-midi
            {"name": "Yaourt grec", "quantity": "150", "unit": "g"},
            {"name": "Fruits rouges", "quantity": "100", "unit": "g"},
            {"name": "Granola", "quantity": "30", "unit": "g"}
        ],
        "repas3": [  # Dîner
            {"name": "Saumon", "quantity": "180", "unit": "g"},
            {"name": "Patate douce", "quantity": "200", "unit": "g"},
            {"name": "Asperges", "quantity": "150", "unit": "g"},
            {"name": "Avocat", "quantity": "1/2", "unit": "unité"}
        ],
        "en_cas": [  # En-cas (si faim)
            # Vide par défaut, à personnaliser selon les besoins
        ]
    }
    
    # 3. Mettre à jour chaque repas avec ses aliments
    for meal in meals:
        meal_type = meal['meal_type']
        if meal_type in foods_by_type:
            foods = foods_by_type[meal_type]
            
            # Mettre à jour le repas avec les aliments
            updated_meal = {
                **meal,
                'foods': foods
            }
            
            response = requests.put(
                f"{API_URL}/diet/admin/meals/{meal['id']}", 
                json=updated_meal
            )
            
            if response.status_code == 200:
                result = response.json()
                if result['success']:
                    print(f"✅ {meal['meal_name']}: {len(foods)} aliments ajoutés")
                else:
                    print(f"❌ Erreur pour {meal['meal_name']}: {result.get('error')}")
            else:
                print(f"❌ Erreur HTTP {response.status_code} pour {meal['meal_name']}")
    
    print("\n🎉 Configuration des aliments terminée!")
    
    # 4. Vérifier le résultat
    response = requests.get(f"{API_URL}/diet/admin/meals")
    meals = response.json()['meals']
    
    print("\n📊 Résumé des repas configurés:")
    for meal in sorted(meals, key=lambda x: x['order_index']):
        foods_count = len(meal.get('foods', []))
        print(f"  {meal['order_index']}. {meal['meal_name']} ({meal['time_slot']}): {foods_count} aliments")
        if meal.get('foods'):
            for food in meal['foods'][:3]:  # Afficher les 3 premiers aliments
                print(f"     - {food['name']}: {food['quantity']} {food['unit']}")
            if len(meal['foods']) > 3:
                print(f"     ... et {len(meal['foods']) - 3} autres")

if __name__ == "__main__":
    test_add_foods()