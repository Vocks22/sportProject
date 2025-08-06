# 🗄️ Configuration de la Base de Données - DietTracker

## ✅ US1.1 : Configuration Base de Données - COMPLÉTÉ

Cette documentation détaille la configuration complète de la base de données pour DietTracker.

## 📋 Acceptance Criteria Status

- ✅ **SQLite configuré avec migrations Alembic**
  - Configuration Alembic créée (`alembic.ini`)
  - Structure de migrations mise en place
  - Migration initiale créée (`001_initial_schema.py`)

- ✅ **Modèles de données créés et migrés**
  - Modèle User avec authentification
  - Modèle Ingredient avec valeurs nutritionnelles
  - Modèle Recipe avec instructions JSON
  - Modèle MealPlan avec planning hebdomadaire
  - Modèle ShoppingList avec liste de courses

- ✅ **Script d'initialisation des données**
  - `scripts/init_data.py` implémenté
  - Données de base pour 23 ingrédients
  - 7 recettes initiales
  - Utilisateur par défaut (fabien)

- ✅ **Tests de connexion réussis**
  - Script de test créé (`scripts/test_database.py`)
  - Tests CRUD implémentés
  - Validation des relations

- ✅ **Configuration des environnements (dev/prod)**
  - `config/development.env` créé
  - `config/production.env.example` créé
  - `src/backend/database/config.py` avec 3 environnements

## 🏗️ Architecture Implémentée

```
src/backend/
├── database/
│   ├── config.py                 # Configuration multi-environnement
│   └── migrations/
│       ├── env.py                # Configuration Alembic
│       ├── script.py.mako        # Template migrations
│       └── versions/
│           └── 001_initial_schema.py  # Migration initiale
├── models/
│   ├── user.py                  # Modèle utilisateur
│   ├── ingredient.py            # Modèle ingrédient
│   ├── recipe.py                # Modèle recette
│   └── meal_plan.py             # Modèles planning et courses
└── main.py                      # Application Flask avec factory pattern
```

## 🚀 Installation et Configuration

### 1. Prérequis

```bash
# Python 3.9+ requis
python3 --version

# Créer environnement virtuel (optionnel mais recommandé)
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

### 2. Installation des dépendances

```bash
# Installer les dépendances Python
pip install -r requirements.txt
```

### 3. Configuration environnement

```bash
# Copier la configuration de développement
cp config/development.env .env

# Pour la production
cp config/production.env.example config/production.env
# Éditer config/production.env avec vos valeurs
```

### 4. Initialisation de la base de données

```bash
# Créer les tables et insérer les données initiales
python scripts/init_data.py

# Pour réinitialiser complètement
python scripts/init_data.py --reset

# Pour forcer la réinitialisation
python scripts/init_data.py --force
```

### 5. Appliquer les migrations Alembic

```bash
# Vérifier l'état des migrations
alembic current

# Appliquer toutes les migrations
alembic upgrade head

# Créer une nouvelle migration
alembic revision --autogenerate -m "Description"

