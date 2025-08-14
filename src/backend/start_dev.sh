#!/bin/bash
# Script de développement rapide avec base Render

echo "🚀 Démarrage du serveur de développement..."
echo "----------------------------------------"

# Charger les variables d'environnement
if [ -f .env.local ]; then
    echo "✅ Chargement de .env.local"
    export $(cat .env.local | xargs)
elif [ -f .env ]; then
    echo "✅ Chargement de .env"
    export $(cat .env | xargs)
else
    echo "⚠️  Pas de fichier .env trouvé"
    echo "Créez .env.local avec DATABASE_URL de Render"
    exit 1
fi

# Vérifier la connexion à la base
echo "🔍 Test de connexion à la base de données..."
python -c "
from database import db
from main import create_app
app = create_app()
with app.app_context():
    try:
        db.engine.connect()
        print('✅ Connexion à la base réussie')
    except Exception as e:
        print(f'❌ Erreur de connexion: {e}')
        exit(1)
"

# Initialiser la base si nécessaire
echo "📝 Vérification/Initialisation de la base..."
python initialize_db.py

# Lancer le serveur Flask en mode debug
echo "----------------------------------------"
echo "🎉 Serveur lancé sur http://localhost:5000"
echo "🔄 Rechargement automatique activé"
echo "📝 Logs en temps réel ci-dessous:"
echo "----------------------------------------"

# Lancer Flask avec rechargement automatique
python -m flask run --host=0.0.0.0 --port=5000 --reload --debug