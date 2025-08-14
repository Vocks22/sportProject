#!/usr/bin/env python3
"""
Script pour exporter/importer la configuration des repas et aliments
Usage:
  - Export: python export_meals_config.py export > meals_config.json
  - Import: python export_meals_config.py import < meals_config.json
"""

import sys
import json
from main import app
from models.diet_program import DietProgram
from database import db

def export_meals():
    """Exporter tous les repas avec leurs aliments"""
    with app.app_context():
        meals = DietProgram.query.order_by(DietProgram.order_index).all()
        
        config = []
        for meal in meals:
            meal_data = {
                'meal_type': meal.meal_type,
                'meal_name': meal.meal_name,
                'time_slot': meal.time_slot,
                'order_index': meal.order_index,
                'foods': meal.foods if meal.foods else []
            }
            config.append(meal_data)
        
        return config

def import_meals(config):
    """Importer la configuration des repas"""
    with app.app_context():
        imported = 0
        updated = 0
        
        for meal_data in config:
            # Chercher si le repas existe déjà
            existing = DietProgram.query.filter_by(meal_type=meal_data['meal_type']).first()
            
            if existing:
                # Mettre à jour le repas existant
                existing.meal_name = meal_data['meal_name']
                existing.time_slot = meal_data['time_slot']
                existing.order_index = meal_data['order_index']
                existing.foods = meal_data['foods']
                updated += 1
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
        
        db.session.commit()
        
        return {
            'imported': imported,
            'updated': updated,
            'total': len(config)
        }

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Export: python export_meals_config.py export > meals_config.json")
        print("  Import: python export_meals_config.py import < meals_config.json")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'export':
        config = export_meals()
        print(json.dumps(config, indent=2, ensure_ascii=False))
        print(f"\n# Exported {len(config)} meals", file=sys.stderr)
        
    elif command == 'import':
        config_json = sys.stdin.read()
        config = json.loads(config_json)
        
        result = import_meals(config)
        print(f"✅ Import successful!")
        print(f"   - New meals: {result['imported']}")
        print(f"   - Updated meals: {result['updated']}")
        print(f"   - Total processed: {result['total']}")
        
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()