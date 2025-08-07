# US1.5 - Architecture Technique : Liste de Courses Interactive

## Vue d'ensemble

L'US1.5 transforme la simple liste de courses statique en un système interactif avancé avec agrégation intelligente, persistance offline, et synchronisation automatique.

## 1. Architecture Système

```
┌─────────────────────────────────────────────────────────────────────┐
│                    ARCHITECTURE US1.5 - VUE GLOBALE               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐ │
│  │   FRONTEND      │◄──►│     BACKEND     │◄──►│   PERSISTENCE   │ │
│  │                 │    │                 │    │                 │ │
│  │ • React + Hooks │    │ • Flask + API   │    │ • PostgreSQL    │ │
│  │ • Zustand Store │    │ • Services      │    │ • Redis Cache   │ │
│  │ • IndexedDB     │    │ • Aggregation   │    │ • IndexedDB     │ │
│  │ • Offline Mode  │    │ • Cache Layer   │    │                 │ │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘ │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│                       FONCTIONNALITÉS CLÉS                         │
│                                                                     │
│ ✅ Cases cochables persistantes    ✅ Agrégation des quantités      │
│ ✅ Groupement par rayon           ✅ Calcul basé sur TOUS repas     │
│ ✅ Export/impression              ✅ Mode offline avec sync         │
│ ✅ Cache intelligent              ✅ Performance optimisée          │
└─────────────────────────────────────────────────────────────────────┘
```

## 2. Modifications de la Base de Données

### 2.1 Extension du modèle ShoppingList

**Nouveaux champs ajoutés :**
- `checked_items_json`: État des cases cochées (JSON)
- `aggregation_rules_json`: Règles d'agrégation appliquées
- `category_grouping_json`: Groupement par rayons
- `estimated_budget`: Budget estimé calculé
- `last_updated`: Timestamp de dernière modification
- `completion_date`: Date de completion de la liste
- `version`: Numéro de version pour gestion des conflits

### 2.2 Nouvelles tables

**`shopping_list_history`** - Historique des modifications
```sql
CREATE TABLE shopping_list_history (
    id SERIAL PRIMARY KEY,
    shopping_list_id INT REFERENCES shopping_lists(id),
    action VARCHAR(50) NOT NULL,
    item_id VARCHAR(100),
    old_value TEXT,
    new_value TEXT,
    user_id VARCHAR(50),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata_json TEXT
);
```

**`store_categories`** - Rayons de magasin personnalisables
```sql
CREATE TABLE store_categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    icon VARCHAR(20),
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    user_id VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(name, user_id)
);
```

## 3. Services Backend

### 3.1 ShoppingService - Service Principal

**Responsabilités :**
- Agrégation intelligente des ingrédients
- Conversion automatique des unités (g→kg, ml→l)
- Groupement par rayons de magasin
- Calcul du budget estimé
- Gestion de l'état des cases cochées

**Algorithmes d'optimisation :**
```python
# Agrégation des quantités
def aggregate_ingredient_quantities(raw_ingredients):
    """
    Exemple: 6x180g poulet → 1.08kg poulet
    Logique: Collecter toutes les occurrences d'un même ingrédient
    """

# Conversion d'unités
AGGREGATION_THRESHOLDS = {
    'g': 1000,    # 1000g → 1kg
    'ml': 1000,   # 1000ml → 1l
    'unités': 12  # 12 unités → 1 douzaine
}

# Mapping catégories → rayons magasin
CATEGORY_TO_STORE_SECTION = {
    'protein': 'protein',      # 🥩 PROTÉINES
    'vegetable': 'vegetable',  # 🥬 LÉGUMES FRAIS
    'fruit': 'fruit',          # 🍓 FRUITS
    'dairy': 'dairy',          # 🥛 PRODUITS LAITIERS
    'grain': 'grain',          # 🌾 CÉRÉALES
    # ... etc
}
```

### 3.2 CacheService - Mise en Cache Redis

**Stratégie de cache multi-niveaux :**
```python
# TTL optimisés par type de données
TTL_SHOPPING_LIST = 3600       # 1 heure
TTL_AGGREGATION = 1800         # 30 minutes  
TTL_MEAL_PLAN_INGREDIENTS = 7200  # 2 heures
TTL_RECIPE_DATA = 86400        # 24 heures

# Clés de cache structurées
PREFIX_SHOPPING_LIST = "sl:"
PREFIX_AGGREGATION = "agg:"
PREFIX_MEAL_PLAN = "mp:"
```

**Invalidation intelligente :**
- Invalidation en cascade lors de modification de plan de repas
- Cache warming pour les données fréquemment accédées
- Compression des données avec pickle

## 4. API Endpoints Étendues

### 4.1 Endpoints Existants Améliorés

**`POST /meal-plans/{id}/shopping-list`**
- Génération avec agrégation optimisée
- Support des préférences d'agrégation
- Calcul automatique du budget

### 4.2 Nouveaux Endpoints Interactifs

**`PATCH /shopping-lists/{id}/items/{item_id}/toggle`**
- Cocher/décocher un article individuel
- Mise à jour optimiste côté client
- Historique des modifications

**`PATCH /shopping-lists/{id}/bulk-toggle`**
- Cocher/décocher plusieurs articles simultanément
- Opération atomique en base
- Optimisation pour "tout cocher/décocher"

**`POST /shopping-lists/{id}/regenerate`**
- Régénération avec préservation des cases cochées
- Mise à jour des quantités et prix
- Gestion des conflits de version

