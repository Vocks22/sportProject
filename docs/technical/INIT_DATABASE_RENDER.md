# Guide d'Initialisation de la Base de Données sur Render

## État Actuel du Déploiement

✅ **Backend**: Opérationnel sur https://diettracker-backend.onrender.com
✅ **Frontend**: Déployé sur https://diettracker-front.netlify.app
✅ **API**: Les endpoints répondent correctement
⏳ **Données**: Base de données vide - initialisation requise

## Analyse des Logs

Les logs montrent que le backend fonctionne correctement:
- `GET /api/diet/today` retourne `200` avec des données vides
- `GET /api/diet/stats` retourne `200` avec statistiques à zéro
- Tables créées avec succès: `✅ Tables de base de données créées/vérifiées`

## Étapes d'Initialisation

### 1. Accéder à la Console Shell de Render

1. Connectez-vous à votre dashboard Render
2. Sélectionnez votre service `diettracker-backend`
3. Cliquez sur l'onglet "Shell" dans le menu latéral
4. Cliquez sur "Connect" pour ouvrir un terminal

### 2. Naviguer vers le Backend

```bash
cd src/backend
```

### 3. Exécuter les Scripts d'Initialisation

#### Option A: Initialisation Complète (Recommandée)

```bash
# 1. Appliquer les migrations pour les tables diet
python migrations/add_diet_tracking.py

# 2. Initialiser le programme diététique avec les 5 repas quotidiens
python scripts/init_diet_program.py

# 3. (Optionnel) Ajouter des données de test
python scripts/seed_production.py
```

#### Option B: Script Rapide Tout-en-Un

```bash
# Créer et exécuter un script d'initialisation rapide
cat > init_all.py << 'EOF'
import sys
import os
sys.path.insert(0, '/opt/render/project/src/src/backend')

from database import db
from main import create_app
from models.diet_program import DietProgram, DietMeal, DietMealFood
from models.food import Food
from datetime import datetime

app = create_app()

with app.app_context():
    # Créer les tables si elles n'existent pas
    db.create_all()
    print("✅ Tables créées/vérifiées")
    
    # Vérifier si un programme existe déjà
    existing = DietProgram.query.filter_by(user_id=1, is_active=True).first()
    if existing:
        print("⚠️ Programme déjà existant")
    else:
        # Créer le programme diététique
        program = DietProgram(
            user_id=1,
            name="Programme Prise de Masse",
            description="Programme diététique structuré en 5 repas",
            start_date=datetime.now().date(),
            is_active=True,
            daily_calories_target=3000,
            daily_protein_target=150,
            daily_carbs_target=400,
            daily_fat_target=100
        )
        db.session.add(program)
        db.session.commit()
        print(f"✅ Programme créé: {program.name}")
        
        # Définir les 5 repas
        meals_data = [
            {"name": "Repas 1 - Petit-déjeuner", "time": "07:00", "order": 1},
            {"name": "Repas 2 - Collation matin", "time": "10:00", "order": 2},
            {"name": "Repas 3 - Déjeuner", "time": "12:30", "order": 3},
            {"name": "Repas 4 - Collation après-midi", "time": "16:00", "order": 4},
            {"name": "Repas 5 - Dîner", "time": "19:30", "order": 5}
        ]
        
        for meal_data in meals_data:
            meal = DietMeal(
                program_id=program.id,
                name=meal_data["name"],
                meal_time=meal_data["time"],
                meal_order=meal_data["order"]
            )
            db.session.add(meal)
            print(f"  ✅ Repas ajouté: {meal.name}")
        
        db.session.commit()
        print("\n🎉 Initialisation complète!")

EOF

python init_all.py
```

### 4. Vérifier l'Initialisation

```bash
# Vérifier que les données sont présentes
python -c "
from database import db
from main import create_app
from models.diet_program import DietProgram

app = create_app()
with app.app_context():
    program = DietProgram.query.filter_by(user_id=1, is_active=True).first()
    if program:
        print(f'✅ Programme actif: {program.name}')
        print(f'   Repas configurés: {len(program.meals)}')
    else:
        print('❌ Aucun programme trouvé')
"
```

## Vérification dans le Frontend

Après l'initialisation:

1. Ouvrez https://diettracker-front.netlify.app
2. Naviguez vers la section "Suivi Diététique"
3. Vous devriez voir:
   - Les 5 repas quotidiens listés
   - Les horaires configurés
   - La possibilité d'ajouter des aliments

## Dépannage

### Si les données ne s'affichent pas:

1. **Vider le cache du navigateur**:
   - Ctrl+Shift+R (Windows/Linux) ou Cmd+Shift+R (Mac)

2. **Vérifier les endpoints API**:
   ```bash
   curl https://diettracker-backend.onrender.com/api/diet/today
   ```
   
   Réponse attendue après initialisation:
   ```json
   {
     "program": {
       "name": "Programme Prise de Masse",
       "daily_calories_target": 3000
     },
     "meals": [
       {"name": "Repas 1 - Petit-déjeuner", "time": "07:00"},
       ...
     ]
   }
   ```

3. **Vérifier les logs en temps réel**:
   - Dashboard Render > Logs
   - Rechercher les erreurs après rafraîchissement

### Si l'initialisation échoue:

1. **Problème de permissions**:
   ```bash
   export PYTHONPATH=/opt/render/project/src/src/backend
   python scripts/init_diet_program.py
   ```

2. **Tables manquantes**:
   ```bash
   python -c "from database import db; from main import create_app; app = create_app(); app.app_context().push(); db.create_all()"
   ```

## Notes Importantes

- Les scripts d'initialisation sont idempotents (peuvent être exécutés plusieurs fois)
- Le programme est créé pour l'utilisateur ID=1 par défaut
- Les horaires des repas peuvent être modifiés dans le script avant exécution
- La base PostgreSQL persiste les données entre les redéploiements

## Prochaines Étapes

Une fois l'initialisation réussie:
1. Tester l'ajout d'aliments via l'interface
2. Vérifier le calcul des macros
3. Tester la fonctionnalité de suivi quotidien
4. Configurer les aliments favoris dans la base