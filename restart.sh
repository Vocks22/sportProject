#!/bin/bash

echo "🔄 Redémarrage des serveurs..."

# Tuer les processus existants
echo "⏹️ Arrêt des serveurs..."
pkill -f "python main.py" 2>/dev/null || true
pkill -f "vite" 2>/dev/null || true
pkill -f "node.*vite" 2>/dev/null || true
sleep 2

# Démarrer le backend
echo "🚀 Démarrage du backend..."
cd src/backend
./venv/bin/python main.py &
BACKEND_PID=$!
echo "   Backend PID: $BACKEND_PID"

sleep 2

# Démarrer le frontend
echo "🚀 Démarrage du frontend..."
cd ../frontend
npm run dev &
FRONTEND_PID=$!
echo "   Frontend PID: $FRONTEND_PID"

echo "✅ Serveurs démarrés!"
echo ""
echo "📍 URLs:"
echo "   Backend:  http://localhost:5000"
echo "   Frontend: http://localhost:5173"
echo ""
echo "⏹️ Pour arrêter: Ctrl+C ou fermez ce terminal"

# Attendre et gérer l'arrêt propre
trap "echo '⏹️ Arrêt...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
wait