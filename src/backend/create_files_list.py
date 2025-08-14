#!/usr/bin/env python3
"""Créer une liste des fichiers modifiés ou créés aujourd'hui."""

import os
from pathlib import Path
from datetime import datetime

# Fichiers créés/modifiés aujourd'hui
files_created = [
    # Configuration
    "src/backend/.env.local",
    "src/backend/.env.example", 
    "src/frontend/.env.development",
    
    # Scripts
    "src/backend/init_diet_local.py",
    "src/backend/initialize_db.py",
    "src/backend/init_db_on_startup.py",
    "src/backend/start_dev.sh",
    "src/backend/run_dev.sh",
    
    # Configuration VS Code
    ".vscode/launch.json",
    ".vscode/tasks.json",
    
    # Documentation
    "docs/technical/FAST_DEVELOPMENT_WORKFLOW.md",
    "docs/technical/INIT_DATABASE_RENDER.md",
    "docs/technical/user-stories/notes 14-08-2025.md",
    
    # Optimisation
    ".slugignore",
    "src/backend/requirements-prod.txt",
    
    # Modifications
    "src/backend/main.py",
    "src/backend/requirements.txt",
    "src/frontend/components/Dashboard.jsx",
    "render.yaml"
]

print("📝 Fichiers créés/modifiés aujourd'hui (14/08/2025):")
print("=" * 50)

for file in files_created:
    full_path = Path("/mnt/d/vibeCode/GitRepo/sportProject") / file
    if full_path.exists():
        print(f"✅ {file}")
    else:
        print(f"❌ {file} (non trouvé)")

print("\n📊 Total:", len([f for f in files_created if (Path("/mnt/d/vibeCode/GitRepo/sportProject") / f).exists()]), "fichiers")