# 🚀 Déploiement sur Netlify - APRÈS RENDER

## ⚠️ Prérequis
Vous devez avoir :
1. ✅ Backend déployé sur Render
2. ✅ URL du backend (ex: `https://diettracker-backend.onrender.com`)

## 📝 Étape 1 : Mettre à jour les URLs dans le Frontend

### Option A : Script Automatique (Recommandé)
```bash
cd src/frontend
node update-api-urls.js
```

### Option B : Manuellement
Modifiez le fichier `.env.production` :
```env
VITE_API_URL=https://diettracker-backend.onrender.com
```

Remplacez `https://diettracker-backend.onrender.com` par VOTRE URL Render !

## 🔧 Étape 2 : Builder le Frontend

```bash
cd src/frontend
npm install
npm run build
```

Cela créera un dossier `dist/` avec votre application.

## 🌐 Étape 3 : Déployer sur Netlify

### Option A : Drag & Drop (Plus Simple)

1. Allez sur [app.netlify.com](https://app.netlify.com)
2. Connectez-vous
3. Sur la page d'accueil, vous verrez une zone "Drag & Drop"
4. **Glissez le dossier `src/frontend/dist`** dans cette zone
5. Attendez le déploiement (~1 minute)
6. Netlify vous donnera une URL comme `https://amazing-site-123.netlify.app`

### Option B : Via GitHub (Auto-deploy)

1. Sur Netlify : **"Add new site"** → **"Import an existing project"**
2. Connectez GitHub
3. Sélectionnez votre repo
4. Configuration :
   - **Base directory** : `src/frontend`
   - **Build command** : `npm run build`
   - **Publish directory** : `src/frontend/dist`
5. **Environment variables** : Cliquez "Show advanced"
   - Ajoutez : `VITE_API_URL` = `https://diettracker-backend.onrender.com`
6. **Deploy site**

## ⚙️ Étape 4 : Configuration Finale

### Sur Netlify
1. **Site settings** → **Domain management**
2. Changez le nom du site (optionnel) : `diettracker.netlify.app`

### Sur Render
1. Retournez sur votre service backend
2. **Environment** → Modifiez `CORS_ORIGINS`
3. Ajoutez votre URL Netlify :
```
http://localhost:5173,https://diettracker.netlify.app
```

## ✅ Test Final

1. Ouvrez votre site Netlify
2. Vérifiez que les pages se chargent
3. Testez l'ajout d'une mesure
4. Vérifiez les graphiques

## 🎉 C'est Fini !

Votre application est maintenant en ligne :
- Frontend : `https://votre-site.netlify.app`
- Backend : `https://votre-backend.onrender.com`

---

## ⚠️ Problèmes Fréquents

### "Page blanche"
→ Ouvrez la console (F12) et vérifiez les erreurs

### "Failed to fetch" ou "CORS error"
→ Vérifiez que CORS_ORIGINS contient votre URL Netlify sur Render

### "API not responding"
→ Le backend Render met ~30 sec à se réveiller après inactivité

### "404 on refresh"
→ Normal avec React Router, le fichier `netlify.toml` gère ça

---

## 📊 Limitations du Plan Gratuit

### Netlify Free
- 100 GB bandwidth/mois
- 300 build minutes/mois
- Parfait pour votre projet !

### Render Free
- S'endort après 15 min d'inactivité
- 750 heures/mois
- Base de données : 1 GB storage

---

## 🚀 Améliorations Futures

1. **Nom de domaine personnalisé** (gratuit sur Netlify)
2. **HTTPS** (automatique sur les deux)
3. **Analytics** (Netlify Analytics)
4. **Formulaire de contact** (Netlify Forms)

---

## 💡 Commandes Utiles

### Redéployer le Frontend
```bash
cd src/frontend
npm run build
netlify deploy --prod --dir=dist
```

### Voir les logs Backend
Dans Render Dashboard → Logs

### Voir les logs Frontend
Dans Netlify Dashboard → Functions logs