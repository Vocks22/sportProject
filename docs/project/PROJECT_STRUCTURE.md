# 📁 Structure du Projet DietTracker

## Vue d'ensemble de l'architecture

```
diettracker/
├── 📄 README.md                    # Documentation principale
├── 📄 LICENSE                      # Licence MIT
├── 📄 .gitignore                   # Fichiers ignorés par Git
├── 📄 package.json                 # Dépendances Node.js
├── 📄 requirements.txt             # Dépendances Python
├── 📄 PROJECT_STRUCTURE.md         # Ce fichier
│
├── 📁 config/                      # Configuration
│   ├── 📄 development.env          # Variables d'environnement dev
│   └── 📄 production.env.example   # Template pour production
│
├── 📁 src/                         # Code source
│   ├── 📁 frontend/                # Application React
│   │   ├── 📄 App.jsx             # Composant racine
│   │   ├── 📁 components/         # Composants réutilisables
│   │   │   ├── 📄 Dashboard.jsx
│   │   │   ├── 📄 Header.jsx
│   │   │   ├── 📄 Sidebar.jsx
│   │   │   ├── 📄 MealPlanning.jsx
│   │   │   ├── 📄 Recipes.jsx
│   │   │   ├── 📄 Shopping.jsx
│   │   │   ├── 📄 Progress.jsx
│   │   │   └── 📄 Mobile*.jsx    # Composants mobile
│   │   ├── 📁 pages/              # Pages complètes
│   │   ├── 📁 hooks/              # Custom React hooks
│   │   ├── 📁 utils/              # Fonctions utilitaires
│   │   ├── 📁 styles/             # CSS et styles
│   │   └── 📁 assets/             # Images et médias
│   │
│   └── 📁 backend/                 # API Flask
│       ├── 📄 main.py             # Point d'entrée Flask
│       ├── 📁 models/             # Modèles de données
│       │   ├── 📄 user.py
│       │   ├── 📄 recipe.py
│       │   ├── 📄 ingredient.py
│       │   └── 📄 meal_plan.py
│       ├── 📁 routes/             # Endpoints API
│       │   ├── 📄 recipes.py
│       │   ├── 📄 ingredients.py
│       │   └── 📄 meal_plans.py
│       ├── 📁 services/           # Logique métier
│       ├── 📁 utils/              # Utilitaires backend
│       └── 📁 database/           # Config et migrations
│
├── 📁 docs/                        # Documentation
│   ├── 📁 technical/              # Docs techniques
│   │   ├── 📄 documentation_technique.md
│   │   ├── 📄 architecture_application.md
│   │   ├── 📄 evaluation_diettracker.md
│   │   └── 📄 plan_action_scrum_diettracker.md
│   ├── 📁 user/                   # Guides utilisateur
│   │   ├── 📄 DietTracker - Guide Utilisateur.md
│   │   ├── 📄 analyse_diete.md
│   │   └── 📄 Bibliothèque*.md
│   └── 📁 api/                    # Documentation API
│
├── 📁 tests/                       # Tests
│   ├── 📁 frontend/               # Tests React
│   ├── 📁 backend/                # Tests Python
│   └── 📁 e2e/                    # Tests end-to-end
│
├── 📁 scripts/                     # Scripts utilitaires
│   ├── 📄 init_data.py           # Initialisation DB
│   └── 📄 init_simple.py         # Init simplifiée
│
└── 📁 public/                      # Fichiers publics
    └── 📄 index.html              # HTML principal
```

## 🏗️ Description des dossiers

### `/src/frontend` - Application React
Contient tout le code de l'interface utilisateur :
- **components/** : Composants React réutilisables
- **pages/** : Pages complètes de l'application
- **hooks/** : Custom hooks pour la logique réutilisable
- **utils/** : Fonctions helper et utilitaires
- **styles/** : Fichiers CSS et configuration Tailwind
- **assets/** : Images, icônes et fichiers médias

### `/src/backend` - API Flask
Backend Python avec Flask :
- **models/** : Modèles SQLAlchemy pour la base de données
- **routes/** : Endpoints API RESTful
- **services/** : Logique métier et services
- **utils/** : Fonctions utilitaires backend
- **database/** : Configuration DB et migrations Alembic

### `/docs` - Documentation
Documentation complète du projet :
- **technical/** : Architecture, spécifications techniques
- **user/** : Guides et manuels utilisateur
- **api/** : Documentation des endpoints API

### `/tests` - Tests automatisés
- **frontend/** : Tests unitaires React (Jest, RTL)
- **backend/** : Tests unitaires Python (pytest)
- **e2e/** : Tests end-to-end (Cypress)

### `/config` - Configuration
Fichiers de configuration pour différents environnements

### `/scripts` - Scripts utilitaires
Scripts Python pour maintenance et initialisation

### `/public` - Fichiers statiques
Assets publics servis directement

## 🔧 Conventions de nommage

### Fichiers
- **Composants React** : PascalCase (ex: `Dashboard.jsx`)
- **Modules Python** : snake_case (ex: `meal_plan.py`)
- **Documentation** : kebab-case (ex: `guide-utilisateur.md`)
- **Config** : lowercase avec extensions (ex: `development.env`)

### Code
- **Classes** : PascalCase
- **Fonctions/Variables JS** : camelCase
- **Fonctions/Variables Python** : snake_case
- **Constantes** : UPPER_SNAKE_CASE
- **CSS Classes** : kebab-case

## 🚀 Commandes utiles

```bash
# Frontend
pnpm run dev        # Lancer le dev server
pnpm run build      # Build production
pnpm run test       # Lancer les tests

# Backend
python main.py      # Lancer le serveur Flask
pytest             # Lancer les tests
alembic upgrade    # Appliquer les migrations

# Scripts
python scripts/init_data.py  # Initialiser la DB
```

## 📝 Notes importantes

1. **Séparation Frontend/Backend** : Architecture découplée pour scalabilité
2. **Organisation modulaire** : Chaque module a une responsabilité unique
3. **Documentation inline** : Code auto-documenté avec docstrings
4. **Tests à tous les niveaux** : Unit, intégration, E2E
5. **Configuration externalisée** : Variables d'environnement pour secrets

## 🔄 Workflow de développement

1. Créer une branche feature depuis `develop`
2. Développer dans le dossier approprié
3. Écrire les tests correspondants
4. Mettre à jour la documentation si nécessaire
5. Créer une Pull Request vers `develop`
6. Après review, merger dans `develop`
7. Release périodiques de `develop` vers `main`

---

*Structure mise à jour le 6 Août 2025*