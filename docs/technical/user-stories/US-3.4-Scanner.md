# 📸 US 3.4 - Scanner de Codes-Barres

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
Utilisateur faisant ses courses ou gérant son inventaire

### Je veux...
Scanner les codes-barres des produits alimentaires pour obtenir automatiquement leurs informations nutritionnelles

### Afin de...
Gagner du temps dans la saisie de mes aliments et avoir des données nutritionnelles précises sans effort

---

## ✅ Acceptance Criteria

- [ ] **Scanner de codes-barres**
  - Scan via caméra en temps réel
  - Support EAN-13, EAN-8, UPC-A
  - QR codes pour recettes partagées
  - Mode flash/torche
  - Auto-focus continu
  - Vibration feedback sur scan

- [ ] **Base de données produits**
  - Intégration Open Food Facts API
  - Cache local produits scannés
  - Ajout manuel si produit absent
  - Contribution communautaire
  - Validation des données

- [ ] **Informations récupérées**
  - Nom du produit
  - Marque
  - Valeurs nutritionnelles /100g
  - Allergènes
  - Labels (Bio, Nutriscore, etc.)
  - Photo du produit

- [ ] **Workflow utilisateur**
  - Scan rapide one-tap
  - Prévisualisation infos avant ajout
  - Quantité personnalisable
  - Ajout direct au journal
  - Historique des scans
  - Favoris produits

- [ ] **Mode batch**
  - Scan multiple courses
  - Liste temporaire
  - Validation groupée
  - Export liste courses

---

## 🔧 Technical Requirements

### Libraries Scanner
- **React Native** : react-native-vision-camera
- **Alternative** : react-native-camera
- **Barcode** : ML Kit (Google) / Vision (Apple)

### APIs Produits
```javascript
// Open Food Facts API
GET https://world.openfoodfacts.org/api/v0/product/{barcode}.json

// Fallback databases
- USDA Food Database
- Nutritionix API
- Custom database
```

### Performance
- Scan en < 1 seconde
- Cache agressif des produits
- Mode offline avec sync
- Compression images

---

## 📊 Definition of Done

- [ ] Code review approuvé
- [ ] Tests unitaires (>75% coverage)
- [ ] Tests avec vrais produits
- [ ] Taux reconnaissance > 95%
- [ ] Documentation API
- [ ] Performance scan < 1s
- [ ] Accessibilité validée
- [ ] Validation Product Owner

---

## 🎯 Sprint Planning

### Découpage des tâches
1. **Camera integration** (2 pts)
   - Setup camera permissions
   - Scanner UI/UX
   - Barcode detection

2. **API integration** (2 pts)
   - Open Food Facts
   - Data mapping
   - Error handling

3. **Product management** (2 pts)
   - Local cache
   - Favorites
   - History

4. **UI Polish** (1 pt)
   - Animations
   - Feedback
   - Tutorial

5. **Testing** (1 pt)
   - Real devices
   - Various barcodes
   - Edge cases

---

## 📝 Notes

### Risques identifiés
- Qualité variable des données OpenFoodFacts
- Performance sur anciens appareils
- Conditions de luminosité difficiles
- Codes-barres endommagés
- Produits régionaux absents

### Améliorations futures
- OCR pour dates de péremption
- Reconnaissance d'image (sans code-barres)
- Scan de tickets de caisse
- Comparaison de prix
- Alternatives plus saines

### Métriques de succès
- 80% produits reconnus premier scan
- < 1s temps de reconnaissance
- 90% satisfaction utilisateurs
- +50% rapidité saisie aliments

---

## 🔗 Liens

- [[US-3.1-React-Native|US 3.1 - App Mobile]]
- [[US-3.3-Offline-Mode|US 3.3 - Mode Offline]]
- [[US-1.5-Shopping|US 1.5 - Liste Courses]]