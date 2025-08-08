# 🔐 US 2.1 - Authentification JWT

> **Status** : 🔴 À FAIRE
> **Points** : 8
> **Sprint** : 5
> **Date prévue** : 02-15 Sept 2025
> **Développeur** : Non assigné
> **Reviewer** : À définir

[[../SCRUM_DASHBOARD|← Dashboard]] | [[../epics/EPIC-2-Advanced|← Epic 2]]

---

## 📝 User Story

### En tant que...
Utilisateur de l'application

### Je veux...
Pouvoir créer un compte et me connecter de manière sécurisée

### Afin de...
Protéger mes données personnelles et accéder à mon profil depuis n'importe où

---

## 🎯 Acceptance Criteria

- [ ] **Inscription**
  - Email + mot de passe
  - Validation email unique
  - Confirmation par email
  - Conditions d'utilisation

- [ ] **Connexion**
  - JWT tokens (access + refresh)
  - Remember me option
  - Session expiration configurable
  - Multi-device support

- [ ] **Sécurité**
  - Bcrypt password hashing
  - Rate limiting login attempts
  - HTTPS enforced
  - CSRF protection

- [ ] **Récupération**
  - Forgot password flow
  - Email avec token temporaire
  - Reset password form
  - Invalidation anciens tokens

- [ ] **Gestion compte**
  - Changement email
  - Changement mot de passe
  - Suppression compte (RGPD)
  - Export données (RGPD)

---

## 🛠️ Solution Technique Proposée

### Backend Implementation

```python
# models/user.py extension
class User(db.Model):
    # Existing fields...
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255))
    email_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    
    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password)
    
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def generate_jwt(self):
        payload = {
            'user_id': self.id,
            'email': self.email,
            'exp': datetime.utcnow() + timedelta(hours=1)
        }
        return jwt.encode(payload, current_app.config['SECRET_KEY'])
```

### API Endpoints

| Méthode | Endpoint | Description | Response |
|---------|----------|-------------|----------|
| POST | `/api/auth/register` | Inscription | 201: Token + User |
| POST | `/api/auth/login` | Connexion | 200: Token + User |
| POST | `/api/auth/logout` | Déconnexion | 204: No Content |
| POST | `/api/auth/refresh` | Refresh token | 200: New token |
| POST | `/api/auth/forgot-password` | Demande reset | 204: Email sent |
| POST | `/api/auth/reset-password` | Reset password | 200: Success |
| GET | `/api/auth/verify-email` | Vérification email | 200: Verified |
| DELETE | `/api/auth/account` | Suppression compte | 204: Deleted |

### Frontend Components

```jsx
// hooks/useAuth.js
export const useAuth = () => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  
  const login = async (email, password) => {
    const response = await api.post('/auth/login', { email, password });
    const { token, user } = response.data;
    
    localStorage.setItem('token', token);
    setUser(user);
    
    return user;
  };
  
  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
  };
  
  const register = async (userData) => {
    const response = await api.post('/auth/register', userData);
    return response.data;
  };
  
  return {
    user,
    loading,
    login,
    logout,
    register,
    isAuthenticated: !!user
  };
};
```

---

## 🔒 Sécurité

### Mesures implémentées

1. **Password Requirements**
   - Minimum 8 caractères
   - 1 majuscule, 1 minuscule
   - 1 chiffre, 1 caractère spécial
   - Vérification contre dictionnaire

2. **Token Security**
   ```python
   # JWT Configuration
   JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
   JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
   JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
   ```

3. **Rate Limiting**
   ```python
   from flask_limiter import Limiter
   
   limiter = Limiter(
       app,
       key_func=lambda: get_remote_address(),
       default_limits=["200 per day", "50 per hour"]
   )
   
   @limiter.limit("5 per minute")
   @app.route('/api/auth/login', methods=['POST'])
   def login():
       # Login logic
   ```

---

## 🧪 Tests

### Tests unitaires
- [ ] Validation email format
- [ ] Hash password correct
- [ ] Token generation
- [ ] Token validation
- [ ] Expiration handling

### Tests d'intégration
- [ ] Flow inscription complet
- [ ] Flow connexion/déconnexion
- [ ] Reset password flow
- [ ] Multi-device sessions

### Tests de sécurité
- [ ] SQL injection
- [ ] XSS attacks
- [ ] CSRF tokens
- [ ] Brute force protection

---

## 📊 Métriques de Succès

### KPIs à mesurer
- Taux de conversion inscription : > 60%
- Temps moyen inscription : < 2 min
- Taux d'échec login : < 5%
- Utilisateurs avec email vérifié : > 80%

### Impact attendu
- Sécurisation complète des données
- Multi-device usage enabled
- Foundation pour features sociales

---

## 🔗 Dépendances

### Libraries
- `flask-jwt-extended` : JWT management
- `flask-bcrypt` : Password hashing
- `flask-mail` : Email sending
- `flask-limiter` : Rate limiting

### Services
- SendGrid/Mailgun pour emails
- Redis pour sessions cache

---

## 🆘 Risques

| Risque | Probabilité | Impact | Mitigation |
|--------|-------------|---------|------------|
| Email deliverability | Moyenne | Haut | Multiple providers |
| Token hijacking | Faible | Très haut | HTTPS + short expiry |
| Password leaks | Faible | Haut | Bcrypt + salting |
| RGPD compliance | Moyenne | Haut | Legal review |

---

## 💡 Notes d'implémentation

### Considérations UX
- Social login options (Google, Apple)
- Passwordless option (magic link)
- Biometric auth mobile
- Progressive disclosure

### Améliorations futures
- 2FA authentication
- OAuth2 providers
- SSO enterprise
- WebAuthn support

---

[[../SCRUM_DASHBOARD|← Dashboard]] | [[US-1.8-Suivi-Repas|← US 1.8]] | [[US-2.2-Multi-Users|US 2.2 →]]