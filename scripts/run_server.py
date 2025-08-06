#!/usr/bin/env python3
"""
Script pour lancer le serveur Flask DietTracker
"""

import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).resolve().parents[1] / 'src' / 'backend'
sys.path.insert(0, str(backend_path))

from main import app

if __name__ == '__main__':
    print("🚀 Démarrage du serveur DietTracker...")
    print("📍 URL: http://localhost:5000")
    print("📍 API: http://localhost:5000/api")
    print("🛑 Appuyez sur Ctrl+C pour arrêter")
    
    # Run without debug to avoid reloading issues
    app.run(host='0.0.0.0', port=5000, debug=False)