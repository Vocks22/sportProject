# 📅 Sélecteurs de Dates pour les Graphiques

## Vue d'ensemble
Tous les graphiques d'évolution du poids disposent maintenant de sélecteurs de dates avancés permettant de visualiser des périodes spécifiques.

## Fonctionnalités

### 1. Sélection Rapide
Boutons pour afficher rapidement :
- **1M** : Dernier mois (30 jours)
- **3M** : 3 derniers mois (90 jours) - Par défaut
- **6M** : 6 derniers mois (180 jours)
- **1Y** : Dernière année (365 jours)
- **Tout** : Toutes les données disponibles

### 2. Sélection Personnalisée 📅
- Cliquez sur le bouton **"📅 Personnalisé"** pour activer le mode de sélection manuelle
- Choisissez une **date de début** et une **date de fin**
- Les dates sont limitées aux données disponibles (juillet 2024 à aujourd'hui)

### 3. Raccourcis de Période
En mode personnalisé, accédez rapidement à :
- **Juillet 24** : Affiche tout le mois de juillet 2024
- **Août 24** : Affiche tout le mois d'août 2024
- **Ce mois** : Affiche le mois en cours

### 4. Options d'Affichage
Pour chaque graphique, vous pouvez activer/désactiver :
- **Tendance** : Ligne de tendance linéaire
- **Masse grasse** : Affichage du pourcentage de masse grasse (si disponible)

## Où les trouver ?

Les sélecteurs de dates sont disponibles sur :
- **Dashboard** : Graphique d'évolution du poids
- **Page Progress** : Graphique détaillé avec statistiques
- **Page Profil** : Section évolution du poids

## Données Disponibles

### Distribution actuelle
- **Juillet 2024** : 31 mesures (100.7kg → 99.0kg)
- **Août 2024** : 4 mesures (99.5kg → 99.0kg)
- **Août 2025** : 3 mesures (100.0kg → 99.0kg)
- **Total** : 38 mesures

### Exemples d'utilisation

#### Voir la progression de juillet 2024
1. Cliquez sur "📅 Personnalisé"
2. Cliquez sur "Juillet 24" ou sélectionnez :
   - Du : 01/07/2024
   - Au : 31/07/2024
3. Le graphique affichera les 31 mesures de juillet

#### Comparer deux mois
1. Activez le mode personnalisé
2. Sélectionnez par exemple :
   - Du : 01/07/2024
   - Au : 31/08/2024
3. Vous verrez la progression sur juillet et août 2024

#### Voir uniquement les données récentes
1. Cliquez sur "1M" pour les 30 derniers jours
2. Ou utilisez "Ce mois" en mode personnalisé

## Informations Affichées

### Statistiques au-dessus du graphique
- **Minimum** : Poids le plus bas sur la période
- **Maximum** : Poids le plus haut sur la période
- **Variation totale** : Différence entre début et fin
- **Distance objectif** : Écart avec l'objectif de poids

### Sous le graphique
- Nombre de points de mesure affichés
- Période sélectionnée (en mode personnalisé)

## Conseils

1. **Pour une vue détaillée** : Utilisez des périodes courtes (1M ou personnalisé)
2. **Pour voir les tendances** : Utilisez des périodes plus longues (6M, 1Y)
3. **Pour analyser un mois spécifique** : Utilisez les raccourcis de période
4. **Pour comparer** : Activez la ligne de tendance

## Notes Techniques

- Les données sont filtrées côté client pour une réactivité maximale
- Les graphiques se mettent à jour instantanément lors du changement de période
- Les dates disponibles sont automatiquement limitées aux données existantes
- La ligne de tendance s'adapte à la période sélectionnée