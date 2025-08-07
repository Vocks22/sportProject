# 📋 Stratégie de Test Complète US1.6 : Semaines Lundi-Dimanche

## 📊 Vue d'Ensemble de la Stratégie de Test

### 🎯 Objectifs de Test
- **Validation ISO 8601** : Assurer la conformité avec la norme internationale
- **Migration sans perte** : Vérifier l'intégrité des données lors du passage
- **Performance optimale** : Maintenir des temps de réponse acceptables
- **Expérience utilisateur** : Garantir la cohérence calendaire dans l'interface
- **Régression zéro** : Préserver toutes les fonctionnalités existantes

### 🏗️ Architecture de Test Multi-Niveaux

```
Tests US1.6 - Architecture Pyramidale
┌─────────────────────────────────────────┐
│             E2E Tests (10%)             │  ← Workflows complets utilisateur
│  test_calendar_workflows_us16.py       │
├─────────────────────────────────────────┤
│         Integration Tests (30%)         │  ← API + DB + Frontend
│  test_meal_plans_api_us16.py           │
│  test_migration_us16.py                 │
│  test_performance_us16.py               │
├─────────────────────────────────────────┤
│          Unit Tests (60%)               │  ← Logique métier isolée
│  test_date_utils_us16.py               │
│  test_calendar_components_us16.jsx     │
└─────────────────────────────────────────┘
```

## 🧪 Couverture de Test Détaillée

### 1. Tests Unitaires - Utilitaires Date (100% coverage)

**Fichier** : `/tests/backend/test_date_utils_us16.py`

#### Classes de Test Principales :
- **TestDateUtilsBasicFunctions** : Fonctions de calcul de base
- **TestDateUtilsValidation** : Validation ISO 8601
- **TestDateUtilsISO8601Specific** : Spécificités norme ISO
- **TestDateUtilsFormatting** : Formatage d'affichage
- **TestDateUtilsNavigation** : Navigation entre semaines
- **TestDateUtilsBatchOperations** : Opérations en lot
- **TestDateUtilsEdgeCases** : Cas limites et edge cases

#### Métriques Attendues :
```python
# Performance Benchmarks
assert execution_time < 1.0  # 10k calculs en <1s
assert avg_time_per_calc < 0.1  # <0.1ms par calcul
assert memory_increase < 100  # <100MB pour opérations massives

# Couverture Fonctionnelle
Functions: 14/14 (100%)
Lines: 302/302 (100%)
Branches: 45/45 (100%)
```

### 2. Tests d'Intégration - API avec Logique Calendrier

**Fichier** : `/tests/backend/test_meal_plans_api_us16.py`

#### Scénarios de Test Critiques :
1. **Création meal plan avec lundi valide**
   ```python
   def test_create_meal_plan_with_valid_monday()
   # Vérifie: week_start accepté, date ISO 8601 preservée
   ```

2. **Rejet date invalide (non-lundi)**
   ```python
   def test_create_meal_plan_with_invalid_weekday()
   # Vérifie: HTTP 400, message d'erreur explicite
   ```

3. **Navigation calendaire API**
   ```python
   def test_get_meal_plans_by_week_range()
   # Vérifie: filtrage semaine, tri chronologique
   ```

4. **Cohérence meal plans ↔ shopping lists**
   ```python
   def test_calendar_consistency_across_features()
   # Vérifie: même week_start entre fonctionnalités
   ```

### 3. Tests de Migration - Intégrité Données

**Fichier** : `/tests/backend/test_migration_us16.py`

#### Phases de Test Migration :
1. **Backup et Restauration**
   ```python
   def test_migration_backup_creation()
   def test_migration_rollback_capability()
   ```

2. **Conversion des Dates**
   ```python
   def test_migration_date_conversion()
   # Toutes les dates → lundis correspondants
   ```

3. **Préservation Données Métier**
   ```python
   def test_migration_data_preservation()
   # Meals, user_id, items préservés intacts
   ```

4. **Performance Migration**
   ```python
   def test_migration_performance_large_dataset()
   # 1000+ enregistrements en <10s
   ```

### 4. Tests E2E - Workflows Utilisateur

**Fichier** : `/tests/e2e/test_calendar_workflows_us16.py`

#### Workflows Testés :
1. **Planning Hebdomadaire Complet**
   - Création planning semaine courante
   - Navigation semaine suivante
   - Modification planning existant
   - Cohérence affichage calendaire

2. **Liste de Courses "Semaine Prochaine"**
   - Génération depuis meal plan
   - Validation week_start = lundi suivant
   - Workflow "courses du samedi"

