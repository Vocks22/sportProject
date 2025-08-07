# 🚀 Guide de Déploiement sur Netlify

## 📝 Checklist Pré-Déploiement

### ✅ À faire avant le déploiement

#### 1. **Backend (API Flask)**
Netlify ne peut héberger que des sites statiques. Vous devez héberger votre backend Flask séparément :

**Options recommandées pour le backend :**
- **Render.com** (gratuit avec limitations)
- **Railway.app** (facile à déployer)
- **Heroku** (payant)
- **PythonAnywhere** (gratuit avec limitations)
- **DigitalOcean App Platform**

#### 2. **Base de données**
SQLite n'est pas adapté pour la production. Options :
- **PostgreSQL** sur Supabase (gratuit)
- **PostgreSQL** sur Neon.tech (gratuit)
- **MySQL** sur PlanetScale (gratuit)
- **PostgreSQL** sur Render

---

## 🔧 Étapes de Déploiement

### Étape 1: Déployer le Backend (Flask)

#### Option A: Déployer sur Render.com (Recommandé - Gratuit)

1. **Créer un compte sur [Render.com](https://render.com)**

2. **Créer un fichier `requirements.txt` dans `/src/backend/`**
```bash
Flask==2.3.2
Flask-SQLAlchemy==3.0.5
Flask-CORS==4.0.0
SQLAlchemy==2.0.19
python-dotenv==1.0.0
gunicorn==21.2.0
psycopg2-binary==2.9.6
```

3. **Créer un `render.yaml` dans la racine du projet**
```yaml
services:
  - type: web
    name: diettracker-api
    env: python
    buildCommand: "pip install -r src/backend/requirements.txt"
    startCommand: "cd src/backend && gunicorn main:app"
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: diettracker-db
          property: connectionString
      - key: FLASK_ENV
        value: production

databases:
  - name: diettracker-db
    databaseName: diettracker
    user: diettracker
```

4. **Modifier `src/backend/database/config.py` pour PostgreSQL**
```python
import os
from urllib.parse import urlparse

class ProductionConfig(Config):
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    if DATABASE_URL:
        # Render utilise postgres:// mais SQLAlchemy veut postgresql://
        if DATABASE_URL.startswith("postgres://"):
            DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
        
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///diettracker.db'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
```

5. **Push sur GitHub et connecter Render**
   - Aller sur Render Dashboard
   - "New +" → "Web Service"
   - Connecter votre repo GitHub
   - Render détectera automatiquement le `render.yaml`

### Étape 2: Déployer le Frontend sur Netlify

#### A. Préparer le Frontend

1. **Mettre à jour les URLs d'API dans tous les composants**

Créer un fichier `src/frontend/src/utils/api.js`:
```javascript
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

export const API_ENDPOINTS = {
  // Users
  getUserProfile: (userId) => `${API_BASE_URL}/api/users/${userId}/profile`,
  updateUserProfile: (userId) => `${API_BASE_URL}/api/users/${userId}/profile`,
  getWeightHistory: (userId) => `${API_BASE_URL}/api/users/${userId}/weight-history`,
  getMeasurements: (userId) => `${API_BASE_URL}/api/users/${userId}/measurements`,
  addMeasurement: (userId) => `${API_BASE_URL}/api/users/${userId}/measurements`,
  
  // Recipes
  getRecipes: () => `${API_BASE_URL}/api/recipes`,
  getRecipe: (id) => `${API_BASE_URL}/api/recipes/${id}`,
  getCookingGuide: (id) => `${API_BASE_URL}/api/recipes/${id}/cooking-guide`,
  
  // Meal Plans
  getMealPlans: () => `${API_BASE_URL}/api/meal-plans`,
  createMealPlan: () => `${API_BASE_URL}/api/meal-plans`,
  
  // Shopping
  getShoppingList: () => `${API_BASE_URL}/api/shopping-list`,
};
```

2. **Modifier tous les fetch() dans les composants**

Exemple dans `Dashboard.jsx`:
```javascript
import { API_ENDPOINTS } from '../utils/api';

// Remplacer
const measResponse = await fetch(`http://localhost:5000/api/users/${userId}/measurements?days=365`)

// Par
const measResponse = await fetch(API_ENDPOINTS.getMeasurements(userId) + '?days=365')
```

#### B. Déployer sur Netlify

1. **Via l'interface Netlify (Plus simple)**
   - Aller sur [netlify.com](https://netlify.com)
   - Se connecter avec GitHub
   - "Add new site" → "Import an existing project"
   - Choisir votre repo GitHub
   - Configuration :
     - Base directory: `src/frontend`
     - Build command: `npm run build`
     - Publish directory: `src/frontend/dist`
   - Cliquer sur "Deploy site"

2. **Via Netlify CLI (Alternative)**
```bash
# Installer Netlify CLI
npm install -g netlify-cli

# Se connecter
netlify login

# Dans src/frontend
cd src/frontend
npm run build

# Déployer
netlify deploy --prod --dir=dist
```

### Étape 3: Configuration des Variables d'Environnement

#### Sur Netlify:
1. Aller dans Site settings → Environment variables
2. Ajouter:
   - `VITE_API_URL` = `https://diettracker-api.onrender.com` (URL de votre backend)

#### Sur Render:
1. Dans le dashboard du service
2. Environment → Add environment variable
3. Ajouter les variables nécessaires

---

## 🔍 Vérifications Post-Déploiement

### Checklist de Validation

- [ ] Le site frontend se charge sur Netlify
- [ ] L'API backend répond sur Render
- [ ] Les requêtes API fonctionnent (CORS configuré)
- [ ] La base de données PostgreSQL est accessible
- [ ] Les données se sauvegardent correctement
- [ ] Les graphiques s'affichent
- [ ] Les uploads d'images fonctionnent (si applicable)

### Débuggage Commun

#### Erreur CORS
Ajouter dans `main.py`:
```python
CORS(app, origins=["https://your-site.netlify.app"])
```

#### Erreur Mixed Content
S'assurer que toutes les URLs utilisent HTTPS

#### API non accessible
Vérifier que le backend est bien déployé et accessible

---

## 📊 Monitoring

### Services Recommandés
- **Sentry** pour le tracking d'erreurs
- **LogRocket** pour le monitoring frontend
- **UptimeRobot** pour surveiller la disponibilité

---

## 🔐 Sécurité

### À implémenter avant la production
1. **Authentication** (JWT tokens)
2. **Rate limiting** sur l'API
3. **HTTPS** partout
4. **Variables d'environnement** pour les secrets
5. **Validation des inputs** côté serveur

---

## 💰 Coûts

### Plan Gratuit
- **Netlify**: 100GB bandwidth/mois
- **Render**: Service dort après 15min d'inactivité
- **Supabase/Neon**: 500MB storage

### Pour un site actif
- Netlify Pro: $19/mois
- Render Starter: $7/mois
- Total: ~$26/mois

---

## 📝 Scripts de Déploiement

### Package.json pour le frontend
```json
{
  "scripts": {
    "build": "vite build",
    "preview": "vite preview",
    "deploy": "npm run build && netlify deploy --prod --dir=dist"
  }
}
```

### Commande de déploiement rapide
```bash
# Dans src/frontend
npm run deploy
```

---

## 🚨 Important

**NE PAS OUBLIER:**
1. Changer toutes les URLs `localhost` en URLs de production
2. Mettre à jour les CORS
3. Migrer de SQLite vers PostgreSQL
4. Ajouter l'authentification
5. Configurer les variables d'environnement
6. Tester sur mobile

---

## 📞 Support

Si vous rencontrez des problèmes:
1. Vérifier les logs Netlify
2. Vérifier les logs Render
3. Tester l'API avec Postman
4. Vérifier la console du navigateur