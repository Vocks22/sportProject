# 🥗 DietTracker - Application de Suivi Nutritionnel

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/username/diettracker)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![React](https://img.shields.io/badge/React-18.2-61dafb.svg)](https://reactjs.org/)
[![Flask](https://img.shields.io/badge/Flask-2.3-black.svg)](https://flask.palletsprojects.com/)

Application web complète de suivi nutritionnel et de planification de repas, développée spécifiquement pour accompagner un programme de perte de poids personnalisé.

## 🌟 Fonctionnalités

- 📊 **Dashboard personnalisé** - Vue d'ensemble quotidienne avec métriques clés
- 📅 **Planification hebdomadaire** - Organisation complète des repas sur 7 jours
- 🍽️ **Bibliothèque de 65+ recettes** - Recettes adaptées avec informations nutritionnelles
- 🛒 **Liste de courses automatique** - Génération intelligente basée sur le planning
- 📈 **Suivi de progression** - Graphiques et statistiques détaillés
- 📱 **Design responsive** - Interface optimisée mobile/tablette/desktop

## 🚀 Démarrage Rapide

### Prérequis

- Node.js 18+ et pnpm
- Python 3.9+
- SQLite3

### Installation

```bash
# Cloner le repository
git clone https://github.com/username/diettracker.git
cd diettracker

# Installation Frontend
cd src/frontend
pnpm install

# Installation Backend
cd ../backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Initialiser la base de données
python scripts/init_data.py
```

### Lancement

```bash
# Terminal 1 - Backend
cd src/backend
python main.py

# Terminal 2 - Frontend
cd src/frontend
pnpm run dev
```

L'application sera accessible sur http://localhost:5173

## 📁 Structure du Projet

```
diettracker/
├── src/
│   ├── frontend/          # Application React
│   │   ├── components/    # Composants UI réutilisables
│   │   ├── pages/        # Pages de l'application
│   │   ├── hooks/        # Custom React hooks
│   │   ├── utils/        # Fonctions utilitaires
│   │   └── assets/       # Images et ressources
│   └── backend/          # API Flask
│       ├── models/       # Modèles SQLAlchemy
│       ├── routes/       # Endpoints API
│       ├── services/     # Logique métier
│       └── database/     # Configuration DB
├── docs/                 # Documentation complète
│   ├── technical/        # Documentation technique
│   ├── user/            # Guide utilisateur
│   └── api/             # Documentation API
├── tests/               # Tests unitaires et E2E
├── scripts/             # Scripts utilitaires
└── config/              # Fichiers de configuration
```

## 🛠️ Stack Technique

### Frontend
- **React 18** - Framework UI
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **shadcn/ui** - Composants UI
- **React Router** - Navigation

### Backend
- **Flask** - Framework web Python
- **SQLAlchemy** - ORM
- **SQLite** - Base de données
- **Flask-CORS** - CORS handling
- **Flask-JWT** - Authentification (à venir)

## 📖 Documentation

- [Guide Utilisateur](docs/user/DietTracker%20-%20Guide%20Utilisateur.md)
- [Documentation Technique](docs/technical/documentation_technique.md)
- [Plan d'Action Scrum](docs/technical/plan_action_scrum_diettracker.md)
- [Évaluation du Projet](docs/technical/evaluation_diettracker.md)

## 🔄 Roadmap

### Phase 1 - Backend & Auth (En cours)
- [ ] Connexion base de données
- [ ] Authentification JWT
- [ ] API CRUD complète

### Phase 2 - Tests & TypeScript
- [ ] Migration TypeScript
- [ ] Tests unitaires (80% coverage)
- [ ] CI/CD pipeline

### Phase 3 - PWA & Optimisations
- [ ] Progressive Web App
- [ ] Mode offline
- [ ] Optimisations performance

### Phase 4 - Features Avancées
- [ ] Analytics avancés
- [ ] Intelligence artificielle
- [ ] Intégrations tierces

## 🤝 Contribution

Les contributions sont les bienvenues ! Consultez [CONTRIBUTING.md](CONTRIBUTING.md) pour les guidelines.

## 📝 License

Ce projet est sous licence MIT - voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 👥 Équipe

Développé pour Fabien - Août 2025

## 🆘 Support

Pour toute question ou problème, créez une [issue](https://github.com/username/diettracker/issues).

---

**Application en production** : https://bpzrmdhk.manus.space