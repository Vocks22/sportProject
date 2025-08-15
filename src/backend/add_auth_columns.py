#!/usr/bin/env python3
"""
Script pour ajouter les colonnes d'authentification à la table users existante
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import db
from main import create_app
from sqlalchemy import text

def add_auth_columns():
    app = create_app()
    with app.app_context():
        try:
            # Ajouter les colonnes manquantes
            with db.engine.connect() as conn:
                # Vérifier si les colonnes existent déjà
                result = conn.execute(text("PRAGMA table_info(users)"))
                columns = [row[1] for row in result]
                
                if 'password_hash' not in columns:
                    print("Ajout de la colonne password_hash...")
                    conn.execute(text("ALTER TABLE users ADD COLUMN password_hash VARCHAR(255)"))
                    conn.commit()
                    print("✅ Colonne password_hash ajoutée")
                else:
                    print("✅ Colonne password_hash existe déjà")
                
                if 'is_active' not in columns:
                    print("Ajout de la colonne is_active...")
                    conn.execute(text("ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT 1"))
                    conn.commit()
                    print("✅ Colonne is_active ajoutée")
                else:
                    print("✅ Colonne is_active existe déjà")
                    
                if 'last_login' not in columns:
                    print("Ajout de la colonne last_login...")
                    conn.execute(text("ALTER TABLE users ADD COLUMN last_login DATETIME"))
                    conn.commit()
                    print("✅ Colonne last_login ajoutée")
                else:
                    print("✅ Colonne last_login existe déjà")
                
            print("\n✅ Migration terminée avec succès!")
            
        except Exception as e:
            print(f"❌ Erreur lors de la migration: {e}")
            raise

if __name__ == '__main__':
    add_auth_columns()