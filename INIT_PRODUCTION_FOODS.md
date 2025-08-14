# Instructions pour initialiser les aliments en production

## Méthode 1: Via l'interface Admin (Recommandé)

1. Allez sur https://diettracker.netlify.app/diet-admin
2. Pour chaque repas, cliquez sur l'icône 🍴 (ChefHat)
3. Ajoutez les aliments un par un avec leurs quantités

## Méthode 2: Via la console Render Shell

1. Allez sur le dashboard Render
2. Ouvrez votre service backend (diettracker-backend)
3. Cliquez sur "Shell" dans le menu de gauche
4. Copiez-collez ces commandes une par une :

```python
# 1. Entrer dans Python
python

# 2. Importer les modules nécessaires
from models.diet_program import DietProgram
from database import db

# 3. Définir les aliments
foods_by_type = {
    "repas1": [
        {"name": "Blanc d'œuf", "quantity": "150", "unit": "g"},
        {"name": "Flocons d'avoine", "quantity": "80", "unit": "g"},
        {"name": "Myrtilles", "quantity": "100", "unit": "g"},
        {"name": "Amandes", "quantity": "20", "unit": "g"},
        {"name": "Banane", "quantity": "1", "unit": "unité"},
        {"name": "Miel", "quantity": "1", "unit": "c.à.s"}
    ],
    "collation1": [
        {"name": "Shaker protéiné", "quantity": "30", "unit": "g"},
        {"name": "Pomme", "quantity": "1", "unit": "unité"},
        {"name": "Noix", "quantity": "30", "unit": "g"},
        {"name": "Eau", "quantity": "500", "unit": "ml"}
    ],
    "repas2": [
        {"name": "Poulet grillé", "quantity": "200", "unit": "g"},
        {"name": "Riz basmati", "quantity": "150", "unit": "g cuit"},
        {"name": "Brocoli", "quantity": "200", "unit": "g"},
        {"name": "Huile d'olive", "quantity": "1", "unit": "c.à.s"},
        {"name": "Salade verte", "quantity": "100", "unit": "g"}
    ],
    "collation2": [
        {"name": "Yaourt grec", "quantity": "150", "unit": "g"},
        {"name": "Fruits rouges", "quantity": "100", "unit": "g"},
        {"name": "Granola", "quantity": "30", "unit": "g"}
    ],
    "repas3": [
        {"name": "Saumon", "quantity": "180", "unit": "g"},
        {"name": "Patate douce", "quantity": "200", "unit": "g"},
        {"name": "Asperges", "quantity": "150", "unit": "g"},
        {"name": "Avocat", "quantity": "1/2", "unit": "unité"}
    ]
}

# 4. Mettre à jour les repas
meals = DietProgram.query.all()
for meal in meals:
    if meal.meal_type in foods_by_type:
        meal.foods = foods_by_type[meal.meal_type]
        print(f"✅ {meal.meal_name}: {len(meal.foods)} aliments")

# 5. Sauvegarder
db.session.commit()
print("🎉 Aliments ajoutés avec succès!")

# 6. Vérifier
for meal in DietProgram.query.order_by(DietProgram.order_index).all():
    print(f"{meal.meal_name}: {len(meal.foods or [])} aliments")

# 7. Quitter Python
exit()
```

## Méthode 3: Script automatique (si disponible)

Si le fichier `init_foods_production.py` est déployé :

```bash
python init_foods_production.py
```

## Vérification

Après l'initialisation, allez sur :
- https://diettracker.netlify.app/ pour voir les aliments dans le dashboard
- https://diettracker.netlify.app/diet-admin pour gérer les aliments

## Notes

- Les aliments sont stockés en JSON dans la colonne `foods` de chaque repas
- Vous pouvez modifier les aliments à tout moment via l'interface admin
- Les quantités peuvent être ajustées selon vos besoins