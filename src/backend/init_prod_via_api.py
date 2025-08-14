#!/usr/bin/env python3
"""Script pour initialiser la base de production via la console Render."""

import sys
import os

# Script à copier-coller dans la console Render Shell

script = """
cd src/backend
python -c "
import sys
import os
sys.path.insert(0, '/opt/render/project/src/src/backend')

from database import db
from main import create_app
from models.diet_program import DietProgram
from datetime import datetime

app = create_app()

with app.app_context():
    # Créer les tables
    db.create_all()
    print('✅ Tables créées')
    
    # Vérifier si des repas existent
    existing = DietProgram.query.count()
    
    if existing == 0:
        print('📝 Création des 5 repas...')
        
        meals = [
            {'meal_type': 'repas1', 'meal_name': 'Petit-déjeuner', 'time_slot': '6h-9h', 'order_index': 1,
             'foods': [{'name': 'Flocons avoine', 'quantity': 100, 'unit': 'g'}]},
            {'meal_type': 'collation1', 'meal_name': 'Collation du matin', 'time_slot': '10h-11h', 'order_index': 2,
             'foods': [{'name': 'Pomme', 'quantity': 1, 'unit': 'unité'}]},
            {'meal_type': 'repas2', 'meal_name': 'Déjeuner', 'time_slot': '12h-14h', 'order_index': 3,
             'foods': [{'name': 'Riz', 'quantity': 150, 'unit': 'g'}]},
            {'meal_type': 'collation2', 'meal_name': 'Collation de l\'après-midi', 'time_slot': '16h-17h', 'order_index': 4,
             'foods': [{'name': 'Shake', 'quantity': 1, 'unit': 'dose'}]},
            {'meal_type': 'repas3', 'meal_name': 'Dîner', 'time_slot': '19h-21h', 'order_index': 5,
             'foods': [{'name': 'Pâtes', 'quantity': 120, 'unit': 'g'}]}
        ]
        
        for meal in meals:
            m = DietProgram(**meal)
            db.session.add(m)
        
        db.session.commit()
        print('✅ 5 repas créés!')
    else:
        print(f'✅ {existing} repas déjà présents')
"
"""

print("📋 INSTRUCTIONS POUR INITIALISER LA BASE DE PRODUCTION")
print("=" * 60)
print("\n1. Allez sur https://dashboard.render.com")
print("2. Sélectionnez 'diettracker-backend'")
print("3. Cliquez sur 'Shell' dans le menu")
print("4. Cliquez sur 'Connect'")
print("5. Copiez-collez cette commande :")
print("\n" + "="*60)
print(script)
print("="*60)
print("\n6. Appuyez sur Entrée pour exécuter")
print("7. Attendez le message '✅ 5 repas créés!'")
print("\n✅ Ensuite rafraîchissez votre site Netlify!")