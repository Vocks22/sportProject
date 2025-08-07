# 🚀 Guide de Déploiement US1.6 - Semaines Lundi-Dimanche

## 📋 Vue d'Ensemble

Ce guide complet documente le processus de déploiement de l'US1.6 qui implémente la logique de semaines ISO 8601 (lundi-dimanche) dans l'application DietTracker. Le pipeline CI/CD automatise tous les aspects du déploiement avec des safeguards robustes.

## 🏗️ Architecture du Pipeline CI/CD

### Workflows GitHub Actions

Notre pipeline comprend 4 workflows principaux :

1. **`us16-ci-cd.yml`** - Pipeline principal CI/CD
2. **`migration-us16.yml`** - Gestion des migrations de données
3. **`rollback-us16.yml`** - Rollback d'urgence
4. **`monitoring-us16.yml`** - Monitoring continu
5. **`quality-gates-us16.yml`** - Gates de qualité

```
┌─────────────────────────────────────────────────────────┐
│                     Pipeline US1.6                     │
├─────────────────────────────────────────────────────────┤
│  🔍 Quality Gates  →  🧪 Tests  →  📊 Migration         │
│           ↓               ↓             ↓               │
│  🚀 Staging Deploy → ✅ Validation → 🌟 Production     │
│           ↓               ↓             ↓               │
│  📈 Monitoring    →  🚨 Alerting  → ⏪ Rollback       │
└─────────────────────────────────────────────────────────┘
```

## 🔄 Processus de Déploiement

### 1. Déclencheurs de Pipeline

#### Déclenchement Automatique
```yaml
# Push vers branches principales
on:
  push:
    branches: [ main, develop, feature/us1.6-* ]
    paths:
      - 'src/**'
      - 'tests/**'
      - 'scripts/**'

# Pull Requests
on:
  pull_request:
    branches: [ main, develop ]
```

#### Déclenchement Manuel
```bash
# Via GitHub Actions UI ou CLI
gh workflow run us16-ci-cd.yml
```

### 2. Étapes du Pipeline Principal

#### Phase 1: Quality Gates (🔍)
- **Durée**: ~10 minutes
- **Objectif**: Validation qualité avant déploiement

```yaml
quality-gates:
  - Analyse code (Flake8, ESLint, Pylint)
  - Scan sécurité (Bandit, Safety, NPM Audit)
  - Coverage analysis (Backend 90%+, Frontend 85%+)
  - Métriques complexité cyclomatique
```

**Seuils de Qualité**:
- Score qualité global: ≥ 7.0/10
- Couverture tests: ≥ 90%
- Issues sécurité: = 0
- Performance: ≥ 6.0/10

#### Phase 2: Tests Automatisés (🧪)
- **Durée**: ~15 minutes
- **Tests parallèles pour optimiser le temps**

```yaml
backend-tests:
  - Tests unitaires date_utils (100% coverage)
  - Tests API meal plans avec week_start
  - Tests migration US1.6
  - Benchmarks performance

frontend-tests:
  - Tests composants calendrier React
  - Tests hook useISOWeek
  - Build production

e2e-tests:
  - Workflows utilisateur complets
  - Navigation calendaire
  - Cohérence inter-composants
```

#### Phase 3: Validation Migration (📊)
- **Durée**: ~5 minutes (staging) / ~20 minutes (production)

```yaml
migration-validation:
  - Analyse données pré-migration
  - Simulation migration (dry-run)
  - Validation intégrité données
  - Tests performance post-migration
```

#### Phase 4: Déploiement Staging (🚀)
- **Durée**: ~8 minutes
- **Déclencheur**: Push vers `develop`

```yaml
deploy-staging:
  - Build frontend optimisé
  - Déploiement Heroku staging
  - Tests post-déploiement
  - Notification équipe
```

#### Phase 5: Déploiement Production (🌟)
- **Durée**: ~12 minutes
- **Déclencheur**: Push vers `main`

```yaml
deploy-production:
  - Backup automatique base de données
  - Déploiement blue-green
  - Tests smoke critiques
  - Activation trafic progressif
  - Monitoring post-déploiement (5 min)
```

## 🗃️ Gestion des Migrations

### Migration Workflow Déclenché Manuellement

```bash
# Via GitHub Actions UI
Workflow: migration-us16.yml
Inputs:
  - environment: staging/production
  - dry_run: true/false
  - backup_before_migration: true/false
```