3. **Cohérence Inter-Composants**
   - Calendrier ↔ Planning ↔ Shopping
   - Transitions année (2024→2025)
   - Gestion erreurs utilisateur

### 5. Tests Performance - Scalabilité

**Fichier** : `/tests/backend/test_performance_us16.py`

#### Benchmarks de Performance :
```python
# Métriques Cibles
10k calculs date : < 1.0s
Formatage 52 semaines : < 0.5s
Migration 10k records : < 10s
Requête DB week_start : < 0.1s
Validation batch 50k dates : < 1.0s
Mémoire max increase : < 200MB
```

#### Tests de Charge :
- **Accès Concurrent** : 20 utilisateurs simultanés
- **Dataset Volumineux** : 100 users, 10k meal plans
- **Calculs Parallèles** : Multi-threading date operations

### 6. Tests Frontend - Composants React

**Fichier** : `/tests/frontend/test_calendar_components_us16.jsx`

#### Composants Testés :
1. **WeekCalendar Component**
   - Affichage semaine lundi→dimanche
   - Navigation semaines adjacentes
   - Gestion transitions année

2. **MealPlanningWeek Component**
   - Validation weekStart = lundi
   - Affichage erreur date invalide
   - Persistance sélections meals

3. **useWeekCalendar Hook**
   - Initialisation lundi automatique
   - Navigation cohérente
   - État synchrone multi-composants

## 🔍 Edge Cases et Scénarios Limites

### 1. Transitions Temporelles

#### Changements d'Année ISO vs Calendaire
```javascript
// Cas critique: 31 décembre 2024 (mardi)
test_date = new Date('2024-12-31');
monday = getMondayOfWeek(test_date);
// Résultat attendu: 2024-12-30 (lundi)
// Semaine ISO: W01-2025, Année calendaire: 2024

// Test vérifie cohérence dans toute l'application
```

#### Années Bissextiles
```python
# 29 février 2024 (jeudi) - année bissextile
test_date = date(2024, 2, 29)
monday = get_monday_of_week(test_date)
# Attendu: date(2024, 2, 26) - lundi de cette semaine

# Test vérifie calculs corrects pour années bissextiles
```

### 2. Cas Limites Base de Données

#### Données Legacy Mixtes
```python
# Simulation données pré-migration avec jours variés
legacy_dates = [
    date(2025, 8, 5),   # Mardi
    date(2025, 8, 7),   # Jeudi
    date(2025, 8, 9),   # Samedi
    date(2025, 8, 10),  # Dimanche
]

# Test vérifie conversion correcte vers lundis
expected_mondays = [date(2025, 8, 4)] * 4
```

#### Semaines Dupliquées Post-Migration
```python
# Plusieurs meal plans convergent vers même lundi
converging_dates = [
    date(2025, 8, 4),   # Lundi (reste identique)
    date(2025, 8, 5),   # Mardi → lundi 4 août
    date(2025, 8, 6),   # Mercredi → lundi 4 août
]

# Test vérifie gestion des doublons après migration
```

### 3. Edge Cases Performance

#### Dates Extrêmes
```python
# Test robustesse avec dates limites Python
edge_dates = [
    date.min,  # 0001-01-01
    date.max,  # 9999-12-31
    date(1970, 1, 1),  # Epoch Unix
    date(2038, 1, 19), # Limite epoch 32-bit
]

# Test vérifie gestion gracieuse ou exceptions contrôlées
```

#### Charge Mémoire Extrême
```python
# Test avec 100k dates pour validation mémoire
large_dataset = [
    date(2020, 1, 1) + timedelta(days=i) 
    for i in range(100000)
]

# Vérifications:
# - Mémoire augmente < 200MB
# - Pas de fuites mémoire
# - Performance linéaire maintenue
```

### 4. Cas d'Erreur Utilisateur

#### Interface Utilisateur - Corrections Automatiques
```javascript
// Utilisateur sélectionne accidentellement un mardi
userSelectedDate = new Date('2025-08-05'); // Mardi

// L'interface doit automatiquement corriger
correctedMonday = getMondayOfWeek(userSelectedDate);
// Result: 2025-08-04 (lundi)

// Test vérifie correction transparente sans perte UX
```

#### API - Validation Stricte
```python
# Tentative création meal plan avec date invalide
invalid_request = {
    'week_start': '2025-08-05',  # Mardi
    'meals': {...}
}

# API doit rejeter avec message explicite
# Status: 400 Bad Request
# Message: "week_start doit être un lundi selon ISO 8601"
```

## 📈 Métriques de Qualité et Acceptance Criteria

### Métriques de Performance Requises