**`GET /shopping-lists/{id}/statistics`**
- Statistiques détaillées par catégorie
- Métriques de completion
- Informations d'agrégation

**`POST /shopping-lists/{id}/export`**
- Préparation des données pour export
- Support de multiples formats (PDF, email, impression)

## 5. Architecture Frontend

### 5.1 Gestion d'État avec Zustand

```javascript
// Store principal avec middleware
const useShoppingListStore = create(
  subscribeWithSelector(
    persist(
      immer((set, get) => ({
        // État
        currentList: null,
        checkedItems: {},
        offlineMode: false,
        pendingActions: [],
        
        // Actions optimistes
        toggleItem: (itemId, checked, optimistic = true),
        bulkToggleItems: (updates, optimistic = true),
        
        // Getters calculés
        getCompletionStats: () => ({
          total, completed, percentage
        }),
        getItemsByCategory: () => ({...})
      }))
    )
  )
)
```

### 5.2 Hooks Personnalisés

**`useShoppingList`** - Hook principal
- Gestion des opérations CRUD
- Mise à jour optimiste avec rollback
- Synchronisation automatique online/offline

**`useNetworkStatus`** - Détection réseau
- Détection automatique online/offline
- Synchronisation automatique lors du retour online
- Queue des actions offline

### 5.3 Persistance Offline

**IndexedDB pour la persistance :**
```javascript
// Configuration IndexedDB
const INDEXED_DB_CONFIG = {
  name: 'diettracker-shopping',
  version: 1,
  stores: {
    shoppingLists: 'id',
    checkedItems: 'listId',
    offlineActions: '++id'
  }
}
```

**Stratégie offline-first :**
1. Mise à jour immédiate de l'UI (optimiste)
2. Sauvegarde locale en IndexedDB
3. Queue des actions pour synchronisation
4. Sync automatique au retour online

## 6. Stratégies de Performance

### 6.1 Optimisations Backend

**Mise en cache multi-niveaux :**
- Redis pour les agrégations fréquentes
- Cache applicatif pour les recettes
- Cache de requêtes SQL pour les ingrédients

**Optimisations de requêtes :**
```python
# Requêtes par batch pour éviter N+1
def optimize_ingredient_queries(ingredient_ids):
    batch_size = 100
    for i in range(0, len(ingredient_ids), batch_size):
        batch = ingredient_ids[i:i + batch_size]
        yield Ingredient.query.filter(Ingredient.id.in_(batch)).all()

# Jointures optimisées
shopping_lists = ShoppingList.query.options(
    joinedload(ShoppingList.meal_plan)
).filter(ShoppingList.id.in_(ids)).all()
```

### 6.2 Optimisations Frontend

**Rendu optimisé :**
- Virtualisation pour les longues listes
- Debouncing des opérations de sauvegarde
- Memoization des calculs complexes

**Gestion mémoire :**
- Cleanup automatique des caches expirés
- Compression des données en local storage
- Limitation de la taille des queues offline

## 7. Monitoring et Observabilité

### 7.1 Métriques Clés

**Performance :**
- Temps de génération des listes
- Taux de cache hit/miss Redis
- Latence des endpoints interactifs

**Usage :**
- Nombre d'articles cochés/décochés
- Fréquence des régénérations
- Utilisation du mode offline

**Erreurs :**
- Échecs de synchronisation
- Conflits de version
- Erreurs de cache Redis

### 7.2 Logging Structuré

```python
# Exemple de log structuré
logger.info("Shopping list aggregated", extra={
    'meal_plan_id': meal_plan.id,
    'total_ingredients': len(raw_ingredients),
    'aggregated_items': len(optimized_ingredients),
    'aggregation_savings': aggregation_percentage,
    'estimated_budget': estimated_budget,
    'processing_time_ms': processing_time
})
```

## 8. Tests et Qualité

### 8.1 Tests Backend

**Tests Unitaires :**
- Service d'agrégation
- Conversions d'unités
- Logique de cache

**Tests d'Intégration :**
- Endpoints API complets
- Cohérence base de données
- Performance sous charge

### 8.2 Tests Frontend

**Tests de Composants :**
- Interactions utilisateur
- États de chargement
- Mode offline

**Tests End-to-End :**
- Flux complet de courses
- Synchronisation online/offline
- Export et impression

## 9. Migration et Déploiement

### 9.1 Stratégie de Migration

```sql
-- Migration 003: Ajout des fonctionnalités US1.5
-- 1. Ajout des colonnes sans rupture
-- 2. Migration des données existantes
-- 3. Création des nouvelles tables
-- 4. Initialisation des rayons par défaut
```

### 9.2 Déploiement Progressif

**Phase 1 :** Backend et API (sans impact frontend)
**Phase 2 :** Frontend avec fallback vers ancien système
**Phase 3 :** Activation complète et monitoring
**Phase 4 :** Suppression du code legacy

## 10. Roadmap Future

### 10.1 Améliorations Prévues

**V2.0 - Personnalisation Avancée :**
- Rayons personnalisables par utilisateur
- Prix réels des magasins partenaires
- Suggestions d'optimisation budget

**V2.1 - Intelligence Artificielle :**
- Prédiction des besoins futurs
- Optimisation automatique des parcours magasin
- Détection d'anomalies dans les listes

**V2.2 - Intégrations :**
- API de livraison à domicile
- Synchronisation avec applications magasin
- Export vers calendriers et rappels

Cette architecture robuste et évolutive positionne l'US1.5 comme une fonctionnalité premium qui améliore significativement l'expérience utilisateur tout en maintenant des performances optimales.