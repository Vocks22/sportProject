#!/usr/bin/env python3
"""
Script simple pour créer l'utilisateur admin
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import db
from models.user import User
from main import create_app

def create_admin():
    app = create_app()
    with app.app_context():
        # Créer les tables si elles n'existent pas
        db.create_all()
        
        # Vérifier si l'utilisateur admin existe
        admin = User.query.filter_by(username='admin').first()
        
        if admin:
            print('✅ Utilisateur admin existe déjà')
            print('   Mise à jour du mot de passe...')
            admin.set_password('admin123')
            db.session.commit()
            print('✅ Mot de passe mis à jour')
        else:
            # Créer l'utilisateur admin
            admin = User(
                username='admin',
                email='admin@diettracker.com',
                is_active=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print('✅ Utilisateur admin créé avec succès!')
        
        print('\n📋 Informations de connexion:')
        print('   Username: admin')
        print('   Password: admin123')
        print('\n⚠️  IMPORTANT: Changez ce mot de passe en production!')

if __name__ == '__main__':
    create_admin()