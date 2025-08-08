/**
 * Composant de carte de repas (US1.8)
 * Affiche un repas avec ses actions (consommer, ajuster, ignorer, remplacer)
 */

import React, { useState } from 'react'
import { useMealTracking } from '../hooks/useMealTracking'
import PortionAdjuster from './PortionAdjuster'
import { Card, CardContent, CardHeader, CardTitle } from './ui/card'
import { Button } from './ui/button'
import { Badge } from './ui/badge'
import { Progress } from './ui/progress'
import { 
  CheckCircle, 
  Clock, 
  X, 
  RotateCcw, 
  Utensils,
  Star,
  Camera,
  MessageSquare,
  ChevronDown,
  ChevronUp,
  Calculator
} from 'lucide-react'

const MealCard = ({ mealTracking, onStatusChange, disabled = false }) => {
  const {
    markMealConsumed,
    adjustMealPortions,
    skipMeal,
    replaceMeal,
    isLoading
  } = useMealTracking()
  
  const [showDetails, setShowDetails] = useState(false)
  const [showPortionAdjuster, setShowPortionAdjuster] = useState(false)
  const [showRating, setShowRating] = useState(false)
  const [satisfaction, setSatisfaction] = useState(0)
  const [notes, setNotes] = useState('')
  const [skipReason, setSkipReason] = useState('')
  const [showSkipReason, setShowSkipReason] = useState(false)
  const [replacementName, setReplacementName] = useState('')
  const [replacementReason, setReplacementReason] = useState('')
  const [showReplacementForm, setShowReplacementForm] = useState(false)
  
  if (!mealTracking) return null
  
  const {
    id,
    meal_name,
    status,
    planned_nutrition = {},
    actual_nutrition = {},
    effective_nutrition = {},
    planned_portion_size = 1,
    actual_portion_size,
    consumption_datetime,
    satisfaction_rating,
    user_notes,
    skip_reason,
    replacement_name,
    replacement_reason
  } = mealTracking
  
  // Statut badges - Enhanced
  const getStatusBadge = () => {
    const statusConfig = {
      planned: { 
        label: 'Planifié', 
        icon: Clock,
        className: 'bg-blue-100 text-blue-800 border-blue-200 shadow-sm animate-pulse'
      },
      consumed: { 
        label: 'Consommé', 
        icon: CheckCircle,
        className: 'bg-green-100 text-green-800 border-green-200 shadow-sm'
      },
      modified: { 
        label: 'Modifié', 
        icon: RotateCcw,
        className: 'bg-orange-100 text-orange-800 border-orange-200 shadow-sm'
      },
      skipped: { 
        label: 'Ignoré', 
        icon: X,
        className: 'bg-red-100 text-red-800 border-red-200 shadow-sm'
      },
      replaced: { 
        label: 'Remplacé', 
        icon: RotateCcw,
        className: 'bg-purple-100 text-purple-800 border-purple-200 shadow-sm'
      }
    }
    
    const config = statusConfig[status] || statusConfig.planned
    const Icon = config.icon
    
    return (
      <Badge className={`flex items-center gap-1 px-2 py-1 text-xs font-medium transition-all duration-200 ${config.className}`}>
        <Icon className="h-3 w-3" />
        <span>{config.label}</span>
      </Badge>
    )
  }
  
  // Actions des boutons selon le statut
  const handleConsume = async () => {
    if (showRating) {
      const consumptionData = {}
      if (satisfaction > 0) consumptionData.satisfaction_rating = satisfaction
      if (notes.trim()) consumptionData.notes = notes.trim()
      
      await markMealConsumed(id, consumptionData)
      setShowRating(false)
      setSatisfaction(0)
      setNotes('')
      onStatusChange?.()
    } else if (status === 'planned') {
      setShowRating(true)
    }
  }
  
  const handleSkip = async () => {
    if (showSkipReason) {
      await skipMeal(id, skipReason.trim())
      setShowSkipReason(false)
      setSkipReason('')
      onStatusChange?.()
    } else {
      setShowSkipReason(true)
    }
  }
  
  const handleReplace = async () => {
    if (showReplacementForm) {
      const replacementData = {
        replacement_name: replacementName.trim(),
        reason: replacementReason.trim()
      }
      
      await replaceMeal(id, replacementData)
      setShowReplacementForm(false)
      setReplacementName('')
      setReplacementReason('')
      onStatusChange?.()
    } else {
      setShowReplacementForm(true)
    }
  }
  
  const handlePortionAdjust = (multiplier, customNutrition) => {
    adjustMealPortions(id, multiplier, customNutrition)
    setShowPortionAdjuster(false)
    onStatusChange?.()
  }
  
  // Calcul du pourcentage de progression nutritionnelle
  const getNutritionProgress = () => {
    if (!planned_nutrition.calories || planned_nutrition.calories === 0) return 0
    const effective = effective_nutrition.calories || 0
    return Math.min(100, (effective / planned_nutrition.calories) * 100)
  }
  
  const formatTime = (datetime) => {
    if (!datetime) return null
    return new Date(datetime).toLocaleTimeString('fr-FR', {
      hour: '2-digit',
      minute: '2-digit'
    })
  }
  
  const canModify = status === 'planned' && !disabled
  const isConsumed = ['consumed', 'modified', 'replaced'].includes(status)
  const isSkipped = status === 'skipped'
  
  return (
    <Card className={`transition-all duration-300 hover:shadow-lg transform hover:-translate-y-1 ${
      disabled ? 'opacity-60' : ''
    } ${
      status === 'consumed' ? 'border-green-200 bg-green-50/30' :
      status === 'skipped' ? 'border-red-200 bg-red-50/30' :
      status === 'replaced' ? 'border-purple-200 bg-purple-50/30' :
      status === 'modified' ? 'border-orange-200 bg-orange-50/30' :
      'border-blue-200 bg-blue-50/30'
    }`}>
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <CardTitle className="flex items-center gap-3 text-gray-800">
              <div className={`p-2 rounded-full transition-all duration-200 ${
                status === 'consumed' ? 'bg-green-100' :
                status === 'skipped' ? 'bg-red-100' :
                status === 'replaced' ? 'bg-purple-100' :
                status === 'modified' ? 'bg-orange-100' :
                'bg-blue-100'
              }`}>
                <Utensils className={`h-4 w-4 ${
                  status === 'consumed' ? 'text-green-600' :
                  status === 'skipped' ? 'text-red-600' :
                  status === 'replaced' ? 'text-purple-600' :
                  status === 'modified' ? 'text-orange-600' :
                  'text-blue-600'
                }`} />
              </div>
              <div className="flex-1">
                <span className="text-base sm:text-lg font-semibold">
                  {meal_name || 'Repas non défini'}
                </span>
                <div className="mt-1">
                  {getStatusBadge()}
                </div>
              </div>
            </CardTitle>
            
            {/* Informations additionnelles selon le statut */}
            {consumption_datetime && (
              <p className="text-sm text-muted-foreground mt-1">
                Consommé à {formatTime(consumption_datetime)}
              </p>
            )}
            
            {skip_reason && (
              <p className="text-sm text-muted-foreground mt-1">
                Raison: {skip_reason}
              </p>
            )}
            
            {replacement_name && (
              <p className="text-sm text-muted-foreground mt-1">
                Remplacé par: {replacement_name}
                {replacement_reason && ` (${replacement_reason})`}
              </p>
            )}
          </div>
          
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setShowDetails(!showDetails)}
            className="ml-2"
          >
            {showDetails ? (
              <ChevronUp className="h-4 w-4" />
            ) : (
              <ChevronDown className="h-4 w-4" />
            )}
          </Button>
        </div>
        
        {/* Barre de progression nutritionnelle */}
        <div className="mt-3">
          <div className="flex justify-between items-center mb-1">
            <span className="text-xs font-medium">Nutrition</span>
            <span className="text-xs text-muted-foreground">
              {Math.round(effective_nutrition.calories || 0)} / {Math.round(planned_nutrition.calories || 0)} kcal
            </span>
          </div>
          <Progress value={getNutritionProgress()} className="h-1" />
        </div>
        
        {/* Note de satisfaction */}
        {satisfaction_rating && (
          <div className="flex items-center gap-1 mt-2">
            {[1, 2, 3, 4, 5].map(star => (
              <Star
                key={star}
                className={`h-4 w-4 ${
                  star <= satisfaction_rating 
                    ? 'text-yellow-500 fill-current' 
                    : 'text-gray-300'
                }`}
              />
            ))}
            <span className="text-sm text-muted-foreground ml-1">
              ({satisfaction_rating}/5)
            </span>
          </div>
        )}
      </CardHeader>
      
      <CardContent className="pt-0">
        {/* Détails étendus */}
        {showDetails && (
          <div className="space-y-4 mb-4">
            {/* Informations nutritionnelles détaillées */}
            <div>
              <h4 className="font-medium mb-2">Valeurs nutritionnelles</h4>
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div>
                  <span className="text-muted-foreground">Protéines:</span>
                  <span className="ml-2 font-medium">
                    {Math.round(effective_nutrition.protein || 0)}g
                  </span>
                </div>
                <div>
                  <span className="text-muted-foreground">Glucides:</span>
                  <span className="ml-2 font-medium">
                    {Math.round(effective_nutrition.carbs || 0)}g
                  </span>
                </div>
                <div>
                  <span className="text-muted-foreground">Lipides:</span>
                  <span className="ml-2 font-medium">
                    {Math.round(effective_nutrition.fat || 0)}g
                  </span>
                </div>
                <div>
                  <span className="text-muted-foreground">Fibres:</span>
                  <span className="ml-2 font-medium">
                    {Math.round(effective_nutrition.fiber || 0)}g
                  </span>
                </div>
              </div>
            </div>
            
            {/* Portion */}
            {(actual_portion_size || planned_portion_size !== 1) && (
              <div>
                <h4 className="font-medium mb-1">Portion</h4>
                <p className="text-sm text-muted-foreground">
                  {actual_portion_size 
                    ? `${Math.round(actual_portion_size * 100)}% de la portion planifiée`
                    : `Portion standard (${planned_portion_size}x)`
                  }
                </p>
              </div>
            )}
            
            {/* Notes utilisateur */}
            {user_notes && (
              <div>
                <h4 className="font-medium mb-1">Notes</h4>
                <p className="text-sm text-muted-foreground bg-gray-50 p-2 rounded">
                  {user_notes}
                </p>
              </div>
            )}
          </div>
        )}
        
        {/* Formulaire de notation lors de la consommation */}
        {showRating && (
          <div className="space-y-3 p-3 bg-gray-50 rounded-lg mb-4">
            <div>
              <label className="text-sm font-medium block mb-2">
                Satisfaction (optionnel)
              </label>
              <div className="flex gap-1">
                {[1, 2, 3, 4, 5].map(star => (
                  <button
                    key={star}
                    onClick={() => setSatisfaction(satisfaction === star ? 0 : star)}
                    className="focus:outline-none"
                    type="button"
                  >
                    <Star
                      className={`h-5 w-5 transition-colors ${
                        star <= satisfaction 
                          ? 'text-yellow-500 fill-current' 
                          : 'text-gray-300 hover:text-yellow-300'
                      }`}
                    />
                  </button>
                ))}
              </div>
            </div>
            
            <div>
              <label className="text-sm font-medium block mb-2">
                Notes (optionnel)
              </label>
              <textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="Comment s'est passé ce repas ?"
                className="w-full p-2 border rounded text-sm resize-none"
                rows="2"
              />
            </div>
            
            <div className="flex gap-2">
              <Button
                size="sm"
                onClick={handleConsume}
                disabled={isLoading}
              >
                Confirmer
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  setShowRating(false)
                  setSatisfaction(0)
                  setNotes('')
                }}
              >
                Annuler
              </Button>
            </div>
          </div>
        )}
        
        {/* Formulaire de raison d'omission */}
        {showSkipReason && (
          <div className="space-y-3 p-3 bg-red-50 rounded-lg mb-4">
            <div>
              <label className="text-sm font-medium block mb-2">
                Pourquoi ignorer ce repas ? (optionnel)
              </label>
              <input
                type="text"
                value={skipReason}
                onChange={(e) => setSkipReason(e.target.value)}
                placeholder="Ex: Pas faim, pas le temps..."
                className="w-full p-2 border rounded text-sm"
              />
            </div>
            
            <div className="flex gap-2">
              <Button
                variant="destructive"
                size="sm"
                onClick={handleSkip}
                disabled={isLoading}
              >
                Confirmer l'omission
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  setShowSkipReason(false)
                  setSkipReason('')
                }}
              >
                Annuler
              </Button>
            </div>
          </div>
        )}
        
        {/* Formulaire de remplacement */}
        {showReplacementForm && (
          <div className="space-y-3 p-3 bg-purple-50 rounded-lg mb-4">
            <div>
              <label className="text-sm font-medium block mb-2">
                Nom du repas de remplacement
              </label>
              <input
                type="text"
                value={replacementName}
                onChange={(e) => setReplacementName(e.target.value)}
                placeholder="Ex: Salade César"
                className="w-full p-2 border rounded text-sm"
                required
              />
            </div>
            
            <div>
              <label className="text-sm font-medium block mb-2">
                Raison du remplacement (optionnel)
              </label>
              <input
                type="text"
                value={replacementReason}
                onChange={(e) => setReplacementReason(e.target.value)}
                placeholder="Ex: Ingrédients manquants"
                className="w-full p-2 border rounded text-sm"
              />
            </div>
            
            <div className="flex gap-2">
              <Button
                variant="secondary"
                size="sm"
                onClick={handleReplace}
                disabled={isLoading || !replacementName.trim()}
              >
                Confirmer le remplacement
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  setShowReplacementForm(false)
                  setReplacementName('')
                  setReplacementReason('')
                }}
              >
                Annuler
              </Button>
            </div>
          </div>
        )}
        
        {/* Ajusteur de portions */}
        {showPortionAdjuster && (
          <div className="mb-4">
            <PortionAdjuster
              currentPortion={actual_portion_size || planned_portion_size}
              plannedNutrition={planned_nutrition}
              onAdjust={handlePortionAdjust}
              onCancel={() => setShowPortionAdjuster(false)}
            />
          </div>
        )}
        
        {/* Actions - Enhanced mobile-first design */}
        {canModify && (
          <div className="grid grid-cols-2 sm:flex gap-2 sm:gap-3">
            <Button
              onClick={handleConsume}
              disabled={isLoading}
              className="flex items-center justify-center gap-2 bg-green-600 hover:bg-green-700 text-white transition-all duration-200 hover:shadow-md transform hover:scale-105 font-medium py-2.5 col-span-2 sm:col-span-1 sm:flex-1"
              aria-label="Marquer comme consommé"
            >
              <CheckCircle className="h-4 w-4" />
              <span className="text-sm">Consommer</span>
            </Button>
            
            <Button
              variant="outline"
              onClick={() => setShowPortionAdjuster(true)}
              disabled={isLoading}
              className="flex items-center justify-center gap-1 hover:bg-blue-50 hover:border-blue-300 transition-all duration-200 hover:shadow-sm transform hover:scale-105 font-medium"
              aria-label="Ajuster la portion"
            >
              <Calculator className="h-4 w-4" />
              <span className="text-xs sm:text-sm">Ajuster</span>
            </Button>
            
            <Button
              variant="outline"
              onClick={handleReplace}
              disabled={isLoading}
              className="flex items-center justify-center gap-1 hover:bg-purple-50 hover:border-purple-300 transition-all duration-200 hover:shadow-sm transform hover:scale-105 font-medium"
              aria-label="Remplacer ce repas"
            >
              <RotateCcw className="h-4 w-4" />
              <span className="text-xs sm:text-sm">Remplacer</span>
            </Button>
            
            <Button
              variant="outline"
              onClick={handleSkip}
              disabled={isLoading}
              className="flex items-center justify-center gap-1 hover:bg-red-50 hover:border-red-300 text-red-700 transition-all duration-200 hover:shadow-sm transform hover:scale-105 font-medium col-span-2 sm:col-span-1"
              aria-label="Ignorer ce repas"
            >
              <X className="h-4 w-4" />
              <span className="text-xs sm:text-sm">Ignorer</span>
            </Button>
          </div>
        )}
        
        {/* Information de statut pour les repas non modifiables - Enhanced */}
        {(isConsumed || isSkipped) && (
          <div className={`text-center py-3 px-4 rounded-lg transition-all duration-200 ${
            isConsumed 
              ? 'bg-green-50 text-green-800 border border-green-200' 
              : 'bg-red-50 text-red-800 border border-red-200'
          }`}>
            <div className="flex items-center justify-center gap-2">
              {isConsumed ? (
                <>
                  <CheckCircle className="h-4 w-4" />
                  <span className="font-medium">Repas terminé avec succès</span>
                </>
              ) : (
                <>
                  <X className="h-4 w-4" />
                  <span className="font-medium">Repas ignoré</span>
                </>
              )}
            </div>
            {consumption_datetime && isConsumed && (
              <p className="text-xs mt-1 opacity-75">
                Consommé à {formatTime(consumption_datetime)}
              </p>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  )
}

export default MealCard