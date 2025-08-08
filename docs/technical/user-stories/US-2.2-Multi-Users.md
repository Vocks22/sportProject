# 👥 US 2.2 - Multi-utilisateurs & Comptes Famille

> **Status** : 🔴 À FAIRE
> **Points** : 13
> **Sprint** : 5
> **Date prévue** : 02-15 Sept 2025
> **Développeur** : Non assigné
> **Reviewer** : À définir

[[../SCRUM_DASHBOARD|← Dashboard]] | [[../epics/EPIC-2-Advanced|← Epic 2]]

---

## 📝 User Story

### En tant que...
Chef de famille gérant l'alimentation du foyer

### Je veux...
Pouvoir créer plusieurs profils sous un seul compte

### Afin de...
Gérer l'alimentation de toute ma famille avec des besoins nutritionnels différents

---

## 🎯 Acceptance Criteria

- [ ] **Gestion des profils**
  - Jusqu'à 5 profils par compte
  - Profil principal (admin)
  - Profils secondaires avec permissions
  - Switch rapide entre profils

- [ ] **Personnalisation par profil**
  - Objectifs nutritionnels individuels
  - Préférences alimentaires
  - Allergies et restrictions
  - Historique séparé

- [ ] **Planning familial**
  - Vue consolidée famille
  - Planning individuel par membre
  - Repas partagés vs individuels
  - Portions ajustées par personne

- [ ] **Liste de courses unifiée**
  - Agrégation tous profils
  - Identification par membre
  - Quantités totales famille
  - Budget par personne

- [ ] **Permissions et contrôles**
  - Admin peut tout modifier
  - Enfants accès limité
  - Privacy entre profils
  - Contrôle parental

---

## 🛠️ Solution Technique Proposée

### Modèle de données

```python
class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    subscription_type = db.Column(db.Enum('free', 'family', 'premium'))
    profiles = db.relationship('Profile', backref='account')
    max_profiles = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime)

class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'))
    name = db.Column(db.String(50))
    avatar_url = db.Column(db.String(200))
    role = db.Column(db.Enum('admin', 'adult', 'teen', 'child'))
    
    # Données personnelles
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    weight = db.Column(db.Float)
    height = db.Column(db.Float)
    activity_level = db.Column(db.String(20))
    
    # Préférences
    dietary_restrictions = db.Column(db.JSON)
    allergies = db.Column(db.JSON)
    preferences = db.Column(db.JSON)
    
    # Objectifs
    calorie_goal = db.Column(db.Integer)
    protein_goal = db.Column(db.Float)
    carbs_goal = db.Column(db.Float)
    fat_goal = db.Column(db.Float)
    
    # Relations
    meal_plans = db.relationship('MealPlan', backref='profile')
    measurements = db.relationship('Measurement', backref='profile')
```

### Architecture Multi-tenant

```javascript
// Context pour gestion multi-profils
const FamilyContext = createContext();

export const FamilyProvider = ({ children }) => {
  const [activeProfile, setActiveProfile] = useState(null);
  const [familyProfiles, setFamilyProfiles] = useState([]);
  
  const switchProfile = (profileId) => {
    const profile = familyProfiles.find(p => p.id === profileId);
    setActiveProfile(profile);
    localStorage.setItem('activeProfileId', profileId);
  };
  
  const createProfile = async (profileData) => {
    if (familyProfiles.length >= maxProfiles) {
      throw new Error('Limite de profils atteinte');
    }
    // API call to create profile
  };
  
  return (
    <FamilyContext.Provider value={{
      activeProfile,
      familyProfiles,
      switchProfile,
      createProfile,
      isAdmin: activeProfile?.role === 'admin'
    }}>
      {children}
    </FamilyContext.Provider>
  );
};
```

---

## 📊 Fonctionnalités Avancées

### Planning Familial Intelligent

