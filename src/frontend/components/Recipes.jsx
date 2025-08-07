import { useState } from 'react'
import { Search, Clock, Users, ChefHat, Filter, Star } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { CookingGuideButton, ChefModeBadge, ChefTipsPreview } from './CookingGuideButton'

export function Recipes() {
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('all')
  const [selectedDifficulty, setSelectedDifficulty] = useState('all')
  const [showChefModeOnly, setShowChefModeOnly] = useState(false)

  // Bibliothèque complète de 65 recettes
  const recipes = [
    // REPAS 1 - Petit-déjeuner (15 recettes)
    {
      id: 1,
      name: "Omelette aux Blancs d'Œufs Classique",
      category: "repas1",
      categoryName: "Petit-déjeuner",
      emoji: "🍳",
      time: "10 min",
      calories: 351,
      protein: 28,
      ingredients: ["3 blancs d'œufs", "40g noix de cajou", "épices"],
      ustensils: ["Poêle antiadhésive"],
      description: "L'omelette classique de votre programme, riche en protéines",
      has_chef_mode: true,
      difficulty_level: "beginner",
      chef_tips: [
        {
          id: "tip1",
          type: "tip",
          title: "Température parfaite",
          description: "Utilisez une température moyenne pour éviter que les blancs d'œufs ne brunissent trop vite",
          importance: "high"
        },
        {
          id: "tip2", 
          type: "secret",
          title: "Secret du chef",
          description: "Ajoutez une pincée d'eau aux blancs d'œufs pour une texture plus moelleuse",
          importance: "medium"
        }
      ]
    },
    {
      id: 2,
      name: "Omelette aux Blancs d'Œufs et Épinards",
      category: "repas1",
      categoryName: "Petit-déjeuner",
      emoji: "🍳",
      time: "12 min",
      calories: 355,
      protein: 29,
      ingredients: ["3 blancs d'œufs", "40g noix de cajou", "50g épinards frais"],
      ustensils: ["Poêle", "passoire"],
      description: "Version enrichie en fer avec des épinards frais"
    },
    {
      id: 3,
      name: "Scrambled aux Blancs d'Œufs et Herbes",
      category: "repas1",
      categoryName: "Petit-déjeuner",
      emoji: "🍳",
      time: "8 min",
      calories: 348,
      protein: 28,
      ingredients: ["3 blancs d'œufs", "40g amandes effilées", "herbes de Provence"],
      ustensils: ["Poêle", "fouet"],
      description: "Œufs brouillés parfumés aux herbes de Provence"
    },
    {
      id: 4,
      name: "Omelette Roulée aux Blancs d'Œufs",
      category: "repas1",
      categoryName: "Petit-déjeuner",
      emoji: "🍳",
      time: "15 min",
      calories: 351,
      protein: 28,
      ingredients: ["3 blancs d'œufs", "40g noix de cajou", "paprika"],
      ustensils: ["Poêle", "spatule"],
      description: "Technique de roulage pour une présentation élégante"
    },
    {
      id: 5,
      name: "Blancs d'Œufs Brouillés aux Champignons",
      category: "repas1",
      categoryName: "Petit-déjeuner",
      emoji: "🍳",
      time: "12 min",
      calories: 350,
      protein: 29,
      ingredients: ["3 blancs d'œufs", "40g amandes", "50g champignons"],
      ustensils: ["Poêle", "couteau"],
      description: "Saveur umami des champignons pour plus de goût"
    },
    {
      id: 6,
      name: "Omelette aux Blancs d'Œufs et Tomates Cerises",
      category: "repas1",
      categoryName: "Petit-déjeuner",
      emoji: "🍳",
      time: "10 min",
      calories: 353,
      protein: 28,
      ingredients: ["3 blancs d'œufs", "40g noix de cajou", "50g tomates cerises"],
      ustensils: ["Poêle", "couteau"],
      description: "Fraîcheur des tomates cerises pour un réveil vitaminé"
    },
    {
      id: 7,
      name: "Blancs d'Œufs à la Ciboulette",
      category: "repas1",
      categoryName: "Petit-déjeuner",
      emoji: "🍳",
      time: "8 min",
      calories: 348,
      protein: 28,
      ingredients: ["3 blancs d'œufs", "40g amandes", "ciboulette fraîche"],
      ustensils: ["Poêle", "ciseaux"],
      description: "Délicatesse de la ciboulette pour un goût raffiné"
    },
    {
      id: 8,
      name: "Omelette aux Blancs d'Œufs et Courgettes",
      category: "repas1",
      categoryName: "Petit-déjeuner",
      emoji: "🍳",
      time: "12 min",
      calories: 352,
      protein: 28,
      ingredients: ["3 blancs d'œufs", "40g noix de cajou", "50g courgettes râpées"],
      ustensils: ["Poêle", "râpe"],
      description: "Légèreté des courgettes pour une texture moelleuse"
    },
    {
      id: 9,
      name: "Blancs d'Œufs aux Fines Herbes",
      category: "repas1",
      categoryName: "Petit-déjeuner",
      emoji: "🍳",
      time: "10 min",
      calories: 348,
      protein: 28,
      ingredients: ["3 blancs d'œufs", "40g amandes", "persil, basilic, ciboulette"],
      ustensils: ["Poêle", "ciseaux"],
      description: "Mélange d'herbes fraîches pour un maximum de saveurs"
    },
    {
      id: 10,
      name: "Omelette aux Blancs d'Œufs et Poivrons",
      category: "repas1",
      categoryName: "Petit-déjeuner",
      emoji: "🍳",
      time: "15 min",
      calories: 354,
      protein: 28,
      ingredients: ["3 blancs d'œufs", "40g noix de cajou", "50g poivrons colorés"],
      ustensils: ["Poêle", "couteau"],
      description: "Couleurs et vitamines des poivrons pour bien commencer"
    },
    {
      id: 11,
      name: "Blancs d'Œufs Façon Tortilla",
      category: "repas1",
      categoryName: "Petit-déjeuner",
      emoji: "🍳",
      time: "12 min",
      calories: 350,
      protein: 28,
      ingredients: ["3 blancs d'œufs", "40g amandes", "ail, paprika fumé"],
      ustensils: ["Poêle", "presse-ail"],
      description: "Inspiration espagnole avec ail et paprika fumé"
    },
    {
      id: 12,
      name: "Omelette aux Blancs d'Œufs et Roquette",
      category: "repas1",
      categoryName: "Petit-déjeuner",
      emoji: "🍳",
      time: "10 min",
      calories: 352,
      protein: 28,
      ingredients: ["3 blancs d'œufs", "40g noix de cajou", "30g roquette"],
      ustensils: ["Poêle", "saladier"],
      description: "Piquant de la roquette pour réveiller les papilles"
    },
    {
      id: 13,
      name: "Blancs d'Œufs aux Épices Orientales",
      category: "repas1",
      categoryName: "Petit-déjeuner",
      emoji: "🍳",
      time: "10 min",
      calories: 348,
      protein: 28,
      ingredients: ["3 blancs d'œufs", "40g amandes", "cumin, coriandre, paprika"],
      ustensils: ["Poêle", "mortier"],
      description: "Voyage culinaire avec des épices orientales"
    },
    {
      id: 14,
      name: "Omelette aux Blancs d'Œufs et Brocolis",
      category: "repas1",
      categoryName: "Petit-déjeuner",
      emoji: "🍳",
      time: "15 min",
      calories: 353,
      protein: 29,
      ingredients: ["3 blancs d'œufs", "40g noix de cajou", "50g brocolis vapeur"],
      ustensils: ["Poêle", "cuit-vapeur"],
      description: "Superaliment brocolis pour un boost nutritionnel"
    },
    {
      id: 15,
      name: "Blancs d'Œufs à l'Italienne",
      category: "repas1",
      categoryName: "Petit-déjeuner",
      emoji: "🍳",
      time: "12 min",
      calories: 350,
      protein: 28,
      ingredients: ["3 blancs d'œufs", "40g amandes", "basilic, origan, ail"],
      ustensils: ["Poêle", "presse-ail"],
      description: "Saveurs italiennes avec basilic et origan"
    },

    // COLLATION 1 - Smoothies (10 recettes)
    {
      id: 16,
      name: "Smoothie Protéiné Classique",
      category: "collation1",
      categoryName: "Smoothie",
      emoji: "🥤",
      time: "5 min",
      calories: 300,
      protein: 12,
      ingredients: ["200ml lait d'amande", "60g avoine", "50g ananas", "1 carré chocolat noir"],
      ustensils: ["Blender"],
      description: "Le smoothie de référence de votre programme"
    },
    {
      id: 17,
      name: "Smoothie Tropical Protéiné",
      category: "collation1",
      categoryName: "Smoothie",
      emoji: "🥤",
      time: "5 min",
      calories: 305,
      protein: 12,
      ingredients: ["200ml lait d'amande", "60g avoine", "50g ananas", "30g mangue"],
      ustensils: ["Blender"],
      description: "Évasion tropicale avec ananas et mangue"
    },
    {
      id: 18,
      name: "Smoothie Chocolat-Banane",
      category: "collation1",
      categoryName: "Smoothie",
      emoji: "🥤",
      time: "5 min",
      calories: 310,
      protein: 13,
      ingredients: ["200ml lait d'amande", "60g avoine", "1/2 banane", "1 carré chocolat noir"],
      ustensils: ["Blender"],
      description: "Gourmandise chocolat-banane pour les envies sucrées"
    },
    {
      id: 19,
      name: "Smoothie Vert Protéiné",
      category: "collation1",
      categoryName: "Smoothie",
      emoji: "🥤",
      time: "5 min",
      calories: 298,
      protein: 12,
      ingredients: ["200ml lait d'amande", "60g avoine", "50g épinards", "50g ananas"],
      ustensils: ["Blender"],
      description: "Détox vert avec épinards et ananas"
    },
    {
      id: 20,
      name: "Smoothie Fruits Rouges Avoine",
      category: "collation1",
      categoryName: "Smoothie",
      emoji: "🥤",
      time: "5 min",
      calories: 295,
      protein: 12,
      ingredients: ["200ml lait d'amande", "60g avoine", "50g fruits rouges mélangés"],
      ustensils: ["Blender"],
      description: "Antioxydants des fruits rouges pour la récupération"
    },
    {
      id: 21,
      name: "Smoothie Vanille-Cannelle",
      category: "collation1",
      categoryName: "Smoothie",
      emoji: "🥤",
      time: "5 min",
      calories: 300,
      protein: 12,
      ingredients: ["200ml lait d'amande", "60g avoine", "50g ananas", "extrait vanille, cannelle"],
      ustensils: ["Blender"],
      description: "Douceur vanillée avec une pointe de cannelle"
    },
    {
      id: 22,
      name: "Smoothie Coco-Ananas",
      category: "collation1",
      categoryName: "Smoothie",
      emoji: "🥤",
      time: "5 min",
      calories: 308,
      protein: 12,
      ingredients: ["200ml lait d'amande", "60g avoine", "50g ananas", "copeaux de coco (5g)"],
      ustensils: ["Blender"],
      description: "Exotisme coco-ananas pour s'évader"
    },
    {
      id: 23,
      name: "Smoothie Chocolat-Menthe",
      category: "collation1",
      categoryName: "Smoothie",
      emoji: "🥤",
      time: "5 min",
      calories: 302,
      protein: 12,
      ingredients: ["200ml lait d'amande", "60g avoine", "1 carré chocolat noir", "menthe fraîche"],
      ustensils: ["Blender"],
      description: "Fraîcheur mentholée avec chocolat noir"
    },
    {
      id: 24,
      name: "Smoothie Pêche-Avoine",
      category: "collation1",
      categoryName: "Smoothie",
      emoji: "🥤",
      time: "5 min",
      calories: 305,
      protein: 12,
      ingredients: ["200ml lait d'amande", "60g avoine", "50g pêche", "1 carré chocolat noir"],
      ustensils: ["Blender"],
      description: "Douceur estivale de la pêche"
    },
    {
      id: 25,
      name: "Smoothie Épicé",
      category: "collation1",
      categoryName: "Smoothie",
      emoji: "🥤",
      time: "5 min",
      calories: 300,
      protein: 12,
      ingredients: ["200ml lait d'amande", "60g avoine", "50g ananas", "gingembre, curcuma"],
      ustensils: ["Blender"],
      description: "Boost énergétique avec gingembre et curcuma"
    },

    // REPAS 2 - Déjeuner (15 recettes)
    {
      id: 26,
      name: "Poulet Grillé aux Brocolis Classique",
      category: "repas2",
      categoryName: "Déjeuner",
      emoji: "🍗",
      time: "20 min",
      calories: 310,
      protein: 35,
      ingredients: ["180g blanc de poulet", "150g brocolis", "5g huile d'olive"],
      ustensils: ["Poêle", "cuit-vapeur"],
      description: "Le classique de votre programme déjeuner",
      has_chef_mode: true,
      difficulty_level: "intermediate",
      chef_tips: [
        {
          id: "tip26-1",
          type: "tip",
          title: "Cuisson parfaite du poulet",
          description: "La température interne doit atteindre 74°C pour une cuisson parfaite",
          importance: "high"
        },
        {
          id: "tip26-2",
          type: "warning",
          title: "Attention",
          description: "Ne pas retourner le poulet trop souvent pour garder les jus à l'intérieur",
          importance: "medium"
        }
      ]
    },
    {
      id: 27,
      name: "Dinde Sautée aux Épinards",
      category: "repas2",
      categoryName: "Déjeuner",
      emoji: "🦃",
      time: "15 min",
      calories: 295,
      protein: 34,
      ingredients: ["180g escalope de dinde", "150g épinards frais", "5g huile d'olive"],
      ustensils: ["Poêle", "passoire"],
      description: "Dinde tendre avec épinards riches en fer"
    },
    {
      id: 28,
      name: "Poulet aux Courgettes Grillées",
      category: "repas2",
      categoryName: "Déjeuner",
      emoji: "🍗",
      time: "25 min",
      calories: 308,
      protein: 35,
      ingredients: ["180g blanc de poulet", "150g courgettes", "5g huile d'olive", "herbes de Provence"],
      ustensils: ["Poêle", "plancha"],
      description: "Courgettes grillées pour une texture croquante"
    },
    {
      id: 29,
      name: "Dinde aux Haricots Verts",
      category: "repas2",
      categoryName: "Déjeuner",
      emoji: "🦃",
      time: "20 min",
      calories: 292,
      protein: 34,
      ingredients: ["180g escalope de dinde", "150g haricots verts", "5g huile d'olive", "ail"],
      ustensils: ["Poêle", "casserole"],
      description: "Haricots verts croquants à l'ail"
    },
    {
      id: 30,
      name: "Poulet Mariné aux Légumes Méditerranéens",
      category: "repas2",
      categoryName: "Déjeuner",
      emoji: "🍗",
      time: "30 min",
      calories: 315,
      protein: 35,
      ingredients: ["180g blanc de poulet", "75g courgettes", "75g aubergines", "5g huile d'olive"],
      ustensils: ["Poêle", "plat à gratin"],
      description: "Saveurs méditerranéennes avec courgettes et aubergines"
    },
    {
      id: 31,
      name: "Dinde au Curry et Brocolis",
      category: "repas2",
      categoryName: "Déjeuner",
      emoji: "🦃",
      time: "18 min",
      calories: 298,
      protein: 34,
      ingredients: ["180g escalope de dinde", "150g brocolis", "5g huile d'olive", "curry"],
      ustensils: ["Poêle", "cuit-vapeur"],
      description: "Épices du curry pour réchauffer les papilles"
    },
    {
      id: 32,
      name: "Poulet aux Champignons et Épinards",
      category: "repas2",
      categoryName: "Déjeuner",
      emoji: "🍗",
      time: "22 min",
      calories: 312,
      protein: 36,
      ingredients: ["180g blanc de poulet", "75g champignons", "75g épinards", "5g huile d'olive"],
      ustensils: ["Poêle", "couteau"],
      description: "Duo champignons-épinards pour plus de saveurs"
    },
    {
      id: 33,
      name: "Dinde Grillée aux Asperges",
      category: "repas2",
      categoryName: "Déjeuner",
      emoji: "🦃",
      time: "20 min",
      calories: 290,
      protein: 34,
      ingredients: ["180g escalope de dinde", "150g asperges vertes", "5g huile d'olive"],
      ustensils: ["Poêle", "cuit-vapeur"],
      description: "Finesse des asperges vertes de saison"
    },
    {
      id: 34,
      name: "Poulet Tandoori aux Légumes Verts",
      category: "repas2",
      categoryName: "Déjeuner",
      emoji: "🍗",
      time: "25 min",
      calories: 318,
      protein: 35,
      ingredients: ["180g blanc de poulet", "150g mélange légumes verts", "5g huile d'olive", "épices tandoori"],
      ustensils: ["Poêle", "bol"],
      description: "Voyage en Inde avec les épices tandoori"
    },
    {
      id: 35,
      name: "Dinde aux Poivrons Colorés",
      category: "repas2",
      categoryName: "Déjeuner",
      emoji: "🦃",
      time: "20 min",
      calories: 296,
      protein: 34,
      ingredients: ["180g escalope de dinde", "150g poivrons mélangés", "5g huile d'olive"],
      ustensils: ["Poêle", "couteau"],
      description: "Arc-en-ciel de poivrons pour les vitamines"
    },
    {
      id: 36,
      name: "Poulet à l'Estragon et Courgettes",
      category: "repas2",
      categoryName: "Déjeuner",
      emoji: "🍗",
      time: "22 min",
      calories: 308,
      protein: 35,
      ingredients: ["180g blanc de poulet", "150g courgettes", "5g huile d'olive", "estragon"],
      ustensils: ["Poêle", "ciseaux"],
      description: "Délicatesse de l'estragon avec courgettes fondantes"
    },
    {
      id: 37,
      name: "Dinde aux Brocolis et Ail",
      category: "repas2",
      categoryName: "Déjeuner",
      emoji: "🦃",
      time: "18 min",
      calories: 295,
      protein: 34,
      ingredients: ["180g escalope de dinde", "150g brocolis", "5g huile d'olive", "ail"],
      ustensils: ["Poêle", "presse-ail"],
      description: "Brocolis à l'ail pour plus de caractère"
    },
    {
      id: 38,
      name: "Poulet Paprika aux Épinards",
      category: "repas2",
      categoryName: "Déjeuner",
      emoji: "🍗",
      time: "20 min",
      calories: 310,
      protein: 35,
      ingredients: ["180g blanc de poulet", "150g épinards", "5g huile d'olive", "paprika fumé"],
      ustensils: ["Poêle", "passoire"],
      description: "Paprika fumé pour une saveur intense"
    },
    {
      id: 39,
      name: "Dinde aux Légumes Asiatiques",
      category: "repas2",
      categoryName: "Déjeuner",
      emoji: "🦃",
      time: "15 min",
      calories: 293,
      protein: 34,
      ingredients: ["180g escalope de dinde", "150g pak-choï", "5g huile d'olive", "gingembre"],
      ustensils: ["Wok", "râpe"],
      description: "Fraîcheur asiatique avec pak-choï et gingembre"
    },
    {
      id: 40,
      name: "Poulet aux Herbes de Provence",
      category: "repas2",
      categoryName: "Déjeuner",
      emoji: "🍗",
      time: "25 min",
      calories: 312,
      protein: 35,
      ingredients: ["180g blanc de poulet", "150g mélange légumes verts", "5g huile d'olive", "herbes de Provence"],
      ustensils: ["Poêle", "mortier"],
      description: "Parfums de Provence avec mélange d'herbes"
    },

    // COLLATION 2 - Blancs d'œufs aux oléagineux (10 recettes)
    {
      id: 41,
      name: "Blancs d'Œufs aux Amandes Classique",
      category: "collation2",
      categoryName: "Collation",
      emoji: "🥜",
      time: "8 min",
      calories: 301,
      protein: 25,
      ingredients: ["3 blancs d'œufs", "40g amandes", "50g fruits rouges"],
      ustensils: ["Poêle", "bol"],
      description: "La collation de référence de votre programme"
    },
    {
      id: 42,
      name: "Blancs d'Œufs aux Noix de Cajou et Myrtilles",
      category: "collation2",
      categoryName: "Collation",
      emoji: "🥜",
      time: "8 min",
      calories: 305,
      protein: 24,
      ingredients: ["3 blancs d'œufs", "40g noix de cajou", "50g myrtilles"],
      ustensils: ["Poêle", "bol"],
      description: "Antioxydants des myrtilles avec cajou croquant"
    },
    {
      id: 43,
      name: "Blancs d'Œufs aux Amandes et Framboises",
      category: "collation2",
      categoryName: "Collation",
      emoji: "🥜",
      time: "8 min",
      calories: 299,
      protein: 25,
      ingredients: ["3 blancs d'œufs", "40g amandes effilées", "50g framboises"],
      ustensils: ["Poêle", "bol"],
      description: "Acidité des framboises avec amandes effilées"
    },
    {
      id: 44,
      name: "Blancs d'Œufs aux Noix et Fraises",
      category: "collation2",
      categoryName: "Collation",
      emoji: "🥜",
      time: "8 min",
      calories: 308,
      protein: 24,
      ingredients: ["3 blancs d'œufs", "40g cerneaux de noix", "50g fraises"],
      ustensils: ["Poêle", "couteau"],
      description: "Oméga-3 des noix avec fraises sucrées"
    },
    {
      id: 45,
      name: "Blancs d'Œufs aux Amandes et Mûres",
      category: "collation2",
      categoryName: "Collation",
      emoji: "🥜",
      time: "8 min",
      calories: 301,
      protein: 25,
      ingredients: ["3 blancs d'œufs", "40g amandes", "50g mûres"],
      ustensils: ["Poêle", "bol"],
      description: "Saveur sauvage des mûres avec amandes"
    },
    {
      id: 46,
      name: "Blancs d'Œufs aux Noisettes et Fruits Rouges",
      category: "collation2",
      categoryName: "Collation",
      emoji: "🥜",
      time: "8 min",
      calories: 303,
      protein: 24,
      ingredients: ["3 blancs d'œufs", "40g noisettes", "50g mélange fruits rouges"],
      ustensils: ["Poêle", "bol"],
      description: "Croquant des noisettes avec fruits rouges"
    },
    {
      id: 47,
      name: "Blancs d'Œufs aux Amandes et Cassis",
      category: "collation2",
      categoryName: "Collation",
      emoji: "🥜",
      time: "8 min",
      calories: 298,
      protein: 25,
      ingredients: ["3 blancs d'œufs", "40g amandes", "50g cassis"],
      ustensils: ["Poêle", "bol"],
      description: "Intensité du cassis avec amandes douces"
    },
    {
      id: 48,
      name: "Blancs d'Œufs aux Pistaches et Fraises",
      category: "collation2",
      categoryName: "Collation",
      emoji: "🥜",
      time: "8 min",
      calories: 306,
      protein: 25,
      ingredients: ["3 blancs d'œufs", "40g pistaches", "50g fraises"],
      ustensils: ["Poêle", "couteau"],
      description: "Raffinement des pistaches avec fraises"
    },
    {
      id: 49,
      name: "Blancs d'Œufs aux Amandes et Groseilles",
      category: "collation2",
      categoryName: "Collation",
      emoji: "🥜",
      time: "8 min",
      calories: 300,
      protein: 25,
      ingredients: ["3 blancs d'œufs", "40g amandes", "50g groseilles"],
      ustensils: ["Poêle", "bol"],
      description: "Acidité piquante des groseilles"
    },
    {
      id: 50,
      name: "Blancs d'Œufs aux Noix de Pécan et Fruits Rouges",
      category: "collation2",
      categoryName: "Collation",
      emoji: "🥜",
      time: "8 min",
      calories: 309,
      protein: 24,
      ingredients: ["3 blancs d'œufs", "40g noix de pécan", "50g fruits rouges"],
      ustensils: ["Poêle", "bol"],
      description: "Douceur des noix de pécan américaines"
    },

    // REPAS 3 - Dîner poisson (15 recettes)
    {
      id: 51,
      name: "Cabillaud en Papillote Classique",
      category: "repas3",
      categoryName: "Dîner",
      emoji: "🐟",
      time: "25 min",
      calories: 270,
      protein: 38,
      ingredients: ["200g filet de cabillaud", "salade verte", "5g huile d'olive", "citron"],
      ustensils: ["Four", "papier sulfurisé"],
      description: "Le classique de votre programme dîner",
      has_chef_mode: true,
      difficulty_level: "advanced",
      chef_tips: [
        {
          id: "tip51-1",
          type: "secret",
          title: "Technique de papillote",
          description: "Préchauffez le four à 200°C et fermez hermétiquement la papillote pour créer un effet vapeur",
          importance: "high"
        },
        {
          id: "tip51-2",
          type: "tip",
          title: "Test de cuisson",
          description: "Le poisson est cuit quand sa chair se défait facilement à la fourchette",
          importance: "medium"
        }
      ]
    },
    {
      id: 52,
      name: "Sole Grillée à la Salade Verte",
      category: "repas3",
      categoryName: "Dîner",
      emoji: "🐟",
      time: "15 min",
      calories: 250,
      protein: 36,
      ingredients: ["200g filet de sole", "salade mélangée", "5g huile d'olive", "herbes"],
      ustensils: ["Poêle", "saladier"],
      description: "Finesse de la sole avec salade fraîche"
    },
    {
      id: 53,
      name: "Cabillaud aux Épinards",
      category: "repas3",
      categoryName: "Dîner",
      emoji: "🐟",
      time: "20 min",
      calories: 275,
      protein: 39,
      ingredients: ["200g filet de cabillaud", "100g épinards", "5g huile d'olive", "ail"],
      ustensils: ["Poêle", "passoire"],
      description: "Fer des épinards avec cabillaud fondant"
    },
    {
      id: 54,
      name: "Sole aux Courgettes Vapeur",
      category: "repas3",
      categoryName: "Dîner",
      emoji: "🐟",
      time: "18 min",
      calories: 255,
      protein: 36,
      ingredients: ["200g filet de sole", "100g courgettes", "5g huile d'olive", "aneth"],
      ustensils: ["Cuit-vapeur", "poêle"],
      description: "Légèreté des courgettes vapeur à l'aneth"
    },
    {
      id: 55,
      name: "Cabillaud au Four aux Tomates Cerises",
      category: "repas3",
      categoryName: "Dîner",
      emoji: "🐟",
      time: "30 min",
      calories: 278,
      protein: 38,
      ingredients: ["200g filet de cabillaud", "100g tomates cerises", "5g huile d'olive", "basilic"],
      ustensils: ["Four", "plat à gratin"],
      description: "Tomates cerises confites au four avec basilic"
    },
    {
      id: 56,
      name: "Sole aux Haricots Verts",
      category: "repas3",
      categoryName: "Dîner",
      emoji: "🐟",
      time: "20 min",
      calories: 252,
      protein: 36,
      ingredients: ["200g filet de sole", "100g haricots verts", "5g huile d'olive", "persil"],
      ustensils: ["Poêle", "casserole"],
      description: "Croquant des haricots verts au persil"
    },
    {
      id: 57,
      name: "Cabillaud Mariné aux Légumes Grillés",
      category: "repas3",
      categoryName: "Dîner",
      emoji: "🐟",
      time: "35 min",
      calories: 280,
      protein: 38,
      ingredients: ["200g filet de cabillaud", "100g légumes grillés", "5g huile d'olive", "thym"],
      ustensils: ["Four", "plancha"],
      description: "Légumes grillés parfumés au thym"
    },
    {
      id: 58,
      name: "Sole à la Provençale",
      category: "repas3",
      categoryName: "Dîner",
      emoji: "🐟",
      time: "25 min",
      calories: 258,
      protein: 36,
      ingredients: ["200g filet de sole", "100g ratatouille", "5g huile d'olive", "herbes de Provence"],
      ustensils: ["Poêle", "casserole"],
      description: "Ratatouille provençale avec herbes du soleil"
    },
    {
      id: 59,
      name: "Cabillaud aux Brocolis Vapeur",
      category: "repas3",
      categoryName: "Dîner",
      emoji: "🐟",
      time: "22 min",
      calories: 272,
      protein: 39,
      ingredients: ["200g filet de cabillaud", "100g brocolis", "5g huile d'olive", "citron"],
      ustensils: ["Cuit-vapeur", "poêle"],
      description: "Brocolis vapeur avec zeste de citron"
    },
    {
      id: 60,
      name: "Sole aux Champignons",
      category: "repas3",
      categoryName: "Dîner",
      emoji: "🐟",
      time: "18 min",
      calories: 254,
      protein: 37,
      ingredients: ["200g filet de sole", "100g champignons", "5g huile d'olive", "persil"],
      ustensils: ["Poêle", "couteau"],
      description: "Umami des champignons avec persil frais"
    },
    {
      id: 61,
      name: "Cabillaud à l'Asiatique",
      category: "repas3",
      categoryName: "Dîner",
      emoji: "🐟",
      time: "20 min",
      calories: 276,
      protein: 38,
      ingredients: ["200g filet de cabillaud", "100g pak-choï", "5g huile d'olive", "gingembre, soja"],
      ustensils: ["Wok", "râpe"],
      description: "Voyage asiatique avec pak-choï et gingembre"
    },
    {
      id: 62,
      name: "Sole aux Épinards et Ail",
      category: "repas3",
      categoryName: "Dîner",
      emoji: "🐟",
      time: "15 min",
      calories: 253,
      protein: 36,
      ingredients: ["200g filet de sole", "100g épinards", "5g huile d'olive", "ail"],
      ustensils: ["Poêle", "presse-ail"],
      description: "Épinards à l'ail avec sole délicate"
    },
    {
      id: 63,
      name: "Cabillaud aux Poivrons",
      category: "repas3",
      categoryName: "Dîner",
      emoji: "🐟",
      time: "25 min",
      calories: 274,
      protein: 38,
      ingredients: ["200g filet de cabillaud", "100g poivrons colorés", "5g huile d'olive", "paprika"],
      ustensils: ["Poêle", "couteau"],
      description: "Poivrons colorés au paprika doux"
    },
    {
      id: 64,
      name: "Sole en Croûte d'Herbes",
      category: "repas3",
      categoryName: "Dîner",
      emoji: "🐟",
      time: "20 min",
      calories: 251,
      protein: 36,
      ingredients: ["200g filet de sole", "salade verte", "5g huile d'olive", "herbes fraîches"],
      ustensils: ["Four", "ciseaux"],
      description: "Croûte d'herbes fraîches pour plus de saveur"
    },
    {
      id: 65,
      name: "Cabillaud aux Légumes Méditerranéens",
      category: "repas3",
      categoryName: "Dîner",
      emoji: "🐟",
      time: "30 min",
      calories: 279,
      protein: 38,
      ingredients: ["200g filet de cabillaud", "100g mélange méditerranéen", "5g huile d'olive", "origan"],
      ustensils: ["Four", "plat à gratin"],
      description: "Mélange méditerranéen à l'origan"
    }
  ]

  const categories = [
    { id: 'all', name: 'Toutes les recettes', count: recipes.length },
    { id: 'repas1', name: 'Petit-déjeuner', count: recipes.filter(r => r.category === 'repas1').length },
    { id: 'collation1', name: 'Smoothies', count: recipes.filter(r => r.category === 'collation1').length },
    { id: 'repas2', name: 'Déjeuner', count: recipes.filter(r => r.category === 'repas2').length },
    { id: 'collation2', name: 'Collations', count: recipes.filter(r => r.category === 'collation2').length },
    { id: 'repas3', name: 'Dîner', count: recipes.filter(r => r.category === 'repas3').length }
  ]

  const difficultyLevels = [
    { id: 'all', name: 'Tous niveaux' },
    { id: 'beginner', name: 'Débutant' },
    { id: 'intermediate', name: 'Intermédiaire' },
    { id: 'advanced', name: 'Avancé' }
  ]

  const filteredRecipes = recipes.filter(recipe => {
    const matchesSearch = recipe.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         recipe.ingredients.some(ing => ing.toLowerCase().includes(searchTerm.toLowerCase()))
    const matchesCategory = selectedCategory === 'all' || recipe.category === selectedCategory
    const matchesDifficulty = selectedDifficulty === 'all' || recipe.difficulty_level === selectedDifficulty
    const matchesChefMode = !showChefModeOnly || recipe.has_chef_mode === true
    
    return matchesSearch && matchesCategory && matchesDifficulty && matchesChefMode
  })

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          🍽️ Bibliothèque de Recettes
        </h1>
        <p className="text-gray-600">
          {recipes.length} recettes adaptées à votre programme alimentaire
        </p>
      </div>

      {/* Filtres */}
      <div className="mb-6 space-y-4">
        {/* Recherche */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
          <input
            type="text"
            placeholder="Rechercher une recette ou un ingrédient..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        {/* Catégories */}
        <div className="flex flex-wrap gap-2">
          {categories.map((category) => (
            <button
              key={category.id}
              onClick={() => setSelectedCategory(category.id)}
              className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
                selectedCategory === category.id
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {category.name} ({category.count})
            </button>
          ))}
        </div>

        {/* Filtres supplémentaires */}
        <div className="flex flex-wrap items-center gap-4">
          {/* Filtre par difficulté */}
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium text-gray-700">Difficulté:</span>
            {difficultyLevels.map((level) => (
              <button
                key={level.id}
                onClick={() => setSelectedDifficulty(level.id)}
                className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
                  selectedDifficulty === level.id
                    ? 'bg-orange-500 text-white'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                {level.name}
              </button>
            ))}
          </div>

          {/* Filtre Mode Chef uniquement */}
          <button
            onClick={() => setShowChefModeOnly(!showChefModeOnly)}
            className={`flex items-center px-3 py-1 rounded-full text-xs font-medium transition-colors ${
              showChefModeOnly
                ? 'bg-gradient-to-r from-orange-500 to-red-500 text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            <ChefHat className="w-3 h-3 mr-1" />
            Mode Chef uniquement
          </button>
        </div>
      </div>

      {/* Résultats */}
      <div className="mb-4">
        <p className="text-gray-600">
          {filteredRecipes.length} recette{filteredRecipes.length > 1 ? 's' : ''} trouvée{filteredRecipes.length > 1 ? 's' : ''}
        </p>
      </div>

      {/* Grille de recettes */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredRecipes.map((recipe) => (
          <Card key={recipe.id} className="hover:shadow-lg transition-shadow">
            <CardHeader className="pb-3">
              <div className="flex items-start justify-between">
                <div className="flex items-center space-x-2">
                  <span className="text-2xl">{recipe.emoji}</span>
                  <div>
                    <CardTitle className="text-lg leading-tight">{recipe.name}</CardTitle>
                    <p className="text-sm text-gray-500">{recipe.categoryName}</p>
                  </div>
                </div>
              </div>
            </CardHeader>
            
            <CardContent className="space-y-4">
              <p className="text-sm text-gray-600">{recipe.description}</p>
              
              {/* Mode Chef Badge */}
              <ChefModeBadge recipe={recipe} />
              
              {/* Infos nutritionnelles */}
              <div className="flex justify-between text-sm">
                <div className="flex items-center space-x-1">
                  <Clock className="w-4 h-4 text-gray-400" />
                  <span>{recipe.time}</span>
                </div>
                <div className="text-right">
                  <div className="font-medium">{recipe.calories} kcal</div>
                  <div className="text-gray-500">{recipe.protein}g protéines</div>
                </div>
              </div>

              {/* Ingrédients */}
              <div>
                <h4 className="font-medium text-sm mb-2">Ingrédients :</h4>
                <ul className="text-xs text-gray-600 space-y-1">
                  {recipe.ingredients.map((ingredient, index) => (
                    <li key={index}>• {ingredient}</li>
                  ))}
                </ul>
              </div>

              {/* Ustensiles */}
              <div>
                <h4 className="font-medium text-sm mb-2">Ustensiles :</h4>
                <div className="flex flex-wrap gap-1">
                  {recipe.ustensils.map((ustensil, index) => (
                    <span key={index} className="text-xs bg-gray-100 px-2 py-1 rounded">
                      {ustensil}
                    </span>
                  ))}
                </div>
              </div>

              {/* Aperçu conseils du chef */}
              <ChefTipsPreview recipe={recipe} />

              {/* Actions */}
              <div className="flex flex-col space-y-2 pt-2">
                <CookingGuideButton recipe={recipe} />
                <Button size="sm" variant="outline" className="flex-1">
                  <ChefHat className="w-4 h-4 mr-1" />
                  Ajouter au planning
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {filteredRecipes.length === 0 && (
        <div className="text-center py-12">
          <div className="text-gray-400 mb-4">
            <Search className="w-12 h-12 mx-auto" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">Aucune recette trouvée</h3>
          <p className="text-gray-500">
            Essayez de modifier vos critères de recherche ou de filtrage.
          </p>
        </div>
      )}
    </div>
  )
}