# Revenir en arrière d'une migration
alembic downgrade -1
```

### 6. Tester la configuration

```bash
# Exécuter les tests de connexion
python scripts/test_database.py
```

## 📊 Schéma de Base de Données

### Tables créées :

#### **users**
- `id` (Integer, PK)
- `username` (String(80), unique)
- `email` (String(120), unique)
- `password_hash` (String(255))
- `current_weight` (Float)
- `target_weight` (Float)
- `height` (Float)
- `age` (Integer)
- `gender` (String(10))
- `activity_level` (String(20))
- `daily_calories_target` (Float, default=1500)
- `daily_protein_target` (Float, default=150)
- `daily_carbs_target` (Float, default=85)
- `daily_fat_target` (Float, default=75)
- `created_at` (DateTime)
- `updated_at` (DateTime)

#### **ingredients**
- `id` (Integer, PK)
- `name` (String(100))
- `category` (String(50))
- `calories_per_100g` (Float)
- `protein_per_100g` (Float)
- `carbs_per_100g` (Float)
- `fat_per_100g` (Float)
- `unit` (String(10), default='g')
- `created_at` (DateTime)

#### **recipes**
- `id` (Integer, PK)
- `name` (String(200))
- `category` (String(50))
- `meal_type` (String(20))
- `ingredients_json` (Text)
- `instructions_json` (Text)
- `prep_time` (Integer)
- `cook_time` (Integer)
- `servings` (Integer, default=1)
- `total_calories` (Float)
- `total_protein` (Float)
- `total_carbs` (Float)
- `total_fat` (Float)
- `utensils_json` (Text)
- `tags_json` (Text)
- `rating` (Float)
- `is_favorite` (Boolean)
- `created_at` (DateTime)
- `updated_at` (DateTime)

#### **meal_plans**
- `id` (Integer, PK)
- `user_id` (String(50))
- `week_start` (Date)
- `meals_json` (Text)
- `daily_calories` (Float)
- `daily_protein` (Float)
- `daily_carbs` (Float)
- `daily_fat` (Float)
- `is_active` (Boolean, default=True)
- `created_at` (DateTime)
- `updated_at` (DateTime)

#### **shopping_lists**
- `id` (Integer, PK)
- `meal_plan_id` (Integer, FK → meal_plans.id)
- `week_start` (Date)
- `items_json` (Text)
- `generated_date` (DateTime)
- `is_completed` (Boolean, default=False)

### Index créés :
- `idx_users_email` sur users.email
- `idx_recipes_category` sur recipes.category
- `idx_recipes_meal_type` sur recipes.meal_type
- `idx_meal_plans_user_id` sur meal_plans.user_id
- `idx_meal_plans_week_start` sur meal_plans.week_start

## 🔧 Configuration Multi-Environnement

### Development
```python
- SQLite local : diettracker_dev.db
- Debug : True
- CORS : localhost:5173, localhost:3000
```

### Testing
```python
- SQLite en mémoire
- Debug : False
- Tests isolés
```

### Production
```python
- PostgreSQL recommandé
- Debug : False
- Variables d'environnement requises
- Logging avancé
```

## 📝 Données Initiales

### Ingrédients (23)
- **Protéines** : Poulet, dinde, cabillaud, sole, blancs d'œuf
- **Légumes** : Brocolis, épinards, haricots verts, courgettes, etc.
- **Fruits** : Ananas, fruits rouges, pamplemousse, etc.
- **Oléagineux** : Noix de cajou, amandes, noix
- **Autres** : Avoine, lait d'amande, huile d'olive, chocolat noir

### Recettes (7)
1. Omelette aux Blancs d'Œufs Classique (repas1)
2. Smoothie Protéiné Classique (collation1)
3. Poulet Grillé aux Brocolis (repas2)
4. Dinde Sautée aux Épinards (repas2)
5. Blancs d'Œufs aux Amandes (collation2)
6. Cabillaud en Papillote (repas3)
7. Sole Grillée à la Salade (repas3)

### Utilisateur par défaut
- Username : fabien
- Email : fabien@diettracker.com
- Objectifs : 1500 kcal/jour, 150g protéines

## ✅ Tests de Validation

Le script `test_database.py` vérifie :
1. ✅ Création des tables
2. ✅ Insertion de données
3. ✅ Lecture des données
4. ✅ Mise à jour des données
5. ✅ Relations entre tables
6. ✅ Comptage des enregistrements
7. ✅ Nettoyage des données test

## 🚦 Status : COMPLÉTÉ

Tous les critères d'acceptation de l'US1.1 sont remplis :
- ✅ Base de données configurée avec SQLAlchemy
- ✅ Migrations Alembic opérationnelles
- ✅ Modèles de données créés
- ✅ Script d'initialisation fonctionnel
- ✅ Configuration multi-environnement
- ✅ Tests de connexion validés

## 📚 Prochaines Étapes

→ Passer à l'US1.2 : API Endpoints Recipes
→ Ou US2.1 : Système d'Authentification JWT

---

*Documentation mise à jour le 6 Août 2025*