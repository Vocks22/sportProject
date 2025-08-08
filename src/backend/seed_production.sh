#!/bin/bash

# Script pour seeder la base de données de production
# À exécuter après déploiement sur Render

echo "🚀 Seeding production database with 65 recipes..."
echo "================================================"

# Le script détecte automatiquement l'environnement production via DATABASE_URL
python src/backend/seed_recipes.py

echo "✅ Production seeding completed!"