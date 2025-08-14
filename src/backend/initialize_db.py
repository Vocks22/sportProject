#!/usr/bin/env python3
"""Script d'initialisation de la base de données."""

import os
import sys
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).resolve().parent))

def init_diet_program():
    """Initialise le programme diététique."""
    from database import db
    from main import create_app
    from models.diet_program import DietProgram, DietMeal
    from datetime import datetime
    
    app = create_app()
    
    with app.app_context():
        try:
            # Vérifier si un programme existe déjà
            existing = DietProgram.query.filter_by(user_id=1, is_active=True).first()
            
            if not existing:
                print("📝 Création du programme diététique...")
                
                # Créer le programme
                program = DietProgram(
                    user_id=1,
                    name="Programme Prise de Masse",
                    description="Programme structuré en 5 repas quotidiens",
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
                meals = [
                    ("Repas 1 - Petit-déjeuner", "07:00", 1),
                    ("Repas 2 - Collation matin", "10:00", 2),
                    ("Repas 3 - Déjeuner", "12:30", 3),
                    ("Repas 4 - Collation après-midi", "16:00", 4),
                    ("Repas 5 - Dîner", "19:30", 5)
                ]
                
                for name, time, order in meals:
                    meal = DietMeal(
                        program_id=program.id,
                        name=name,
                        meal_time=time,
                        meal_order=order
                    )
                    db.session.add(meal)
                
                db.session.commit()
                print(f"✅ Programme '{program.name}' créé avec {len(meals)} repas")
                return True
            else:
                print(f"✅ Programme existant: {existing.name}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    init_diet_program()