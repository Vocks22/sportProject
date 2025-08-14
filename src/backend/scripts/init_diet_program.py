"""
Script d'initialisation du programme de diète fixe de Fabien
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import db
from models.diet_program import DietProgram
from main import create_app

def init_diet_program():
    """Initialise le programme alimentaire fixe dans la base de données"""
    
    # Programme alimentaire structuré selon la feuille du coach
    diet_program = [
        {
            'meal_type': 'repas1',
            'meal_name': 'Petit-déjeuner',
            'time_slot': '6h-9h',
            'order_index': 1,
            'foods': [
                {'name': 'Blancs d\'œufs', 'quantity': '3', 'unit': 'unités'},
                {'name': 'Œuf entier', 'quantity': '1', 'unit': 'unité'},
                {'name': 'Noix de cajou', 'quantity': '40', 'unit': 'g'},
                {'name': 'Jus de pamplemousse', 'quantity': '1', 'unit': 'verre'},
                {'name': 'Café ou thé sans sucre', 'quantity': '1', 'unit': 'tasse'},
                {'name': 'Multi vitamines', 'quantity': '1', 'unit': 'dose (3000mg CLA)'}
            ]
        },
        {
            'meal_type': 'collation1',
            'meal_name': 'Collation du matin',
            'time_slot': '10h-11h',
            'order_index': 2,
            'foods': [
                {'name': 'Lait d\'amande', 'quantity': '200', 'unit': 'ml'},
                {'name': 'Flocons d\'avoine', 'quantity': '60', 'unit': 'g'},
                {'name': 'Ananas', 'quantity': '50', 'unit': 'g'},
                {'name': 'Carré de chocolat noir', 'quantity': '1', 'unit': 'carré'}
            ]
        },
        {
            'meal_type': 'repas2',
            'meal_name': 'Déjeuner',
            'time_slot': '12h-14h',
            'order_index': 3,
            'foods': [
                {'name': 'Viande blanche maigre', 'quantity': '180', 'unit': 'g'},
                {'name': 'Légumes verts', 'quantity': '150', 'unit': 'g'},
                {'name': 'Huile d\'olive', 'quantity': '5', 'unit': 'g'},
                {'name': 'Sel', 'quantity': '1', 'unit': 'g'},
                {'name': 'Multi vitamines', 'quantity': '1', 'unit': 'dose (3000mg CLA)'}
            ]
        },
        {
            'meal_type': 'collation2',
            'meal_name': 'Collation de l\'après-midi',
            'time_slot': '16h-17h',
            'order_index': 4,
            'foods': [
                {'name': 'Blancs d\'œufs', 'quantity': '3', 'unit': 'unités'},
                {'name': 'Amandes', 'quantity': '40', 'unit': 'g'},
                {'name': 'Fruits rouges', 'quantity': '50', 'unit': 'g'}
            ]
        },
        {
            'meal_type': 'repas3',
            'meal_name': 'Dîner',
            'time_slot': '19h-21h',
            'order_index': 5,
            'foods': [
                {'name': 'Poisson blanc maigre', 'quantity': '200', 'unit': 'g'},
                {'name': 'Salade verte', 'quantity': 'à volonté', 'unit': ''},
                {'name': 'Huile d\'olive', 'quantity': '5', 'unit': 'g'},
                {'name': 'Sel', 'quantity': '1', 'unit': 'g'}
            ]
        }
    ]
    
    app = create_app()
    
    with app.app_context():
        # Vérifier si le programme existe déjà
        existing = DietProgram.query.first()
        if existing:
            print("⚠️  Programme de diète déjà initialisé")
            # Optionnel : mettre à jour
            response = input("Voulez-vous réinitialiser le programme ? (o/n): ")
            if response.lower() != 'o':
                return
            
            # Supprimer l'ancien programme
            DietProgram.query.delete()
            db.session.commit()
            print("✅ Ancien programme supprimé")
        
        # Ajouter le nouveau programme
        for meal_data in diet_program:
            meal = DietProgram(
                meal_type=meal_data['meal_type'],
                meal_name=meal_data['meal_name'],
                time_slot=meal_data['time_slot'],
                order_index=meal_data['order_index'],
                foods=meal_data['foods']
            )
            db.session.add(meal)
        
        db.session.commit()
        print(f"✅ Programme de diète initialisé avec {len(diet_program)} repas")
        
        # Afficher le programme
        print("\n📋 Programme alimentaire quotidien :")
        print("-" * 50)
        for meal in DietProgram.query.order_by(DietProgram.order_index).all():
            print(f"\n{meal.order_index}. {meal.meal_name} ({meal.time_slot})")
            for food in meal.foods:
                print(f"   - {food['name']}: {food['quantity']} {food['unit']}")

if __name__ == "__main__":
    init_diet_program()