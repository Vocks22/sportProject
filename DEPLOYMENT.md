# 🚀 Déploiement Rapide sur Netlify

## ⚠️ État Actuel du Projet

**IMPORTANT**: Ce projet nécessite un **backend Flask** et une **base de données**.
Netlify ne peut héberger que le **frontend React**. 

## 📋 Ce qu'il reste à faire

### 1️⃣ **Héberger le Backend Flask** (OBLIGATOIRE)
   
Le backend doit être déployé séparément sur :
- **Render.com** (✅ Recommandé - Gratuit)
- **Railway.app** 
- **Heroku** (Payant)

**Temps estimé**: 30 minutes

### 2️⃣ **Migrer la Base de Données**

SQLite → PostgreSQL
- **Supabase** (✅ Recommandé - Gratuit)
- **Neon.tech** (Gratuit)

**Temps estimé**: 20 minutes

### 3️⃣ **Modifier les URLs dans le Frontend**

Remplacer tous les `http://localhost:5000` par l'URL de votre backend

**Fichiers à modifier**:
```
- components/Dashboard.jsx
- components/Progress.jsx  
- components/MealPlanning.jsx
- pages/ProfilePage.jsx
- pages/MeasurementsPage.jsx
- hooks/*.js
```

**Temps estimé**: 15 minutes

### 4️⃣ **Déployer sur Netlify**

```bash
cd src/frontend
npm run build
# Puis drag & drop le dossier 'dist' sur Netlify
```

**Temps estimé**: 5 minutes

---

## 🎯 Guide Étape par Étape

### Étape 1: Backend sur Render.com

1. Créer un compte sur [render.com](https://render.com)
2. Fork ce repo sur GitHub
3. Sur Render: New → Web Service → Connecter votre repo
4. Configuration:
   - Build Command: `pip install -r src/backend/requirements.txt`
   - Start Command: `cd src/backend && gunicorn main:app`
5. Ajouter une base PostgreSQL
6. Noter l'URL du backend: `https://votre-app.onrender.com`

### Étape 2: Frontend sur Netlify

1. Modifier `.env.production`:
```env
VITE_API_URL=https://votre-app.onrender.com/api
```

2. Build local:
```bash
cd src/frontend
npm install
npm run build
```

3. Sur [netlify.com](https://netlify.com):
   - Drag & drop le dossier `dist`
   - Ou: connecter GitHub et auto-deploy

### Étape 3: Configuration CORS

Dans `src/backend/main.py`, ajouter votre URL Netlify:
```python
CORS(app, origins=[
    "http://localhost:3000",
    "https://votre-site.netlify.app"  # Ajouter cette ligne
])
```

---

## ✅ Checklist Finale

- [ ] Backend déployé et accessible
- [ ] Base de données PostgreSQL configurée
- [ ] URLs mises à jour dans le frontend
- [ ] Frontend déployé sur Netlify
- [ ] CORS configuré
- [ ] Variables d'environnement définies
- [ ] Test complet de l'application

---

## 🆘 Problèmes Fréquents

### "API non accessible"
→ Vérifier que le backend est bien démarré sur Render

### "CORS error"
→ Ajouter l'URL Netlify dans les origines CORS

### "Database error"
→ Vérifier DATABASE_URL dans les variables d'environnement

### "Page blanche"
→ Vérifier la console du navigateur pour les erreurs

---

## 💡 Tips

1. **Testez localement d'abord** avec le backend en production
2. **Utilisez les logs** de Render et Netlify pour debugger
3. **Commencez par le backend** avant le frontend
4. **Gardez SQLite** pour le développement local

---

## 📞 Besoin d'aide ?

1. Consultez `/docs/deployment/netlify-deployment-guide.md` pour plus de détails
2. Vérifiez les logs sur Render Dashboard
3. Vérifiez les logs sur Netlify Dashboard

---

## ⏱️ Temps Total Estimé

**1h30** pour tout déployer de zéro

- 30 min - Backend + DB
- 15 min - Migration des URLs
- 15 min - Build Frontend
- 10 min - Deploy Netlify
- 20 min - Tests et debug