# 🌐 US 2.4 - Partage Social

> **Status** : 🔴 À FAIRE
> **Points** : 8
> **Sprint** : 6
> **Date prévue** : 16-29 Sept 2025
> **Développeur** : Non assigné
> **Reviewer** : À définir

[[../SCRUM_DASHBOARD|← Dashboard]] | [[../epics/EPIC-2-Advanced|← Epic 2]]

---

## 📝 User Story

### En tant que...
Utilisateur fier de ma progression

### Je veux...
Pouvoir partager mes réussites et recettes sur les réseaux sociaux

### Afin de...
Motiver mes amis, recevoir des encouragements et créer une communauté de soutien

---

## 🎯 Acceptance Criteria

- [ ] **Partage de Progression**
  - Graphique perte de poids
  - Badges de réussite
  - Statistiques personnalisées
  - Photo avant/après (optionnel)

- [ ] **Partage de Recettes**
  - Photo du plat
  - Infos nutritionnelles
  - Lien vers recette publique
  - Hashtags automatiques

- [ ] **Intégrations Sociales**
  - Facebook
  - Instagram
  - Twitter/X
  - WhatsApp
  - Pinterest (recettes)

- [ ] **Communauté Interne**
  - Profils publics/privés
  - Follow autres utilisateurs
  - Likes et commentaires
  - Feed d'activité

- [ ] **Challenges Sociaux**
  - Créer/rejoindre challenges
  - Classements hebdomadaires
  - Badges collectifs
  - Motivation de groupe

---

## 🛠️ Solution Technique Proposée

### API Partage Social

```python
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO

class SocialShareService:
    def __init__(self):
        self.templates = self._load_templates()
        
    def generate_progress_card(self, user_id, period='month'):
        """Génère une carte de progression visuelle"""
        user = User.query.get(user_id)
        stats = self._calculate_stats(user, period)
        
        # Template image 1080x1080 (Instagram)
        img = Image.open('templates/progress_card.png')
        draw = ImageDraw.Draw(img)
        
        # Ajout des données
        font_title = ImageFont.truetype('fonts/bold.ttf', 60)
        font_stats = ImageFont.truetype('fonts/regular.ttf', 40)
        
        # Titre
        draw.text((540, 100), f"{stats['weight_lost']}kg perdus!", 
                 font=font_title, anchor="mm", fill='#2ECC71')
        
        # Stats
        y_pos = 300
        for stat, value in stats.items():
            draw.text((540, y_pos), f"{stat}: {value}", 
                     font=font_stats, anchor="mm")
            y_pos += 80
        
        # Graphique de progression
        graph = self._generate_weight_graph(user, period)
        img.paste(graph, (140, 600))
        
        # Watermark
        draw.text((540, 1000), "#DietTracker #HealthyLife", 
                 font=font_stats, anchor="mm", fill='#95A5A6')
        
        return img
    
    def share_to_instagram(self, image, caption, hashtags):
        """Partage sur Instagram via API"""
        # Instagram Graph API
        access_token = get_user_instagram_token()
        
        # Upload image
        media_url = self._upload_to_cdn(image)
        
        # Create media container
        response = requests.post(
            f'https://graph.facebook.com/v17.0/{IG_USER_ID}/media',
            params={
                'image_url': media_url,
                'caption': f"{caption}\n\n{' '.join(hashtags)}",
                'access_token': access_token
            }
        )
        
        container_id = response.json()['id']
        
        # Publish
        publish_response = requests.post(
            f'https://graph.facebook.com/v17.0/{IG_USER_ID}/media_publish',
            params={
                'creation_id': container_id,
                'access_token': access_token
            }
        )
        
        return publish_response.json()
```

### Composant React de Partage