### Étapes de Migration

1. **Pré-Migration**
   ```python
   # Validation sécurité
   safety_checks = run_safety_checks()
   data_analysis = analyze_current_state()
   
   # Critères bloquants
   - Données corrompues
   - Connexions actives > seuil
   - Espace disque insuffisant
   ```

2. **Backup Automatique**
   ```bash
   # Backup complet avec métadonnées
   backup_file="backup_us16_pre_migration_${timestamp}.sql"
   retention: 365 jours
   ```

3. **Exécution Migration**
   ```python
   # Migration par batch pour performance
   migrate_to_iso8601_weeks.py \
     --execute \
     --batch-size=1000 \
     --progress-callback
   ```

4. **Validation Post-Migration**
   ```python
   # Tests intégrité
   validate_us16_data_integrity.py --post-migration
   validate_us16_implementation.py --full-validation
   
   # Tests performance
   pytest test_performance_us16.py --benchmark-only
   ```

## ⏪ Stratégie de Rollback

### Types de Rollback

1. **Rollback Application** (Code seulement)
2. **Rollback Database** (Données seulement) 
3. **Rollback Complet** (Code + Données)

### Déclenchement Rollback

```bash
# Workflow manuel d'urgence
gh workflow run rollback-us16.yml \
  --field environment=production \
  --field rollback_type=full \
  --field reason="Critical bug detected"
```

### Processus de Rollback

1. **Validation Autorisation**
   - Utilisateurs autorisés seulement
   - Vérification état système

2. **Rollback Application**
   ```bash
   # Retour version précédente
   git checkout $previous_stable_commit
   heroku deploy --rollback
   ```

3. **Rollback Database**
   ```python
   # Restauration backup
   backup_restore_us16.py \
     --restore-backup \
     --file="$backup_file"
   ```

4. **Validation Post-Rollback**
   - Tests sanité
   - Monitoring 30 minutes
   - Création incident GitHub

## 📊 Monitoring et Alertes

### Monitoring Automatique

```yaml
# Programmé toutes les 15 minutes (heures bureau)
# Toutes les heures (hors heures bureau)
schedule:
  - cron: '*/15 9-17 * * 1-5'  # Business hours
  - cron: '0 * * * *'          # After hours
```

### Métriques Surveillées

#### Santé Système
- Endpoint `/health` (< 200ms)
- Connectivité base de données
- Temps de réponse API (p95 < 500ms)

#### Fonctionnalités US1.6
- API meal plans avec `week_start`
- Navigation calendaire
- Validation dates ISO 8601
- Performance calculs de dates

#### Seuils d'Alerte
```yaml
response_time_threshold: 500ms
success_rate_threshold: 95%
consecutive_failures_max: 3
```

### Script de Monitoring Avancé

```bash
# Monitoring continu post-déploiement
python scripts/monitor_production_health.py \
  --duration 60 \
  --interval 30 \
  --verbose
```

## 🔒 Sécurité et Secrets

### Secrets GitHub Actions Requis

```yaml
# Heroku Deployment
HEROKU_API_KEY: "your-heroku-api-key"
HEROKU_EMAIL: "your-email@domain.com"

# Database Connections
STAGING_DATABASE_URL: "postgresql://..."
PRODUCTION_DATABASE_URL: "postgresql://..."

# Backup & Recovery
PROD_BACKUP_WEBHOOK: "https://..."
PROD_BACKUP_TOKEN: "webhook-token"
PROD_ROLLBACK_WEBHOOK: "https://..."
PROD_ROLLBACK_TOKEN: "rollback-token"

# Monitoring & Alerts
SLACK_WEBHOOK_URL: "https://hooks.slack.com/..."

# Traffic Management
PROD_TRAFFIC_SWITCH_WEBHOOK: "https://..."
PROD_DEPLOY_TOKEN: "deploy-token"
```

### Gestion des Secrets

1. **Rotation Automatique**: Secrets renouvelés tous les 90 jours
2. **Principe du Moindre Privilège**: Accès minimal requis
3. **Audit Trail**: Logs d'utilisation des secrets
4. **Chiffrement**: Tous les secrets chiffrés au repos

## 🎯 Environnements

### Staging
- **URL**: https://diettracker-staging.herokuapp.com
- **Purpose**: Tests d'intégration pré-production
- **Base de données**: Copie sanitisée production
- **Déploiement**: Automatique sur `develop`