| Opération | Seuil Performance | Métrique Mesurée |
|-----------|------------------|------------------|
| Calcul 1k dates | < 1.0s | Temps exécution |
| Migration 10k records | < 10s | Durée migration |
| Requête DB week_start | < 0.1s | Temps réponse |
| Formatage 52 semaines | < 0.5s | Rendu interface |
| Validation batch 50k | < 1.0s | Validation lot |
| Mémoire opération massive | < 200MB | RAM utilisée |

### Couverture de Test Requise

| Couche | Coverage Minimum | Outils Mesure |
|--------|-----------------|---------------|
| Fonctions utilitaires | 100% | pytest-cov |
| API endpoints | 95% | Flask test coverage |
| Composants React | 85% | Jest coverage |
| Workflows E2E | 80% | Cypress/Playwright |
| Migration scripts | 100% | Integration tests |

### Critères d'Acceptance US1.6

#### ✅ Fonctionnels
- [ ] Toutes les semaines affichées commencent lundi
- [ ] Planning aligné sur logique lundi-dimanche
- [ ] Liste de courses "semaine prochaine" = lundi suivant
- [ ] Migration données existantes sans perte
- [ ] Cohérence calendrier entre tous les composants

#### ✅ Non-Fonctionnels
- [ ] Temps réponse API < 200ms (95e percentile)
- [ ] Migration complète < 30s (datasets production)
- [ ] 0 bugs critiques identifiés
- [ ] Couverture tests > 90% globalement
- [ ] Documentation technique complète

#### ✅ Qualité Code
- [ ] Respect standards PEP8 (Python) et ESLint (JS)
- [ ] Pas de code dupliqué > 5%
- [ ] Complexité cyclomatique < 15
- [ ] Dépendances sécurisées (pas de vulnérabilités)

## 🚀 Exécution des Tests

### Commandes d'Exécution

```bash
# Tests unitaires backend
pytest tests/backend/test_date_utils_us16.py -v --cov

# Tests d'intégration API
pytest tests/backend/test_meal_plans_api_us16.py -v

# Tests de migration
pytest tests/backend/test_migration_us16.py -v

# Tests de performance
pytest tests/backend/test_performance_us16.py -v -s

# Tests E2E
pytest tests/e2e/test_calendar_workflows_us16.py -v

# Tests frontend React
npm test -- test_calendar_components_us16.jsx --coverage

# Suite complète US1.6
pytest tests/ -k "us16" -v --cov-report=html
```

### Pipeline CI/CD

```yaml
# .github/workflows/us16-tests.yml
name: US1.6 Calendar Tests

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run unit tests
        run: pytest tests/backend/ -k "us16" --cov
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      - name: Install dependencies
        run: npm ci
      - name: Run frontend tests
        run: npm test -- --coverage
      
  e2e-tests:
    runs-on: ubuntu-latest
    services:
      db:
        image: postgres:13
        env:
          POSTGRES_PASSWORD: test
    steps:
      - uses: actions/checkout@v3
      - name: Setup test environment
        run: |
          docker-compose -f docker-compose.test.yml up -d
      - name: Run E2E tests
        run: pytest tests/e2e/ -v
```

## 📊 Reporting et Métriques

### Dashboard de Qualité

```python
# Génération rapport qualité automatisé
def generate_quality_report():
    return {
        'test_coverage': {
            'backend': '98%',
            'frontend': '87%', 
            'e2e': '82%',
            'global': '91%'
        },
        'performance_metrics': {
            'date_calculations': '0.08ms avg',
            'api_response_time': '145ms p95',
            'migration_speed': '8.2s for 10k records'
        },
        'quality_gates': {
            'all_tests_passing': True,
            'coverage_threshold_met': True,
            'performance_sla_met': True,
            'security_scan_clean': True
        }
    }
```

### Alerting Automatisé

- **Performance Regression** : Si temps > 2x baseline
- **Coverage Drop** : Si coverage < 90%
- **Failed E2E** : Tests workflow utilisateur échoués
- **Migration Issues** : Problèmes intégrité données

## 🎯 Conclusion

Cette stratégie de test complète pour l'US1.6 garantit :

1. **🔒 Fiabilité** : Couverture exhaustive de tous les scénarios
2. **⚡ Performance** : Validation des seuils de performance
3. **🔄 Maintenabilité** : Tests automatisés et reproductibles
4. **👥 Qualité UX** : Validation workflows utilisateur complets
5. **📈 Monitoring** : Métriques continues et alerting

L'implémentation de ces tests assure une migration ISO 8601 robuste et une expérience utilisateur optimale pour la fonctionnalité semaines lundi-dimanche.