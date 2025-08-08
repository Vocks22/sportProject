# 💎 US 2.6 - Features Premium

> **Status** : 🔴 À FAIRE
> **Points** : 21
> **Sprint** : 8
> **Date prévue** : 14-27 Oct 2025
> **Développeur** : Non assigné
> **Reviewer** : À définir

[[../SCRUM_DASHBOARD|← Dashboard]] | [[../epics/EPIC-2-Advanced|← Epic 2]]

---

## 📝 User Story

### En tant que...
Utilisateur power user voulant plus de fonctionnalités

### Je veux...
Accéder à des features premium via abonnement

### Afin de...
Avoir une expérience enrichie et des outils avancés pour atteindre mes objectifs plus rapidement

---

## 🎯 Acceptance Criteria

- [ ] **Système d'Abonnement**
  - Plans : Free, Premium, Family
  - Paiement mensuel/annuel
  - Essai gratuit 14 jours
  - Gestion via Stripe

- [ ] **Features Premium**
  - Recettes illimitées (vs 50)
  - IA Nutritionniste
  - Export illimité
  - Analytics avancés
  - Pas de publicité
  - Support prioritaire
  - Thèmes personnalisés

- [ ] **Paywall Smart**
  - Teasing features locked
  - Upgrade prompts contextuels
  - Pricing dynamique
  - Offres spéciales

- [ ] **Gestion Abonnement**
  - Upgrade/Downgrade
  - Pause abonnement
  - Historique factures
  - Annulation facile

---

## 🛠️ Solution Technique

### Modèle Subscription

```python
class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    plan = db.Column(db.Enum('free', 'premium', 'family'))
    status = db.Column(db.Enum('active', 'cancelled', 'expired', 'trial'))
    stripe_subscription_id = db.Column(db.String(100))
    current_period_start = db.Column(db.DateTime)
    current_period_end = db.Column(db.DateTime)
    trial_end = db.Column(db.DateTime)
    
    def has_feature(self, feature):
        """Vérifie accès à une feature"""
        features_map = {
            'free': ['basic_recipes', 'basic_planning'],
            'premium': ['unlimited_recipes', 'ai_coach', 'advanced_analytics'],
            'family': ['all_premium', 'multi_profiles']
        }
        return feature in features_map.get(self.plan, [])
```

### Stripe Integration

```javascript
const PremiumUpgrade = () => {
  const handleSubscribe = async (priceId) => {
    const { sessionId } = await api.post('/api/create-checkout-session', {
      priceId,
      successUrl: window.location.origin + '/success',
      cancelUrl: window.location.origin + '/premium'
    });
    
    const stripe = await loadStripe(STRIPE_PUBLIC_KEY);
    await stripe.redirectToCheckout({ sessionId });
  };
  
  return (
    <div className="pricing-table">
      <PlanCard 
        name="Premium"
        price="9.99€"
        features={premiumFeatures}
        onSubscribe={() => handleSubscribe('price_premium_monthly')}
      />
    </div>
  );
};
```

---

## 💰 Pricing Strategy

| Plan | Mensuel | Annuel | Features |
|------|---------|--------|----------|
| Free | 0€ | 0€ | Basique |
| Premium | 9.99€ | 89.99€ | Toutes features |
| Family | 14.99€ | 134.99€ | 5 profils + Premium |

---

## 📊 Métriques

- Conversion free→premium : 8%
- Churn mensuel : < 5%
- LTV : 180€
- Trial conversion : 40%

---

[[../SCRUM_DASHBOARD|← Dashboard]] | [[US-2.5-Notifications|← US 2.5]] | [[US-2.7-API-Integration|US 2.7 →]]