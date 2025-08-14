#!/bin/bash
# Script de démarrage intelligent pour le développement

echo "🚀 Démarrage du serveur de développement..."

# Activer l'environnement virtuel
source venv/bin/activate

# Tuer les anciens processus sur le port 5000
echo "🔄 Nettoyage du port 5000..."
pkill -f "python main.py" 2>/dev/null
pkill -f "flask run" 2>/dev/null
lsof -ti:5000 | xargs kill -9 2>/dev/null

# Attendre que le port soit libéré
sleep 1

# Charger les variables d'environnement
export $(cat .env.local | xargs)

# Lancer le serveur
echo "✅ Lancement sur http://localhost:5000"
echo "📝 Logs en temps réel ci-dessous:"
echo "----------------------------------------"

python main.py