```jsx
const ShareModal = ({ type, data }) => {
  const [selectedPlatforms, setSelectedPlatforms] = useState([]);
  const [caption, setCaption] = useState('');
  const [preview, setPreview] = useState(null);
  const [sharing, setSharing] = useState(false);
  
  useEffect(() => {
    // Générer preview
    generatePreview();
  }, [type, data]);
  
  const generatePreview = async () => {
    const response = await api.post('/api/social/preview', {
      type,
      data,
      template: 'modern'
    });
    setPreview(response.data.preview_url);
    setCaption(response.data.suggested_caption);
  };
  
  const handleShare = async () => {
    setSharing(true);
    
    const promises = selectedPlatforms.map(platform => 
      api.post('/api/social/share', {
        platform,
        type,
        data,
        caption,
        hashtags: generateHashtags()
      })
    );
    
    try {
      await Promise.all(promises);
      toast.success('Partagé avec succès!');
      trackEvent('social_share', { platforms: selectedPlatforms });
    } catch (error) {
      toast.error('Erreur lors du partage');
    } finally {
      setSharing(false);
    }
  };
  
  return (
    <Modal isOpen onClose={onClose}>
      <h2>Partager ma réussite</h2>
      
      <div className="preview-container">
        <img src={preview} alt="Preview" />
      </div>
      
      <textarea
        value={caption}
        onChange={(e) => setCaption(e.target.value)}
        placeholder="Ajoutez un message..."
        maxLength={280}
      />
      
      <div className="platforms">
        {['facebook', 'instagram', 'twitter', 'whatsapp'].map(platform => (
          <PlatformToggle
            key={platform}
            platform={platform}
            selected={selectedPlatforms.includes(platform)}
            onToggle={() => togglePlatform(platform)}
          />
        ))}
      </div>
      
      <button 
        onClick={handleShare}
        disabled={!selectedPlatforms.length || sharing}
      >
        {sharing ? 'Partage en cours...' : 'Partager'}
      </button>
    </Modal>
  );
};
```

### Système de Challenges

```python
class Challenge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.Text)
    type = db.Column(db.Enum('weight_loss', 'steps', 'meals', 'custom'))
    target = db.Column(db.JSON)  # {value: 5, unit: 'kg'}
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relations
    participants = db.relationship('ChallengeParticipant', backref='challenge')
    
    def get_leaderboard(self):
        """Calcule le classement actuel"""
        leaderboard = []
        for participant in self.participants:
            progress = participant.calculate_progress()
            leaderboard.append({
                'user': participant.user,
                'progress': progress,
                'rank': None
            })
        
        # Tri et ranking
        leaderboard.sort(key=lambda x: x['progress'], reverse=True)
        for idx, entry in enumerate(leaderboard, 1):
            entry['rank'] = idx
        
        return leaderboard
```

---

## 📊 Templates de Partage

### Cards Progression
```
🎯 Achievement Cards
├── Perte de poids (avant/après)
├── Streak (jours consécutifs)
├── Objectif atteint
├── Badge spécial
└── Statistiques mensuelles
```

### Formats Optimisés
| Plateforme | Format | Dimensions | Features |
|------------|--------|------------|----------|
| Instagram | Carré | 1080x1080 | Stories, Feed |
| Facebook | Rectangle | 1200x630 | Timeline, Stories |
| Twitter | Paysage | 1024x512 | Tweet card |
| WhatsApp | Carré | 800x800 | Status |

---

## 🏆 Gamification Sociale

### Badges Partageables
- 🥇 **First Goal** : Premier objectif atteint
- 🔥 **Hot Streak** : 30 jours consécutifs
- 💪 **Transformer** : -10kg atteints
- 🌱 **Healthy Habit** : 100 repas équilibrés
- 👥 **Team Player** : 5 challenges terminés

### Challenges Populaires
1. **Summer Body** : -5kg en 8 semaines
2. **No Sugar November** : 30 jours sans sucre
3. **10K Steps** : 10,000 pas/jour pendant 1 mois
4. **Meal Prep Master** : 4 semaines de préparation

---

## 🧪 Tests

### Tests unitaires
- [ ] Génération images partage
- [ ] Intégration APIs sociales
- [ ] Calcul classements
- [ ] Privacy settings

### Tests d'intégration  
- [ ] Partage multi-plateformes
- [ ] Challenges temps réel
- [ ] Notifications sociales
- [ ] Modération contenu

### Tests UX
- [ ] Flow de partage intuitif
- [ ] Preview responsive
- [ ] Temps de génération < 2s

---

## 📊 Métriques de Succès

### KPIs
- Partages/mois : > 500
- Taux engagement : +30%
- Nouveaux users via partage : 15%
- Challenges actifs : > 10

### Impact Business
- Acquisition organique
- Rétention améliorée
- Effet réseau
- Brand awareness

---

## 🆘 Risques

| Risque | Impact | Mitigation |
|--------|---------|------------|
| API limits | Haut | Rate limiting |
| Privacy concerns | Haut | Opt-in strict |
| Contenu inapproprié | Moyen | Modération AI |
| Spam | Moyen | Limites quotidiennes |

---

[[../SCRUM_DASHBOARD|← Dashboard]] | [[US-2.3-Export|← US 2.3]] | [[US-2.5-Notifications|US 2.5 →]]