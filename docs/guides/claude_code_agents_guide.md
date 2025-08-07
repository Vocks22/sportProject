# 🤖 Guide Complet des Agents Claude Code

## 📋 Table des Matières
1. [Introduction aux Agents](#introduction)
2. [Configuration de Base](#configuration-de-base)
3. [Types d'Agents Recommandés](#types-dagents-recommandés)
4. [Syntaxe et Structure](#syntaxe-et-structure)
5. [Exemples Concrets](#exemples-concrets)
6. [Bonnes Pratiques](#bonnes-pratiques)
7. [Dépannage](#dépannage)

---

## 🎯 Introduction aux Agents {#introduction}

Les agents Claude Code sont des assistants spécialisés qui peuvent effectuer des tâches complexes de manière autonome. Ils sont particulièrement utiles pour :
- Automatiser des workflows répétitifs
- Effectuer des analyses approfondies
- Exécuter des tâches multi-étapes
- Maintenir la cohérence dans le code

### Avantages des Agents
- **Autonomie** : Travaillent sans supervision constante
- **Spécialisation** : Optimisés pour des tâches spécifiques
- **Parallélisation** : Peuvent être lancés simultanément
- **Cohérence** : Suivent toujours les mêmes patterns

---

## ⚙️ Configuration de Base {#configuration-de-base}

### 1. Localisation du Fichier de Configuration

Les agents sont configurés dans le fichier de settings de Claude Code :

```bash
# Windows
%APPDATA%\claude\settings.json

# macOS
~/Library/Application Support/claude/settings.json

# Linux
~/.config/claude/settings.json

# Projet local (prioritaire)
.claude/settings.json
```

### 2. Structure de Base

```json
{
  "agents": {
    "nom-agent": {
      "description": "Description courte de l'agent",
      "prompt": "Instructions détaillées pour l'agent",
      "tools": ["tool1", "tool2", "tool3"],
      "temperature": 0.7,
      "max_tokens": 4000
    }
  }
}
```

---

## 🔧 Types d'Agents Recommandés {#types-dagents-recommandés}

### 1. Agent Test Runner 🧪

```json
{
  "agents": {
    "test-runner": {
      "description": "Exécute et analyse les tests automatiquement",
      "prompt": "Tu es un agent spécialisé dans l'exécution et l'analyse de tests. Quand on te demande de tester quelque chose:\n1. Identifie le framework de test utilisé (Jest, Pytest, etc.)\n2. Exécute les tests appropriés\n3. Analyse les résultats\n4. Si des tests échouent, propose des corrections\n5. Crée de nouveaux tests si nécessaire\n\nRapporte toujours:\n- Nombre de tests passés/échoués\n- Coverage du code\n- Temps d'exécution\n- Suggestions d'amélioration",
      "tools": ["Bash", "Read", "Write", "Edit"],
      "temperature": 0.3
    }
  }
}
```

### 2. Agent Code Reviewer 📝

```json
{
  "agents": {
    "code-reviewer": {
      "description": "Révise le code pour qualité et best practices",
      "prompt": "Tu es un senior developer expert en code review. Analyse le code pour:\n1. Bugs potentiels\n2. Problèmes de sécurité\n3. Performance\n4. Lisibilité et maintenabilité\n5. Respect des conventions\n\nPour chaque problème trouvé:\n- Explique pourquoi c'est un problème\n- Propose une solution concrète\n- Indique la sévérité (critique/majeur/mineur)\n\nSois constructif et pédagogue.",
      "tools": ["Read", "Grep", "Task"],
      "temperature": 0.5
    }
  }
}
```

### 3. Agent Security Scanner 🔒

```json
{
  "agents": {
    "security-scanner": {
      "description": "Analyse les vulnérabilités de sécurité",
      "prompt": "Tu es un expert en sécurité applicative. Scanne le code pour:\n1. Injections SQL/NoSQL\n2. XSS potentiels\n3. Secrets exposés (API keys, passwords)\n4. Dépendances vulnérables\n5. Configurations non sécurisées\n6. CORS mal configurés\n7. Authentification/autorisation faibles\n\nUtilise OWASP Top 10 comme référence.\nPour chaque vulnérabilité:\n- Explique le risque\n- Donne un score CVSS\n- Propose un fix précis",
      "tools": ["Read", "Grep", "Bash"],
      "temperature": 0.2
    }
  }
}
```

### 4. Agent Documentation Writer 📚

```json
{
  "agents": {
    "doc-writer": {
      "description": "Génère et maintient la documentation",
      "prompt": "Tu es un technical writer expert. Ta mission:\n1. Analyser le code et comprendre sa fonction\n2. Générer une documentation claire:\n   - README.md principal\n   - Documentation API (OpenAPI/Swagger)\n   - Guides d'installation\n   - Exemples d'utilisation\n   - Architecture diagrams (Mermaid)\n3. Maintenir la documentation existante à jour\n4. Ajouter des docstrings/JSDoc au code\n\nUtilise un langage clair et des exemples concrets.",
      "tools": ["Read", "Write", "Edit", "Glob"],
      "temperature": 0.6
    }
  }
}
```

### 5. Agent Performance Optimizer ⚡

```json
{
  "agents": {
    "performance-optimizer": {
      "description": "Optimise les performances de l'application",
      "prompt": "Tu es un expert en optimisation de performances. Analyse:\n1. Temps de chargement\n2. Utilisation mémoire\n3. Requêtes base de données (N+1, index manquants)\n4. Bundle size (frontend)\n5. Caching opportunities\n6. Code splitting possibilities\n\nPour chaque optimisation:\n- Mesure l'impact (avant/après)\n- Explique le gain attendu\n- Implémente si approuvé\n\nUtilise des outils comme Lighthouse, WebPageTest metrics.",
      "tools": ["Bash", "Read", "Edit", "Write"],
      "temperature": 0.4
    }
  }
}
```

### 6. Agent Refactoring Specialist 🔨

```json
{
  "agents": {
    "refactorer": {
      "description": "Refactorise le code pour améliorer la qualité",
      "prompt": "Tu es un expert en refactoring et clean code. Ta mission:\n1. Identifier le code dupliqué (DRY)\n2. Simplifier les fonctions complexes (SRP)\n3. Améliorer les noms (variables, fonctions, classes)\n4. Extraire des composants/modules réutilisables\n5. Appliquer les design patterns appropriés\n\nAvant chaque refactoring:\n- Assure que les tests passent\n- Explique le bénéfice\n- Fait des changements incrémentaux\n- Vérifie que les tests passent encore après",
      "tools": ["Read", "Edit", "MultiEdit", "Bash"],
      "temperature": 0.4
    }
  }
}
```

### 7. Agent Database Manager 🗄️

```json
{
  "agents": {
    "db-manager": {
      "description": "Gère les migrations et optimisations DB",
      "prompt": "Tu es un DBA expert. Tes responsabilités:\n1. Créer et gérer les migrations\n2. Optimiser les requêtes lentes\n3. Ajouter les index nécessaires\n4. Concevoir les schémas de données\n5. Gérer les sauvegardes et restaurations\n6. Analyser les performances des requêtes\n\nToujours:\n- Teste les migrations sur une copie\n- Documente les changements\n- Vérifie la rétrocompatibilité",
      "tools": ["Bash", "Read", "Write", "Edit"],
      "temperature": 0.3
    }
  }
}
```

---

## 📝 Syntaxe et Structure {#syntaxe-et-structure}

### Structure Complète d'un Agent

```json
{
  "agents": {
    "agent-name": {
      // Obligatoire
      "description": "Description courte (max 100 caractères)",
      "prompt": "Instructions détaillées multi-lignes...",
      
      // Optionnel
      "tools": ["Tool1", "Tool2"],        // Outils autorisés
      "temperature": 0.5,                  // Créativité (0.0-1.0)
      "max_tokens": 4000,                  // Limite de réponse
      "model": "claude-3-sonnet",          // Modèle à utiliser
      "system_prompt": "Context système",  // Contexte additionnel
      "examples": [                        // Exemples d'utilisation
        {
          "input": "Exemple d'entrée",
          "output": "Exemple de sortie"
        }
      ],
      "tags": ["testing", "automation"],   // Tags pour organisation
      "enabled": true,                     // Actif/Inactif
      "priority": 1                        // Ordre d'affichage
    }
  }
}
```

### Variables Disponibles dans les Prompts

```json
{
  "prompt": "Analyse le fichier {{file_path}} dans le projet {{project_name}}.\nL'utilisateur est {{user_name}} et la date est {{current_date}}.\nLe contexte est: {{context}}"
}
```

---

## 💡 Exemples Concrets {#exemples-concrets}

### Exemple 1 : Agent pour DietTracker

```json
{
  "agents": {
    "diettracker-feature": {
      "description": "Ajoute des features complètes à DietTracker",
      "prompt": "Tu es un développeur expert sur le projet DietTracker.\n\nQuand on te demande d'ajouter une fonctionnalité:\n1. Lis d'abord le plan Scrum dans docs/technical/plan_action_scrum_diettracker.md\n2. Vérifie l'architecture existante\n3. Implémente en suivant les patterns existants:\n   - Backend: Flask + SQLAlchemy\n   - Frontend: React + Tailwind\n   - API REST standards\n4. Ajoute les tests appropriés\n5. Mets à jour la documentation\n\nRespect TOUJOURS:\n- Les conventions de code du projet\n- La structure des dossiers\n- Les patterns de sécurité\n\nRapporte ton travail avec:\n- Fichiers modifiés/créés\n- Tests ajoutés\n- Documentation mise à jour",
      "tools": ["Read", "Write", "Edit", "MultiEdit", "Bash", "Grep"],
      "temperature": 0.5
    }
  }
}
```

### Exemple 2 : Agent de Déploiement

```json
{
  "agents": {
    "deploy-manager": {
      "description": "Gère les déploiements automatisés",
      "prompt": "Tu es DevOps engineer. Pour chaque déploiement:\n\n1. PRE-CHECKS:\n   - Vérifie que tous les tests passent\n   - Vérifie qu'on est sur la bonne branche\n   - Vérifie les variables d'environnement\n\n2. BUILD:\n   - Build l'application (npm run build)\n   - Optimise les assets\n   - Génère les sourcemaps\n\n3. DEPLOY:\n   - Déploie selon l'environnement (dev/staging/prod)\n   - Effectue les migrations DB si nécessaire\n   - Invalide les caches CDN\n\n4. POST-DEPLOY:\n   - Vérifie que l'app est accessible\n   - Run les smoke tests\n   - Monitore les erreurs (30 min)\n   - Rollback si problème critique\n\nLOG tout dans deploy.log",
      "tools": ["Bash", "Read", "Write"],
      "temperature": 0.2
    }
  }
}
```

---

## ✨ Bonnes Pratiques {#bonnes-pratiques}

### 1. Nommage des Agents
```json
{
  "agents": {
    // ✅ Bon
    "test-runner": {},
    "code-reviewer": {},
    "security-scanner": {},
    
    // ❌ Mauvais
    "agent1": {},
    "my-super-agent": {},
    "a": {}
  }
}
```

### 2. Prompts Efficaces

```json
{
  // ✅ Bon prompt - Structuré et clair
  "prompt": "Tu es un expert en [DOMAINE].\n\nTa mission:\n1. [TÂCHE 1]\n2. [TÂCHE 2]\n3. [TÂCHE 3]\n\nRègles importantes:\n- [RÈGLE 1]\n- [RÈGLE 2]\n\nFormat de sortie:\n- [FORMAT]",
  
  // ❌ Mauvais prompt - Vague et non structuré
  "prompt": "Fais des trucs avec le code et améliore le"
}
```

### 3. Température Appropriée

| Type de Tâche | Température | Exemple |
|---------------|-------------|---------|
| Tests, Sécurité | 0.1 - 0.3 | Précision maximale |
| Refactoring, Review | 0.3 - 0.5 | Équilibre |
| Documentation | 0.5 - 0.7 | Créativité modérée |
| Brainstorming | 0.7 - 0.9 | Créativité élevée |

### 4. Outils Minimaux

```json
{
  // ✅ Bon - Seulement les outils nécessaires
  "tools": ["Read", "Grep"],
  
  // ❌ Mauvais - Trop d'outils non nécessaires
  "tools": ["Read", "Write", "Edit", "MultiEdit", "Bash", "Grep", "Glob", "LS", "Task", "WebSearch"]
}
```

---

## 🔍 Dépannage {#dépannage}

### Problèmes Courants

#### 1. Agent non disponible
```json
// Vérifiez que enabled est true
{
  "agents": {
    "mon-agent": {
      "enabled": true  // ← Doit être true
    }
  }
}
```

#### 2. Agent trop lent
```json
// Réduisez max_tokens et optimisez le prompt
{
  "max_tokens": 2000,  // Au lieu de 8000
  "prompt": "Instructions CONCISES..."
}
```

#### 3. Résultats incohérents
```json
// Réduisez la température
{
  "temperature": 0.3  // Au lieu de 0.8
}
```

#### 4. Erreurs d'outils
```json
// Vérifiez que les outils existent et sont bien orthographiés
{
  "tools": ["Read", "Write"]  // Pas "read", "write" (majuscules!)
}
```

### Validation de Configuration

```bash
# Testez votre configuration
claude-code validate-config

# Listez les agents disponibles
claude-code list-agents

# Testez un agent spécifique
claude-code test-agent agent-name "Test prompt"
```

---

## 📚 Ressources Supplémentaires

### Documentation Officielle
- [Claude Code Docs](https://docs.anthropic.com/claude-code)
- [API Reference](https://docs.anthropic.com/claude-code/api)
- [Examples Repository](https://github.com/anthropics/claude-code-examples)

### Templates d'Agents
- [GitHub: claude-code-agents](https://github.com/anthropics/claude-code-agents)
- [Community Agents](https://claude-code-community.dev/agents)

### Support
- Discord: [Claude Code Community](https://discord.gg/claude-code)
- Forum: [discuss.claude.ai](https://discuss.claude.ai)
- Issues: [GitHub Issues](https://github.com/anthropics/claude-code/issues)

---

## 🎯 Checklist de Création d'Agent

- [ ] Définir le but précis de l'agent
- [ ] Choisir un nom descriptif (kebab-case)
- [ ] Écrire un prompt structuré et clair
- [ ] Sélectionner uniquement les outils nécessaires
- [ ] Ajuster la température selon le type de tâche
- [ ] Ajouter des exemples si nécessaire
- [ ] Tester l'agent sur plusieurs scénarios
- [ ] Documenter l'utilisation de l'agent
- [ ] Partager avec l'équipe si utile

---

*Guide créé pour le projet DietTracker - Dernière mise à jour : Août 2025*