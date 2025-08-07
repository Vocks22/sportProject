import React from 'react'
import { useState, useEffect } from 'react'
import { ChefHat, Clock, Users, Star, X } from 'lucide-react'
import { Button } from './ui/button'
import { CookingGuide } from './CookingGuide'

const DIFFICULTY_COLORS = {
  beginner: 'text-green-600',
  intermediate: 'text-yellow-600',
  advanced: 'text-red-600'
}

const DIFFICULTY_LABELS = {
  beginner: 'Débutant',
  intermediate: 'Intermédiaire', 
  advanced: 'Avancé'
}

export function CookingGuideButton({ recipe }) {
  const [showCookingGuide, setShowCookingGuide] = useState(false)
  
  // Empêcher le scroll du body quand la modale est ouverte
  useEffect(() => {
    if (showCookingGuide) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = 'unset'
    }
    
    return () => {
      document.body.style.overflow = 'unset'
    }
  }, [showCookingGuide])

  if (!recipe.has_chef_mode) {
    return null
  }

  return (
    <>
      <Button 
        onClick={() => setShowCookingGuide(true)}
        className="w-full bg-gradient-to-r from-orange-500 to-red-500 hover:from-orange-600 hover:to-red-600 text-white"
      >
        <ChefHat className="w-4 h-4 mr-2" />
        Mode Chef
        {recipe.difficulty_level && (
          <span className={`ml-2 text-xs ${DIFFICULTY_COLORS[recipe.difficulty_level]}`}>
            ({DIFFICULTY_LABELS[recipe.difficulty_level]})
          </span>
        )}
      </Button>

      {/* Modale plein écran pour le Mode Chef avec overlay et animation */}
      {showCookingGuide && (
        <>
          {/* Overlay sombre */}
          <div 
            className="fixed inset-0 z-40 bg-black bg-opacity-50 transition-opacity duration-300"
            onClick={() => setShowCookingGuide(false)}
          />
          
          {/* Contenu de la modale */}
          <div className="fixed inset-0 z-50 bg-white animate-slide-in overflow-hidden">
            {/* Bouton fermer fixe en haut à droite */}
            <button
              onClick={() => setShowCookingGuide(false)}
              className="fixed top-4 right-4 z-[60] p-3 bg-white rounded-full shadow-xl hover:bg-gray-100 transition-all duration-200 hover:scale-110"
              aria-label="Fermer le mode chef"
            >
              <X className="w-6 h-6 text-gray-700" />
            </button>
            
            {/* Container scrollable pour le contenu */}
            <div className="h-full w-full overflow-y-auto overflow-x-hidden bg-gradient-to-b from-gray-50 to-white">
              <CookingGuide 
                recipeId={recipe.id}
                onBack={() => setShowCookingGuide(false)}
              />
            </div>
          </div>
        </>
      )}
    </>
  )
}

// Composant compact pour afficher les badges du mode chef
export function ChefModeBadge({ recipe }) {
  if (!recipe.has_chef_mode) {
    return null
  }

  return (
    <div className="flex items-center space-x-2">
      <div className="flex items-center bg-orange-100 text-orange-800 px-2 py-1 rounded-full text-xs">
        <ChefHat className="w-3 h-3 mr-1" />
        Mode Chef
      </div>
      {recipe.difficulty_level && (
        <div className={`px-2 py-1 rounded-full text-xs font-medium ${
          recipe.difficulty_level === 'beginner' ? 'bg-green-100 text-green-800' :
          recipe.difficulty_level === 'intermediate' ? 'bg-yellow-100 text-yellow-800' :
          'bg-red-100 text-red-800'
        }`}>
          {DIFFICULTY_LABELS[recipe.difficulty_level]}
        </div>
      )}
    </div>
  )
}

// Composant pour afficher un aperçu des conseils du chef dans une carte de recette
export function ChefTipsPreview({ recipe }) {
  if (!recipe.chef_tips || recipe.chef_tips.length === 0) {
    return null
  }

  const highPriorityTips = recipe.chef_tips.filter(tip => tip.importance === 'high')
  const tipsToShow = highPriorityTips.length > 0 ? highPriorityTips.slice(0, 1) : recipe.chef_tips.slice(0, 1)

  return (
    <div className="mt-2">
      <h5 className="text-xs font-medium text-gray-700 mb-1 flex items-center">
        <Star className="w-3 h-3 mr-1 text-yellow-500" />
        Conseil du Chef
      </h5>
      {tipsToShow.map((tip, index) => (
        <p key={index} className="text-xs text-gray-600 italic">
          "{tip.description.length > 80 ? `${tip.description.substring(0, 80)}...` : tip.description}"
        </p>
      ))}
    </div>
  )
}