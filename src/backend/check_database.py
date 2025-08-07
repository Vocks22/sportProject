#!/usr/bin/env python3
"""
Script pour vérifier l'état de la base de données
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from flask import Flask
from database import db
from database.config import get_config
from sqlalchemy import text, inspect

def check_database():
    """Vérifie l'état actuel de la base de données"""
    
    # Configuration Flask
    app = Flask(__name__)
    config = get_config('development')
    app.config.from_object(config)
    db.init_app(app)
    
    with app.app_context():
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        print("📊 Tables dans la base de données:")
        for table in tables:
            print(f"\n✅ Table: {table}")
            columns = inspector.get_columns(table)
            print(f"   Colonnes ({len(columns)}):")
            for col in columns[:10]:  # Afficher max 10 colonnes
                print(f"     - {col['name']}: {col['type']}")
            if len(columns) > 10:
                print(f"     ... et {len(columns) - 10} autres colonnes")
            
            # Compter les lignes
            try:
                result = db.session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar()
                print(f"   Nombre de lignes: {count}")
            except:
                pass

if __name__ == '__main__':
    try:
        check_database()
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)