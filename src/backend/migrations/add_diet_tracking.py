"""
Migration pour ajouter les tables de suivi de diète
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import db
from models.diet_program import DietProgram, DietTracking, DietStreak
from main import create_app

def migrate():
    """Crée les nouvelles tables pour le suivi de diète"""
    app = create_app()
    
    with app.app_context():
        # Créer les tables
        db.create_all()
        print("✅ Tables de suivi de diète créées avec succès")
        
        # Vérifier si les tables existent
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        
        if 'diet_program' in tables:
            print("✓ Table diet_program créée")
        if 'diet_tracking' in tables:
            print("✓ Table diet_tracking créée")
        if 'diet_streak' in tables:
            print("✓ Table diet_streak créée")
        
        print("\n📝 Pour initialiser le programme de diète, exécutez :")
        print("   python scripts/init_diet_program.py")

if __name__ == "__main__":
    migrate()