### Production
- **URL**: https://diettracker-app.herokuapp.com
- **Purpose**: Environment de production
- **Base de données**: PostgreSQL production
- **Déploiement**: Automatique sur `main` après validation

## 📈 Métriques de Performance

### Benchmarks US1.6

| Opération | Seuil | Méthode de Test |
|-----------|-------|----------------|
| Calcul date utils | < 10ms | pytest-benchmark |
| API meal plans | < 500ms | Requêtes HTTP |
| Navigation calendaire | < 200ms | Tests E2E |
| Migration 10k records | < 10s | Script migration |
| Requête DB week_start | < 100ms | Tests SQL |

### Load Testing

```python
# Configuration Locust
users = 20
spawn_rate = 2
run_time = 120s
endpoints = [
    "/api/meal-plans",
    "/api/meal-plans/week/{date}",
    "/health"
]
```

## 🚨 Procédures d'Urgence

### Incident Response

1. **Détection Automatique**
   - Monitoring continu détecte anomalie
   - Alerte Slack automatique
   - Issue GitHub créée

2. **Escalade**
   ```
   L1: Developer on-call (0-15min)
   L2: DevOps Lead (15-30min)  
   L3: Tech Lead (30-60min)
   L4: Management (60min+)
   ```

3. **Communication**
   - Status page mise à jour
   - Communication client si nécessaire
   - Post-mortem dans les 48h

### Rollback d'Urgence

```bash
# Rollback immédiat production
gh workflow run rollback-us16.yml \
  --field environment=production \
  --field rollback_type=full \
  --field reason="EMERGENCY: System down"
```

### Contacts d'Urgence

- **DevOps Lead**: @devops-lead
- **Tech Lead**: @tech-lead  
- **On-call Engineer**: @oncall
- **Management**: @management

## 📝 Checklist de Déploiement

### Pré-Déploiement

- [ ] Tous les tests passent localement
- [ ] Code review approuvée
- [ ] Documentation mise à jour
- [ ] Backup production récent disponible
- [ ] Équipe prête pour monitoring

### Pendant le Déploiement

- [ ] Pipeline CI/CD surveillé
- [ ] Métriques de performance monitored
- [ ] Équipe disponible pour rollback
- [ ] Communication aux parties prenantes

### Post-Déploiement

- [ ] Tests smoke manuels
- [ ] Monitoring renforcé 2h
- [ ] Vérification métriques business
- [ ] Documentation mise à jour
- [ ] Lessons learned capturées

## 🔧 Troubleshooting

### Problèmes Courants

#### Migration Fails
```bash
# Debug migration
python validate_us16_data_integrity.py --debug
python migrate_to_iso8601_weeks.py --dry-run --verbose
```

#### Performance Degradation
```bash
# Monitoring détaillé
python monitor_production_health.py --duration 30 --verbose
pytest tests/backend/test_performance_us16.py --benchmark-only
```

#### Rollback Issues
```bash
# Vérification backup
python backup_restore_us16.py --verify-backup --file=$BACKUP_FILE
```

### Logs et Diagnostics

- **Application Logs**: Heroku logs --tail
- **Pipeline Logs**: GitHub Actions logs
- **Database Logs**: PostgreSQL logs
- **Monitoring Data**: Artifacts dans workflows

## 📚 Ressources Additionnelles

### Documentation Technique
- [Architecture US1.6](./US1.6_ARCHITECTURE_TECHNIQUE.md)
- [Guide Migration](./US1.6_MIGRATION_GUIDE.md)
- [Stratégie Tests](./US1.6_TEST_STRATEGY_COMPLETE.md)

### Scripts Utiles
- `scripts/monitor_production_health.py` - Monitoring avancé
- `scripts/validate_us16_implementation.py` - Validation US1.6
- `scripts/backup_restore_us16.py` - Backup/restore

### Workflows GitHub Actions
- `.github/workflows/us16-ci-cd.yml` - Pipeline principal
- `.github/workflows/migration-us16.yml` - Migrations
- `.github/workflows/rollback-us16.yml` - Rollback
- `.github/workflows/monitoring-us16.yml` - Monitoring

---

**✨ Ce guide assure un déploiement sûr et fiable de l'US1.6 avec tous les safeguards nécessaires pour maintenir la stabilité du système en production.**