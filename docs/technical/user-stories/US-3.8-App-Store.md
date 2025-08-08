# 🚀 US 3.8 - Publication App Stores

> **Status** : 📝 À FAIRE
> **Points** : 13
> **Sprint** : À planifier
> **Date de livraison** : À définir
> **Développeur** : À assigner
> **Reviewer** : À assigner

[[../SCRUM_DASHBOARD|← Dashboard]] | [[../epics/EPIC-3-Mobile|← Epic Mobile]]

---

## 📝 User Story

### En tant que...
Product Owner de DietTracker

### Je veux...
Publier l'application mobile sur l'App Store iOS et Google Play Store

### Afin de...
Rendre l'application accessible au grand public et permettre sa distribution officielle sur les stores

---

## ✅ Acceptance Criteria

- [ ] **Préparation App Store (iOS)**
  - Compte Apple Developer ($99/an)
  - Certificats et provisioning profiles
  - App Store Connect configuration
  - TestFlight beta testing
  - Screenshots (6.5", 5.5", iPad)
  - App Preview video
  - Metadata multilingue

- [ ] **Préparation Google Play**
  - Compte Google Play Console ($25)
  - Signing keys configuration
  - Play Console setup
  - Internal/Beta testing tracks
  - Screenshots (phone, tablet, wear)
  - Feature graphic
  - Privacy policy

- [ ] **Conformité & Legal**
  - RGPD compliance
  - Privacy Policy
  - Terms of Service
  - Age rating (4+, Everyone)
  - Content rating questionnaire
  - Export compliance
  - Licences open source

- [ ] **Optimisation ASO**
  - Titre optimisé (30 car)
  - Description courte/longue
  - Keywords research
  - Catégorie appropriée
  - Icône haute résolution
  - Localisation (5+ langues)
  - A/B testing assets

- [ ] **Build Production**
  - Code obfuscation
  - Minification assets
  - App bundles (AAB)
  - Universal binary iOS
  - Crash reporting setup
  - Analytics integration
  - Version numbering

- [ ] **Process de release**
  - CI/CD pipeline
  - Automated builds
  - Code signing
  - Release notes
  - Staged rollout
  - Rollback plan

---

## 🔧 Technical Requirements

### Build Configuration
```javascript
// iOS Release
- Xcode Archive
- Bitcode enabled
- dSYM files
- App thinning
- ProGuard rules

// Android Release
- AAB format
- R8/ProGuard
- Multi-APK support
- App signing v2
- Baseline profiles
```

### Store Requirements
| Critère | App Store | Google Play |
|---------|-----------|-------------|
| Taille max | 4GB | 150MB APK |
| Min OS | iOS 13+ | Android 7+ |
| Review | 24-48h | 2-3h |
| Updates | Manual review | Auto-publish |
| Beta | TestFlight | Open/Closed |

### Monitoring Post-Launch
- Crashlytics
- Performance monitoring
- User reviews tracking
- Download analytics
- Revenue reporting

---

## 📊 Definition of Done

- [ ] Code review final approuvé
- [ ] Tests E2E complets passants
- [ ] Build production signé
- [ ] Metadata complet (2 langues min)
- [ ] Assets conformes guidelines
- [ ] Beta testing validé (50+ users)
- [ ] Documentation mise à jour
- [ ] Store listing approuvé
- [ ] Validation Product Owner

---

## 🎯 Sprint Planning

### Découpage des tâches
1. **Setup accounts** (2 pts)
   - Developer accounts
   - Banking/tax info
   - Team management

2. **Assets création** (3 pts)
   - Screenshots
   - Videos
   - Graphics
   - Translations

3. **Build pipeline** (3 pts)
   - CI/CD setup
   - Signing automation
   - Version management

4. **Beta testing** (2 pts)
   - TestFlight setup
   - Play Console tracks
   - Feedback collection

5. **Store submission** (3 pts)
   - Listing optimization
   - Review preparation
   - Launch coordination

---

## 📝 Notes

### Risques identifiés
- Rejet App Store (guidelines strictes)
- Délais review imprévisibles
- Metadata rejection
- Crash au lancement
- Mauvaises reviews initiales
- Violation policies

### Checklist Pre-Launch
- [ ] Tous les liens fonctionnent
- [ ] Pas de contenu placeholder
- [ ] Login/signup fonctionne
- [ ] Paiements testés (sandbox)
- [ ] Crashlytics activé
- [ ] Support email configuré
- [ ] FAQ disponible

### Marketing Launch
- Press kit préparé
- Social media annonces
- Email campaign
- Landing page updated
- Influencers contactés
- ASO keywords optimisés

### Métriques de succès
- 1000 downloads semaine 1
- 4.0+ rating moyen
- < 1% crash rate
- 30% D7 retention
- Featured possibility

---

## 🔗 Liens

- [[US-3.1-React-Native|US 3.1 - App Mobile]]
- [[US-3.3-Offline-Mode|US 3.3 - Mode Offline]]
- [[US-2.1-Auth|US 2.1 - Authentification]]