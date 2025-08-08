/**
 * Composant d'ajustement des portions (US1.8)
 * Permet d'ajuster la taille des portions et de voir l'impact nutritionnel
 */

import React, { useState, useMemo } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from './ui/card'
import { Button } from './ui/button'
import { Badge } from './ui/badge'
import { Calculator, Utensils } from 'lucide-react'

const PortionAdjuster = ({ 
  currentPortion = 1, 
  plannedNutrition = {}, 
  onAdjust, 
  onCancel 
}) => {
  const [portion, setPortion] = useState(currentPortion)
  const [customNutrition, setCustomNutrition] = useState({})
  const [showCustom, setShowCustom] = useState(false)
  
  // Calcul des valeurs nutritionnelles ajustées
  const adjustedNutrition = useMemo(() => {
    const base = {
      calories: plannedNutrition.calories || 0,
      protein: plannedNutrition.protein || 0,
      carbs: plannedNutrition.carbs || 0,
      fat: plannedNutrition.fat || 0,
      fiber: plannedNutrition.fiber || 0,
      sodium: plannedNutrition.sodium || 0,
      sugar: plannedNutrition.sugar || 0
    }
    
    const adjusted = {}
    Object.keys(base).forEach(key => {
      adjusted[key] = Math.round((base[key] * portion) * 10) / 10
    })
    
    // Remplacer par les valeurs personnalisées si définies
    return { ...adjusted, ...customNutrition }
  }, [portion, plannedNutrition, customNutrition])
  
  // Portions prédéfinies communes
  const commonPortions = [
    { value: 0.25, label: '1/4', description: 'Très petit' },
    { value: 0.5, label: '1/2', description: 'Petit' },
    { value: 0.75, label: '3/4', description: 'Réduit' },
    { value: 1, label: '1', description: 'Normal' },
    { value: 1.25, label: '1.25', description: 'Augmenté' },
    { value: 1.5, label: '1.5', description: 'Grand' },
    { value: 2, label: '2', description: 'Double' }
  ]
  
  const handlePortionSelect = (newPortion) => {
    setPortion(newPortion)
  }
  
  
  const handleCustomNutritionChange = (nutrient, value) => {
    const numValue = parseFloat(value) || 0
    setCustomNutrition(prev => ({
      ...prev,
      [nutrient]: numValue
    }))
  }
  
  const handleConfirm = () => {
    const finalNutrition = showCustom && Object.keys(customNutrition).length > 0
      ? adjustedNutrition
      : {}
    
    onAdjust(portion, finalNutrition)
  }
  
  const getVariationBadge = () => {
    const variation = ((portion - currentPortion) / currentPortion) * 100
    
    if (Math.abs(variation) < 1) {
      return <Badge variant="outline">Aucun changement</Badge>
    } else if (variation > 0) {
      return <Badge variant="secondary">+{Math.round(variation)}%</Badge>
    } else {
      return <Badge variant="destructive">{Math.round(variation)}%</Badge>
    }
  }
  
  const formatNutrient = (value) => {
    if (value === 0) return '0'
    if (value < 1) return value.toFixed(1)
    return Math.round(value).toString()
  }
  
  return (
    <Card className="border-orange-200 bg-gradient-to-br from-orange-50 to-yellow-50 shadow-lg animate-in slide-in-from-bottom-4 duration-300">
      <CardHeader className="pb-4">
        <CardTitle className="flex items-center justify-between text-orange-800">
          <div className="flex items-center gap-2">
            <div className="p-2 bg-orange-100 rounded-full">
              <Calculator className="h-5 w-5 text-orange-600" />
            </div>
            <span className="text-lg font-bold">Ajuster la portion</span>
          </div>
          {getVariationBadge()}
        </CardTitle>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {/* Portions prédéfinies - Enhanced */}
        <div>
          <h4 className="font-semibold mb-3 text-sm text-gray-700 flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-orange-500"></div>
            Portions courantes
          </h4>
          <div className="grid grid-cols-3 sm:grid-cols-4 gap-2 sm:gap-3">
            {commonPortions.map(({ value, label, description }) => (
              <Button
                key={value}
                variant={portion === value ? "default" : "outline"}
                size="sm"
                onClick={() => handlePortionSelect(value)}
                className={`flex flex-col p-3 h-auto min-h-[60px] transition-all duration-200 transform hover:scale-105 ${
                  portion === value 
                    ? 'bg-orange-600 hover:bg-orange-700 text-white shadow-md border-orange-600' 
                    : 'hover:bg-orange-50 hover:border-orange-300 border-gray-200'
                }`}
                aria-label={`Sélectionner portion ${label} (${description})`}
              >
                <span className="font-bold text-base">{label}×</span>
                <span className={`text-xs mt-1 ${
                  portion === value ? 'text-orange-100' : 'text-gray-600'
                }`}>
                  {description}
                </span>
              </Button>
            ))}
          </div>
        </div>
        
        {/* Slider pour ajustement précis - Enhanced */}
        <div className="bg-white/70 rounded-lg p-4 border border-orange-100">
          <div className="flex items-center justify-between mb-3">
            <h4 className="font-semibold text-sm text-gray-700 flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-blue-500"></div>
              Ajustement précis
            </h4>
            <div className="flex items-center gap-2">
              <span className="text-xs text-gray-600">Portion:</span>
              <span className="text-lg font-bold text-orange-600 bg-orange-100 px-3 py-1 rounded-full shadow-sm">
                {portion}×
              </span>
            </div>
          </div>
          
          <div className="relative">
            <input
              type="range"
              min={0.1}
              max={3}
              step={0.1}
              value={portion}
              onChange={(e) => setPortion(parseFloat(e.target.value))}
              className="w-full h-3 bg-gradient-to-r from-red-200 via-yellow-200 to-green-200 rounded-lg appearance-none cursor-pointer slider"
              style={{
                background: `linear-gradient(to right, #fca5a5 0%, #fed7aa 50%, #86efac 100%)`,
              }}
              aria-label={`Ajuster la portion à ${portion} fois la portion standard`}
            />
            <div className="flex justify-between text-xs text-gray-600 mt-2 px-1">
              <span className="bg-white px-2 py-1 rounded shadow-sm">0.1×</span>
              <span className="bg-white px-2 py-1 rounded shadow-sm">1.5×</span>
              <span className="bg-white px-2 py-1 rounded shadow-sm">3×</span>
            </div>
          </div>
          
          {/* Visual feedback for portion size */}
          <div className="mt-3 text-center">
            <div className={`inline-block px-3 py-1 rounded-full text-xs font-medium ${
              portion < 0.5 ? 'bg-red-100 text-red-700' :
              portion < 0.8 ? 'bg-yellow-100 text-yellow-700' :
              portion <= 1.2 ? 'bg-green-100 text-green-700' :
              portion <= 1.5 ? 'bg-blue-100 text-blue-700' :
              'bg-orange-100 text-orange-700'
            }`}>
              {portion < 0.5 ? '🍽️ Très petite portion' :
               portion < 0.8 ? '🥄 Petite portion' :
               portion <= 1.2 ? '✅ Portion normale' :
               portion <= 1.5 ? '🍲 Grande portion' :
               '🍽️ Très grande portion'}
            </div>
          </div>
        </div>
        
        {/* Aperçu nutritionnel */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <h4 className="font-medium text-sm">Valeurs ajustées</h4>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowCustom(!showCustom)}
              className="text-xs h-auto p-1"
            >
              {showCustom ? 'Masquer' : 'Personnaliser'}
            </Button>
          </div>
          
          <div className="grid grid-cols-2 gap-3 text-sm bg-white p-3 rounded border">
            <div className="flex justify-between">
              <span className="text-muted-foreground">Calories:</span>
              <span className="font-medium">
                {formatNutrient(adjustedNutrition.calories)} kcal
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Protéines:</span>
              <span className="font-medium">
                {formatNutrient(adjustedNutrition.protein)} g
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Glucides:</span>
              <span className="font-medium">
                {formatNutrient(adjustedNutrition.carbs)} g
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Lipides:</span>
              <span className="font-medium">
                {formatNutrient(adjustedNutrition.fat)} g
              </span>
            </div>
          </div>
        </div>
        
        {/* Personnalisation nutritionnelle */}
        {showCustom && (
          <div className="bg-white p-3 rounded border space-y-3">
            <h4 className="font-medium text-sm">Valeurs personnalisées</h4>
            <p className="text-xs text-muted-foreground">
              Remplacez les valeurs calculées si vous connaissez les vraies valeurs nutritionnelles
            </p>
            
            <div className="grid grid-cols-2 gap-3">
              {[
                { key: 'calories', label: 'Calories (kcal)' },
                { key: 'protein', label: 'Protéines (g)' },
                { key: 'carbs', label: 'Glucides (g)' },
                { key: 'fat', label: 'Lipides (g)' }
              ].map(({ key, label }) => (
                <div key={key}>
                  <label className="text-xs text-muted-foreground block mb-1">
                    {label}
                  </label>
                  <input
                    type="number"
                    min="0"
                    step="0.1"
                    placeholder={formatNutrient(adjustedNutrition[key])}
                    onChange={(e) => handleCustomNutritionChange(key, e.target.value)}
                    className="w-full p-1 border rounded text-sm h-8"
                  />
                </div>
              ))}
            </div>
          </div>
        )}
        
        {/* Comparaison avec l'original */}
        <div className="bg-white p-3 rounded border">
          <h4 className="font-medium text-sm mb-2">Comparaison</h4>
          <div className="grid grid-cols-3 gap-2 text-xs">
            <div className="text-center">
              <div className="text-muted-foreground">Original</div>
              <div className="font-mono">
                {Math.round(plannedNutrition.calories || 0)} kcal
              </div>
            </div>
            <div className="text-center">
              <div className="text-muted-foreground">Ajusté</div>
              <div className="font-mono font-semibold">
                {Math.round(adjustedNutrition.calories)} kcal
              </div>
            </div>
            <div className="text-center">
              <div className="text-muted-foreground">Différence</div>
              <div className={`font-mono ${
                adjustedNutrition.calories > plannedNutrition.calories 
                  ? 'text-orange-600' 
                  : adjustedNutrition.calories < plannedNutrition.calories 
                  ? 'text-green-600' 
                  : 'text-gray-600'
              }`}>
                {adjustedNutrition.calories > plannedNutrition.calories ? '+' : ''}
                {Math.round(adjustedNutrition.calories - (plannedNutrition.calories || 0))} kcal
              </div>
            </div>
          </div>
        </div>
        
        {/* Boutons d'action - Enhanced */}
        <div className="flex flex-col sm:flex-row gap-3 pt-4">
          <Button
            onClick={handleConfirm}
            disabled={portion === currentPortion && Object.keys(customNutrition).length === 0}
            className="flex-1 bg-orange-600 hover:bg-orange-700 text-white transition-all duration-200 hover:shadow-lg transform hover:scale-105 py-3 font-semibold"
            size="lg"
            aria-label="Appliquer l'ajustement de portion"
          >
            <Utensils className="h-5 w-5 mr-2" />
            <span>Appliquer l'ajustement</span>
          </Button>
          <Button
            variant="outline"
            onClick={onCancel}
            className="sm:w-auto hover:bg-gray-50 hover:border-gray-300 transition-all duration-200 py-3 font-medium"
            size="lg"
            aria-label="Annuler l'ajustement"
          >
            <span>Annuler</span>
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}

export default PortionAdjuster