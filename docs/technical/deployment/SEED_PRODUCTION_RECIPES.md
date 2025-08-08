# 📚 Guide de déploiement des 65 recettes en production

## 🎯 Objectif
Déployer les 65 recettes avec mode chef dans la base de données de production sur Render.

## 📍 État actuel
- **Local (dev)** : ✅ 65 recettes créées et fonctionnelles
- **Production (Render)** : ❌ Seulement 2 recettes de test

## 🚀 Méthodes de déploiement

### Méthode 1 : Via Render Shell (Recommandée)

1. **Connexion au dashboard Render**
   - Aller sur https://dashboard.render.com
   - Sélectionner votre service backend

2. **Ouvrir la console Shell**
   - Cliquer sur "Shell" dans le menu du service
   - Attendre le chargement de la console

3. **Exécuter le script de seeding**
   ```bash
   cd src/backend
   python seed_recipes.py
   ```

4. **Vérification**
   - Le script affichera :
     - Nombre de recettes existantes
     - Création des ingrédients
     - Progression de création des recettes
     - Statistiques finales

### Méthode 2 : Depuis votre machine locale

1. **Récupérer l'URL de la base de données**
   - Dashboard Render → Service → Environment → DATABASE_URL
   - Copier la valeur complète

2. **Exécuter localement avec la DB de production**
   ```bash
   # Linux/Mac
   export DATABASE_URL="postgresql://user:password@host/database"
   
   # Windows PowerShell
   $env:DATABASE_URL="postgresql://user:password@host/database"
   
   # Exécuter le script
   cd src/backend
   python seed_recipes.py
   ```

### Méthode 3 : Via GitHub Actions (Automatique)

Créer `.github/workflows/seed-production.yml` :
```yaml
name: Seed Production Database

on:
  workflow_dispatch:  # Déclenchement manuel

jobs:
  seed:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: |
          pip install -r src/backend/requirements.txt
      - name: Seed database
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
        run: |
          cd src/backend
          python seed_recipes.py
```

## ✅ Validation post-déploiement

1. **Vérifier via l'API**
   ```bash
   curl https://diettracker-backend.onrender.com/api/recipes
   ```
   - Devrait retourner `"total": 65`

2. **Vérifier dans l'application**
   - Ouvrir https://diettracker-web.netlify.app
   - Aller dans la section "Recettes"
   - Vérifier la présence des 65 recettes

3. **Vérifier le mode chef**
   ```bash
   curl "https://diettracker-backend.onrender.com/api/recipes?has_chef_mode=true"
   ```
   - Devrait retourner 20 recettes avec mode chef

## 📊 Résultats attendus

Après exécution du script :
- **65 recettes** totales créées
- **52 ingrédients** dans la base
- **20 recettes** avec mode chef complet
- Répartition :
  - 15 petits-déjeuners (repas1)
  - 10 smoothies (collation1)
  - 15 déjeuners (repas2)
  - 10 collations (collation2)
  - 15 dîners (repas3)

## ⚠️ Notes importantes

1. **Backup** : Les recettes existantes seront remplacées
2. **Temps d'exécution** : ~30 secondes
3. **Idempotent** : Le script peut être exécuté plusieurs fois sans problème
4. **Mode production** : En production, le script ne demande pas de confirmation

## 🔧 Troubleshooting

### Erreur de connexion à la base
- Vérifier que DATABASE_URL est correctement définie
- Vérifier que l'IP est autorisée sur Render

### Erreur de module manquant
```bash
pip install -r requirements.txt
```

### Les recettes n'apparaissent pas dans l'app
- Vider le cache du navigateur
- Vérifier que le backend est bien redéployé
- Vérifier les logs Render pour les erreurs

## 📝 Script utilisé
Le script `src/backend/seed_recipes.py` :
- Détecte automatiquement l'environnement (dev/prod)
- Crée les ingrédients nécessaires
- Insère les 65 recettes avec toutes leurs données
- Gère le mode chef pour 20 recettes
- Affiche des statistiques de progression