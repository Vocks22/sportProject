// Script pour ajouter le mode chef à toutes les recettes dans Recipes.jsx
import fs from 'fs';

// Lire le fichier
const filePath = './src/frontend/components/Recipes.jsx';
let content = fs.readFileSync(filePath, 'utf8');

// Fonction pour générer des conseils chef selon la catégorie
function generateChefTips(recipeName, category) {
  const tips = [];
  
  // Conseil général basé sur la catégorie
  if (category.includes('repas1')) {
    tips.push({
      type: "tip",
      title: "Timing parfait",
      description: "Pour un petit-déjeuner optimal, préparez cette recette juste avant de consommer",
      importance: "high"
    });
  } else if (category.includes('repas2')) {
    tips.push({
      type: "tip",
      title: "Conservation",
      description: "Cette collation peut être préparée à l'avance et conservée au frais",
      importance: "medium"
    });
  } else if (category.includes('repas3')) {
    tips.push({
      type: "tip",
      title: "Cuisson optimale",
      description: "Ne pas trop cuire pour conserver tous les nutriments",
      importance: "high"
    });
  } else if (category.includes('repas4')) {
    tips.push({
      type: "tip",
      title: "Hydratation",
      description: "Accompagnez cette collation d'un grand verre d'eau",
      importance: "medium"
    });
  } else {
    tips.push({
      type: "tip",
      title: "Équilibre",
      description: "Respectez les portions pour maintenir l'équilibre nutritionnel",
      importance: "high"
    });
  }
  
  // Ajouter un conseil secret
  tips.push({
    type: "secret",
    title: "Astuce du chef",
    description: "Utilisez des épices pour rehausser les saveurs sans ajouter de calories",
    importance: "medium"
  });
  
  return tips;
}

// Fonction pour déterminer la difficulté
function getDifficulty(time) {
  const minutes = parseInt(time);
  if (minutes <= 10) return "beginner";
  if (minutes <= 20) return "intermediate";
  return "advanced";
}

// Regex pour trouver chaque objet recette
const recipeRegex = /(\{[^}]*id:\s*\d+[^}]*\})/g;

// Traiter chaque recette
content = content.replace(recipeRegex, (match) => {
  // Si la recette a déjà has_chef_mode, on ne fait rien
  if (match.includes('has_chef_mode')) {
    return match;
  }
  
  // Extraire le nom et la catégorie
  const nameMatch = match.match(/name:\s*"([^"]+)"/);
  const categoryMatch = match.match(/category:\s*"([^"]+)"/);
  const timeMatch = match.match(/time:\s*"([^"]+)"/);
  
  if (nameMatch && categoryMatch && timeMatch) {
    const name = nameMatch[1];
    const category = categoryMatch[1];
    const time = timeMatch[1];
    const difficulty = getDifficulty(time);
    
    // Ajouter has_chef_mode et difficulty_level avant la dernière accolade
    const lastBraceIndex = match.lastIndexOf('}');
    const chefData = `,
      has_chef_mode: true,
      difficulty_level: "${difficulty}"`;
    
    return match.slice(0, lastBraceIndex) + chefData + match.slice(lastBraceIndex);
  }
  
  return match;
});

// Écrire le fichier modifié
fs.writeFileSync(filePath, content, 'utf8');
console.log('✅ Mode chef ajouté à toutes les recettes!');