```python
def generate_family_meal_plan(account_id, week):
    """
    Génère un planning optimisé pour toute la famille
    """
    profiles = Profile.query.filter_by(account_id=account_id).all()
    
    family_plan = {
        'shared_meals': [],  # Repas partagés
        'individual_meals': {},  # Repas individuels
        'shopping_list': []  # Liste courses consolidée
    }
    
    for meal_slot in ['breakfast', 'lunch', 'dinner']:
        # Détecter si repas peut être partagé
        can_share = check_dietary_compatibility(profiles)
        
        if can_share:
            # Un seul repas avec portions ajustées
            shared_recipe = find_compatible_recipe(profiles)
            portions = calculate_family_portions(shared_recipe, profiles)
            family_plan['shared_meals'].append({
                'recipe': shared_recipe,
                'portions': portions
            })
        else:
            # Repas individuels
            for profile in profiles:
                individual_meal = generate_individual_meal(profile)
                family_plan['individual_meals'][profile.id] = individual_meal
    
    return family_plan
```

### Dashboard Famille

| Membre | Calories | Protéines | Objectif | Progression |
|--------|----------|-----------|----------|-------------|
| Papa | 2200/2500 | 120g | Maintien | ████████░░ 88% |
| Maman | 1650/1800 | 90g | -5kg/mois | █████████░ 92% |
| Tom (14) | 2100/2300 | 100g | Croissance | █████████░ 91% |
| Emma (8) | 1400/1600 | 60g | Santé | ████████░░ 87% |

---

## 🆘 UI/UX Spécifique

### Sélecteur de Profil

```jsx
const ProfileSwitcher = () => {
  const { familyProfiles, activeProfile, switchProfile } = useFamily();
  
  return (
    <div className="profile-switcher">
      {familyProfiles.map(profile => (
        <button
          key={profile.id}
          onClick={() => switchProfile(profile.id)}
          className={activeProfile?.id === profile.id ? 'active' : ''}
        >
          <Avatar src={profile.avatar} />
          <span>{profile.name}</span>
          {profile.role === 'child' && <LockIcon />}
        </button>
      ))}
      <button className="add-profile">
        <PlusIcon /> Ajouter
      </button>
    </div>
  );
};
```

### Permissions par Rôle

| Fonctionnalité | Admin | Adulte | Ado | Enfant |
|----------------|-------|--------|-----|--------|
| Voir tous profils | ✅ | ✅ | ❌ | ❌ |
| Modifier planning | ✅ | ✅ | ✅ | ❌ |
| Gérer abonnement | ✅ | ❌ | ❌ | ❌ |
| Supprimer profil | ✅ | ❌ | ❌ | ❌ |
| Voir statistiques | ✅ | ✅ | ✅ | 🔶 |

---

## 🧪 Tests

### Tests unitaires
- [ ] Création profils multiples
- [ ] Validation limites (5 max)
- [ ] Permissions par rôle
- [ ] Calculs nutritionnels par profil

### Tests d'intégration
- [ ] Switch profil complet
- [ ] Planning familial généré
- [ ] Liste courses agrégée
- [ ] Sync cross-device

### Tests utilisabilité
- [ ] Navigation entre profils
- [ ] Clarté des permissions
- [ ] Performance 5 profils

---

## 📊 Métriques de Succès

### KPIs à mesurer
- Taux adoption compte famille : > 30%
- Profils moyens par compte : 3.2
- Rétention +6 mois : +45%
- Engagement cross-profil : 80%

### Impact business
- Upsell vers plan famille
- Réduction churn familial
- Augmentation LTV client

---

## 🆘 Risques

| Risque | Probabilité | Impact | Mitigation |
|--------|-------------|---------|------------|
| Complexité UX | Haute | Moyen | User testing intensif |
| Performance | Moyenne | Haut | Caching agressif |
| Privacy concerns | Moyenne | Haut | Encryption profils |
| Conflits planning | Haute | Faible | Règles priorité |

---

## 💡 Notes d'implémentation

### Pricing
- **Free** : 1 profil
- **Family** : 5 profils - 9.99€/mois
- **Premium** : Illimité - 14.99€/mois

### Améliorations futures
- Profils temporaires (invités)
- Partage entre familles
- Sync avec Google Family
- Gamification enfants

---

[[../SCRUM_DASHBOARD|← Dashboard]] | [[US-2.1-Auth|← US 2.1]] | [[US-2.3-Export|US 2.3 →]]