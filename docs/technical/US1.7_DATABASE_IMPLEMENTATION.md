# US1.7 - Profil Utilisateur Réel - Implémentation Base de Données

## Vue d'ensemble

Cette documentation détaille l'implémentation complète de la base de données pour l'US1.7 : **Profil Utilisateur Réel**. Cette User Story étend considérablement le modèle utilisateur existant pour supporter un profil complet avec historique, métriques de santé avancées, et fonctionnalités de suivi.

**Version:** 1.0.0  
**Date:** 2025-08-07  
**Migration:** 006_user_profile_real_us17.py  
**Database Administrator:** Claude Code

---

## Modifications de la Base de Données

### 1. Extensions de la Table `users`

#### Nouvelles Colonnes Ajoutées

**Informations Personnelles Étendues**
```sql
birth_date DATE                    -- Date de naissance (remplace age pour plus de précision)
goals TEXT                         -- Objectifs utilisateur (JSON)
medical_conditions TEXT            -- Conditions médicales (JSON)
dietary_restrictions TEXT          -- Restrictions alimentaires (JSON)
preferred_cuisine_types TEXT       -- Types de cuisine préférés (JSON)
```

**Métriques de Santé Avancées**
```sql
body_fat_percentage FLOAT          -- Pourcentage de masse grasse
muscle_mass_percentage FLOAT       -- Pourcentage de masse musculaire  
water_percentage FLOAT             -- Pourcentage d'eau corporelle
bone_density FLOAT                 -- Densité osseuse
metabolic_age INTEGER              -- Âge métabolique
```

**Objectifs Nutritionnels Étendus**
```sql
daily_fiber_target FLOAT DEFAULT 25.0    -- Objectif fibres quotidien (g)
daily_sodium_target FLOAT DEFAULT 2300.0 -- Objectif sodium quotidien (mg)
daily_sugar_target FLOAT DEFAULT 50.0    -- Objectif sucre quotidien (g)
daily_water_target FLOAT DEFAULT 2000.0  -- Objectif eau quotidien (ml)
```

**Préférences et Paramètres**
```sql
timezone VARCHAR(50) DEFAULT 'UTC'        -- Fuseau horaire utilisateur
language VARCHAR(10) DEFAULT 'fr'         -- Langue préférée
units_system VARCHAR(10) DEFAULT 'metric' -- Système d'unités (metric/imperial)
notification_preferences TEXT             -- Préférences notifications (JSON)
```

**Cache de Performance**
```sql
cached_bmr FLOAT                   -- BMR en cache pour performance
cached_tdee FLOAT                  -- TDEE en cache pour performance
cache_last_updated DATETIME        -- Timestamp dernière mise à jour cache
```

**Statut et Validation**
```sql
profile_completed BOOLEAN DEFAULT FALSE    -- Profil complet ou non
profile_validated BOOLEAN DEFAULT FALSE    -- Profil validé ou non
last_profile_update DATETIME              -- Dernière mise à jour profil
```

**Sécurité et Audit**
```sql
last_login DATETIME               -- Dernière connexion
login_count INTEGER DEFAULT 0     -- Nombre de connexions
is_active BOOLEAN DEFAULT TRUE    -- Compte actif ou non
deactivated_at DATETIME          -- Date de désactivation si applicable
```

### 2. Nouvelles Tables

#### Table `weight_history`
Historique détaillé des pesées utilisateur.

```sql
CREATE TABLE weight_history (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    weight FLOAT NOT NULL,
    body_fat_percentage FLOAT,
    muscle_mass_percentage FLOAT,
    water_percentage FLOAT,
    recorded_date DATE NOT NULL,
    measurement_time TIME,
    notes TEXT,
    measurement_method VARCHAR(50) DEFAULT 'manual',
    data_source VARCHAR(100),         -- 'manual', 'scale_api', 'mobile_app'
    is_verified BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(user_id, recorded_date)    -- Un seul poids par jour par utilisateur
);
```

#### Table `user_goals_history`
Traçabilité complète des objectifs utilisateur.

