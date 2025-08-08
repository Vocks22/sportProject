# 🔔 US 3.5 - Notifications Push

> **Status** : 📝 À FAIRE
> **Points** : 5
> **Sprint** : À planifier
> **Date de livraison** : À définir
> **Développeur** : À assigner
> **Reviewer** : À assigner

[[../SCRUM_DASHBOARD|← Dashboard]] | [[../epics/EPIC-3-Mobile|← Epic Mobile]]

---

## 📝 User Story

### En tant que...
Utilisateur de l'application mobile DietTracker

### Je veux...
Recevoir des notifications pertinentes et personnalisées pour mes repas et objectifs

### Afin de...
Rester engagé dans mon suivi nutritionnel et ne pas oublier d'enregistrer mes repas

---

## ✅ Acceptance Criteria

- [ ] **Types de notifications**
  - Rappels de repas (petit-déj, déjeuner, dîner)
  - Rappel saisie quotidienne
  - Objectifs atteints
  - Planning hebdomadaire disponible
  - Liste de courses générée
  - Tips nutritionnels
  - Nouvelles recettes matching préférences

- [ ] **Personnalisation**
  - Horaires configurables par repas
  - Fréquence ajustable
  - Types activables/désactivables
  - Mode Ne Pas Déranger
  - Jours de la semaine
  - Snooze temporaire

- [ ] **Contenu intelligent**
  - Messages personnalisés
  - Emojis contextuels
  - Quick actions (log meal, view recipe)
  - Deep linking vers sections
  - Rich notifications (images)

- [ ] **Gestion des préférences**
  - Settings in-app détaillés
  - Opt-in/out granulaire
  - Historique notifications
  - Analytics engagement
  - A/B testing messages

- [ ] **Compliance**
  - Permission iOS/Android
  - RGPD consent
  - Unsubscribe facile
  - Data minimization

---

## 🔧 Technical Requirements

### Services Push
- **iOS** : APNs (Apple Push Notification service)
- **Android** : FCM (Firebase Cloud Messaging)
- **Backend** : Node.js + Bull Queue
- **Alternative** : OneSignal / Pusher

### Architecture
```javascript
// Notification Service
- Token management
- Segmentation utilisateurs
- Scheduling (cron jobs)
- Template engine
- Delivery tracking
- Retry mechanism
```

### Payload Structure
```json
{
  "title": "🥗 Heure du déjeuner!",
  "body": "N'oubliez pas d'enregistrer votre repas",
  "data": {
    "type": "meal_reminder",
    "meal": "lunch",
    "deepLink": "/log-meal/lunch"
  },
  "badge": 1,
  "sound": "default"
}
```

---

## 📊 Definition of Done

- [ ] Code review approuvé
- [ ] Tests unitaires (>80% coverage)
- [ ] Tests sur devices réels
- [ ] Taux de delivery > 95%
- [ ] Documentation technique
- [ ] Settings UI complet
- [ ] Analytics intégrés
- [ ] Validation Product Owner

---

## 🎯 Sprint Planning

### Découpage des tâches
1. **Infrastructure** (1 pt)
   - FCM/APNs setup
   - Token management
   - Backend service

2. **Scheduling** (1 pt)
   - Cron jobs
   - Time zones
   - Queue system

3. **UI Settings** (1 pt)
   - Preferences screen
   - Permission flow
   - Toggle controls

4. **Templates** (1 pt)
   - Message templates
   - Personalization
   - Localization

5. **Analytics** (1 pt)
   - Tracking delivery
   - Engagement metrics
   - A/B testing

---

## 📝 Notes

### Risques identifiés
- Battery drain si trop fréquent
- Notification fatigue
- Permissions refusées
- Delivery rates variables
- Time zones complexes

### Best Practices
- Max 2-3 notifications/jour
- Timing intelligent (pas pendant repas)
- Messages variés (éviter répétition)
- Value-driven content
- Respect quiet hours

### Métriques de succès
- 60% opt-in rate
- 25% click-through rate
- < 5% unsubscribe/mois
- +30% engagement quotidien
- 4.5/5 satisfaction

---

## 🔗 Liens

- [[US-3.1-React-Native|US 3.1 - App Mobile]]
- [[US-3.6-Widgets|US 3.6 - Widgets]]
- [[US-1.8-Suivi-Repas|US 1.8 - Suivi Repas]]