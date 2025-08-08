/**
 * Modal d'ajout rapide de repas/collations (US1.8)
 * Permet d'ajouter rapidement un repas hors plan ou une collation
 */

import React, { useState, useEffect } from 'react'
import { apiRequest } from '../src/config/api'
import { Card, CardContent, CardHeader, CardTitle } from './ui/card'
import { Button } from './ui/button'
import { Badge } from './ui/badge'
import { 
  X, 
  Search, 
  Plus, 
  Utensils,
  Clock,
  Calculator,
  Star
} from 'lucide-react'

const QuickAddModal = ({ 
  isOpen, 
  onClose, 
  mealType = null, 
  selectedDate, 
  onMealAdded 
}) => {
  const { userId, markMealConsumed } = useMealTracking()
  
  const [step, setStep] = useState('search') // search, custom, nutrition, confirm
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState([])
  const [isSearching, setIsSearching] = useState(false)
  const [selectedRecipe, setSelectedRecipe] = useState(null)
  
  // Données pour repas personnalisé
  const [customMeal, setCustomMeal] = useState({
    name: '',
    calories: '',
    protein: '',
    carbs: '',
    fat: '',
    fiber: '',
    portion: 1
  })
  
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  
  // Labels des types de repas
  const mealTypeLabels = {
    repas1: 'Petit-déjeuner',
    repas2: 'Déjeuner',
    repas3: 'Dîner',
    collation: 'Collation'
  }
  
  // Reset lors de l'ouverture/fermeture
  useEffect(() => {
    if (isOpen) {
      setStep('search')
      setSearchQuery('')
      setSearchResults([])
      setSelectedRecipe(null)
      setCustomMeal({
        name: '',
        calories: '',
        protein: '',
        carbs: '',
        fat: '',
        fiber: '',
        portion: 1
      })
      setError('')
    }
  }, [isOpen])
  
  // Recherche de recettes
  const searchRecipes = async (query) => {
    if (!query.trim()) {
      setSearchResults([])
      return
    }
    
    setIsSearching(true)
    try {
      const response = await apiRequest(`recipes?search=${encodeURIComponent(query)}&per_page=10`)
      setSearchResults(response.recipes || [])
    } catch (error) {
      console.error('Erreur de recherche:', error)
      setSearchResults([])
    } finally {
      setIsSearching(false)
    }
  }
  
  // Effet de recherche avec debounce
  useEffect(() => {
    const timer = setTimeout(() => {
      if (searchQuery) {
        searchRecipes(searchQuery)
      }
    }, 300)
    
    return () => clearTimeout(timer)
  }, [searchQuery])
  
  // Sélectionner une recette
  const handleSelectRecipe = (recipe) => {
    setSelectedRecipe(recipe)
    setStep('confirm')
  }
  
  // Créer un repas personnalisé
  const handleCustomMeal = () => {
    setStep('custom')
  }
  
  // Valider et ajouter le repas
  const handleConfirmAdd = async () => {
    setIsLoading(true)
    setError('')
    
    try {
      // Créer un tracking entry temporaire
      const mealData = selectedRecipe ? {
        meal_name: selectedRecipe.name,
        recipe_id: selectedRecipe.id,
        planned_calories: selectedRecipe.total_calories || 0,
        planned_protein: selectedRecipe.total_protein || 0,
        planned_carbs: selectedRecipe.total_carbs || 0,
        planned_fat: selectedRecipe.total_fat || 0
      } : {
        meal_name: customMeal.name,
        planned_calories: parseFloat(customMeal.calories) || 0,
        planned_protein: parseFloat(customMeal.protein) || 0,
        planned_carbs: parseFloat(customMeal.carbs) || 0,
        planned_fat: parseFloat(customMeal.fat) || 0
      }
      
      // Créer le tracking entry via l'API
      const trackingData = {
        user_id: userId,
        meal_date: selectedDate,
        meal_type: mealType,
        ...mealData,
        status: 'planned'
      }
      
      // Appel API pour créer le tracking
      const response = await apiRequest('meal-tracking', {
        method: 'POST',
        body: JSON.stringify(trackingData)
      })
      
      if (response.success) {
        // Ne pas demander de confirmation immédiate
        // L'utilisateur pourra marquer comme consommé depuis l'interface principale
        onMealAdded?.()
        onClose()
      }
      
    } catch (error) {
      setError(`Erreur lors de l'ajout: ${error.message}`)
    } finally {
      setIsLoading(false)
    }
  }
  
  // Validation du repas personnalisé
  const isCustomMealValid = () => {
    return customMeal.name.trim() && 
           (customMeal.calories || customMeal.protein || customMeal.carbs || customMeal.fat)
  }
  
  if (!isOpen) return null
  
  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4 animate-in fade-in duration-300">
      <div className="bg-white rounded-xl shadow-2xl max-w-md w-full max-h-[90vh] overflow-hidden animate-in zoom-in-95 duration-300">
        {/* Header - Enhanced */}
        <div className="flex items-center justify-between p-4 sm:p-6 border-b border-gray-200 bg-gradient-to-r from-blue-50 to-purple-50">
          <div>
            <h2 className="text-lg sm:text-xl font-bold flex items-center gap-3 text-gray-800">
              <div className="p-2 bg-blue-100 rounded-full">
                <Plus className="h-5 w-5 text-blue-600" />
              </div>
              <span>Ajouter {mealType && mealTypeLabels[mealType]}</span>
            </h2>
            <p className="text-sm text-gray-600 mt-1">
              Recherchez une recette ou créez un repas personnalisé
            </p>
          </div>
          <Button 
            variant="ghost" 
            size="sm" 
            onClick={onClose}
            className="hover:bg-white/50 transition-colors duration-200"
            aria-label="Fermer la modal"
          >
            <X className="h-5 w-5" />
          </Button>
        </div>
        
        <div className="p-4 max-h-[calc(90vh-80px)] overflow-y-auto">
          {error && (
            <div className="bg-red-50 text-red-700 p-3 rounded mb-4 text-sm">
              {error}
            </div>
          )}
          
          {/* Étape: Recherche */}
          {step === 'search' && (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">
                  Rechercher une recette
                </label>
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Ex: salade, poulet, pasta..."
                    className="w-full pl-10 pr-4 py-3 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 text-sm"
                    autoFocus
                  />
                </div>
              </div>
              
              {/* Résultats de recherche */}
              {isSearching ? (
                <div className="text-center py-4 text-gray-500">
                  Recherche en cours...
                </div>
              ) : searchResults.length > 0 ? (
                <div className="space-y-2 max-h-60 overflow-y-auto">
                  {searchResults.map((recipe) => (
                    <Card
                      key={recipe.id}
                      className="cursor-pointer hover:shadow-md transition-shadow"
                      onClick={() => handleSelectRecipe(recipe)}
                    >
                      <CardContent className="p-3">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <h3 className="font-medium">{recipe.name}</h3>
                            <div className="flex items-center gap-2 mt-1 text-sm text-gray-500">
                              <span>{Math.round(recipe.total_calories || 0)} kcal</span>
                              {recipe.total_protein && (
                                <span>• {Math.round(recipe.total_protein)}g protéines</span>
                              )}
                            </div>
                            {recipe.category && (
                              <Badge variant="outline" className="mt-2 text-xs">
                                {recipe.category}
                              </Badge>
                            )}
                          </div>
                          <Utensils className="h-4 w-4 text-gray-400" />
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              ) : searchQuery && !isSearching ? (
                <div className="text-center py-4 text-gray-500">
                  Aucune recette trouvée
                </div>
              ) : null}
              
              {/* Option repas personnalisé */}
              <div className="pt-4 border-t">
                <Button
                  variant="outline"
                  onClick={handleCustomMeal}
                  className="w-full flex items-center gap-2"
                >
                  <Calculator className="h-4 w-4" />
                  Créer un repas personnalisé
                </Button>
              </div>
            </div>
          )}
          
          {/* Étape: Repas personnalisé */}
          {step === 'custom' && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="font-medium">Repas personnalisé</h3>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setStep('search')}
                >
                  Retour
                </Button>
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-1">
                  Nom du repas *
                </label>
                <input
                  type="text"
                  value={customMeal.name}
                  onChange={(e) => setCustomMeal(prev => ({ ...prev, name: e.target.value }))}
                  placeholder="Ex: Salade maison"
                  className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
              
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-sm font-medium mb-1">
                    Calories
                  </label>
                  <input
                    type="number"
                    min="0"
                    value={customMeal.calories}
                    onChange={(e) => setCustomMeal(prev => ({ ...prev, calories: e.target.value }))}
                    placeholder="kcal"
                    className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium mb-1">
                    Protéines
                  </label>
                  <input
                    type="number"
                    min="0"
                    step="0.1"
                    value={customMeal.protein}
                    onChange={(e) => setCustomMeal(prev => ({ ...prev, protein: e.target.value }))}
                    placeholder="g"
                    className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium mb-1">
                    Glucides
                  </label>
                  <input
                    type="number"
                    min="0"
                    step="0.1"
                    value={customMeal.carbs}
                    onChange={(e) => setCustomMeal(prev => ({ ...prev, carbs: e.target.value }))}
                    placeholder="g"
                    className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium mb-1">
                    Lipides
                  </label>
                  <input
                    type="number"
                    min="0"
                    step="0.1"
                    value={customMeal.fat}
                    onChange={(e) => setCustomMeal(prev => ({ ...prev, fat: e.target.value }))}
                    placeholder="g"
                    className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>
              
              <div className="flex gap-2">
                <Button
                  onClick={() => setStep('confirm')}
                  disabled={!isCustomMealValid()}
                  className="flex-1"
                >
                  Continuer
                </Button>
                <Button
                  variant="outline"
                  onClick={() => setStep('search')}
                >
                  Annuler
                </Button>
              </div>
            </div>
          )}
          
          {/* Étape: Confirmation */}
          {step === 'confirm' && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="font-medium">Confirmation</h3>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setStep(selectedRecipe ? 'search' : 'custom')}
                >
                  Modifier
                </Button>
              </div>
              
              <Card className="bg-blue-50">
                <CardContent className="p-4">
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <h4 className="font-medium">
                        {selectedRecipe ? selectedRecipe.name : customMeal.name}
                      </h4>
                      <div className="text-sm text-gray-600 flex items-center gap-1 mt-1">
                        <Clock className="h-3 w-3" />
                        {mealTypeLabels[mealType]} - {new Date(selectedDate).toLocaleDateString('fr-FR')}
                      </div>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-3 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Calories:</span>
                      <span className="font-medium">
                        {Math.round(selectedRecipe?.total_calories || parseFloat(customMeal.calories) || 0)} kcal
                      </span>
                    </div>
                    
                    <div className="flex justify-between">
                      <span className="text-gray-600">Protéines:</span>
                      <span className="font-medium">
                        {Math.round(selectedRecipe?.total_protein || parseFloat(customMeal.protein) || 0)}g
                      </span>
                    </div>
                    
                    <div className="flex justify-between">
                      <span className="text-gray-600">Glucides:</span>
                      <span className="font-medium">
                        {Math.round(selectedRecipe?.total_carbs || parseFloat(customMeal.carbs) || 0)}g
                      </span>
                    </div>
                    
                    <div className="flex justify-between">
                      <span className="text-gray-600">Lipides:</span>
                      <span className="font-medium">
                        {Math.round(selectedRecipe?.total_fat || parseFloat(customMeal.fat) || 0)}g
                      </span>
                    </div>
                  </div>
                  
                  {selectedRecipe?.category && (
                    <div className="mt-3">
                      <Badge variant="outline">
                        {selectedRecipe.category}
                      </Badge>
                    </div>
                  )}
                </CardContent>
              </Card>
              
              <div className="flex gap-2">
                <Button
                  onClick={handleConfirmAdd}
                  disabled={isLoading}
                  className="flex-1 flex items-center gap-2"
                >
                  {isLoading ? (
                    <>Ajout en cours...</>
                  ) : (
                    <>
                      <Plus className="h-4 w-4" />
                      Ajouter ce repas
                    </>
                  )}
                </Button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default QuickAddModal