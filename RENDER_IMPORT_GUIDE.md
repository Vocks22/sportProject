# 📋 Guide d'import pour Render

## Instructions pour importer vos repas dans Render

### Étape 1: Accéder au Shell Render
1. Allez dans votre tableau de bord Render
2. Cliquez sur votre service backend
3. Cliquez sur l'onglet "Shell"

### Étape 2: Naviguer vers le bon répertoire
Dans le shell Render, exécutez ces commandes :

```bash
# Vérifier où vous êtes
pwd

# Lister les fichiers pour voir la structure
ls -la

# Le backend devrait être dans ~/project/src
# Si vous voyez un dossier 'src', naviguez dedans :
cd ~/project/src

# Vérifier que vous avez bien les fichiers Python
ls *.py
```

### Étape 3: Lancer l'import
Une fois dans le bon répertoire, exécutez :

```bash
# Lancer le script d'import
python import_meals_render.py
```

### Résultat attendu
Vous devriez voir :
```
🚀 Import des repas et aliments...
========================================
  ✓ Mis à jour: Petit-déjeuner
  ✓ Mis à jour: Collation du matin
  ✓ Mis à jour: Déjeuner
  ✓ Mis à jour: Collation de l'après-midi
  ✓ Mis à jour: Dîner

✅ Import terminé avec succès!
   - Nouveaux repas: 0
   - Repas mis à jour: 5
   - Total traité: 5

📊 Résumé des calories:
   - Petit-déjeuner: 389 kcal
   - Collation du matin: 316 kcal
   - Déjeuner: 375 kcal
   - Collation de l'après-midi: 310 kcal
   - Dîner: 219 kcal
   - TOTAL JOURNALIER: 1609 kcal
```

## En cas de problème

### Si vous ne trouvez pas le fichier
Le fichier `import_meals_render.py` a été créé dans `/src/backend/`. 
Si vous ne le trouvez pas, c'est qu'il faut d'abord le déployer :

1. Commitez et pushez les changements sur GitHub
2. Render se mettra à jour automatiquement
3. Attendez que le déploiement soit terminé
4. Revenez au Shell et réessayez

### Structure des répertoires dans Render
Typiquement dans Render, votre code est dans :
- `~/project/src/` pour le code backend
- Les fichiers Python sont directement dans ce dossier

### Commandes de diagnostic
Si vous avez des doutes sur l'emplacement :
```bash
# Chercher le fichier main.py
find ~ -name "main.py" 2>/dev/null

# Chercher le fichier d'import
find ~ -name "import_meals_render.py" 2>/dev/null

# Voir la structure complète
ls -la ~/project/
```