```sql
CREATE TABLE user_goals_history (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    goal_type VARCHAR(50) NOT NULL,   -- 'weight_loss', 'muscle_gain', 'maintenance'
    target_value FLOAT,
    target_date DATE,
    start_date DATE NOT NULL,
    end_date DATE,
    status VARCHAR(20) DEFAULT 'active', -- 'active', 'completed', 'abandoned', 'paused'
    progress_percentage FLOAT DEFAULT 0.0,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### Table `user_measurements`
Mesures corporelles diverses (tour de taille, bras, etc.).

```sql
CREATE TABLE user_measurements (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    measurement_type VARCHAR(50) NOT NULL, -- 'waist', 'chest', 'hip', 'arm', 'thigh'
    value FLOAT NOT NULL,
    unit VARCHAR(10) DEFAULT 'cm',
    recorded_date DATE NOT NULL,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 3. Contraintes de Validation

**Contraintes sur `users`**
```sql
-- Poids positif
CHECK (current_weight IS NULL OR current_weight > 0)
CHECK (target_weight IS NULL OR target_weight > 0)

-- Taille réaliste (50-300 cm)
CHECK (height IS NULL OR (height > 50 AND height < 300))

-- Âge réaliste (0-150 ans)
CHECK (age IS NULL OR (age > 0 AND age < 150))

-- Pourcentages valides (0-100%)
CHECK (body_fat_percentage IS NULL OR (body_fat_percentage >= 0 AND body_fat_percentage <= 100))
CHECK (muscle_mass_percentage IS NULL OR (muscle_mass_percentage >= 0 AND muscle_mass_percentage <= 100))
CHECK (water_percentage IS NULL OR (water_percentage >= 0 AND water_percentage <= 100))
```

**Contraintes sur `weight_history`**
```sql
-- Poids positif obligatoire
CHECK (weight > 0)

-- Pourcentages valides
CHECK (body_fat_percentage IS NULL OR (body_fat_percentage >= 0 AND body_fat_percentage <= 100))
```

### 4. Index de Performance

**Index sur `users`**
```sql
-- Recherches de profil
CREATE INDEX idx_users_profile_status ON users(profile_completed, is_active, last_profile_update);
CREATE INDEX idx_users_birth_date ON users(birth_date);
CREATE INDEX idx_users_cache_updated ON users(cache_last_updated);
```

**Index sur `weight_history`**
```sql
-- Requêtes chronologiques
CREATE INDEX idx_weight_history_user_date ON weight_history(user_id, recorded_date);
CREATE INDEX idx_weight_history_date_range ON weight_history(recorded_date, user_id);
```

**Index sur `user_goals_history`**
```sql
-- Requêtes d'objectifs
CREATE INDEX idx_goals_history_user_status ON user_goals_history(user_id, status, start_date);
CREATE INDEX idx_goals_history_type_status ON user_goals_history(goal_type, status);
```

**Index sur `user_measurements`**
```sql
-- Requêtes de mesures
CREATE INDEX idx_measurements_user_type_date ON user_measurements(user_id, measurement_type, recorded_date);
```

### 5. Vues de Rapports

#### Vue `v_user_profile_complete`
Profil utilisateur complet avec données calculées.

```sql
CREATE VIEW v_user_profile_complete AS
SELECT 
    u.id,
    u.username,
    u.email,
    u.birth_date,
    CASE 
        WHEN u.birth_date IS NOT NULL 
        THEN DATE_PART('year', AGE(u.birth_date))
        ELSE u.age
    END as calculated_age,
    u.current_weight,
    u.target_weight,
    u.height,
    u.gender,
    u.activity_level,
    u.goals,
    u.medical_conditions,
    u.dietary_restrictions,
    u.body_fat_percentage,
    u.muscle_mass_percentage,
    u.cached_bmr,
    u.cached_tdee,
    u.profile_completed,
    u.profile_validated,
    u.last_profile_update,
    u.created_at,
    -- Dernière pesée
    wh_last.weight as last_recorded_weight,
    wh_last.recorded_date as last_weight_date,
    -- Évolution du poids (30 derniers jours)
    (u.current_weight - wh_30d.weight) as weight_change_30d,
    -- Objectif actuel
    goal_current.goal_type as current_goal_type,
    goal_current.target_value as current_goal_target,
    goal_current.target_date as current_goal_date,
    goal_current.progress_percentage as current_goal_progress
FROM users u
LEFT JOIN LATERAL (
    SELECT weight, recorded_date 
    FROM weight_history wh1 
    WHERE wh1.user_id = u.id 
    ORDER BY recorded_date DESC 
    LIMIT 1
) wh_last ON true
LEFT JOIN LATERAL (
    SELECT weight
    FROM weight_history wh2 
    WHERE wh2.user_id = u.id 
      AND recorded_date <= CURRENT_DATE - INTERVAL '30 days'
    ORDER BY recorded_date DESC 
    LIMIT 1
) wh_30d ON true
LEFT JOIN LATERAL (
    SELECT goal_type, target_value, target_date, progress_percentage
    FROM user_goals_history gh 
    WHERE gh.user_id = u.id 
      AND status = 'active'
    ORDER BY start_date DESC 
    LIMIT 1
) goal_current ON true;
```

#### Vue `v_weight_evolution`
Évolution détaillée du poids avec tendances.

```sql
CREATE VIEW v_weight_evolution AS
SELECT 
    wh.user_id,
    wh.recorded_date,
    wh.weight,
    wh.body_fat_percentage,
    wh.muscle_mass_percentage,
    -- Évolution par rapport à la pesée précédente
    LAG(wh.weight) OVER (PARTITION BY wh.user_id ORDER BY wh.recorded_date) as previous_weight,
    wh.weight - LAG(wh.weight) OVER (PARTITION BY wh.user_id ORDER BY wh.recorded_date) as weight_change,
    -- Évolution depuis le début
    FIRST_VALUE(wh.weight) OVER (PARTITION BY wh.user_id ORDER BY wh.recorded_date ROWS UNBOUNDED PRECEDING) as initial_weight,
    wh.weight - FIRST_VALUE(wh.weight) OVER (PARTITION BY wh.user_id ORDER BY wh.recorded_date ROWS UNBOUNDED PRECEDING) as total_weight_change,
    -- Moyenne mobile sur 7 jours
    AVG(wh.weight) OVER (
        PARTITION BY wh.user_id 
        ORDER BY wh.recorded_date 
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) as weight_avg_7d,
    u.target_weight,
    -- Distance de l'objectif
    ABS(wh.weight - u.target_weight) as distance_to_target,
    -- Progression vers l'objectif (en %)
    CASE 
        WHEN u.target_weight IS NOT NULL AND u.current_weight IS NOT NULL
        THEN 100.0 * (u.current_weight - wh.weight) / (u.current_weight - u.target_weight)
        ELSE NULL
    END as progress_percentage
FROM weight_history wh
JOIN users u ON wh.user_id = u.id
ORDER BY wh.user_id, wh.recorded_date;
```

#### Vue `v_progress_stats`
Statistiques de progression utilisateur.

```sql
CREATE VIEW v_progress_stats AS
SELECT 
    u.id as user_id,
    u.username,
    -- Statistiques de poids
    COUNT(wh.id) as total_weigh_ins,
    MIN(wh.recorded_date) as first_weigh_in,
    MAX(wh.recorded_date) as last_weigh_in,
    MIN(wh.weight) as min_weight,
    MAX(wh.weight) as max_weight,
    AVG(wh.weight) as avg_weight,
    -- Évolution récente
    (SELECT weight FROM weight_history WHERE user_id = u.id ORDER BY recorded_date DESC LIMIT 1) as current_weight,
    (SELECT weight FROM weight_history WHERE user_id = u.id ORDER BY recorded_date ASC LIMIT 1) as initial_weight,
    -- Objectifs
    u.target_weight,
    -- Progression
    CASE 
        WHEN u.target_weight IS NOT NULL 
        THEN (SELECT weight FROM weight_history WHERE user_id = u.id ORDER BY recorded_date DESC LIMIT 1) - u.target_weight
        ELSE NULL
    END as remaining_to_target,
    -- Activité récente
    (SELECT COUNT(*) FROM weight_history WHERE user_id = u.id AND recorded_date > CURRENT_DATE - INTERVAL '30 days') as weigh_ins_30d,
    (SELECT COUNT(*) FROM weight_history WHERE user_id = u.id AND recorded_date > CURRENT_DATE - INTERVAL '7 days') as weigh_ins_7d,
    -- Cache de calculs
    u.cached_bmr,
    u.cached_tdee,
    u.cache_last_updated,
    -- Statut du profil
    u.profile_completed,
    u.profile_validated,
    u.last_profile_update
FROM users u
LEFT JOIN weight_history wh ON u.id = wh.user_id
GROUP BY u.id, u.username, u.target_weight, u.cached_bmr, u.cached_tdee, 
         u.cache_last_updated, u.profile_completed, u.profile_validated, u.last_profile_update;
```

### 6. Triggers Automatiques (PostgreSQL)

#### Trigger pour Historique Automatique du Poids

```sql
-- Fonction trigger
CREATE OR REPLACE FUNCTION fn_weight_history_auto()
RETURNS TRIGGER AS $$
BEGIN
    -- Si le poids a changé, ajouter une entrée dans l'historique
    IF OLD.current_weight IS DISTINCT FROM NEW.current_weight 
       AND NEW.current_weight IS NOT NULL THEN
        
        INSERT INTO weight_history (
            user_id, 
            weight, 
            body_fat_percentage,
            muscle_mass_percentage,
            water_percentage,
            recorded_date,
            notes,
            measurement_method,
            data_source
        ) VALUES (
            NEW.id,
            NEW.current_weight,
            NEW.body_fat_percentage,
            NEW.muscle_mass_percentage,
            NEW.water_percentage,
            CURRENT_DATE,
            'Mise à jour automatique du profil',
            'profile_update',
            'user_profile'
        )
        ON CONFLICT (user_id, recorded_date) 
        DO UPDATE SET 
            weight = EXCLUDED.weight,
            body_fat_percentage = EXCLUDED.body_fat_percentage,
            muscle_mass_percentage = EXCLUDED.muscle_mass_percentage,
            water_percentage = EXCLUDED.water_percentage,
            updated_at = CURRENT_TIMESTAMP;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger
CREATE TRIGGER trg_weight_history_auto
    AFTER UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION fn_weight_history_auto();
```

#### Trigger pour Invalidation du Cache

```sql
-- Fonction trigger
CREATE OR REPLACE FUNCTION fn_cache_update()
RETURNS TRIGGER AS $$
BEGIN
    -- Invalider le cache si des données pertinentes ont changé
    IF OLD.current_weight IS DISTINCT FROM NEW.current_weight
       OR OLD.height IS DISTINCT FROM NEW.height
       OR OLD.age IS DISTINCT FROM NEW.age
       OR OLD.gender IS DISTINCT FROM NEW.gender
       OR OLD.activity_level IS DISTINCT FROM NEW.activity_level THEN
        
        NEW.cached_bmr = NULL;
        NEW.cached_tdee = NULL;
        NEW.cache_last_updated = NULL;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger
CREATE TRIGGER trg_cache_update
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION fn_cache_update();
```

---

## Modèle SQLAlchemy Étendu

### Classe `User` Mise à Jour

```python
class User(db.Model):
    __tablename__ = 'users'
    
    # ... colonnes existantes ...
    
    # Nouvelles colonnes US1.7
    birth_date = db.Column(db.Date, nullable=True)
    goals = db.Column(db.Text, nullable=True)
    medical_conditions = db.Column(db.Text, nullable=True)
    dietary_restrictions = db.Column(db.Text, nullable=True)
    preferred_cuisine_types = db.Column(db.Text, nullable=True)
    
    # Métriques de santé
    body_fat_percentage = db.Column(db.Float, nullable=True)
    muscle_mass_percentage = db.Column(db.Float, nullable=True)
    water_percentage = db.Column(db.Float, nullable=True)
    bone_density = db.Column(db.Float, nullable=True)
    metabolic_age = db.Column(db.Integer, nullable=True)
    
    # Cache de performance
    cached_bmr = db.Column(db.Float, nullable=True)
    cached_tdee = db.Column(db.Float, nullable=True)
    cache_last_updated = db.Column(db.DateTime, nullable=True)
    
    # Relations
    weight_history = relationship('WeightHistory', back_populates='user', cascade='all, delete-orphan')
    goals_history = relationship('UserGoalsHistory', back_populates='user', cascade='all, delete-orphan')
    measurements = relationship('UserMeasurement', back_populates='user', cascade='all, delete-orphan')
    
    # Propriétés calculées
    @property
    def calculated_age(self) -> Optional[int]:
        """Calcule l'âge à partir de la date de naissance"""
        if self.birth_date:
            today = date.today()
            return today.year - self.birth_date.year - (
                (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
            )
        return self.age
    
    @property
    def bmi(self) -> Optional[float]:
        """Calcule l'IMC"""
        if self.current_weight and self.height:
            height_m = self.height / 100
            return round(self.current_weight / (height_m ** 2), 1)
        return None
    
    @property
    def bmr(self) -> Optional[float]:
        """Retourne le BMR calculé ou en cache"""
        # Cache valide pendant 7 jours
        if (self.cached_bmr and self.cache_last_updated and 
            (datetime.utcnow() - self.cache_last_updated).days < 7):
            return self.cached_bmr
        
        # Calcul Harris-Benedict révisé
        if self.current_weight and self.height and self.calculated_age and self.gender:
            if self.gender.lower() == 'male':
                bmr = 88.362 + (13.397 * self.current_weight) + (4.799 * self.height) - (5.677 * self.calculated_age)
            elif self.gender.lower() == 'female':
                bmr = 447.593 + (9.247 * self.current_weight) + (3.098 * self.height) - (4.330 * self.calculated_age)
            else:
                return None
            
            # Mise à jour du cache
            self.cached_bmr = round(bmr, 1)
            self.cache_last_updated = datetime.utcnow()
            return self.cached_bmr
        
        return None
    
    @property
    def tdee(self) -> Optional[float]:
        """Retourne le TDEE calculé ou en cache"""
        if (self.cached_tdee and self.cache_last_updated and 
            (datetime.utcnow() - self.cache_last_updated).days < 7):
            return self.cached_tdee
        
        bmr = self.bmr
        if bmr and self.activity_level:
            multipliers = {
                'sedentary': 1.2,
                'lightly_active': 1.375,
                'moderately_active': 1.55,
                'very_active': 1.725,
                'extremely_active': 1.9
            }
            
            multiplier = multipliers.get(self.activity_level, 1.2)
            tdee = bmr * multiplier
            
            self.cached_tdee = round(tdee, 1)
            self.cache_last_updated = datetime.utcnow()
            return self.cached_tdee
        
        return None
```

### Nouveaux Modèles

```python
class WeightHistory(db.Model):
    """Historique des pesées"""
    __tablename__ = 'weight_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    weight = db.Column(db.Float, nullable=False)
    body_fat_percentage = db.Column(db.Float, nullable=True)
    recorded_date = db.Column(db.Date, nullable=False)
    # ... autres colonnes ...
    
    user = relationship('User', back_populates='weight_history')

class UserGoalsHistory(db.Model):
    """Historique des objectifs"""
    __tablename__ = 'user_goals_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    goal_type = db.Column(db.String(50), nullable=False)
    # ... autres colonnes ...
    
    user = relationship('User', back_populates='goals_history')

class UserMeasurement(db.Model):
    """Mesures corporelles"""
    __tablename__ = 'user_measurements'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    measurement_type = db.Column(db.String(50), nullable=False)
    value = db.Column(db.Float, nullable=False)
    # ... autres colonnes ...
    
    user = relationship('User', back_populates='measurements')
```

---

## Scripts et Outils

### 1. Script de Backup Spécialisé
- **Fichier:** `scripts/backup_restore_us17.py`
- **Fonctions:** Backup complet, export données, validation intégrité, rollback

### 2. Script de Test
- **Fichier:** `scripts/test_us17_migration.py`
- **Fonctions:** Tests automatisés de la migration, validation structure, performance

### 3. Migration Alembic
- **Fichier:** `database/migrations/versions/006_user_profile_real_us17.py`
- **Fonctions:** Migration complète avec rollback

---

## Requêtes Optimisées Types

### Profil Utilisateur Complet
```sql
SELECT * FROM v_user_profile_complete WHERE user_id = ?;
```

### Évolution du Poids (30 derniers jours)
```sql
SELECT * FROM v_weight_evolution 
WHERE user_id = ? 
  AND recorded_date >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY recorded_date;
```

### Statistiques de Progression
```sql
SELECT * FROM v_progress_stats WHERE user_id = ?;
```

### Recherche Utilisateurs par Critères
```sql
SELECT * FROM users 
WHERE profile_completed = true 
  AND is_active = true 
  AND bmi_category = 'normal'
ORDER BY last_profile_update DESC;
```

---

## Monitoring et Maintenance

### Requêtes de Surveillance

**Intégrité des données**
```sql
-- Utilisateurs avec données incohérentes
SELECT id, username, current_weight, height 
FROM users 
WHERE current_weight IS NOT NULL AND current_weight <= 0;

-- Historique orphelin
SELECT COUNT(*) FROM weight_history wh
LEFT JOIN users u ON wh.user_id = u.id
WHERE u.id IS NULL;
```

**Performance**
```sql
-- Utilisation du cache BMR/TDEE
SELECT 
    COUNT(*) as total_users,
    COUNT(cached_bmr) as users_with_bmr_cache,
    COUNT(cached_tdee) as users_with_tdee_cache,
    AVG(EXTRACT(days FROM (CURRENT_TIMESTAMP - cache_last_updated))) as avg_cache_age_days
FROM users 
WHERE profile_completed = true;
```

### Maintenance Recommandée

**Quotidienne**
- Vérification des contraintes d'intégrité
- Nettoyage des caches expirés (> 7 jours)

**Hebdomadaire**
- Analyse des statistiques d'utilisation des index
- Validation de la cohérence des vues

**Mensuelle**
- Archivage des anciens historiques (> 2 ans)
- Optimisation des requêtes basée sur les métriques

---

## Migration et Rollback

### Procédure de Migration

1. **Backup complet pré-migration**
   ```bash
   python scripts/backup_restore_us17.py --action backup --name pre_migration
   ```

2. **Application de la migration**
   ```bash
   alembic upgrade 006
   ```

3. **Validation post-migration**
   ```bash
   python scripts/test_us17_migration.py
   python scripts/backup_restore_us17.py --action validate
   ```

### Procédure de Rollback

1. **Rollback automatique**
   ```bash
   python scripts/backup_restore_us17.py --action rollback --confirm
   ```

2. **Rollback manuel**
   ```bash
   alembic downgrade 005
   ```

---

## Impact sur les Performances

### Optimisations Implémentées

1. **Cache BMR/TDEE** - Réduit les calculs répétitifs
2. **Index composites** - Optimise les requêtes fréquentes
3. **Vues pré-calculées** - Accélère les rapports
4. **Contraintes efficaces** - Validation rapide des données

### Métriques de Performance Attendues

- **Requête profil complet** : < 10ms
- **Historique poids (30 jours)** : < 20ms
- **Statistiques utilisateur** : < 50ms
- **Recherche utilisateurs** : < 100ms

---

## Sécurité et Conformité

### Données Sensibles

- **Conditions médicales** : Chiffrement recommandé en production
- **Données de santé** : Anonymisation pour les rapports
- **Audit trail** : Toutes les modifications tracées

### Conformité RGPD

- **Droit à l'oubli** : Suppression en cascade implémentée
- **Portabilité** : Export JSON complet disponible
- **Consentement** : Flags de validation du profil

---

Cette implémentation fournit une base robuste et évolutive pour le Profil Utilisateur Réel, avec des performances optimisées et une traçabilité complète des données de santé.