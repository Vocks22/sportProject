# Maquettes Interface Utilisateur

## Vue d'ensemble de l'Application

### Layout Principal
```
┌─────────────────────────────────────────────────────────────┐
│ Header: Logo | Navigation | Profil                          │
├─────────────────────────────────────────────────────────────┤
│ Sidebar │ Contenu Principal                                 │
│         │                                                   │
│ • Dashboard                                                 │
│ • Planning                                                  │
│ • Recettes                                                  │
│ • Courses                                                   │
│ • Suivi                                                     │
│         │                                                   │
└─────────────────────────────────────────────────────────────┘
```

## Page 1: Dashboard (Tableau de Bord)

### Layout Desktop
```
┌─────────────────────────────────────────────────────────────┐
│                    DASHBOARD                                │
├─────────────────────────────────────────────────────────────┤
│ ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ │
│ │   Aujourd'hui   │ │   Cette Semaine │ │    Objectifs    │ │
│ │                 │ │                 │ │                 │ │
│ │ Repas 1: ✓      │ │ Lun ■■■■■       │ │ Calories: 85%   │ │
│ │ Collation: ✓    │ │ Mar ■■■■□       │ │ Protéines: 92%  │ │
│ │ Repas 2: ⏰     │ │ Mer ■■■□□       │ │ Poids: -2.3kg   │ │
│ │ Collation: □    │ │ Jeu ■■□□□       │ │                 │ │
│ │ Repas 3: □      │ │ Ven □□□□□       │ │ 🎯 Objectif:    │ │
│ │                 │ │ Sam □□□□□       │ │ -5kg ce mois    │ │
│ │ Calories: 850   │ │ Dim □□□□□       │ │                 │ │
│ │ / 1500 kcal     │ │                 │ │                 │ │
│ └─────────────────┘ └─────────────────┘ └─────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────────┐ │
│ │                 Repas du Jour                           │ │
│ │                                                         │ │
│ │ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐        │ │
│ │ │   Repas 1   │ │   Repas 2   │ │   Repas 3   │        │ │
│ │ │             │ │             │ │             │        │ │
│ │ │ [Image]     │ │ [Image]     │ │ [Image]     │        │ │
│ │ │ Omelette    │ │ Poulet      │ │ Cabillaud   │        │ │
│ │ │ aux blancs  │ │ grillé      │ │ en papillote│        │ │
│ │ │             │ │             │ │             │        │ │
│ │ │ 351 kcal    │ │ 310 kcal    │ │ 270 kcal    │        │ │
│ │ │ ✓ Terminé   │ │ ⏰ 12h30    │ │ 🕖 19h00    │        │ │
│ │ └─────────────┘ └─────────────┘ └─────────────┘        │ │
│ └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│ ┌─────────────────┐ ┌─────────────────────────────────────┐ │
│ │   Rappels       │ │        Progression                  │ │
│ │                 │ │                                     │ │
│ │ 🛒 Liste de     │ │ ┌─────────────────────────────────┐ │ │
│ │    courses      │ │ │     Calories (1500/jour)       │ │ │
│ │    samedi       │ │ │ ████████████░░░░░░░░░░░░░░░░░░░ │ │ │
│ │                 │ │ │              85%                │ │ │
│ │ 🏃 Sport        │ │ └─────────────────────────────────┘ │ │
│ │    mardi 18h    │ │ ┌─────────────────────────────────┐ │ │
│ │                 │ │ │     Protéines (150g/jour)      │ │ │
│ │ 💊 Vitamines    │ │ │ ██████████████████░░░░░░░░░░░░░ │ │ │
│ │    matin        │ │ │              92%                │ │ │
│ │                 │ │ └─────────────────────────────────┘ │ │
│ └─────────────────┘ └─────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Éléments Interactifs
- **Cartes de repas**: Cliquables pour voir les détails
- **Barres de progression**: Animées avec couleurs selon le pourcentage
- **Rappels**: Notifications avec actions rapides
- **Boutons d'action**: "Marquer comme terminé", "Voir recette"

## Page 2: Planification des Repas

### Vue Calendrier Hebdomadaire
```
┌─────────────────────────────────────────────────────────────┐
│              PLANIFICATION DES REPAS                       │
│ ┌─────────────┐ ┌─────────────┐ [Semaine du 6-12 Août]    │
│ │ ← Semaine   │ │ Semaine →   │ [Générer Plan Auto]       │
│ │ précédente  │ │ suivante    │ [Nouvelle Recette]        │
│ └─────────────┘ └─────────────┘                           │
├─────────────────────────────────────────────────────────────┤
│        │  Lun  │  Mar  │  Mer  │  Jeu  │  Ven  │  Sam  │  Dim │
├────────┼───────┼───────┼───────┼───────┼───────┼───────┼──────┤
│ Repas 1│ ┌───┐ │ ┌───┐ │ ┌───┐ │ ┌───┐ │ ┌───┐ │ ┌───┐ │ ┌──┐ │
│        │ │[🍳]│ │ │[🍳]│ │ │[🍳]│ │ │[🍳]│ │ │[🍳]│ │ │[🍳]│ │ │🍳│ │
│        │ │Omel│ │ │Omel│ │ │Omel│ │ │Omel│ │ │Omel│ │ │Omel│ │ │Om│ │
│        │ │351k│ │ │351k│ │ │351k│ │ │351k│ │ │351k│ │ │351k│ │ │35│ │
│        │ └───┘ │ └───┘ │ └───┘ │ └───┘ │ └───┘ │ └───┘ │ └──┘ │
├────────┼───────┼───────┼───────┼───────┼───────┼───────┼──────┤
│Collat. │ ┌───┐ │ ┌───┐ │ ┌───┐ │ ┌───┐ │ ┌───┐ │ ┌───┐ │ ┌──┐ │
│        │ │[🥤]│ │ │[🥤]│ │ │[🥤]│ │ │[🥤]│ │ │[🥤]│ │ │[🥤]│ │ │🥤│ │
│        │ │Smoo│ │ │Smoo│ │ │Smoo│ │ │Smoo│ │ │Smoo│ │ │Smoo│ │ │Sm│ │
│        │ │300k│ │ │300k│ │ │300k│ │ │300k│ │ │300k│ │ │300k│ │ │30│ │
│        │ └───┘ │ └───┘ │ └───┘ │ └───┘ │ └───┘ │ └───┘ │ └──┘ │
├────────┼───────┼───────┼───────┼───────┼───────┼───────┼──────┤
│ Repas 2│ ┌───┐ │ ┌───┐ │ ┌───┐ │ ┌───┐ │ ┌───┐ │ ┌───┐ │ ┌──┐ │
│        │ │[🍗]│ │ │[🦃]│ │ │[🍗]│ │ │[🦃]│ │ │[🍗]│ │ │[🦃]│ │ │🍗│ │
│        │ │Poul│ │ │Dind│ │ │Poul│ │ │Dind│ │ │Poul│ │ │Dind│ │ │Po│ │
│        │ │310k│ │ │295k│ │ │310k│ │ │295k│ │ │310k│ │ │295k│ │ │31│ │
│        │ └───┘ │ └───┘ │ └───┘ │ └───┘ │ └───┘ │ └───┘ │ └──┘ │
├────────┼───────┼───────┼───────┼───────┼───────┼───────┼──────┤
│Collat. │ ┌───┐ │ ┌───┐ │ ┌───┐ │ ┌───┐ │ ┌───┐ │ ┌───┐ │ ┌──┐ │
│        │ │[🥜]│ │ │[🥜]│ │ │[🥜]│ │ │[🥜]│ │ │[🥜]│ │ │[🥜]│ │ │🥜│ │
│        │ │Aman│ │ │Aman│ │ │Aman│ │ │Aman│ │ │Aman│ │ │Aman│ │ │Am│ │
│        │ │301k│ │ │301k│ │ │301k│ │ │301k│ │ │301k│ │ │301k│ │ │30│ │
│        │ └───┘ │ └───┘ │ └───┘ │ └───┘ │ └───┘ │ └───┘ │ └──┘ │
├────────┼───────┼───────┼───────┼───────┼───────┼───────┼──────┤
│ Repas 3│ ┌───┐ │ ┌───┐ │ ┌───┐ │ ┌───┐ │ ┌───┐ │ ┌───┐ │ ┌──┐ │
│        │ │[🐟]│ │ │[🐟]│ │ │[🐟]│ │ │[🐟]│ │ │[🐟]│ │ │[🐟]│ │ │🐟│ │
│        │ │Cabi│ │ │Sole│ │ │Cabi│ │ │Sole│ │ │Cabi│ │ │Sole│ │ │Ca│ │
│        │ │270k│ │ │250k│ │ │270k│ │ │250k│ │ │270k│ │ │250k│ │ │27│ │
│        │ └───┘ │ └───┘ │ └───┘ │ └───┘ │ └───┘ │ └───┘ │ └──┘ │
├────────┼───────┼───────┼───────┼───────┼───────┼───────┼──────┤
│ Total  │ 1532k │ 1497k │ 1532k │ 1497k │ 1532k │ 1497k │1532k │
└────────┴───────┴───────┴───────┴───────┴───────┴───────┴──────┘

