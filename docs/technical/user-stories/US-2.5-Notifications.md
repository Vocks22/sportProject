# 🔔 US 2.5 - Système de Notifications

> **Status** : 🔴 À FAIRE
> **Points** : 13
> **Sprint** : 7
> **Date prévue** : 30 Sept - 13 Oct 2025
> **Développeur** : Non assigné
> **Reviewer** : À définir

[[../SCRUM_DASHBOARD|← Dashboard]] | [[../epics/EPIC-2-Advanced|← Epic 2]]

---

## 📝 User Story

### En tant que...
Utilisateur souhaitant rester engagé

### Je veux...
Recevoir des notifications pertinentes et personnalisées

### Afin de...
Ne pas oublier mes objectifs et maintenir ma motivation

---

## 🎯 Acceptance Criteria

- [ ] **Notifications Push**
  - Mobile (iOS/Android)
  - Web push notifications
  - Desktop notifications
  - Email notifications

- [ ] **Types de Notifications**
  - Rappel de pesée (samedi matin)
  - Heure des repas
  - Planning non rempli
  - Objectif atteint
  - Challenge update
  - Nouveau follower

- [ ] **Personnalisation**
  - Choix des types actifs
  - Horaires personnalisés
  - Fréquence ajustable
  - Mode silencieux

- [ ] **Smart Notifications**
  - ML pour timing optimal
  - Éviter spam
  - Contexte utilisateur
  - A/B testing

---

## 🛠️ Solution Technique

### Backend Service

```python
from celery import Celery
from firebase_admin import messaging
import schedule

class NotificationService:
    def __init__(self):
        self.celery = Celery('notifications')
        self.fcm = messaging
        
    def send_push(self, user_id, notification):
        """Envoie notification push"""
        user = User.query.get(user_id)
        tokens = user.device_tokens
        
        message = messaging.MulticastMessage(
            notification=messaging.Notification(
                title=notification.title,
                body=notification.body,
                image=notification.image_url
            ),
            data=notification.data,
            tokens=tokens
        )
        
        response = messaging.send_multicast(message)
        return response
    
    @celery.task
    def schedule_meal_reminders(self):
        """Rappels de repas programmés"""
        users = User.query.filter_by(
            notifications_enabled=True
        ).all()
        
        for user in users:
            next_meal = self.get_next_meal(user)
            if next_meal:
                self.send_push(user.id, {
                    'title': f'🍽️ {next_meal.type.capitalize()}',
                    'body': f'{next_meal.recipe.name} - {next_meal.calories} kcal',
                    'data': {'type': 'meal_reminder', 'meal_id': next_meal.id}
                })
```

---

## 📊 Métriques

- Open rate : > 40%
- CTR : > 25%
- Opt-out : < 5%
- Engagement boost : +35%

---

[[../SCRUM_DASHBOARD|← Dashboard]] | [[US-2.4-Social|← US 2.4]] | [[US-2.6-Premium|US 2.6 →]]