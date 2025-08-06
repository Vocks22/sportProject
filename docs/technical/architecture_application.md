# Architecture de l'Application de Suivi de Diète

## Architecture Technique

### Stack Technologique
- **Frontend**: React.js avec TypeScript
- **Backend**: Flask (Python)
- **Base de données**: SQLite (pour simplicité) ou PostgreSQL (pour production)
- **Styling**: Tailwind CSS pour un design moderne et responsive
- **État global**: React Context API
- **Routing**: React Router
- **API**: RESTful API avec Flask-RESTful
- **Authentification**: JWT (optionnel pour version simple)

### Structure du Projet

```
diet-tracker/
├── backend/
│   ├── app.py                 # Application Flask principale
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py           # Modèle utilisateur
│   │   ├── recipe.py         # Modèle recette
│   │   ├── ingredient.py     # Modèle ingrédient
│   │   ├── meal_plan.py      # Modèle planification repas
│   │   └── shopping_list.py  # Modèle liste de courses
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── recipes.py        # Routes pour recettes
│   │   ├── meal_plans.py     # Routes pour planification
│   │   ├── nutrition.py      # Routes pour calculs nutritionnels
│   │   └── shopping.py       # Routes pour listes de courses
│   ├── data/
│   │   ├── nutrition_db.json # Base de données nutritionnelles
│   │   └── recipes_db.json   # Base de données recettes
│   └── requirements.txt
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── common/        # Composants réutilisables
│   │   │   ├── dashboard/     # Tableau de bord
│   │   │   ├── meal-planning/ # Planification des repas
│   │   │   ├── recipes/       # Gestion des recettes
│   │   │   ├── shopping/      # Listes de courses
│   │   │   └── nutrition/     # Suivi nutritionnel
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx
│   │   │   ├── MealPlanning.tsx
│   │   │   ├── Recipes.tsx
│   │   │   ├── Shopping.tsx
│   │   │   └── Progress.tsx
│   │   ├── hooks/            # Hooks personnalisés
│   │   ├── services/         # Services API
│   │   ├── types/            # Types TypeScript
│   │   └── utils/            # Utilitaires
│   ├── package.json
│   └── tailwind.config.js
└── README.md
```

## Modèles de Données

### Ingrédient
```json
{
  "id": "string",
  "name": "string",
  "category": "protein|vegetable|fruit|nuts|grain|fat",
  "nutrition_per_100g": {
    "calories": "number",
    "protein": "number",
    "carbs": "number",
    "fat": "number"
  },
  "unit": "g|ml|piece"
}
```

### Recette
```json
{
  "id": "string",
  "name": "string",
  "category": "breakfast|lunch|dinner|snack",
  "meal_type": "repas1|repas2|repas3|collation",
  "ingredients": [
    {
      "ingredient_id": "string",
      "quantity": "number",
      "unit": "string"
    }
  ],
  "instructions": ["string"],
  "prep_time": "number",
  "cook_time": "number",
  "servings": "number",
  "nutrition_total": {
    "calories": "number",
    "protein": "number",
    "carbs": "number",
    "fat": "number"
  },
  "utensils": ["string"],
  "tags": ["string"]
}
```

### Plan de Repas
```json
{
  "id": "string",
  "user_id": "string",
  "week_start": "date",
  "meals": {
    "monday": {
      "repas1": "recipe_id",
      "collation1": "recipe_id",
      "repas2": "recipe_id",
      "collation2": "recipe_id",
      "repas3": "recipe_id"
    },
    // ... autres jours
  },
  "nutrition_summary": {
    "daily_calories": "number",
    "daily_protein": "number",
    "daily_carbs": "number",
    "daily_fat": "number"
  }
}
```

### Liste de Courses
```json
{
  "id": "string",
  "meal_plan_id": "string",
  "week_start": "date",
  "items": [
    {
      "ingredient_id": "string",
      "name": "string",
      "quantity": "number",
      "unit": "string",
      "category": "string",
      "checked": "boolean"
    }
  ],
  "generated_date": "date"
}
```

## Architecture Frontend

### Pages Principales

#### 1. Dashboard (Tableau de Bord)
- Vue d'ensemble de la semaine
- Progression des objectifs
- Rappels et notifications
- Résumé nutritionnel du jour

#### 2. Planification des Repas
- Calendrier hebdomadaire/mensuel
- Glisser-déposer des recettes
- Génération automatique de plans
- Prévisualisation nutritionnelle

#### 3. Bibliothèque de Recettes
- Catalogue de recettes par catégorie
- Filtres par type de repas, ingrédients
- Détails nutritionnels
- Instructions de préparation

#### 4. Liste de Courses
- Génération automatique
- Organisation par catégories
- Mode shopping avec cases à cocher
- Historique des listes

#### 5. Suivi Nutritionnel
- Graphiques de progression
- Comparaison objectifs/réalisé
- Historique des repas
- Analyse des tendances

### Composants Réutilisables

#### Navigation
- Header avec menu principal
- Sidebar pour navigation rapide
- Breadcrumbs pour orientation

#### Cartes de Recettes
- Image, titre, temps de préparation
- Informations nutritionnelles
- Actions (voir détails, ajouter au plan)

#### Calendrier de Repas
- Vue semaine/mois
- Slots pour chaque repas
- Drag & drop functionality
- Indicateurs nutritionnels

#### Calculateur Nutritionnel
- Affichage en temps réel
- Graphiques circulaires
- Barres de progression
- Comparaison avec objectifs

## Design System

