#!/bin/bash

# 🚀 Script de setup pour DietTracker
# Ce script installe toutes les dépendances nécessaires

echo "========================================="
echo "🚀 SETUP DIETTRACKER"
echo "========================================="

# Vérifier Python
echo "📌 Vérification de Python..."
python3 --version
if [ $? -ne 0 ]; then
    echo "❌ Python 3 n'est pas installé"
    echo "Installez Python 3.9+ depuis https://www.python.org"
    exit 1
fi

# Installer pip si nécessaire
echo "📌 Vérification de pip..."
python3 -m pip --version
if [ $? -ne 0 ]; then
    echo "⚠️ pip n'est pas installé"
    echo "Installation de pip..."
    
    # Sur Ubuntu/Debian
    if command -v apt-get &> /dev/null; then
        echo "Système Debian/Ubuntu détecté"
        echo "Exécutez: sudo apt-get update && sudo apt-get install python3-pip python3.12-venv"
    fi
    
    # Sur macOS
    if command -v brew &> /dev/null; then
        echo "Système macOS détecté"
        echo "Exécutez: brew install python3"
    fi
    
    # Sur Windows (WSL)
    echo "Pour Windows/WSL, installez python3-pip avec:"
    echo "sudo apt update && sudo apt install python3-pip python3-venv"
    
    exit 1
fi

# Créer environnement virtuel
echo "📌 Création de l'environnement virtuel..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "❌ Impossible de créer l'environnement virtuel"
    echo "Installez python3-venv: sudo apt install python3.12-venv"
    exit 1
fi

# Activer environnement virtuel
echo "📌 Activation de l'environnement virtuel..."
source venv/bin/activate

# Installer les dépendances Python
echo "📌 Installation des dépendances Python..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "========================================="
echo "✅ SETUP TERMINÉ AVEC SUCCÈS!"
echo "========================================="
echo ""
echo "Prochaines étapes:"
echo "1. Activer l'environnement: source venv/bin/activate"
echo "2. Initialiser la DB: python scripts/init_data.py"
echo "3. Lancer le serveur: cd src/backend && python main.py"
echo ""