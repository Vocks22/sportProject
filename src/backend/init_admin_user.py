#!/usr/bin/env python3
"""
Script pour créer l'utilisateur administrateur
"""
import os
import sys
import getpass
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import db
from models.user import User
from main import create_app


def init_admin_user():
    """Crée ou met à jour l'utilisateur admin"""
    
    app = create_app()
    with app.app_context():
        print("\n🔐 Configuration de l'utilisateur administrateur")
        print("-" * 50)
        
        # Demander les informations
        username = input("Nom d'utilisateur (par défaut: admin): ").strip() or "admin"
        email = input("Email (par défaut: admin@diettracker.com): ").strip() or "admin@diettracker.com"
        
        # Vérifier si l'utilisateur existe déjà
        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()
        
        if existing_user:
            print(f"\n⚠️  L'utilisateur '{existing_user.username}' existe déjà.")
            update = input("Voulez-vous mettre à jour le mot de passe? (o/n): ").lower()
            if update != 'o':
                print("❌ Opération annulée.")
                return
            
            # Demander le nouveau mot de passe
            while True:
                password = getpass.getpass("Nouveau mot de passe (min 8 caractères): ")
                if len(password) < 8:
                    print("❌ Le mot de passe doit faire au moins 8 caractères.")
                    continue
                    
                password_confirm = getpass.getpass("Confirmer le mot de passe: ")
                if password != password_confirm:
                    print("❌ Les mots de passe ne correspondent pas.")
                    continue
                    
                break
            
            existing_user.set_password(password)
            db.session.commit()
            print(f"✅ Mot de passe mis à jour pour '{existing_user.username}'")
            
        else:
            # Créer un nouvel utilisateur
            print("\n📝 Création d'un nouvel utilisateur")
            
            while True:
                password = getpass.getpass("Mot de passe (min 8 caractères): ")
                if len(password) < 8:
                    print("❌ Le mot de passe doit faire au moins 8 caractères.")
                    continue
                    
                password_confirm = getpass.getpass("Confirmer le mot de passe: ")
                if password != password_confirm:
                    print("❌ Les mots de passe ne correspondent pas.")
                    continue
                    
                break
            
            # Créer l'utilisateur
            new_user = User(
                username=username,
                email=email,
                is_active=True
            )
            new_user.set_password(password)
            
            db.session.add(new_user)
            db.session.commit()
            
            print(f"✅ Utilisateur '{username}' créé avec succès!")
        
        print("\n📋 Informations de connexion:")
        print(f"   Username: {username}")
        print(f"   Email: {email}")
        print("\n⚠️  IMPORTANT: Notez ces informations en lieu sûr!")
        print("   Le mot de passe ne peut pas être récupéré, seulement réinitialisé.")


if __name__ == '__main__':
    init_admin_user()