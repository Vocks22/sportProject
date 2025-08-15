# 📊 Guide Complet d'Intégration Withings Health API

## Table des matières
1. [Vue d'ensemble](#vue-densemble)
2. [Prérequis](#prérequis)
3. [Configuration Withings Developer](#configuration-withings-developer)
4. [Configuration de l'Application](#configuration-de-lapplication)
5. [Test de l'Intégration](#test-de-lintégration)
6. [Utilisation Quotidienne](#utilisation-quotidienne)
7. [Dépannage](#dépannage)
8. [Sécurité et Confidentialité](#sécurité-et-confidentialité)

---

## 🎯 Vue d'ensemble

L'intégration Withings permet de synchroniser automatiquement les données de votre balance connectée avec l'application DietTracker. Plus besoin de saisir manuellement votre poids !

### Données synchronisées
- ✅ **Poids** (kg)
- ✅ **IMC** (calculé automatiquement)
- ✅ **Masse grasse** (kg et %)
- ✅ **Masse musculaire** (kg et %)
- ✅ **Masse hydrique** (%)
- ✅ **Masse osseuse** (kg)
- ✅ **Fréquence cardiaque** (si disponible)
- ✅ **Température corporelle** (si disponible)

### Appareils compatibles
- ✅ Body+ (WBS05)
- ✅ Body Comp (WBS12)
- ✅ Body Scan (WBS08)
- ✅ Body Cardio (WBS04)
- ✅ Body (WBS06)
- ✅ Tous les futurs appareils Withings

---

## 📋 Prérequis

### 1. Compte Withings Health Mate
- Téléchargez l'application **Health Mate** sur votre smartphone
- Créez un compte sur https://account.withings.com
- Configurez votre balance selon les instructions du fabricant
- Effectuez au moins une pesée pour vérifier que tout fonctionne

### 2. Compte Withings Developer
- Allez sur https://developer.withings.com
- Cliquez sur **"Sign Up"** si vous n'avez pas de compte
- Utilisez le même email que votre compte Health Mate (recommandé)

### 3. Application DietTracker
- Assurez-vous d'avoir accès à votre application DietTracker
- Vérifiez que vous pouvez vous connecter avec vos identifiants

---

## 🔧 Configuration Withings Developer

### Étape 1 : Créer une nouvelle application

1. Connectez-vous sur https://developer.withings.com
2. Allez dans **"My Apps"** → **"Create an app"**
3. Remplissez le formulaire :

```
Application Name: DietTracker
Description: Personal nutrition and weight tracking application
Logo: (optionnel pour le moment)
Application Type: Web Application
```

### Étape 2 : Configurer les URLs

Dans la section **"OAuth 2.0 - Registered URLs"** :

#### Pour la PRODUCTION (Netlify) :
```
Callback URL:
https://diettracker.netlify.app/withings/callback

Notification URL (Webhook):
https://diettracker-backend.onrender.com/api/withings/webhook
```

#### Pour le DÉVELOPPEMENT LOCAL :
```
Callback URL:
http://localhost:5173/withings/callback

Notification URL:
(Utilisez ngrok ou laissez vide pour les tests)
```

### Étape 3 : Configurer les permissions (Scopes)

Cochez les permissions suivantes :
- ✅ `user.info` - Informations de base de l'utilisateur
- ✅ `user.metrics` - Mesures de poids et composition corporelle
- ✅ `user.activity` - Données d'activité (optionnel)

### Étape 4 : Sauvegarder et récupérer les clés

Après avoir sauvegardé, vous obtiendrez :
```
Client ID: abc123def456...
Client Secret: xyz789uvw012...
```

⚠️ **IMPORTANT** : Gardez ces clés secrètes et sécurisées !

---

## ⚙️ Configuration de l'Application

### 1. Configuration Backend (Flask)

#### Créer le fichier `.env` dans `/src/backend/` :
```bash
# Withings OAuth Configuration
WITHINGS_CLIENT_ID=abc123def456...
WITHINGS_CLIENT_SECRET=xyz789uvw012...
WITHINGS_REDIRECT_URI=https://diettracker.netlify.app/withings/callback

# Pour le développement local, utilisez :
# WITHINGS_REDIRECT_URI=http://localhost:5173/withings/callback
```

#### Vérifier l'installation des dépendances :
```bash
cd src/backend
./venv/bin/pip install requests
```

### 2. Déploiement sur Render

Si votre backend est sur Render.com :

1. Allez dans le dashboard Render
2. Sélectionnez votre service `diettracker-backend`
3. Allez dans **Environment** → **Environment Variables**
4. Ajoutez :
   - `WITHINGS_CLIENT_ID` = votre_client_id
   - `WITHINGS_CLIENT_SECRET` = votre_client_secret
   - `WITHINGS_REDIRECT_URI` = https://diettracker.netlify.app/withings/callback

### 3. Base de données

Les tables nécessaires sont créées automatiquement :
- `withings_auth` - Stocke les tokens OAuth2
- `withings_measurements` - Stocke les mesures synchronisées

---

## 🧪 Test de l'Intégration

### Étape 1 : Connexion initiale

1. **Connectez-vous** à DietTracker
2. Allez dans **Mon Profil** (`/profile`)
3. Trouvez la section **"Balance Withings"**
4. Cliquez sur **"Connecter Withings"**

### Étape 2 : Autorisation OAuth2

1. Vous serez redirigé vers Withings
2. Connectez-vous avec vos identifiants Health Mate
3. **Autorisez** DietTracker à accéder à vos données :
   - ✅ Lire vos mesures de poids
   - ✅ Lire votre composition corporelle
4. Cliquez sur **"Autoriser"**

### Étape 3 : Vérification

1. Vous serez redirigé vers DietTracker
2. Un message de succès devrait apparaître
3. La section Withings affichera **"Compte connecté"**
4. Cliquez sur **"Synchroniser maintenant"**
5. Vos dernières mesures devraient apparaître

### Test avec votre balance

1. Montez sur votre balance Withings
2. Attendez la synchronisation avec Health Mate (WiFi)
3. Dans DietTracker, cliquez **"Synchroniser maintenant"**
4. Le nouveau poids devrait apparaître

---

## 📱 Utilisation Quotidienne

### Synchronisation automatique

#### Option 1 : Webhook (Temps réel)
- Chaque pesée déclenche une notification
- DietTracker reçoit les données en quelques secondes
- Aucune action requise de votre part

#### Option 2 : Synchronisation à la connexion
- À chaque connexion à DietTracker
- Les dernières mesures sont récupérées
- Idéal pour un suivi quotidien

#### Option 3 : Synchronisation manuelle
- Bouton **"Synchroniser maintenant"**
- Récupère les 5 dernières mesures
- Utile après plusieurs pesées

### Routine recommandée

1. **Matin** : Pesée à jeun après être allé aux toilettes
2. **Synchronisation** : Automatique via webhook
3. **Vérification** : Consultez votre progression dans DietTracker
4. **Analyse** : Visualisez les tendances sur les graphiques

---

## 🔧 Dépannage

### Problème : "Compte Withings non connecté"

**Solutions :**
1. Vérifiez que les clés API sont correctement configurées
2. Reconnectez votre compte Withings
3. Vérifiez la connexion internet

### Problème : "Token expiré"

**Solutions :**
1. Déconnectez Withings dans DietTracker
2. Reconnectez votre compte
3. Les tokens sont automatiquement renouvelés

### Problème : "Pas de nouvelles mesures"

**Vérifications :**
1. La balance est-elle connectée au WiFi ?
2. Health Mate affiche-t-il les mesures ?
3. Essayez la synchronisation manuelle
4. Vérifiez la date/heure de votre balance

### Problème : "Erreur 401 Unauthorized"

**Solutions :**
1. Les clés API sont-elles correctes ?
2. Le compte Withings est-il bien connecté ?
3. Essayez de vous reconnecter

### Logs de débogage

Pour voir les logs côté serveur :
```bash
# Backend Flask
tail -f src/backend/app.log

# Frontend React (console navigateur)
F12 → Console
```

---

## 🔒 Sécurité et Confidentialité

### Protection des données

1. **Tokens OAuth2** :
   - Stockés de manière sécurisée en base de données
   - Jamais exposés côté client
   - Renouvelés automatiquement

2. **Données de santé** :
   - Chiffrées en transit (HTTPS)
   - Stockées uniquement sur vos serveurs
   - Jamais partagées avec des tiers

3. **Accès limité** :
   - Seules les données autorisées sont accessibles
   - Révocable à tout moment
   - Conforme au RGPD

### Révocation d'accès

#### Depuis DietTracker :
1. Profil → Balance Withings
2. Cliquez sur l'icône de déconnexion
3. Confirmez la déconnexion

#### Depuis Withings :
1. https://account.withings.com
2. Paramètres → Applications
3. Trouvez "DietTracker"
4. Cliquez sur "Révoquer l'accès"

---

## 📊 Utilisation avancée

### Récupération de l'historique

Pour récupérer tout votre historique de pesées :
```python
# Dans routes/withings.py, modifiez :
'lastupdate': 0  # Récupère tout l'historique
# En :
'lastupdate': timestamp_30_jours  # Derniers 30 jours
```

### Ajout de notifications

Vous pouvez ajouter des notifications quand :
- ✅ Nouveau record de poids atteint
- ✅ Objectif de poids proche
- ✅ Pas de pesée depuis X jours
- ✅ Variation anormale détectée

### Export des données

Les données peuvent être exportées en :
- CSV pour Excel
- JSON pour analyses
- PDF pour rapports médicaux

---

## 🆘 Support et Ressources

### Documentation officielle
- [Withings API Documentation](https://developer.withings.com/api)
- [OAuth2 Guide](https://developer.withings.com/oauth2)
- [Mesures disponibles](https://developer.withings.com/api/reference/measure-getmeas)

### Communauté
- [Forum Withings Developer](https://developer.withings.com/forum)
- [Stack Overflow - Tag Withings](https://stackoverflow.com/questions/tagged/withings)

### Contact support
- **Withings** : developer@withings.com
- **DietTracker** : Via GitHub Issues

---

## 🎉 Félicitations !

Votre balance Withings est maintenant connectée à DietTracker. Profitez d'un suivi automatique et précis de votre progression !

### Prochaines étapes suggérées :
1. ✅ Effectuez votre première pesée synchronisée
2. ✅ Configurez vos objectifs de poids
3. ✅ Explorez les graphiques de progression
4. ✅ Activez les rappels de pesée quotidienne

---

*Guide créé le 15/08/2025 - Version 1.0*
*Compatible avec Withings API v2*