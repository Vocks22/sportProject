# 🚀 Déploiement sur Render - MAINTENANT

## 📋 Étape 1 : Sur GitHub
1. **Pushez vos changements** sur GitHub
   ```bash
   git push origin main
   ```

## 🔧 Étape 2 : Sur Render.com

### A. Créer le Service Web

1. **Dashboard Render** → Cliquez sur **"New +"** → **"Web Service"**

2. **Connectez votre repo GitHub**
   - Cliquez sur "Connect GitHub"
   - Autorisez Render
   - Sélectionnez votre repo `sportProject`

3. **Configuration du Service** :
   
   | Paramètre | Valeur |
   |-----------|---------|
   | **Name** | diettracker-backend |
   | **Region** | Frankfurt (EU) |
   | **Branch** | main |
   | **Root Directory** | (laisser vide) |
   | **Runtime** | Python 3 |
   | **Build Command** | pip install -r src/backend/requirements.txt |
   | **Start Command** | cd src/backend && gunicorn main:app --bind 0.0.0.0:$PORT |

4. **Plan** : Sélectionnez **"Free"**

5. Cliquez sur **"Create Web Service"**

### B. Ajouter une Base de Données PostgreSQL

1. **Dashboard** → **"New +"** → **"PostgreSQL"**

2. **Configuration** :
   - **Name** : `diettracker-db`
   - **Database** : `diettracker`
   - **User** : `diettracker`
   - **Region** : Frankfurt (EU)
   - **Plan** : Free

3. Cliquez sur **"Create Database"**

### C. Connecter la DB au Service

1. Allez dans votre service `diettracker-backend`
2. Onglet **"Environment"**
3. Cliquez sur **"Add Environment Variable"**
4. Ajoutez :
   - **Key** : `DATABASE_URL`
   - **Value** : Copiez l'URL depuis votre database (Internal Database URL)

5. Ajoutez aussi :
   - `SECRET_KEY` = `your-secret-key-here-change-this`
   - `JWT_SECRET_KEY` = `your-jwt-secret-key-here`
   - `FLASK_ENV` = `production`

### D. Initialiser la Base de Données

Une fois le service déployé :

1. Dans Render Dashboard → votre service → **"Shell"**
2. Exécutez :
```bash
cd src/backend
python3
>>> from main import app
>>> from database import db
>>> with app.app_context():
...     db.create_all()
...     print("Tables created!")
>>> exit()
```

## 📝 Étape 3 : Noter l'URL de votre Backend

Une fois déployé, Render vous donnera une URL comme :
```
https://diettracker-backend.onrender.com
```

**NOTEZ CETTE URL** - Vous en aurez besoin pour Netlify !

## ✅ Vérification

Testez votre API :
```
https://diettracker-backend.onrender.com/api/users/1/profile
```

Vous devriez voir une réponse JSON (même si c'est une erreur 404, c'est bon signe !).

## 🎯 Prochaine Étape : Netlify

Une fois que votre backend Render fonctionne, passez au déploiement Netlify !

---

## ⚠️ Problèmes Possibles

### "Build failed"
→ Vérifiez que `requirements.txt` est bien dans `src/backend/`

### "Application failed to respond"
→ Vérifiez le Start Command : `cd src/backend && gunicorn main:app --bind 0.0.0.0:$PORT`

### "Database connection failed"
→ Vérifiez que DATABASE_URL est bien configuré dans Environment

---

## 💡 Tips

- Le service gratuit de Render **s'endort après 15 min d'inactivité**
- Le premier chargement après sommeil prend ~30 secondes
- Les logs sont dans l'onglet "Logs" de votre service