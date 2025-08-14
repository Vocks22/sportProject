# 📋 Synchroniser les aliments avec la production

## Méthode 1: Import automatique (Recommandé)

### Étape 1: Dans Render Shell
```bash
# Se connecter au shell Render
# Aller dans votre service backend > Shell

# Télécharger le fichier de configuration
cat > meals_production.json << 'EOF'
# Coller ici le contenu du fichier meals_production.json
EOF

# Importer la configuration
python export_meals_config.py import < meals_production.json
```

## Méthode 2: Via l'interface admin

1. Allez sur https://diettracker.netlify.app/diet-admin
2. Pour chaque repas, cliquez sur 🍴
3. Recréez manuellement les aliments selon votre configuration locale

## Configuration actuelle à copier

Le fichier `meals_production.json` contient votre configuration actuelle avec :
- Les 5-6 repas configurés
- Les horaires personnalisés
- Tous les aliments avec leurs quantités et calories

## Vérification

Après la synchronisation, vérifiez sur https://diettracker.netlify.app/ que :
- Les repas s'affichent dans le bon ordre
- Les aliments sont présents
- Les calories sont calculées correctement

## Notes

- Les aliments personnalisés (créés via "Ajouter un aliment") sont stockés localement dans le navigateur
- Pour les synchroniser, exportez-les depuis le localStorage et importez-les sur l'autre navigateur
- La configuration des repas et aliments de base est stockée dans la base de données