### Palette de Couleurs
```css
:root {
  /* Couleurs principales */
  --primary-green: #10B981;      /* Vert principal (santé/nutrition) */
  --primary-blue: #3B82F6;       /* Bleu principal (confiance) */
  --primary-orange: #F59E0B;     /* Orange (énergie/motivation) */
  
  /* Couleurs secondaires */
  --secondary-light: #F3F4F6;    /* Gris clair (backgrounds) */
  --secondary-medium: #6B7280;   /* Gris moyen (texte secondaire) */
  --secondary-dark: #1F2937;     /* Gris foncé (texte principal) */
  
  /* Couleurs d'état */
  --success: #10B981;            /* Succès */
  --warning: #F59E0B;            /* Attention */
  --error: #EF4444;              /* Erreur */
  --info: #3B82F6;               /* Information */
  
  /* Couleurs nutritionnelles */
  --protein-color: #8B5CF6;      /* Violet pour protéines */
  --carbs-color: #F59E0B;        /* Orange pour glucides */
  --fat-color: #EF4444;          /* Rouge pour lipides */
  --calories-color: #10B981;     /* Vert pour calories */
}
```

### Typographie
```css
/* Polices */
--font-primary: 'Inter', sans-serif;     /* Police principale */
--font-secondary: 'Poppins', sans-serif; /* Titres et accents */

/* Tailles */
--text-xs: 0.75rem;    /* 12px */
--text-sm: 0.875rem;   /* 14px */
--text-base: 1rem;     /* 16px */
--text-lg: 1.125rem;   /* 18px */
--text-xl: 1.25rem;    /* 20px */
--text-2xl: 1.5rem;    /* 24px */
--text-3xl: 1.875rem;  /* 30px */
--text-4xl: 2.25rem;   /* 36px */
```

### Espacements
```css
/* Système d'espacement basé sur 4px */
--space-1: 0.25rem;   /* 4px */
--space-2: 0.5rem;    /* 8px */
--space-3: 0.75rem;   /* 12px */
--space-4: 1rem;      /* 16px */
--space-5: 1.25rem;   /* 20px */
--space-6: 1.5rem;    /* 24px */
--space-8: 2rem;      /* 32px */
--space-10: 2.5rem;   /* 40px */
--space-12: 3rem;     /* 48px */
```

### Composants UI

#### Boutons
- Primaire: Fond vert, texte blanc
- Secondaire: Bordure, fond transparent
- Danger: Fond rouge pour suppressions
- Tailles: sm, md, lg

#### Cartes
- Ombre subtile
- Bordures arrondies
- Padding cohérent
- Hover effects

#### Formulaires
- Labels clairs
- Validation en temps réel
- États d'erreur visuels
- Placeholders informatifs

## Fonctionnalités Détaillées

### 1. Planification Intelligente
- **Auto-génération**: Création automatique de plans basés sur les préférences
- **Rotation**: Éviter la répétition excessive des mêmes recettes
- **Équilibrage**: Respect des macronutriments cibles
- **Flexibilité**: Possibilité de modifier manuellement

### 2. Calculs Nutritionnels
- **Temps réel**: Mise à jour instantanée lors des modifications
- **Précision**: Calculs basés sur les quantités exactes
- **Visualisation**: Graphiques et indicateurs visuels
- **Historique**: Suivi des tendances sur plusieurs semaines

### 3. Gestion des Listes de Courses
- **Génération automatique**: Basée sur le plan de repas
- **Optimisation**: Regroupement par catégories d'aliments
- **Quantités intelligentes**: Calcul des quantités exactes nécessaires
- **Mode shopping**: Interface optimisée pour les courses

### 4. Bibliothèque de Recettes
- **Recherche avancée**: Filtres multiples (ingrédients, temps, calories)
- **Favoris**: Système de favoris personnalisé
- **Variations**: Suggestions de variations pour éviter la monotonie
- **Évaluation**: Système de notes et commentaires

### 5. Suivi et Progression
- **Objectifs**: Définition et suivi d'objectifs personnalisés
- **Graphiques**: Visualisation des progrès
- **Rappels**: Notifications pour les repas et courses
- **Historique**: Conservation des données sur plusieurs mois

## Responsive Design

### Breakpoints
```css
/* Mobile first approach */
--mobile: 320px;      /* Smartphones */
--tablet: 768px;      /* Tablettes */
--desktop: 1024px;    /* Ordinateurs */
--large: 1280px;      /* Grands écrans */
```

### Adaptations Mobile
- Navigation par onglets en bas
- Cartes empilées verticalement
- Formulaires optimisés pour le tactile
- Calendrier adapté aux petits écrans

### Adaptations Tablette
- Sidebar rétractable
- Grille de cartes 2 colonnes
- Calendrier vue semaine optimisée

### Adaptations Desktop
- Sidebar fixe
- Grille de cartes 3-4 colonnes
- Vue calendrier mois complète
- Raccourcis clavier

## Performance et Optimisation

### Frontend
- **Lazy loading**: Chargement différé des composants
- **Memoization**: React.memo pour éviter les re-renders
- **Bundle splitting**: Séparation du code par routes
- **Image optimization**: Formats WebP, lazy loading

### Backend
- **Caching**: Cache des calculs nutritionnels
- **Pagination**: Pour les listes de recettes
- **Compression**: Gzip pour les réponses API
- **Indexation**: Index sur les champs de recherche

### Base de Données
- **Normalisation**: Structure optimisée
- **Index**: Sur les champs fréquemment utilisés
- **Requêtes optimisées**: Éviter les N+1 queries
- **Backup**: Sauvegarde automatique des données