┌─────────────────────────────────────────────────────────────┐
│                    Résumé Nutritionnel                     │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────┐ │
│ │  Calories   │ │  Protéines  │ │   Glucides  │ │ Lipides │ │
│ │             │ │             │ │             │ │         │ │
│ │   1515      │ │    145g     │ │     85g     │ │   75g   │ │
│ │ ████████░░  │ │ ███████████ │ │ ██████░░░░░ │ │ ███████ │ │
│ │    101%     │ │    97%      │ │    85%      │ │   94%   │ │
│ └─────────────┘ └─────────────┘ └─────────────┘ └─────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Fonctionnalités Drag & Drop
- **Glisser-déposer**: Recettes depuis la bibliothèque vers le calendrier
- **Échange**: Permuter des repas entre différents jours
- **Duplication**: Copier un repas vers plusieurs jours
- **Suppression**: Retirer un repas du planning

## Page 3: Bibliothèque de Recettes

### Vue Grille avec Filtres
```
┌─────────────────────────────────────────────────────────────┐
│                  BIBLIOTHÈQUE DE RECETTES                  │
├─────────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Filtres:                                                │ │
│ │ [Tous] [Repas 1] [Repas 2] [Repas 3] [Collations]     │ │
│ │ [🔍 Rechercher...] [Calories ▼] [Temps ▼] [+ Nouveau] │ │
│ └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────┐ │
│ │ [Image]     │ │ [Image]     │ │ [Image]     │ │ [Image] │ │
│ │             │ │             │ │             │ │         │ │
│ │ Omelette    │ │ Poulet      │ │ Cabillaud   │ │ Smoothie│ │
│ │ aux blancs  │ │ grillé      │ │ papillote   │ │ protéiné│ │
│ │             │ │             │ │             │ │         │ │
│ │ ⭐⭐⭐⭐⭐    │ │ ⭐⭐⭐⭐☆    │ │ ⭐⭐⭐⭐⭐    │ │ ⭐⭐⭐⭐☆ │ │
│ │ 351 kcal    │ │ 310 kcal    │ │ 270 kcal    │ │ 300 kcal│ │
│ │ 🕐 15 min   │ │ 🕐 25 min   │ │ 🕐 20 min   │ │ 🕐 5 min│ │
│ │             │ │             │ │             │ │         │ │
│ │ [❤️] [👁️] [+] │ │ [❤️] [👁️] [+] │ │ [❤️] [👁️] [+] │ │ [❤️][👁️][+]│ │
│ └─────────────┘ └─────────────┘ └─────────────┘ └─────────┘ │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────┐ │
│ │ [Image]     │ │ [Image]     │ │ [Image]     │ │ [Image] │ │
│ │             │ │             │ │             │ │         │ │
│ │ Dinde       │ │ Sole        │ │ Blancs      │ │ Fruits  │ │
│ │ épinards    │ │ grillée     │ │ d'œufs      │ │ rouges  │ │
│ │             │ │             │ │ amandes     │ │ amandes │ │
│ │ ⭐⭐⭐⭐☆    │ │ ⭐⭐⭐⭐⭐    │ │ ⭐⭐⭐⭐☆    │ │ ⭐⭐⭐⭐⭐ │ │
│ │ 295 kcal    │ │ 250 kcal    │ │ 301 kcal    │ │ 301 kcal│ │
│ │ 🕐 20 min   │ │ 🕐 15 min   │ │ 🕐 10 min   │ │ 🕐 2 min│ │
│ │             │ │             │ │             │ │         │ │
│ │ [❤️] [👁️] [+] │ │ [❤️] [👁️] [+] │ │ [❤️] [👁️] [+] │ │ [❤️][👁️][+]│ │
│ └─────────────┘ └─────────────┘ └─────────────┘ └─────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Détail d'une Recette (Modal)
```
┌─────────────────────────────────────────────────────────────┐
│                    OMELETTE AUX BLANCS D'ŒUFS              │
│                                                        [✕]  │
├─────────────────────────────────────────────────────────────┤
│ ┌─────────────────┐ ┌─────────────────────────────────────┐ │
│ │                 │ │ Informations Nutritionnelles        │ │
│ │     [Image]     │ │                                     │ │
│ │   de la recette │ │ 🔥 Calories: 351 kcal              │ │
│ │                 │ │ 🥩 Protéines: 36g                  │ │
│ │                 │ │ 🍞 Glucides: 12g                   │ │
│ │                 │ │ 🥑 Lipides: 18g                    │ │
│ │                 │ │                                     │ │
│ │                 │ │ ⏱️ Préparation: 5 min              │ │
│ │                 │ │ 🍳 Cuisson: 10 min                 │ │
│ │                 │ │ 👥 Portions: 1                     │ │
│ └─────────────────┘ └─────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│ Ingrédients:                                                │
│ • 3 blancs d'œufs (99g)                                    │
│ • 40g de noix de cajou                                     │ │
│ • Épices (herbes de Provence, paprika)                     │
│ • 1g de sel                                                │
├─────────────────────────────────────────────────────────────┤
│ Instructions:                                               │
│ 1. Séparer les blancs des jaunes d'œufs                   │
│ 2. Battre les blancs d'œufs dans un bol                   │
│ 3. Assaisonner avec les épices et le sel                  │
│ 4. Chauffer une poêle antiadhésive à feu moyen            │
│ 5. Verser les blancs battus dans la poêle                 │
│ 6. Cuire 3-4 minutes de chaque côté                       │
│ 7. Servir avec les noix de cajou                          │
├─────────────────────────────────────────────────────────────┤
│ Ustensiles nécessaires:                                     │
│ • Poêle antiadhésive                                       │
│ • Fouet                                                    │
│ • Bol de préparation                                       │
│ • Balance de cuisine                                       │
├─────────────────────────────────────────────────────────────┤
│ [❤️ Ajouter aux favoris] [📅 Ajouter au planning] [🛒 Courses] │
└─────────────────────────────────────────────────────────────┘
```

## Page 4: Liste de Courses

### Vue Liste Organisée
```
┌─────────────────────────────────────────────────────────────┐
│                    LISTE DE COURSES                        │
│ Semaine du 6-12 Août 2025                                  │
│ Générée le 3 août 2025                              [📧][🖨️] │
├─────────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ 🥩 PROTÉINES                                           │ │
│ │ ☐ Blanc de poulet - 1080g (6 portions de 180g)       │ │
│ │ ☐ Escalope de dinde - 540g (3 portions de 180g)      │ │
│ │ ☐ Filet de cabillaud - 800g (4 portions de 200g)     │ │
│ │ ☐ Filet de sole - 600g (3 portions de 200g)          │ │
│ │ ☐ Œufs frais - 42 œufs (6 par jour)                  │ │
│ └─────────────────────────────────────────────────────────┘ │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ 🥜 OLÉAGINEUX                                          │ │
│ │ ☐ Noix de cajou - 280g (7 portions de 40g)           │ │
│ │ ☐ Amandes - 280g (7 portions de 40g)                 │ │
│ └─────────────────────────────────────────────────────────┘ │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ 🥬 LÉGUMES                                             │ │
│ │ ☐ Brocolis - 525g (3.5 portions de 150g)             │ │
│ │ ☐ Épinards frais - 525g (3.5 portions de 150g)       │ │
│ │ ☐ Salade verte (mélange) - 700g                       │ │
│ │ ☐ Ail - 1 tête                                        │ │
│ └─────────────────────────────────────────────────────────┘ │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ 🍓 FRUITS                                              │ │
│ │ ☐ Ananas frais - 350g (7 portions de 50g)            │ │
│ │ ☐ Fruits rouges mélangés - 350g                       │ │
│ │ ☐ Pamplemousse - 7 unités                             │ │
│ └─────────────────────────────────────────────────────────┘ │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ 🥛 PRODUITS LAITIERS & ALTERNATIVES                   │ │
│ │ ☐ Lait d'amande - 1.4L (200ml par jour)              │ │
│ └─────────────────────────────────────────────────────────┘ │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ 🌾 CÉRÉALES                                            │ │
│ │ ☐ Flocons d'avoine - 420g (7 portions de 60g)        │ │
│ └─────────────────────────────────────────────────────────┘ │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ 🫒 CONDIMENTS & ÉPICES                                │ │
│ │ ☐ Huile d'olive extra vierge - 70ml                   │ │
│ │ ☐ Sel de mer - 1 paquet                               │ │
│ │ ☐ Herbes de Provence - 1 pot                          │ │
│ │ ☐ Paprika - 1 pot                                     │ │
│ │ ☐ Chocolat noir 70% - 1 tablette                      │ │
│ └─────────────────────────────────────────────────────────┘ │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ 💊 COMPLÉMENTS                                         │ │
│ │ ☐ Multi-vitamines - 1 boîte                           │ │
│ │ ☐ CLA 3000mg - 1 boîte                                │ │
│ └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│ 📊 Résumé: 23 articles | Budget estimé: 85-95€             │
│ [✓ Tout cocher] [☐ Tout décocher] [🔄 Régénérer]          │
└─────────────────────────────────────────────────────────────┘
```

### Mode Shopping (Mobile)
```
┌─────────────────────────┐
│    LISTE DE COURSES     │
│   Mode Shopping 🛒      │
├─────────────────────────┤
│ ☐ Blanc de poulet       │
│   1080g                 │
│ ☐ Escalope de dinde     │
│   540g                  │
│ ☐ Filet de cabillaud    │
│   800g                  │
│ ☐ Filet de sole         │
│   600g                  │
│ ☐ Œufs frais            │
│   42 œufs               │
├─────────────────────────┤
│ Progression: 0/23       │
│ ████░░░░░░░░░░░░░░░░░░░ │
│                         │
│ [Suivant: Oléagineux]   │
└─────────────────────────┘
```

## Page 5: Suivi et Progression

### Graphiques et Statistiques
```
┌─────────────────────────────────────────────────────────────┐
│                    SUIVI & PROGRESSION                     │
├─────────────────────────────────────────────────────────────┤
│ ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ │
│ │   Poids Actuel  │ │   Objectif      │ │   Progression   │ │
│ │                 │ │                 │ │                 │ │
│ │     72.7 kg     │ │    -5 kg        │ │    -2.3 kg      │ │
│ │                 │ │   ce mois       │ │   en 6 jours    │ │
│ │   ⬇️ -0.4 kg    │ │                 │ │                 │ │
│ │  depuis hier    │ │  🎯 Reste:      │ │   📈 Rythme:    │ │
│ │                 │ │    -2.7 kg      │ │   -0.38kg/jour  │ │
│ └─────────────────┘ └─────────────────┘ └─────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────────┐ │
│ │                 Évolution du Poids                      │ │
│ │                                                         │ │
│ │ 76kg ┌─┐                                               │ │
│ │      │ │                                               │ │
│ │ 75kg │ └─┐                                             │ │
│ │      │   │                                             │ │
│ │ 74kg │   └─┐                                           │ │
│ │      │     │                                           │ │
│ │ 73kg │     └─┐                                         │ │
│ │      │       └─┐                                       │ │
│ │ 72kg │         └─●                                     │ │
│ │      └─────────────────────────────────────────────────│ │
│ │      1/8  2/8  3/8  4/8  5/8  6/8  7/8  8/8  9/8     │ │
│ └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────────┐ │
│ │              Répartition Nutritionnelle                │ │
│ │                                                         │ │
│ │ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐        │ │
│ │ │  Protéines  │ │   Glucides  │ │   Lipides   │        │ │
│ │ │             │ │             │ │             │        │ │
│ │ │     40%     │ │     22%     │ │     38%     │        │ │
│ │ │   145g/j    │ │    85g/j    │ │    75g/j    │        │ │
│ │ │             │ │             │ │             │        │ │
│ │ │ ████████    │ │ ████░░░░    │ │ ███████░    │        │ │
│ │ │   Optimal   │ │   Correct   │ │   Optimal   │        │ │
│ │ └─────────────┘ └─────────────┘ └─────────────┘        │ │
│ └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│ ┌─────────────────┐ ┌─────────────────────────────────────┐ │
│ │   Habitudes     │ │           Prochains Objectifs      │ │
│ │                 │ │                                     │ │
│ │ 🍽️ Repas pris   │ │ 🎯 Atteindre 70kg (dans 7 jours)  │ │
│ │   cette semaine │ │                                     │ │
│ │   ████████████  │ │ 🏃 Maintenir 3 séances/semaine    │ │
│ │   18/21 (86%)   │ │                                     │ │
│ │                 │ │ 💧 Augmenter hydratation à 4L      │ │
│ │ 🏃 Sport        │ │                                     │ │
│ │   ██████░░░░░░  │ │ 📊 Stabiliser à -0.3kg/jour       │ │
│ │   2/3 (67%)     │ │                                     │ │
│ │                 │ │                                     │ │
│ │ 💧 Hydratation  │ │                                     │ │
│ │   ████████░░░░  │ │                                     │ │
│ │   3.2/3.5L      │ │                                     │ │
│ └─────────────────┘ └─────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Responsive Design

