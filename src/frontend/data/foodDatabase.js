// Base de données des aliments avec leurs valeurs nutritionnelles
export const FOOD_DATABASE = [
  {
    id: 'blanc_oeuf',
    name: 'Blanc d\'œuf',
    category: 'proteine',
    defaultUnit: 'g',
    units: {
      'g': { calories: 0.52, protein: 0.11, carbs: 0.007, fat: 0.002 },
      'unité': { calories: 17, protein: 3.6, carbs: 0.2, fat: 0.06, grams: 33 }
    }
  },
  {
    id: 'oeuf_entier',
    name: 'Œuf entier',
    category: 'proteine',
    defaultUnit: 'unité',
    units: {
      'unité': { calories: 70, protein: 6, carbs: 0.5, fat: 5, grams: 50 },
      'g': { calories: 1.4, protein: 0.12, carbs: 0.01, fat: 0.1 }
    }
  },
  {
    id: 'noix_cajou',
    name: 'Noix de cajou',
    category: 'lipide',
    defaultUnit: 'g',
    units: {
      'g': { calories: 5.53, protein: 0.18, carbs: 0.30, fat: 0.44 },
      'poignée': { calories: 166, protein: 5.4, carbs: 9, fat: 13.2, grams: 30 }
    }
  },
  {
    id: 'jus_pomme',
    name: 'Jus de pomme',
    category: 'glucide',
    defaultUnit: 'ml',
    units: {
      'ml': { calories: 0.46, protein: 0.001, carbs: 0.11, fat: 0.001 },
      'verre': { calories: 115, protein: 0.25, carbs: 27.5, fat: 0.25, ml: 250 }
    }
  },
  {
    id: 'cafe',
    name: 'Café',
    category: 'boisson',
    defaultUnit: 'tasse',
    units: {
      'tasse': { calories: 2, protein: 0.3, carbs: 0.4, fat: 0, ml: 200 },
      'ml': { calories: 0.01, protein: 0.0015, carbs: 0.002, fat: 0 }
    }
  },
  {
    id: 'lait_amandes',
    name: 'Lait d\'amandes',
    category: 'boisson',
    defaultUnit: 'ml',
    units: {
      'ml': { calories: 0.17, protein: 0.004, carbs: 0.008, fat: 0.015 },
      'verre': { calories: 42.5, protein: 1, carbs: 2, fat: 3.75, ml: 250 }
    }
  },
  {
    id: 'avoine',
    name: 'Avoine (flocons)',
    category: 'glucide',
    defaultUnit: 'g',
    units: {
      'g': { calories: 3.89, protein: 0.137, carbs: 0.66, fat: 0.069 },
      'tasse': { calories: 311, protein: 11, carbs: 52.8, fat: 5.5, grams: 80 }
    }
  },
  {
    id: 'pomme',
    name: 'Pomme',
    category: 'fruit',
    defaultUnit: 'unité',
    units: {
      'unité': { calories: 95, protein: 0.5, carbs: 25, fat: 0.3, grams: 180 },
      'g': { calories: 0.53, protein: 0.003, carbs: 0.14, fat: 0.002 }
    }
  },
  {
    id: 'viande_blanche',
    name: 'Viande blanche maigre',
    category: 'proteine',
    defaultUnit: 'g',
    units: {
      'g': { calories: 1.65, protein: 0.31, carbs: 0, fat: 0.036 },
      'portion': { calories: 247.5, protein: 46.5, carbs: 0, fat: 5.4, grams: 150 }
    }
  },
  {
    id: 'legumes_verts',
    name: 'Légumes verts',
    category: 'legume',
    defaultUnit: 'g',
    units: {
      'g': { calories: 0.25, protein: 0.02, carbs: 0.04, fat: 0.002 },
      'portion': { calories: 50, protein: 4, carbs: 8, fat: 0.4, grams: 200 }
    }
  },
  {
    id: 'huile_olive',
    name: 'Huile d\'olive',
    category: 'lipide',
    defaultUnit: 'c.à.s',
    units: {
      'c.à.s': { calories: 120, protein: 0, carbs: 0, fat: 13.5, ml: 15 },
      'c.à.c': { calories: 40, protein: 0, carbs: 0, fat: 4.5, ml: 5 },
      'ml': { calories: 8, protein: 0, carbs: 0, fat: 0.9 }
    }
  },
  {
    id: 'amandes',
    name: 'Amandes',
    category: 'lipide',
    defaultUnit: 'g',
    units: {
      'g': { calories: 5.79, protein: 0.21, carbs: 0.22, fat: 0.49 },
      'poignée': { calories: 173.7, protein: 6.3, carbs: 6.6, fat: 14.7, grams: 30 }
    }
  },
  {
    id: 'poisson_blanc',
    name: 'Poisson blanc maigre',
    category: 'proteine',
    defaultUnit: 'g',
    units: {
      'g': { calories: 0.82, protein: 0.18, carbs: 0, fat: 0.01 },
      'portion': { calories: 147.6, protein: 32.4, carbs: 0, fat: 1.8, grams: 180 }
    }
  },
  {
    id: 'salade_verte',
    name: 'Salade verte',
    category: 'legume',
    defaultUnit: 'g',
    units: {
      'g': { calories: 0.15, protein: 0.013, carbs: 0.029, fat: 0.002 },
      'portion': { calories: 15, protein: 1.3, carbs: 2.9, fat: 0.2, grams: 100 }
    }
  },
  {
    id: 'cla',
    name: 'CLA (supplément)',
    category: 'supplement',
    defaultUnit: 'mg',
    units: {
      'mg': { calories: 0, protein: 0, carbs: 0, fat: 0 },
      'gélule': { calories: 10, protein: 0, carbs: 0, fat: 1, mg: 1000 }
    }
  },
  {
    id: 'chocolat_noir',
    name: 'Chocolat noir 70%',
    category: 'autre',
    defaultUnit: 'carré',
    units: {
      'carré': { calories: 30, protein: 0.5, carbs: 2.5, fat: 2.1, grams: 5 },
      'g': { calories: 6, protein: 0.1, carbs: 0.5, fat: 0.42 }
    }
  }
];

// Fonction pour obtenir un aliment par son ID
export const getFoodById = (id) => {
  return FOOD_DATABASE.find(food => food.id === id);
};

// Fonction pour calculer les calories
export const calculateCalories = (foodId, quantity, unit) => {
  const food = getFoodById(foodId);
  if (!food || !food.units[unit]) return 0;
  
  return Math.round(food.units[unit].calories * quantity);
};

// Fonction pour calculer les macros
export const calculateMacros = (foodId, quantity, unit) => {
  const food = getFoodById(foodId);
  if (!food || !food.units[unit]) return { protein: 0, carbs: 0, fat: 0 };
  
  const unitData = food.units[unit];
  return {
    protein: Math.round(unitData.protein * quantity * 10) / 10,
    carbs: Math.round(unitData.carbs * quantity * 10) / 10,
    fat: Math.round(unitData.fat * quantity * 10) / 10
  };
};

// Obtenir les unités disponibles pour un aliment
export const getFoodUnits = (foodId) => {
  const food = getFoodById(foodId);
  if (!food) return [];
  return Object.keys(food.units);
};