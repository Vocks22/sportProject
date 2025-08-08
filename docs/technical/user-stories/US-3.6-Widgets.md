# 📊 US 3.6 - Widgets Écran d'Accueil

> **Status** : 📝 À FAIRE
> **Points** : 8
> **Sprint** : À planifier
> **Date de livraison** : À définir
> **Développeur** : À assigner
> **Reviewer** : À assigner

[[../SCRUM_DASHBOARD|← Dashboard]] | [[../epics/EPIC-3-Mobile|← Epic Mobile]]

---

## 📝 User Story

### En tant que...
Utilisateur voulant un accès rapide à mes données nutritionnelles

### Je veux...
Des widgets sur mon écran d'accueil pour visualiser et interagir avec mes données sans ouvrir l'app

### Afin de...
Suivre mes objectifs nutritionnels d'un coup d'œil et enregistrer rapidement mes repas

---

## ✅ Acceptance Criteria

- [ ] **Types de widgets**
  - Calories du jour (consommées/objectif)
  - Macros circulaire (protéines, glucides, lipides)
  - Prochain repas planifié
  - Quick log (ajout rapide)
  - Eau consommée
  - Streaks (jours consécutifs)
  - Recette du jour

- [ ] **Tailles supportées**
  - Small (2x2) : Une métrique
  - Medium (4x2) : Graphique ou multi-métriques
  - Large (4x4) : Dashboard complet
  - iOS 14+ Widget families
  - Android resizable widgets

- [ ] **Interactions**
  - Tap pour ouvrir section app
  - Long press pour options
  - Quick actions (iOS)
  - Refresh pull (Android)
  - Configuration depuis app

- [ ] **Personnalisation**
  - Choix des métriques
  - Couleurs/thèmes
  - Période affichée
  - Unités (kcal, kJ)
  - Transparence

- [ ] **Mise à jour**
  - Refresh automatique (timeline)
  - Update après log meal
  - Sync avec app ouverte
  - Background refresh intelligent

---

## 🔧 Technical Requirements

### iOS Widgets
```swift
// WidgetKit Framework
- SwiftUI views
- Timeline Provider
- Intents Configuration
- App Groups (data sharing)
- Background Processing
```

### Android Widgets
```kotlin
// App Widget Framework
- RemoteViews
- AppWidgetProvider
- PendingIntent
- WorkManager updates
- Glance (Jetpack Compose)
```

### Data Sync
- Shared container (iOS)
- Content Provider (Android)
- Real-time updates
- Cache optimization

---

## 📊 Definition of Done

- [ ] Code review approuvé
- [ ] Tests unitaires (>75% coverage)
- [ ] Tests sur différentes tailles écran
- [ ] Documentation configuration
- [ ] Performance validée
- [ ] < 50ms render time
- [ ] Accessibilité testée
- [ ] Validation Product Owner

---

## 🎯 Sprint Planning

### Découpage des tâches
1. **Architecture widgets** (2 pts)
   - Data layer sharing
   - Update mechanism
   - Timeline setup

2. **iOS implementation** (2 pts)
   - WidgetKit setup
   - SwiftUI views
   - Configuration

3. **Android implementation** (2 pts)
   - AppWidget setup
   - RemoteViews
   - Glance migration

4. **UI/UX** (1 pt)
   - Designs par taille
   - Animations
   - Dark mode

5. **Testing** (1 pt)
   - Different sizes
   - Update scenarios
   - Battery impact

---

## 📝 Notes

### Risques identifiés
- Limite refresh iOS (budget)
- Complexité partage données
- Performance sur anciens OS
- Battery drain potentiel
- Inconsistance cross-platform

### Optimisations
- Batch updates
- Smart refresh scheduling
- Image caching
- Minimal data transfer
- Progressive disclosure

### Guidelines Platform
- iOS: Max 4 timeline entries/heure
- Android: Max 30min update interval
- Taille max: iOS 5MB, Android 2MB
- Respecter system theme

### Métriques de succès
- 40% utilisateurs ajoutent widget
- 70% retention après 30 jours
- +25% engagement quotidien
- < 1% impact batterie
- 4.5/5 rating widgets

---

## 🔗 Liens

- [[US-3.1-React-Native|US 3.1 - App Mobile]]
- [[US-3.5-Notifications|US 3.5 - Notifications]]
- [[US-1.8-Suivi-Repas|US 1.8 - Suivi Repas]]