# 🔌 US 2.7 - Intégrations API Tierces

> **Status** : 🔴 À FAIRE
> **Points** : 13
> **Sprint** : 8
> **Date prévue** : 14-27 Oct 2025
> **Développeur** : Non assigné
> **Reviewer** : À définir

[[../SCRUM_DASHBOARD|← Dashboard]] | [[../epics/EPIC-2-Advanced|← Epic 2]]

---

## 📝 User Story

### En tant que...
Utilisateur avec plusieurs apps santé

### Je veux...
Connecter DietTracker avec mes autres applications

### Afin de...
Avoir une vue unifiée de ma santé sans double saisie

---

## 🎯 Acceptance Criteria

- [ ] **Fitness Trackers**
  - Google Fit
  - Apple Health
  - Fitbit
  - Garmin Connect
  - Strava

- [ ] **Nutrition Apps**
  - MyFitnessPal sync
  - Cronometer import
  - Lose It! data

- [ ] **Calendriers**
  - Google Calendar
  - Outlook Calendar
  - Apple Calendar

- [ ] **Wearables Data**
  - Poids automatique
  - Activité physique
  - Sommeil
  - Fréquence cardiaque

- [ ] **Export API**
  - REST API publique
  - Webhooks
  - OAuth2
  - Rate limiting

---

## 🛠️ Solution Technique

### API Gateway

```python
from flask_restx import Api, Resource, Namespace
from flask_limiter import Limiter

api = Api(version='1.0', title='DietTracker API')
limiter = Limiter(key_func=lambda: get_api_key())

@api.route('/v1/integrations/googlefit')
class GoogleFitIntegration(Resource):
    @limiter.limit("100/hour")
    @require_oauth('fitness.read')
    def post(self):
        """Sync avec Google Fit"""
        service = GoogleFitService(
            credentials=request.oauth_token
        )
        
        # Import données
        weight_data = service.get_weight_data()
        activity_data = service.get_activity_data()
        
        # Sync avec notre DB
        for weight in weight_data:
            WeightHistory.create_or_update(
                user_id=current_user.id,
                weight=weight.value,
                date=weight.timestamp,
                source='google_fit'
            )
        
        return {'synced': len(weight_data)}, 200
```

### Webhooks System

```javascript
const WebhookManager = {
  register: async (url, events) => {
    const webhook = await api.post('/api/webhooks', {
      url,
      events,
      secret: generateSecret()
    });
    return webhook;
  },
  
  trigger: async (event, data) => {
    const webhooks = await getWebhooksForEvent(event);
    
    webhooks.forEach(webhook => {
      const signature = createHmac('sha256', webhook.secret)
        .update(JSON.stringify(data))
        .digest('hex');
      
      fetch(webhook.url, {
        method: 'POST',
        headers: {
          'X-DietTracker-Signature': signature,
          'X-DietTracker-Event': event
        },
        body: JSON.stringify(data)
      });
    });
  }
};
```

### OAuth2 Provider

```python
from authlib.integrations.flask_oauth2 import AuthorizationServer

authorization = AuthorizationServer()

@app.route('/oauth/authorize', methods=['GET', 'POST'])
def authorize():
    user = current_user()
    if request.method == 'GET':
        grant = authorization.validate_consent_request(end_user=user)
        return render_template('authorize.html', grant=grant)
    
    if request.form['confirm']:
        grant_user = user
    else:
        grant_user = None
    
    return authorization.create_authorization_response(grant_user=grant_user)

@app.route('/oauth/token', methods=['POST'])
def issue_token():
    return authorization.create_token_response()
```

---

## 🔗 Intégrations Disponibles

### Import
- ✅ Google Fit : Poids, activité
- ✅ Apple Health : Toutes métriques
- ✅ MyFitnessPal : Historique repas
- ✅ Fitbit : Sommeil, calories

### Export
- ✅ Google Calendar : Planning repas
- ✅ Webhooks : Events temps réel
- ✅ API REST : Accès complet

---

## 📊 Métriques

- Intégrations actives/user : 2.3
- Sync frequency : 4x/jour
- API calls : 10k/jour
- Webhook delivery : 99.9%

---

## 🎯 Rate Limits

| Tier | Requests/Hour | Burst |
|------|--------------|-------|
| Free | 100 | 10 |
| Premium | 1000 | 100 |
| Enterprise | Custom | Custom |

---

[[../SCRUM_DASHBOARD|← Dashboard]] | [[US-2.6-Premium|← US 2.6]] | [[../epics/EPIC-3-Mobile|Epic 3 →]]