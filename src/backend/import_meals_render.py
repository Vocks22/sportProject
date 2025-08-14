#!/usr/bin/env python3
"""
Script simplifié pour importer les repas dans Render
Usage direct dans le shell Render:
  python import_meals_render.py
"""

import json
from main import app
from models.diet_program import DietProgram
from database import db

# Configuration des repas à importer
MEALS_CONFIG = [
  {
    "meal_type": "repas1",
    "meal_name": "Petit-déjeuner",
    "time_slot": "6h-9h",
    "order_index": 1,
    "foods": [
      {
        "name": "Blanc d'œuf",
        "quantity": "3",
        "unit": "unité",
        "calories": 51
      },
      {
        "name": "Noix de cajou",
        "quantity": "40",
        "unit": "g",
        "calories": 221
      },
      {
        "name": "Jus de pomme",
        "quantity": "1",
        "unit": "verre",
        "calories": 115
      },
      {
        "name": "Café",
        "quantity": "1",
        "unit": "tasse",
        "calories": 2
      },
      {
        "name": "CLA (supplément)",
        "quantity": "3000",
        "unit": "mg",
        "calories": 0
      }
    ]
  },
  {
    "meal_type": "collation1",
    "meal_name": "Collation du matin",
    "time_slot": "10h-11h",
    "order_index": 2,
    "foods": [
      {
        "name": "Lait d'amandes",
        "quantity": "150",
        "unit": "ml",
        "calories": 26
      },
      {
        "name": "Avoine (flocons)",
        "quantity": "60",
        "unit": "g",
        "calories": 233
      },
      {
        "name": "Pomme",
        "quantity": "50",
        "unit": "g",
        "calories": 27
      },
      {
        "name": "Chocolat noir 70%",
        "quantity": "1",
        "unit": "carré",
        "calories": 30
      }
    ]
  },
  {
    "meal_type": "repas2",
    "meal_name": "Déjeuner",
    "time_slot": "12h-14h",
    "order_index": 3,
    "foods": [
      {
        "name": "Viande blanche maigre",
        "quantity": "180",
        "unit": "g",
        "calories": 297
      },
      {
        "name": "Légumes verts",
        "quantity": "150",
        "unit": "g",
        "calories": 38
      },
      {
        "name": "Huile d'olive",
        "quantity": "5",
        "unit": "ml",
        "calories": 40
      },
      {
        "name": "CLA (supplément)",
        "quantity": "3000",
        "unit": "mg",
        "calories": 0
      }
    ]
  },
  {
    "meal_type": "collation2",
    "meal_name": "Collation de l'après-midi",
    "time_slot": "16h-17h",
    "order_index": 4,
    "foods": [
      {
        "name": "Blanc d'œuf",
        "quantity": "3",
        "unit": "unité",
        "calories": 51
      },
      {
        "name": "Amandes",
        "quantity": "40",
        "unit": "g",
        "calories": 232
      },
      {
        "name": "Pomme",
        "quantity": "50",
        "unit": "g",
        "calories": 27
      }
    ]
  },
  {
    "meal_type": "repas3",
    "meal_name": "Dîner",
    "time_slot": "19h-23h",
    "order_index": 5,
    "foods": [
      {
        "name": "Poisson blanc maigre",
        "quantity": "200",
        "unit": "g",
        "calories": 164
      },
      {
        "name": "Salade verte",
        "quantity": "100",
        "unit": "g",
        "calories": 15
      },
      {
        "name": "Huile d'olive",
        "quantity": "5",
        "unit": "ml",
        "calories": 40
      }
    ]
  }
]

def import_meals():
    """Importer la configuration des repas"""
    with app.app_context():
        imported = 0
        updated = 0
        
        for meal_data in MEALS_CONFIG:
            # Chercher si le repas existe déjà
            existing = DietProgram.query.filter_by(meal_type=meal_data['meal_type']).first()
            
            if existing:
                # Mettre à jour le repas existant
                existing.meal_name = meal_data['meal_name']
                existing.time_slot = meal_data['time_slot']
                existing.order_index = meal_data['order_index']
                existing.foods = meal_data['foods']
                updated += 1
                print(f"  ✓ Mis à jour: {meal_data['meal_name']}")
            else:
                # Créer un nouveau repas
                new_meal = DietProgram(
                    meal_type=meal_data['meal_type'],
                    meal_name=meal_data['meal_name'],
                    time_slot=meal_data['time_slot'],
                    order_index=meal_data['order_index'],
                    foods=meal_data['foods']
                )
                db.session.add(new_meal)
                imported += 1
                print(f"  ✓ Créé: {meal_data['meal_name']}")
        
        db.session.commit()
        
        print("\n✅ Import terminé avec succès!")
        print(f"   - Nouveaux repas: {imported}")
        print(f"   - Repas mis à jour: {updated}")
        print(f"   - Total traité: {len(MEALS_CONFIG)}")
        
        # Afficher le résumé des calories
        print("\n📊 Résumé des calories:")
        total_daily = 0
        for meal in MEALS_CONFIG:
            meal_total = sum(food['calories'] for food in meal['foods'])
            total_daily += meal_total
            print(f"   - {meal['meal_name']}: {meal_total} kcal")
        print(f"   - TOTAL JOURNALIER: {total_daily} kcal")

if __name__ == "__main__":
    print("🚀 Import des repas et aliments...")
    print("=" * 40)
    import_meals()