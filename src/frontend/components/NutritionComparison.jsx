/**
 * Composant de comparaison nutritionnelle (US1.8)
 * Compare les valeurs nutritionnelles planifiées vs réelles vs objectifs
 */

import React from 'react'
import { Card, CardContent, CardHeader, CardTitle } from './ui/card'
import { Progress } from './ui/progress'
import { Badge } from './ui/badge'
import { TrendingUp, TrendingDown, Target, Activity } from 'lucide-react'

const NutritionComparison = ({ 
  actualNutrition = {}, 
  targetNutrition = {}, 
  plannedNutrition = {} 
}) => {
  
  // Calculer les pourcentages d'atteinte des objectifs
  const calculateProgress = (actual, target) => {
    if (!target || target === 0) return 0
    return Math.min(100, (actual / target) * 100)
  }
  
  // Calculer la différence en pourcentage
  const calculateDifference = (actual, planned) => {
    if (!planned || planned === 0) return 0
    return ((actual - planned) / planned) * 100
  }
  
  // Obtenir le badge de statut pour un nutriment
  const getStatusBadge = (actual, target, nutrient) => {
    if (!target) return null
    
    const percentage = (actual / target) * 100
    const isGoodExcess = ['protein', 'fiber'].includes(nutrient)
    
    if (percentage >= 95 && percentage <= 105) {
      return <Badge variant="default" className="bg-green-100 text-green-800">Optimal</Badge>
    } else if (percentage >= 85 && percentage <= 115) {
      return <Badge variant="secondary" className="bg-yellow-100 text-yellow-800">Bon</Badge>
    } else if (percentage > 115) {
      if (isGoodExcess && percentage <= 150) {
        return <Badge variant="secondary" className="bg-blue-100 text-blue-800">Bien+</Badge>
      } else {
        return <Badge variant="destructive" className="bg-red-100 text-red-800">Excès</Badge>
      }
    } else {
      return <Badge variant="destructive" className="bg-orange-100 text-orange-800">Insuffisant</Badge>
    }
  }
  
  // Obtenir l'icône de tendance
  const getTrendIcon = (actual, planned) => {
    const diff = calculateDifference(actual, planned)
    if (Math.abs(diff) < 5) return null
    
    return diff > 0 ? (
      <TrendingUp className="h-4 w-4 text-green-600" />
    ) : (
      <TrendingDown className="h-4 w-4 text-red-600" />
    )
  }
  
  // Définition des nutriments à afficher
  const nutrients = [
    {
      key: 'calories',
      label: 'Calories',
      unit: 'kcal',
      color: 'blue',
      icon: Activity
    },
    {
      key: 'protein',
      label: 'Protéines',
      unit: 'g',
      color: 'green',
      icon: Target
    },
    {
      key: 'carbs',
      label: 'Glucides',
      unit: 'g',
      color: 'yellow',
      icon: Target
    },
    {
      key: 'fat',
      label: 'Lipides',
      unit: 'g',
      color: 'purple',
      icon: Target
    }
  ]
  
  const formatValue = (value) => {
    if (!value) return '0'
    return Math.round(value * 10) / 10
  }
  
  const hasData = Object.values(actualNutrition).some(v => v > 0) || 
                  Object.values(plannedNutrition).some(v => v > 0)
  
  if (!hasData) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center py-8">
          <div className="text-center text-muted-foreground">
            <Activity className="h-8 w-8 mx-auto mb-2 opacity-50" />
            <p>Aucune donnée nutritionnelle disponible</p>
          </div>
        </CardContent>
      </Card>
    )
  }
  
  return (
    <Card className="shadow-lg border-0 bg-gradient-to-br from-white via-blue-50/20 to-purple-50/20 animate-in slide-in-from-right-4 duration-300">
      <CardHeader className="pb-4">
        <CardTitle className="flex items-center gap-3 text-gray-800">
          <div className="p-2 bg-blue-100 rounded-full">
            <Target className="h-5 w-5 text-blue-600" />
          </div>
          <div className="flex-1">
            <span className="text-xl font-bold">Comparaison nutritionnelle</span>
            <p className="text-sm text-gray-600 mt-1 font-normal">
              Suivez votre progression vers vos objectifs quotidiens
            </p>
          </div>
        </CardTitle>
      </CardHeader>
      
      <CardContent className="space-y-6">
        {nutrients.map(({ key, label, unit, color, icon: Icon }, index) => {
          const actual = actualNutrition[key] || 0
          const target = targetNutrition[key] || 0
          const planned = plannedNutrition[key] || 0
          const progress = calculateProgress(actual, target)
          const difference = calculateDifference(actual, planned)
          
          return (
            <div 
              key={key} 
              className={`space-y-3 p-4 rounded-lg bg-white/60 backdrop-blur-sm border border-gray-100 shadow-sm hover:shadow-md transition-all duration-200 animate-in slide-in-from-left-4`}
              style={{ animationDelay: `${index * 100}ms` }}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className={`p-2 rounded-full ${
                    color === 'blue' ? 'bg-blue-100' :
                    color === 'green' ? 'bg-green-100' :
                    color === 'yellow' ? 'bg-yellow-100' :
                    'bg-purple-100'
                  }`}>
                    <Icon className={`h-4 w-4 ${
                      color === 'blue' ? 'text-blue-600' :
                      color === 'green' ? 'text-green-600' :
                      color === 'yellow' ? 'text-yellow-600' :
                      'text-purple-600'
                    }`} />
                  </div>
                  <div className="flex-1">
                    <span className="font-semibold text-gray-800 text-base">{label}</span>
                    {target > 0 && (
                      <div className="mt-1">
                        {getStatusBadge(actual, target, key)}
                      </div>
                    )}
                  </div>
                </div>
                <div className="flex items-center gap-3 text-sm">
                  {getTrendIcon(actual, planned)}
                  <div className="text-right">
                    <div className="font-bold text-gray-800">
                      {formatValue(actual)} {unit}
                    </div>
                    {target > 0 && (
                      <div className="text-xs text-gray-500">
                        sur {formatValue(target)} {unit}
                      </div>
                    )}
                  </div>
                </div>
              </div>
              
              {/* Barre de progression vers l'objectif - Enhanced */}
              {target > 0 && (
                <div className="space-y-2">
                  <div className="relative">
                    <Progress 
                      value={progress} 
                      className={`h-3 shadow-inner ${
                        color === 'blue' ? 'bg-blue-50' :
                        color === 'green' ? 'bg-green-50' :
                        color === 'yellow' ? 'bg-yellow-50' :
                        'bg-purple-50'
                      }`}
                    />
                    {/* Progress indicator */}
                    <div 
                      className={`absolute top-0 h-3 rounded-full transition-all duration-500 ${
                        progress >= 95 ? 'bg-green-500 shadow-green-200' :
                        progress >= 80 ? `${
                          color === 'blue' ? 'bg-blue-500 shadow-blue-200' :
                          color === 'green' ? 'bg-green-500 shadow-green-200' :
                          color === 'yellow' ? 'bg-yellow-500 shadow-yellow-200' :
                          'bg-purple-500 shadow-purple-200'
                        }` :
                        'bg-red-400 shadow-red-200'
                      } shadow-lg`}
                      style={{ width: `${Math.min(progress, 100)}%` }}
                    />
                  </div>
                  <div className="flex justify-between items-center text-xs">
                    <span className="text-gray-600 bg-gray-100 px-2 py-1 rounded">
                      Objectif: {formatValue(target)} {unit}
                    </span>
                    <div className="flex items-center gap-2">
                      <span className={`font-bold px-2 py-1 rounded ${
                        progress >= 95 ? 'text-green-700 bg-green-100' :
                        progress >= 80 ? 'text-blue-700 bg-blue-100' :
                        'text-red-700 bg-red-100'
                      }`}>
                        {Math.round(progress)}%
                      </span>
                    </div>
                  </div>
                </div>
              )}
              
              {/* Comparaison planifié vs réel */}
              {planned > 0 && (
                <div className="bg-gray-50 p-2 rounded text-xs space-y-1">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Planifié:</span>
                    <span className="font-mono">{formatValue(planned)} {unit}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Réel:</span>
                    <span className="font-mono">{formatValue(actual)} {unit}</span>
                  </div>
                  {Math.abs(difference) > 1 && (
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Écart:</span>
                      <span className={`font-mono ${
                        difference > 0 ? 'text-orange-600' : 'text-green-600'
                      }`}>
                        {difference > 0 ? '+' : ''}{Math.round(difference)}%
                      </span>
                    </div>
                  )}
                </div>
              )}
            </div>
          )
        })}
        
        {/* Résumé global - Enhanced */}
        <div className="mt-8 p-6 bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 rounded-xl border border-blue-100 shadow-lg animate-in slide-in-from-bottom-4 duration-500">
          <h4 className="font-bold text-lg mb-4 flex items-center gap-3 text-gray-800">
            <div className="p-2 bg-blue-100 rounded-full">
              <Activity className="h-5 w-5 text-blue-600" />
            </div>
            <span>Résumé quotidien</span>
          </h4>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {/* Calories Card */}
            <div className="bg-white/70 p-4 rounded-lg border border-blue-100 backdrop-blur-sm">
              <div className="text-gray-600 text-sm mb-1">Calories consommées</div>
              <div className="font-bold text-2xl text-blue-600">
                {formatValue(actualNutrition.calories || 0)}
                <span className="text-sm text-gray-500 ml-1">kcal</span>
              </div>
              {targetNutrition.calories && (
                <div className="text-xs text-gray-500 mt-1">
                  sur {formatValue(targetNutrition.calories)} kcal
                </div>
              )}
            </div>
            
            {/* Balance Card */}
            <div className="bg-white/70 p-4 rounded-lg border border-blue-100 backdrop-blur-sm">
              <div className="text-gray-600 text-sm mb-1">Balance nutritionnelle</div>
              <div className="font-semibold">
                {targetNutrition.calories ? (
                  <div className="flex items-center gap-2">
                    <Badge 
                      className={`px-3 py-1 text-sm font-bold ${
                        Math.abs(calculateProgress(actualNutrition.calories || 0, targetNutrition.calories) - 100) <= 10 
                          ? "bg-green-100 text-green-800" 
                          : calculateProgress(actualNutrition.calories || 0, targetNutrition.calories) > 110
                          ? "bg-red-100 text-red-800"
                          : "bg-yellow-100 text-yellow-800"
                      }`}
                    >
                      {Math.round(calculateProgress(actualNutrition.calories || 0, targetNutrition.calories))}%
                    </Badge>
                    <span className="text-xs text-gray-500">
                      {Math.abs(calculateProgress(actualNutrition.calories || 0, targetNutrition.calories) - 100) <= 10 
                        ? "Parfait !"
                        : calculateProgress(actualNutrition.calories || 0, targetNutrition.calories) > 110
                        ? "Dépassé"
                        : "En cours"}
                    </span>
                  </div>
                ) : (
                  <span className="text-gray-400">Objectif non défini</span>
                )}
              </div>
            </div>
            
            {/* Proteins Card */}
            <div className="bg-white/70 p-4 rounded-lg border border-green-100 backdrop-blur-sm">
              <div className="text-gray-600 text-sm mb-1">Protéines</div>
              <div className="font-bold text-xl text-green-600">
                {formatValue(actualNutrition.protein || 0)}
                <span className="text-sm text-gray-500 ml-1">g</span>
                {targetNutrition.protein && (
                  <span className="text-sm text-gray-500 ml-1">
                    /{formatValue(targetNutrition.protein)}g
                  </span>
                )}
              </div>
            </div>
            
            {/* Quick Stats Card */}
            <div className="bg-white/70 p-4 rounded-lg border border-purple-100 backdrop-blur-sm">
              <div className="text-gray-600 text-sm mb-2">Répartition</div>
              <div className="space-y-1 text-xs">
                <div className="flex justify-between">
                  <span className="text-gray-600">Glucides:</span>
                  <span className="font-semibold text-yellow-600">
                    {formatValue(actualNutrition.carbs || 0)}g
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Lipides:</span>
                  <span className="font-semibold text-purple-600">
                    {formatValue(actualNutrition.fat || 0)}g
                  </span>
                </div>
              </div>
            </div>
          </div>
          
          {/* Conseil nutritionnel - Enhanced */}
          {targetNutrition.calories && (
            <div className="mt-6 p-4 bg-white/80 rounded-lg border border-gray-200 shadow-sm">
              {(() => {
                const calorieProgress = calculateProgress(actualNutrition.calories || 0, targetNutrition.calories)
                const proteinProgress = calculateProgress(actualNutrition.protein || 0, targetNutrition.protein || 0)
                
                if (calorieProgress < 80) {
                  return (
                    <div className="flex items-start gap-3">
                      <div className="w-8 h-8 bg-orange-100 rounded-full flex items-center justify-center">
                        <span className="text-sm">💡</span>
                      </div>
                      <div>
                        <h5 className="font-semibold text-orange-700 mb-1">Continuez à manger !</h5>
                        <p className="text-orange-600 text-sm">
                          Il vous reste environ <span className="font-bold">{Math.round(targetNutrition.calories - (actualNutrition.calories || 0))} kcal</span> à consommer pour atteindre votre objectif quotidien.
                        </p>
                      </div>
                    </div>
                  )
                } else if (calorieProgress > 110) {
                  return (
                    <div className="flex items-start gap-3">
                      <div className="w-8 h-8 bg-red-100 rounded-full flex items-center justify-center">
                        <span className="text-sm">⚠️</span>
                      </div>
                      <div>
                        <h5 className="font-semibold text-red-700 mb-1">Objectif dépassé</h5>
                        <p className="text-red-600 text-sm">
                          Vous avez consommé <span className="font-bold">{Math.round((actualNutrition.calories || 0) - targetNutrition.calories)} kcal</span> de plus que votre objectif. Pas de panique, demain est un nouveau jour !
                        </p>
                      </div>
                    </div>
                  )
                } else if (targetNutrition.protein && proteinProgress < 80) {
                  return (
                    <div className="flex items-start gap-3">
                      <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                        <span className="text-sm">🥩</span>
                      </div>
                      <div>
                        <h5 className="font-semibold text-blue-700 mb-1">Plus de protéines</h5>
                        <p className="text-blue-600 text-sm">
                          Pensez à ajouter plus de protéines à votre alimentation. Il vous manque encore <span className="font-bold">{Math.round(targetNutrition.protein - (actualNutrition.protein || 0))}g</span>.
                        </p>
                      </div>
                    </div>
                  )
                } else {
                  return (
                    <div className="flex items-start gap-3">
                      <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                        <span className="text-sm">✅</span>
                      </div>
                      <div>
                        <h5 className="font-semibold text-green-700 mb-1">Excellent travail !</h5>
                        <p className="text-green-600 text-sm">
                          Vous êtes en bonne voie pour atteindre vos objectifs nutritionnels. Continuez ainsi !
                        </p>
                      </div>
                    </div>
                  )
                }
              })()}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}

export default NutritionComparison