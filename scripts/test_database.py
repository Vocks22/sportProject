#!/usr/bin/env python3
"""
Script de test de la connexion et des modèles de base de données
"""

import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).resolve().parents[1] / 'src' / 'backend'
sys.path.insert(0, str(backend_path))

from flask import Flask
from models.user import db, User
from models.ingredient import Ingredient
from models.recipe import Recipe
from models.meal_plan import MealPlan
from database.config import get_config

def test_connection():
    """Test database connection and basic operations"""
    print("🔧 Test de connexion à la base de données...")
    
    # Create app with test configuration
    app = Flask(__name__)
    config = get_config('development')
    app.config.from_object(config)
    db.init_app(app)
    
    with app.app_context():
        try:
            # Test 1: Create tables
            print("\n1️⃣ Création des tables...")
            db.create_all()
            print("   ✅ Tables créées avec succès")
            
            # Test 2: Insert test data
            print("\n2️⃣ Insertion de données test...")
            
            # Create test ingredient
            test_ingredient = Ingredient(
                name="Test Ingredient",
                category="test",
                calories_per_100g=100,
                protein_per_100g=10,
                carbs_per_100g=20,
                fat_per_100g=5,
                unit="g"
            )
            db.session.add(test_ingredient)
            db.session.commit()
            print("   ✅ Ingrédient test créé")
            
            # Test 3: Query data
            print("\n3️⃣ Lecture des données...")
            ingredient = Ingredient.query.filter_by(name="Test Ingredient").first()
            if ingredient:
                print(f"   ✅ Ingrédient trouvé: {ingredient.name}")
                print(f"      - Catégorie: {ingredient.category}")
                print(f"      - Calories/100g: {ingredient.calories_per_100g}")
            
            # Test 4: Update data
            print("\n4️⃣ Mise à jour des données...")
            ingredient.calories_per_100g = 150
            db.session.commit()
            print("   ✅ Données mises à jour")
            
            # Test 5: Check relationships
            print("\n5️⃣ Test des relations...")
            test_user = User(
                username="test_user",
                email="test@diettracker.com"
            )
            db.session.add(test_user)
            db.session.commit()
            print("   ✅ Utilisateur test créé")
            
            # Test 6: Count records
            print("\n6️⃣ Comptage des enregistrements...")
            print(f"   - Ingrédients: {Ingredient.query.count()}")
            print(f"   - Utilisateurs: {User.query.count()}")
            print(f"   - Recettes: {Recipe.query.count()}")
            print(f"   - Plans de repas: {MealPlan.query.count()}")
            
            # Test 7: Clean up test data
            print("\n7️⃣ Nettoyage des données test...")
            db.session.delete(ingredient)
            db.session.delete(test_user)
            db.session.commit()
            print("   ✅ Données test supprimées")
            
            print("\n" + "="*50)
            print("🎉 TOUS LES TESTS RÉUSSIS!")
            print("="*50)
            print("\n📊 Configuration utilisée:")
            print(f"   - Base de données: {config.SQLALCHEMY_DATABASE_URI}")
            print(f"   - Environment: {config.FLASK_ENV if hasattr(config, 'FLASK_ENV') else 'development'}")
            
            return True
            
        except Exception as e:
            print(f"\n❌ ERREUR: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

def test_alembic():
    """Test Alembic migrations"""
    print("\n🔄 Test des migrations Alembic...")
    
    try:
        import subprocess
        from pathlib import Path
        
        project_root = Path(__file__).resolve().parents[1]
        
        # Check if alembic.ini exists
        alembic_ini = project_root / 'alembic.ini'
        if not alembic_ini.exists():
            print("   ⚠️ alembic.ini non trouvé")
            return False
        
        print("   ✅ Configuration Alembic trouvée")
        
        # Check migrations folder
        migrations_dir = project_root / 'src' / 'backend' / 'database' / 'migrations'
        if migrations_dir.exists():
            print(f"   ✅ Dossier migrations existe: {migrations_dir}")
            
            # Count migration files
            versions_dir = migrations_dir / 'versions'
            if versions_dir.exists():
                migration_files = list(versions_dir.glob('*.py'))
                print(f"   ✅ {len(migration_files)} fichier(s) de migration trouvé(s)")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erreur: {str(e)}")
        return False

if __name__ == '__main__':
    print("="*50)
    print("🧪 TEST DE LA CONFIGURATION BASE DE DONNÉES")
    print("="*50)
    
    # Test database connection
    db_test_passed = test_connection()
    
    # Test Alembic setup
    alembic_test_passed = test_alembic()
    
    # Summary
    print("\n" + "="*50)
    print("📋 RÉSUMÉ DES TESTS")
    print("="*50)
    print(f"✅ Connexion DB: {'RÉUSSI' if db_test_passed else 'ÉCHOUÉ'}")
    print(f"✅ Configuration Alembic: {'RÉUSSI' if alembic_test_passed else 'ÉCHOUÉ'}")
    
    if db_test_passed and alembic_test_passed:
        print("\n🎊 Tous les tests sont passés avec succès!")
        print("\nProchaines étapes:")
        print("1. Exécuter: python scripts/init_data.py")
        print("2. Lancer le serveur: cd src/backend && python main.py")
    else:
        print("\n⚠️ Certains tests ont échoué. Vérifiez la configuration.")