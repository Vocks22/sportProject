# 🚀 EPIC 2 - Features Avancées

> **Status** : 🔵 NON DÉMARRÉ
> **Points totaux** : 120
> **Points complétés** : 0
> **Priorité** : 🟡 MOYENNE
> **Sprint prévu** : Sprints 5-8 (Sept-Oct 2025)

[[../SCRUM_DASHBOARD|← Retour au Dashboard]]

---

## 📝 Description

### Vision
Transformer DietTracker en une plateforme collaborative et sociale permettant le partage, l'authentification multi-utilisateurs et l'export de données.

### Objectifs Business
- Augmenter la rétention utilisateur de 40%
- Permettre l'usage familial (compte famille)
- Monétisation via features premium
- Création d'une communauté d'utilisateurs

### Valeur Utilisateur
En tant qu'utilisateur régulier, je veux des fonctionnalités avancées pour personnaliser mon expérience et partager avec ma communauté.

---

## 📊 User Stories

### 🔴 À Faire

#### [[../user-stories/US-2.1-Auth|US 2.1 - Authentification JWT]]
**Points** : 8 | **Priorité** : HAUTE | **Sprint** : 5

**Résumé pour PM** : Système de connexion sécurisé avec tokens JWT pour protéger les données utilisateur.

**Acceptance Criteria** :
- [ ] Login/Logout sécurisé
- [ ] Refresh tokens
- [ ] Password reset
- [ ] Email verification

---

#### [[../user-stories/US-2.2-Multi-Users|US 2.2 - Multi-utilisateurs]]
**Points** : 13 | **Priorité** : HAUTE | **Sprint** : 5

**Résumé pour PM** : Permettre plusieurs profils par compte (famille) avec gestion des permissions.

**Livrables** :
- Comptes famille (jusqu'à 5 profils)
- Permissions par profil
- Partage de recettes entre profils
- Planning familial unifié

---

#### [[../user-stories/US-2.3-Export|US 2.3 - Export PDF/Excel]]
**Points** : 5 | **Priorité** : MOYENNE | **Sprint** : 6

**Résumé pour PM** : Exporter les données en formats standards pour analyse externe.

**Formats supportés** :
- PDF pour planning hebdomadaire
- Excel pour données nutritionnelles
- CSV pour historique poids
- JSON pour backup complet

---

#### [[../user-stories/US-2.4-Social|US 2.4 - Partage Social]]
**Points** : 8 | **Priorité** : MOYENNE | **Sprint** : 6

**Résumé pour PM** : Partager ses réussites et recettes sur les réseaux sociaux.

**Features** :
- Partage de progression
- Recettes publiques/privées
- Challenges entre amis
- Intégration Instagram/Facebook

---

#### [[../user-stories/US-2.5-Notifications|US 2.5 - Système de Notifications]]
**Points** : 13 | **Priorité** : HAUTE | **Sprint** : 7

**Résumé pour PM** : Rappels et notifications push pour améliorer l'engagement.

**Types de notifications** :
- Rappel de pesée hebdomadaire
- Heure des repas
- Objectifs atteints
- Planning non rempli

---

#### [[../user-stories/US-2.6-Premium|US 2.6 - Features Premium]]
**Points** : 21 | **Priorité** : BASSE | **Sprint** : 8

**Résumé pour PM** : Monétisation via abonnement premium.

**Features Premium** :
- Recettes illimitées
- Coaching IA personnalisé
- Analytics avancés
- Pas de publicité
- Support prioritaire

---

#### [[../user-stories/US-2.7-API-Integration|US 2.7 - Intégrations API]]
**Points** : 13 | **Priorité** : BASSE | **Sprint** : 8

**Résumé pour PM** : Connecté avec des services tiers pour enrichir l'expérience.

**Intégrations prévues** :
- Google Fit / Apple Health
- MyFitnessPal sync
- Fitbit / Garmin
- Calendrier Google/Outlook

---

## 📈 Métriques de l'Epic

### Progression
```
US 2.1 Auth       ░░░░░░░░░░ 0%
US 2.2 Multi-user ░░░░░░░░░░ 0%
US 2.3 Export     ░░░░░░░░░░ 0%
US 2.4 Social     ░░░░░░░░░░ 0%
US 2.5 Notifs     ░░░░░░░░░░ 0%
US 2.6 Premium    ░░░░░░░░░░ 0%
US 2.7 API        ░░░░░░░░░░ 0%

Total: 0/86 points (0%)
```

### KPIs Prévus
- **Rétention** : +40% après implémentation
- **Engagement** : 2x sessions/semaine
- **Conversion Premium** : 5% des utilisateurs
- **Partages sociaux** : 100/mois

---

## 🔗 Dépendances

### Techniques
- Auth0 ou JWT custom
- Stripe pour paiements
- SendGrid pour emails
- OneSignal pour push

### Prerequisites
- Epic 1 (MVP) terminé à 100%
- Tests E2E en place
- Infrastructure scaling ready

---

## 🚀 Definition of Done

Pour que l'Epic soit considéré comme terminé :

1. ☐ Sécurité auditée (OWASP)
2. ☐ RGPD compliant
3. ☐ Tests de charge validés
4. ☐ Documentation API complète
5. ☐ Onboarding utilisateur optimisé
6. ☐ Métriques de succès atteintes

---

## 📝 Notes pour le Tech Lead

### Architecture
- Migration vers microservices recommandée
- Auth service séparé
- Queue system pour notifications
- CDN pour assets

### Stack technique suggérée
- **Auth** : Auth0 ou Supabase
- **Payments** : Stripe
- **Notifications** : RabbitMQ + OneSignal
- **Export** : Puppeteer pour PDF

### Points d'attention
1. Scalabilité multi-tenant
2. Sécurité des données sensibles
3. Performance avec users multiples
4. Gestion des limites API tierces

---

## 💼 Notes pour le Product Manager

### Stratégie de lancement
1. **Phase 1** : Auth + Multi-users (MVP social)
2. **Phase 2** : Export + Notifications
3. **Phase 3** : Premium + Intégrations

### Pricing suggéré
- **Free** : 1 utilisateur, 50 recettes
- **Family** : 9.99€/mois, 5 utilisateurs
- **Premium** : 14.99€/mois, illimité

### Risques
- Complexité UX avec multi-users
- Coût infrastructure augmenté
- Support client à prévoir
- RGPD compliance critique

---

[[../SCRUM_DASHBOARD|← Retour au Dashboard]] | [[EPIC-3-Mobile|Epic 3 →]]