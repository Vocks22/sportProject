#!/usr/bin/env python3
"""Script d'initialisation de la base de données pour développement local."""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv('.env.local')

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).resolve().parent))

def init_diet_program():
    """Initialise le programme diététique avec les 5 repas."""
    from database import db
    from main import create_app
    from models.diet_program import DietProgram
    from datetime import datetime
    
    app = create_app()
    
    with app.app_context():
        try:
            # Créer les tables
            db.create_all()
            print("✅ Tables créées/vérifiées")
            
            # Vérifier si des repas existent déjà
            existing_meals = DietProgram.query.count()
            
            if existing_meals == 0:
                print("📝 Création des 5 repas quotidiens...")
                
                # Configuration des 5 repas
                meals_config = [
                    {
                        'meal_type': 'repas1',
                        'meal_name': 'Petit-déjeuner',
                        'time_slot': '7h00-8h00',
                        'order_index': 1,
                        'foods': [
                            {'name': 'Flocons d\'avoine', 'quantity': 100, 'unit': 'g'},
                            {'name': 'Banane', 'quantity': 1, 'unit': 'unité'},
                            {'name': 'Beurre d\'amande', 'quantity': 20, 'unit': 'g'}
                        ]
                    },
                    {
                        'meal_type': 'collation1',
                        'meal_name': 'Collation matin',
                        'time_slot': '10h00-10h30',
                        'order_index': 2,
                        'foods': [
                            {'name': 'Pomme', 'quantity': 1, 'unit': 'unité'},
                            {'name': 'Amandes', 'quantity': 30, 'unit': 'g'}
                        ]
                    },
                    {
                        'meal_type': 'repas2',
                        'meal_name': 'Déjeuner',
                        'time_slot': '12h30-13h30',
                        'order_index': 3,
                        'foods': [
                            {'name': 'Riz blanc', 'quantity': 150, 'unit': 'g'},
                            {'name': 'Poulet', 'quantity': 200, 'unit': 'g'},
                            {'name': 'Légumes verts', 'quantity': 200, 'unit': 'g'}
                        ]
                    },
                    {
                        'meal_type': 'collation2',
                        'meal_name': 'Collation après-midi',
                        'time_slot': '16h00-16h30',
                        'order_index': 4,
                        'foods': [
                            {'name': 'Shake protéiné', 'quantity': 1, 'unit': 'dose'},
                            {'name': 'Fruits secs', 'quantity': 40, 'unit': 'g'}
                        ]
                    },
                    {
                        'meal_type': 'repas3',
                        'meal_name': 'Dîner',
                        'time_slot': '19h30-20h30',
                        'order_index': 5,
                        'foods': [
                            {'name': 'Pâtes complètes', 'quantity': 120, 'unit': 'g'},
                            {'name': 'Saumon', 'quantity': 150, 'unit': 'g'},
                            {'name': 'Salade verte', 'quantity': 100, 'unit': 'g'}
                        ]
                    }
                ]
                
                # Créer chaque repas
                for meal_config in meals_config:
                    meal = DietProgram(**meal_config)
                    db.session.add(meal)
                    print(f"  ✅ {meal_config['meal_name']} ajouté")
                
                db.session.commit()
                print(f"\n🎉 Programme diététique initialisé avec {len(meals_config)} repas!")
                
            else:
                print(f"✅ {existing_meals} repas déjà configurés")
                
                # Afficher les repas existants
                meals = DietProgram.query.order_by(DietProgram.order_index).all()
                print("\n📋 Repas configurés:")
                for meal in meals:
                    print(f"  {meal.order_index}. {meal.meal_name} ({meal.time_slot})")
                
        except Exception as e:
            print(f"❌ Erreur: {e}")
            db.session.rollback()
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Initialisation de la base de données Render Frankfurt...")
    print(f"📍 URL: {os.getenv('DATABASE_URL')[:50]}...")
    init_diet_program()