"""
Script pour vérifier l'état de la base de données sur Render
"""

import os
import sys
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent))

from flask import Flask
from database import db
from database.config import get_config
from sqlalchemy import inspect, text

def check_database():
    """Vérifie l'état de la base de données"""
    
    # Déterminer l'environnement
    env = os.environ.get('FLASK_ENV', 'development')
    print(f"🔍 Environnement détecté: {env}")
    
    config = get_config(env)
    app = Flask(__name__)
    app.config.from_object(config)
    
    print(f"📊 Base de données: {app.config.get('SQLALCHEMY_DATABASE_URI', 'Non configurée')[:50]}...")
    
    db.init_app(app)
    
    with app.app_context():
        try:
            # Tester la connexion
            db.session.execute(text('SELECT 1'))
            print("✅ Connexion à la base de données réussie")
            
            # Lister les tables
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            if tables:
                print(f"\n📋 Tables existantes ({len(tables)}):")
                for table in tables:
                    # Compter les lignes
                    result = db.session.execute(text(f'SELECT COUNT(*) FROM {table}'))
                    count = result.scalar()
                    print(f"   - {table}: {count} lignes")
            else:
                print("\n⚠️ Aucune table trouvée dans la base de données")
                print("   Exécutez init_production_db.py pour initialiser la base")
                
        except Exception as e:
            print(f"\n❌ Erreur de connexion à la base de données:")
            print(f"   {str(e)}")
            return False
    
    return True

if __name__ == "__main__":
    # Permettre de forcer l'environnement via argument
    if len(sys.argv) > 1:
        os.environ['FLASK_ENV'] = sys.argv[1]
    
    check_database()