#!/usr/bin/env python3
"""
Script d'initialisation automatique de la base de données au démarrage.
Ce script s'exécute rapidement et vérifie/initialise les données de base.
"""

import os
import sys
from datetime import datetime
from pathlib import Path

# Configuration du path
sys.path.insert(0, str(Path(__file__).resolve().parent))

def init_database():
    """Initialise la base de données avec les données de base."""
    from database import db
    from main import create_app
    from models.diet_program import DietProgram, DietMeal
    from models.food import Food
    
    app = create_app()
    
    with app.app_context():
        # Créer les tables si nécessaire
        db.create_all()
        print("✅ Tables vérifiées")
        
        # Vérifier si le programme existe déjà
        existing_program = DietProgram.query.filter_by(user_id=1, is_active=True).first()
        
        if not existing_program:
            print("📝 Création du programme diététique...")
            
            # Créer le programme principal
            program = DietProgram(
                user_id=1,
                name="Programme Prise de Masse",
                description="Programme diététique structuré en 5 repas quotidiens",
                start_date=datetime.now().date(),
                is_active=True,
                daily_calories_target=3000,
                daily_protein_target=150,
                daily_carbs_target=400,
                daily_fat_target=100
            )
            db.session.add(program)
            db.session.commit()
            
            # Ajouter les 5 repas
            meals_config = [
                ("Repas 1 - Petit-déjeuner", "07:00", 1),
                ("Repas 2 - Collation matin", "10:00", 2),
                ("Repas 3 - Déjeuner", "12:30", 3),
                ("Repas 4 - Collation après-midi", "16:00", 4),
                ("Repas 5 - Dîner", "19:30", 5)
            ]
            
            for name, time, order in meals_config:
                meal = DietMeal(
                    program_id=program.id,
                    name=name,
                    meal_time=time,
                    meal_order=order
                )
                db.session.add(meal)
            
            db.session.commit()
            print(f"✅ Programme '{program.name}' créé avec {len(meals_config)} repas")
        else:
            print(f"✅ Programme existant: {existing_program.name}")
        
        # Vérifier si des aliments de base existent
        food_count = Food.query.count()
        if food_count == 0:
            print("📝 Ajout d'aliments de base...")
            
            # Ajouter quelques aliments de base
            basic_foods = [
                ("Riz blanc cuit", 130, 2.7, 28.2, 0.3, "100g"),
                ("Poulet grillé", 165, 31.0, 0.0, 3.6, "100g"),
                ("Brocoli cuit", 35, 2.8, 7.2, 0.4, "100g"),
                ("Avocat", 160, 2.0, 8.5, 14.7, "100g"),
                ("Œufs entiers", 155, 13.0, 1.1, 11.0, "100g"),
                ("Flocons d'avoine", 389, 16.9, 66.3, 6.9, "100g"),
                ("Banane", 89, 1.1, 22.8, 0.3, "100g"),
                ("Amandes", 579, 21.2, 21.6, 49.9, "100g")
            ]
            
            for name, cal, prot, carbs, fat, unit in basic_foods:
                food = Food(
                    name=name,
                    calories=cal,
                    protein=prot,
                    carbs=carbs,
                    fat=fat,
                    unit=unit,
                    category="base"
                )
                db.session.add(food)
            
            db.session.commit()
            print(f"✅ {len(basic_foods)} aliments de base ajoutés")
        else:
            print(f"✅ {food_count} aliments déjà en base")
        
        print("\n🎉 Base de données initialisée avec succès!")
        return True

if __name__ == "__main__":
    try:
        init_database()
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation: {e}")
        sys.exit(1)