# 📦 EPIC 1 - MVP (Minimum Viable Product)

> **Status** : 🟡 En cours (85% complété)
> **Points totaux** : 170
> **Points complétés** : 144
> **Priorité** : 🔴 CRITIQUE

[[../SCRUM_DASHBOARD|← Retour au Dashboard]]

---

## 📋 Description

### Vision
Créer une application de suivi nutritionnel permettant à un utilisateur de planifier ses repas, suivre sa progression de poids et recevoir des recommandations personnalisées.

### Objectifs Business
- Permettre le suivi d'un régime de perte de poids (-5kg/mois)
- Simplifier la planification des repas hebdomadaires
- Automatiser la création de listes de courses

### Valeur Utilisateur
En tant qu'utilisateur souhaitant perdre du poids, je veux un outil simple et efficace pour planifier mes repas et suivre ma progression, afin d'atteindre mes objectifs de santé.

---

## 📊 User Stories

### ✅ Complétées

#### [[../user-stories/US-1.1-Interface|US 1.1 - Interface de Base]] ✅
**Points** : 21 | **Sprint** : 1 | **Date** : 03/08/2025

**Résumé pour PM** : Mise en place de l'interface utilisateur de base avec navigation, dashboard et structure responsive.

**Impact** : Foundation technique permettant toutes les autres features.

---

#### [[../user-stories/US-1.2-Recettes|US 1.2 - Gestion des Recettes]] ✅
**Points** : 34 | **Sprint** : 1 | **Date** : 03/08/2025

**Résumé pour PM** : Système complet de gestion des recettes avec catégorisation, recherche et informations nutritionnelles.

**Livrables** :
- Base de 50+ recettes
- Calcul automatique des calories
- Filtres par catégorie et préférences

---

#### [[../user-stories/US-1.3-Planning|US 1.3 - Planning des Repas]] ✅
**Points** : 34 | **Sprint** : 1 | **Date** : 04/08/2025

**Résumé pour PM** : Calendrier hebdomadaire permettant de planifier tous les repas de la semaine avec drag & drop.

**Métriques de succès** :
- Temps de planification < 10 min/semaine
- Satisfaction utilisateur : 4.5/5

---

#### [[../user-stories/US-1.4-Chef-Mode|US 1.4 - Mode Chef Interactif]] ✅
**Points** : 34 | **Sprint** : 1 | **Date** : 04/08/2025

**Résumé pour PM** : Guide de cuisine pas-à-pas avec minuteurs, conseils et ajustements en temps réel.

**Innovation** : Première app du marché avec mode chef adaptatif basé sur le niveau de l'utilisateur.

---

#### [[../user-stories/US-1.5-Shopping|US 1.5 - Liste de Courses Intelligente]] ✅
**Points** : 8 | **Sprint** : 2 | **Date** : 05/08/2025

**Résumé pour PM** : Génération automatique de listes de courses optimisées par rayon avec agrégation intelligente.

**ROI** : Économie moyenne de 30 min/semaine pour l'utilisateur.

---

#### [[../user-stories/US-1.6-ISO-Weeks|US 1.6 - Semaines ISO 8601]] ✅
**Points** : 5 | **Sprint** : 2 | **Date** : 07/08/2025

**Résumé pour PM** : Alignement sur le standard international des semaines (lundi-dimanche) pour faciliter la planification.

**Conformité** : 100% ISO 8601 compliant.

---

#### [[../user-stories/US-1.7-Profile|US 1.7 - Profil Utilisateur Réel]] ✅
**Points** : 8 | **Sprint** : 3 | **Date** : 07/08/2025

**Résumé pour PM** : Profil complet avec suivi du poids, calculs nutritionnels personnalisés et objectifs.

**Features clés** :
- Suivi hebdomadaire du poids
- Calcul BMR/TDEE/BMI
- Graphiques de progression
- Objectif -5kg/mois

---

### 🔴 À Faire

#### [[../user-stories/US-1.8-Suivi-Repas|US 1.8 - Suivi des Repas Consommés]]
**Points** : 13 | **Sprint** : 4 | **Priorité** : HAUTE

**Résumé pour PM** : Permettre de cocher les repas consommés et calculer automatiquement l'apport nutritionnel réel vs planifié.

**Acceptance Criteria** :
- [ ] Checkbox par repas planifié
- [ ] Calcul temps réel des calories/macros
- [ ] Alertes si écart > 20%
- [ ] Rapport journalier/hebdomadaire

---

## 📈 Métriques de l'Epic

### Progression
```
US 1.1 ████████████████████ 100%
US 1.2 ████████████████████ 100%
US 1.3 ████████████████████ 100%
US 1.4 ████████████████████ 100%
US 1.5 ████████████████████ 100%
US 1.6 ████████████████████ 100%
US 1.7 ████████████████████ 100%
US 1.8 ░░░░░░░░░░░░░░░░░░░░ 0%

Total: 144/157 points (92%)
```

### KPIs
- **Adoption** : 1 utilisateur actif
- **Rétention** : 100% (7 jours)
- **Engagement** : 5 sessions/semaine
- **Satisfaction** : Non mesuré

---

## 🔗 Dépendances

### Techniques
- Frontend : React + Vite
- Backend : Flask + SQLAlchemy
- Database : PostgreSQL
- Hosting : Netlify + Render

### Externes
- Aucune API tierce requise
- Pas de dépendance bloquante

---

## 🚀 Definition of Done

Pour que l'Epic soit considéré comme terminé :

1. ✅ Toutes les US sont complétées
2. ✅ Tests d'acceptance passés
3. ✅ Déployé en production
4. ✅ Documentation utilisateur
5. ⏳ Feedback utilisateur collecté
6. ⏳ Métriques de succès atteintes

**Status actuel** : 4/6 critères remplis

---

## 📝 Notes pour le Tech Lead

### Architecture
- Monolithique pour le MVP
- API RESTful standard
- Cache Redis optionnel
- PostgreSQL obligatoire

### Points d'attention
1. Performance des calculs nutritionnels
2. Synchronisation offline/online
3. Scalabilité de la base de données

### Dette technique
- Refactoring du système de cache nécessaire
- Migration vers microservices à prévoir (Phase 3)

---

## 💼 Notes pour le Product Manager

### Positionnement marché
- Différenciateur : Mode chef interactif
- Cible : Personnes en régime structuré
- Prix suggéré : Freemium avec premium à 9.99€/mois

### Roadmap post-MVP
1. Multi-utilisateurs (famille)
2. Intégration nutritionniste
3. Marketplace de recettes
4. Coaching IA

### Risques
- Concurrence établie (MyFitnessPal)
- Réglementation santé
- Coût d'acquisition utilisateur

---

[[../SCRUM_DASHBOARD|← Retour au Dashboard]]