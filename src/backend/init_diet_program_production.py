#!/usr/bin/env python3
"""
Script pour initialiser ou vérifier le programme de diète en production
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import db
from models.diet_program import DietProgram
from main import create_app

def init_diet_program_production():
    """Initialise le programme alimentaire si nécessaire"""
    
    app = create_app()
    with app.app_context():
        # Vérifier si les repas existent déjà
        existing_meals = DietProgram.query.all()
        
        if len(existing_meals) >= 5:
            print(f"✅ {len(existing_meals)} repas déjà présents dans la base")
            for meal in existing_meals:
                print(f"  - ID:{meal.id} Type:{meal.meal_type} Nom:{meal.meal_name}")
            return
        
        print("📦 Initialisation des repas manquants...")
        
        # Programme alimentaire structuré
        diet_program = [
            {
                'meal_type': 'repas1',
                'meal_name': 'Petit-déjeuner',
                'time_slot': '6h-9h',
                'order_index': 1,
                'foods': [
                    {'name': 'Blancs d\'œufs', 'quantity': '3', 'unit': 'unités'},
                    {'name': 'Œuf entier', 'quantity': '1', 'unit': 'unité'},
                    {'name': 'Noix de cajou', 'quantity': '40', 'unit': 'g'}
                ]
            },
            {
                'meal_type': 'collation1',
                'meal_name': 'Collation du matin',
                'time_slot': '10h-11h',
                'order_index': 2,
                'foods': [
                    {'name': 'Lait d\'amande', 'quantity': '200', 'unit': 'ml'},
                    {'name': 'Flocons d\'avoine', 'quantity': '60', 'unit': 'g'}
                ]
            },
            {
                'meal_type': 'repas2',
                'meal_name': 'Déjeuner',
                'time_slot': '12h-14h',
                'order_index': 3,
                'foods': [
                    {'name': 'Viande blanche maigre', 'quantity': '180', 'unit': 'g'},
                    {'name': 'Légumes verts', 'quantity': '150', 'unit': 'g'}
                ]
            },
            {
                'meal_type': 'collation2',
                'meal_name': 'Collation de l\'après-midi',
                'time_slot': '16h-17h',
                'order_index': 4,
                'foods': [
                    {'name': 'Blancs d\'œufs', 'quantity': '4', 'unit': 'unités'},
                    {'name': 'Amandes', 'quantity': '40', 'unit': 'g'}
                ]
            },
            {
                'meal_type': 'repas3',
                'meal_name': 'Dîner',
                'time_slot': '19h30-21h',
                'order_index': 5,
                'foods': [
                    {'name': 'Poisson blanc', 'quantity': '150', 'unit': 'g'},
                    {'name': 'Légumes cuits', 'quantity': '150', 'unit': 'g'}
                ]
            }
        ]
        
        # Créer les repas manquants
        for meal_data in diet_program:
            # Vérifier si ce type de repas existe déjà
            existing = DietProgram.query.filter_by(meal_type=meal_data['meal_type']).first()
            if not existing:
                meal = DietProgram(**meal_data)
                db.session.add(meal)
                print(f"  ✅ Ajouté: {meal_data['meal_name']} ({meal_data['meal_type']})")
            else:
                print(f"  ⏭️  Existe déjà: {existing.meal_name} ({existing.meal_type})")
        
        db.session.commit()
        print("✅ Programme alimentaire initialisé avec succès!")
        
        # Afficher le résultat final
        final_meals = DietProgram.query.order_by(DietProgram.order_index).all()
        print("\n📋 Repas dans la base:")
        for meal in final_meals:
            print(f"  - ID:{meal.id} Type:{meal.meal_type} Nom:{meal.meal_name}")

if __name__ == '__main__':
    init_diet_program_production()