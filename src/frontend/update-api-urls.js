#!/usr/bin/env node

/**
 * Script pour remplacer toutes les URLs localhost par des variables d'environnement
 */

const fs = require('fs');
const path = require('path');

// Patterns à remplacer
const patterns = [
  {
    pattern: /http:\/\/localhost:5000/g,
    replacement: '${import.meta.env.VITE_API_URL || "http://localhost:5000"}'
  },
  {
    pattern: /fetch\(`http:\/\/localhost:5000/g,
    replacement: 'fetch(`${import.meta.env.VITE_API_URL || "http://localhost:5000"}'
  }
];

// Fichiers à modifier
const filesToUpdate = [
  'components/Dashboard.jsx',
  'components/Progress.jsx',
  'components/MealPlanning.jsx',
  'components/Recipes.jsx',
  'components/Shopping.jsx',
  'components/WeightChart.jsx',
  'components/CookingGuide.jsx',
  'components/ProgressAlerts.jsx',
  'pages/ProfilePage.jsx',
  'pages/MeasurementsPage.jsx',
  'hooks/useShoppingList.js',
  'hooks/useUserProfile.js',
];

console.log('🔄 Mise à jour des URLs d\'API...\n');

filesToUpdate.forEach(file => {
  const filePath = path.join(__dirname, file);
  
  if (fs.existsSync(filePath)) {
    let content = fs.readFileSync(filePath, 'utf8');
    let modified = false;
    
    patterns.forEach(({ pattern, replacement }) => {
      if (pattern.test(content)) {
        content = content.replace(pattern, replacement);
        modified = true;
      }
    });
    
    if (modified) {
      fs.writeFileSync(filePath, content);
      console.log(`✅ ${file} - URLs mises à jour`);
    } else {
      console.log(`⏭️  ${file} - Pas de changement nécessaire`);
    }
  } else {
    console.log(`❌ ${file} - Fichier non trouvé`);
  }
});

console.log('\n✨ Mise à jour terminée!');
console.log('\n📝 N\'oubliez pas de:');
console.log('   1. Définir VITE_API_URL dans Netlify');
console.log('   2. Déployer votre backend sur Render/Heroku');
console.log('   3. Mettre à jour les CORS dans Flask');