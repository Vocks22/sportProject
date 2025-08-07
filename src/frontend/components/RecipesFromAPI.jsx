import { useState, useEffect } from 'react'
import { Search, Clock, Users, ChefHat, Filter, Star, AlertCircle, Loader2 } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { CookingGuideButton, ChefModeBadge, ChefTipsPreview } from './CookingGuideButton'

export function Recipes() {
  const [recipes, setRecipes] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('all')
  const [selectedDifficulty, setSelectedDifficulty] = useState('all')
  const [showChefModeOnly, setShowChefModeOnly] = useState(false)

  // Charger les recettes depuis l'API
  useEffect(() => {
    fetchRecipes()
  }, [])

  const fetchRecipes = async () => {
    try {
      setLoading(true)
      setError(null)
      
      const response = await fetch('/api/recipes')
      if (!response.ok) {
        throw new Error('Erreur lors du chargement des recettes')
      }
      
      const data = await response.json()
      
      // Transformer les données pour correspondre au format attendu
      const transformedRecipes = data.recipes.map(recipe => ({
        ...recipe,
        emoji: getCategoryEmoji(recipe.category),
        categoryName: getCategoryName(recipe.category),
        time: `${recipe.prep_time + recipe.cook_time} min`,
        calories: recipe.total_calories,
        protein: recipe.total_protein,
        ustensils: recipe.utensils || []
      }))
      
      setRecipes(transformedRecipes)
    } catch (err) {
      console.error('Erreur:', err)
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  // Fonctions utilitaires pour mapper les catégories
  const getCategoryEmoji = (category) => {
    const emojis = {
      'breakfast': '🍳',
      'meal1': '🍳',
      'snack': '🥤',
      'snack1': '🥤',
      'lunch': '🍗',
      'meal2': '🍗',
      'snack2': '🥜',
      'dinner': '🐟',
      'meal3': '🐟'
    }
    return emojis[category] || '🍽️'
  }

  const getCategoryName = (category) => {
    const names = {
      'breakfast': 'Petit-déjeuner',
      'meal1': 'Petit-déjeuner',
      'snack': 'Smoothie',
      'snack1': 'Smoothie',
      'lunch': 'Déjeuner',
      'meal2': 'Déjeuner',
      'snack2': 'Collation',
      'dinner': 'Dîner',
      'meal3': 'Dîner'
    }
    return names[category] || category
  }

  // Catégories dynamiques basées sur les recettes chargées
  const categories = [
    { id: 'all', name: 'Toutes les recettes', count: recipes.length },
    { id: 'breakfast', name: 'Petit-déjeuner', count: recipes.filter(r => r.category === 'breakfast' || r.category === 'meal1').length },
    { id: 'snack', name: 'Smoothies', count: recipes.filter(r => r.category === 'snack' || r.category === 'snack1').length },
    { id: 'lunch', name: 'Déjeuner', count: recipes.filter(r => r.category === 'lunch' || r.category === 'meal2').length },
    { id: 'snack2', name: 'Collations', count: recipes.filter(r => r.category === 'snack2').length },
    { id: 'dinner', name: 'Dîner', count: recipes.filter(r => r.category === 'dinner' || r.category === 'meal3').length }
  ].filter(cat => cat.count > 0 || cat.id === 'all')

  const difficultyLevels = [
    { id: 'all', name: 'Tous niveaux' },
    { id: 'beginner', name: 'Débutant' },
    { id: 'intermediate', name: 'Intermédiaire' },
    { id: 'advanced', name: 'Avancé' }
  ]

  // Filtrage des recettes
  const filteredRecipes = recipes.filter(recipe => {
    const matchesSearch = recipe.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         (recipe.ingredients && recipe.ingredients.some(ing => 
                           (typeof ing === 'string' ? ing : ing.name || '').toLowerCase().includes(searchTerm.toLowerCase())
                         ))
    
    const matchesCategory = selectedCategory === 'all' || 
                           recipe.category === selectedCategory ||
                           (selectedCategory === 'breakfast' && (recipe.category === 'breakfast' || recipe.category === 'meal1')) ||
                           (selectedCategory === 'snack' && (recipe.category === 'snack' || recipe.category === 'snack1')) ||
                           (selectedCategory === 'lunch' && (recipe.category === 'lunch' || recipe.category === 'meal2')) ||
                           (selectedCategory === 'dinner' && (recipe.category === 'dinner' || recipe.category === 'meal3'))
    
    const matchesDifficulty = selectedDifficulty === 'all' || recipe.difficulty_level === selectedDifficulty
    const matchesChefMode = !showChefModeOnly || recipe.has_chef_mode === true
    
    return matchesSearch && matchesCategory && matchesDifficulty && matchesChefMode
  })

  // Affichage du loader
  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <Loader2 className="w-8 h-8 animate-spin text-blue-500 mx-auto mb-4" />
          <p className="text-gray-600">Chargement des recettes...</p>
        </div>
      </div>
    )
  }

  // Affichage de l'erreur
  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <AlertCircle className="w-8 h-8 text-red-500 mx-auto mb-4" />
          <p className="text-red-600 mb-4">{error}</p>
          <Button onClick={fetchRecipes} variant="outline">
            Réessayer
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header avec recherche et filtres */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h1 className="text-2xl font-bold mb-6">Bibliothèque de Recettes</h1>
        
        {/* Barre de recherche */}
        <div className="relative mb-4">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
          <input
            type="text"
            placeholder="Rechercher une recette ou un ingrédient..."
            className="w-full pl-10 pr-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>

        {/* Filtres */}
        <div className="flex flex-wrap gap-4">
          {/* Filtre par catégorie */}
          <div className="flex-1 min-w-[200px]">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Catégorie
            </label>
            <select
              className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
            >
              {categories.map(cat => (
                <option key={cat.id} value={cat.id}>
                  {cat.name} ({cat.count})
                </option>
              ))}
            </select>
          </div>

          {/* Filtre par difficulté */}
          <div className="flex-1 min-w-[200px]">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Difficulté
            </label>
            <select
              className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              value={selectedDifficulty}
              onChange={(e) => setSelectedDifficulty(e.target.value)}
            >
              {difficultyLevels.map(level => (
                <option key={level.id} value={level.id}>
                  {level.name}
                </option>
              ))}
            </select>
          </div>

          {/* Toggle Mode Chef */}
          <div className="flex items-end">
            <Button
              variant={showChefModeOnly ? "default" : "outline"}
              onClick={() => setShowChefModeOnly(!showChefModeOnly)}
              className="flex items-center gap-2"
            >
              <ChefHat className="w-4 h-4" />
              Mode Chef uniquement
            </Button>
          </div>
        </div>
      </div>

      {/* Statistiques */}
      <div className="grid grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="text-2xl font-bold">{filteredRecipes.length}</div>
            <div className="text-sm text-gray-600">Recettes trouvées</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="text-2xl font-bold">
              {filteredRecipes.filter(r => r.has_chef_mode).length}
            </div>
            <div className="text-sm text-gray-600">Avec Mode Chef</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="text-2xl font-bold">
              {Math.round(filteredRecipes.reduce((acc, r) => acc + (r.calories || 0), 0) / Math.max(filteredRecipes.length, 1))}
            </div>
            <div className="text-sm text-gray-600">Calories moyennes</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="text-2xl font-bold">
              {Math.round(filteredRecipes.reduce((acc, r) => acc + (r.protein || 0), 0) / Math.max(filteredRecipes.length, 1))}g
            </div>
            <div className="text-sm text-gray-600">Protéines moyennes</div>
          </CardContent>
        </Card>
      </div>

      {/* Grille de recettes */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {filteredRecipes.map(recipe => (
          <Card key={recipe.id} className="hover:shadow-lg transition-shadow">
            <CardHeader className="pb-3">
              <div className="flex justify-between items-start mb-2">
                <span className="text-3xl">{recipe.emoji}</span>
                {recipe.is_favorite && (
                  <Star className="w-5 h-5 text-yellow-500 fill-current" />
                )}
              </div>
              <CardTitle className="text-lg">{recipe.name}</CardTitle>
              <div className="flex items-center gap-2 mt-2">
                <span className="text-xs bg-gray-100 px-2 py-1 rounded">
                  {recipe.categoryName}
                </span>
                {recipe.has_chef_mode && (
                  <ChefModeBadge recipe={recipe} />
                )}
              </div>
            </CardHeader>
            <CardContent className="space-y-3">
              <p className="text-sm text-gray-600">
                {recipe.description || 'Recette délicieuse et nutritive'}
              </p>
              
              <div className="flex items-center justify-between text-sm">
                <div className="flex items-center gap-1">
                  <Clock className="w-4 h-4 text-gray-400" />
                  <span>{recipe.time}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="font-medium">{recipe.calories} kcal</span>
                  <span className="text-blue-600 font-medium">{recipe.protein}g</span>
                </div>
              </div>

              {recipe.chef_tips && recipe.chef_tips.length > 0 && (
                <ChefTipsPreview recipe={recipe} />
              )}

              {recipe.has_chef_mode && (
                <CookingGuideButton recipe={recipe} />
              )}
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Message si aucune recette trouvée */}
      {filteredRecipes.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-500">Aucune recette ne correspond à vos critères de recherche.</p>
        </div>
      )}
    </div>
  )
}