### Mobile (320px-768px)
- Navigation par onglets en bas
- Cartes empilées verticalement
- Calendrier vue jour/3 jours
- Listes simplifiées avec actions swipe

### Tablette (768px-1024px)
- Sidebar rétractable
- Grille 2 colonnes pour les cartes
- Calendrier vue semaine optimisée
- Modals adaptées à l'écran

### Desktop (1024px+)
- Sidebar fixe
- Grille 3-4 colonnes
- Vue calendrier complète
- Raccourcis clavier
- Drag & drop avancé

## Interactions et Animations

### Micro-interactions
- **Hover effects**: Élévation des cartes, changement de couleur
- **Loading states**: Spinners, skeleton screens
- **Success feedback**: Animations de validation, notifications toast
- **Transitions**: Smooth entre les pages, fade in/out

### Animations
- **Barres de progression**: Animation de remplissage
- **Graphiques**: Animation d'apparition des données
- **Drag & drop**: Feedback visuel pendant le glissement
- **Modal**: Slide in/out, backdrop blur

### États Interactifs
- **Boutons**: Disabled, loading, success states
- **Formulaires**: Validation en temps réel, états d'erreur
- **Cartes**: Sélectionnées, favorites, en cours d'édition
- **Navigation**: Active state, breadcrumbs

