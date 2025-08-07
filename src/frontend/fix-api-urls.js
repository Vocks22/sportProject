/**
 * Script pour corriger toutes les URLs API hardcodées
 */

import fs from 'fs';
import path from 'path';

const API_URL_REPLACEMENT = '${import.meta.env.VITE_API_URL || "http://localhost:5000"}/api';

const files = [
  'pages/ProfilePage.jsx',
  'pages/MeasurementsPage.jsx',
  'components/Progress.jsx',
  'components/Dashboard.jsx'
];

files.forEach(file => {
  const filePath = path.join(process.cwd(), file);
  let content = fs.readFileSync(filePath, 'utf8');
  
  // Remplacer les URLs hardcodées
  content = content.replace(
    /`http:\/\/localhost:5000\/api/g,
    '`${import.meta.env.VITE_API_URL || "http://localhost:5000"}/api'
  );
  
  // Ajouter l'import si nécessaire
  if (!content.includes('import.meta.env.VITE_API_URL') && content.includes('${import.meta.env.VITE_API_URL')) {
    console.log(`✅ Mise à jour de ${file}`);
  }
  
  fs.writeFileSync(filePath, content);
});

console.log('✅ Toutes les URLs API ont été mises à jour !');