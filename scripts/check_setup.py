#!/usr/bin/env python3
"""
Script de vérification de l'installation DietTracker
Peut être exécuté SANS les dépendances installées
"""

import sys
import os
from pathlib import Path

def check_python_version():
    """Vérifier la version de Python"""
    print("🔍 Vérification de Python...")
    version = sys.version_info
    print(f"   Version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print("   ❌ Python 3.9+ requis")
        return False
    print("   ✅ Version Python OK")
    return True

def check_project_structure():
    """Vérifier la structure du projet"""
    print("\n🔍 Vérification de la structure du projet...")
    
    required_dirs = [
        'src/backend',
        'src/backend/models',
        'src/backend/routes',
        'src/backend/database',
        'src/frontend',
        'src/frontend/components',
        'scripts',
        'config',
        'docs'
    ]
    
    project_root = Path(__file__).resolve().parents[1]
    all_good = True
    
    for dir_path in required_dirs:
        full_path = project_root / dir_path
        if full_path.exists():
            print(f"   ✅ {dir_path}")
        else:
            print(f"   ❌ {dir_path} manquant")
            all_good = False
    
    return all_good

def check_config_files():
    """Vérifier les fichiers de configuration"""
    print("\n🔍 Vérification des fichiers de configuration...")
    
    required_files = [
        'requirements.txt',
        'package.json',
        'alembic.ini',
        'config/development.env',
        'src/backend/main.py',
        'scripts/init_data.py'
    ]
    
    project_root = Path(__file__).resolve().parents[1]
    all_good = True
    
    for file_path in required_files:
        full_path = project_root / file_path
        if full_path.exists():
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} manquant")
            all_good = False
    
    return all_good

def check_dependencies():
    """Vérifier si les dépendances peuvent être installées"""
    print("\n🔍 Vérification des modules Python...")
    
    try:
        import pip
        print("   ✅ pip disponible")
    except ImportError:
        print("   ❌ pip non disponible - installez python3-pip")
        return False
    
    # Vérifier si les modules sont installés
    modules_to_check = [
        ('flask', 'Flask'),
        ('sqlalchemy', 'SQLAlchemy'),
        ('alembic', 'Alembic'),
        ('flask_cors', 'Flask-CORS')
    ]
    
    installed = []
    missing = []
    
    for module_name, display_name in modules_to_check:
        try:
            __import__(module_name)
            installed.append(display_name)
        except ImportError:
            missing.append(display_name)
    
    if installed:
        print(f"   ✅ Modules installés: {', '.join(installed)}")
    if missing:
        print(f"   ⚠️ Modules manquants: {', '.join(missing)}")
        print("   → Exécutez: pip install -r requirements.txt")
    
    return len(missing) == 0

def check_database():
    """Vérifier si la base de données peut être créée"""
    print("\n🔍 Vérification de SQLite...")
    
    try:
        import sqlite3
        version = sqlite3.sqlite_version
        print(f"   ✅ SQLite disponible (version {version})")
        
        # Tester la création d'une DB temporaire
        test_db = Path(__file__).resolve().parents[1] / 'test_db.sqlite'
        conn = sqlite3.connect(str(test_db))
        conn.execute("CREATE TABLE test (id INTEGER PRIMARY KEY)")
        conn.close()
        test_db.unlink()  # Supprimer le fichier test
        print("   ✅ Création de base de données OK")
        return True
    except Exception as e:
        print(f"   ❌ Erreur SQLite: {e}")
        return False

def main():
    """Fonction principale"""
    print("="*50)
    print("🏥 DIAGNOSTIC D'INSTALLATION - DIETTRACKER")
    print("="*50)
    
    checks = {
        "Python": check_python_version(),
        "Structure": check_project_structure(),
        "Config": check_config_files(),
        "Database": check_database(),
        "Dependencies": check_dependencies()
    }
    
    print("\n" + "="*50)
    print("📊 RÉSUMÉ")
    print("="*50)
    
    all_passed = all(checks.values())
    
    for check_name, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"{status} {check_name}")
    
    print("\n" + "="*50)
    
    if all_passed:
        print("🎉 TOUT EST OK! Vous pouvez lancer l'application")
        print("\nCommandes à exécuter:")
        print("1. python scripts/init_data.py")
        print("2. cd src/backend && python main.py")
    else:
        print("⚠️ INSTALLATION INCOMPLÈTE")
        print("\nActions requises:")
        
        if not checks["Python"]:
            print("1. Installez Python 3.9+")
        
        if not checks["Dependencies"]:
            print("2. Installez les dépendances:")
            print("   - Linux/Mac: pip3 install -r requirements.txt")
            print("   - Windows: pip install -r requirements.txt")
        
        if not checks["Structure"] or not checks["Config"]:
            print("3. Vérifiez que tous les fichiers sont présents")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())