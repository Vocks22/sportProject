/**
 * Composant de résumé quotidien du suivi des repas (US1.8)
 * Affiche les statistiques, scores d'adhérence et métriques de la journée
 */

import React, { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from './ui/card'
import { Progress } from './ui/progress'
import { Badge } from './ui/badge'
import { Button } from './ui/button'
import { 
  BarChart3, 
  Target, 
  Award, 
  TrendingUp, 
  Clock,
  Star,
  CheckCircle,
  XCircle,
  RotateCcw,
  ChevronDown,
  ChevronUp
} from 'lucide-react'

const DailySummary = ({ summary, nutritionTotals = {}, completionStats = {} }) => {
  const [showDetails, setShowDetails] = useState(false)
  
  if (!summary) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center py-8">
          <div className="text-center text-muted-foreground">
            <BarChart3 className="h-8 w-8 mx-auto mb-2 opacity-50" />
            <p>Résumé quotidien non disponible</p>
          </div>
        </CardContent>
      </Card>
    )
  }
  
  const {
    adherence_scores = {},
    meal_stats = {},
    deficit_surplus = {},
    timing = {},
    quality = {},
    achievements = {}
  } = summary
  
  // Obtenir le badge de score
  const getScoreBadge = (score) => {
    if (score >= 90) return <Badge className="bg-green-100 text-green-800">Excellent</Badge>
    if (score >= 80) return <Badge className="bg-blue-100 text-blue-800">Très bien</Badge>
    if (score >= 70) return <Badge className="bg-yellow-100 text-yellow-800">Bien</Badge>
    if (score >= 60) return <Badge variant="secondary">Correct</Badge>
    return <Badge variant="destructive">À améliorer</Badge>
  }
  
  // Obtenir la couleur de la barre de progression
  const getProgressColor = (score) => {
    if (score >= 80) return 'bg-green-500'
    if (score >= 60) return 'bg-yellow-500'
    return 'bg-red-500'
  }
  
  // Formater les valeurs nutritionnelles
  const formatNutrient = (value) => {
    if (!value) return '0'
    return Math.round(value * 10) / 10
  }
  
  // Formater les déficits/surplus
  const formatDeficitSurplus = (value, unit = '') => {
    if (!value) return '0'
    const formatted = formatNutrient(Math.abs(value))
    const sign = value > 0 ? '+' : '-'
    return `${sign}${formatted}${unit}`
  }
  
  const mainScore = adherence_scores?.overall_nutrition || 0
  const planAdherence = adherence_scores?.plan_adherence || 0
  const targetAdherence = adherence_scores?.target_adherence || 0
  
  return (
    <div className="space-y-6">
      {/* Carte principale avec score global - Enhanced */}
      <Card className="bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 shadow-lg border-0 animate-in slide-in-from-top-4 duration-500">
        <CardHeader className="pb-4">
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-3">
              <div className={`p-3 rounded-full transition-all duration-300 ${
                mainScore >= 90 ? 'bg-yellow-100 animate-bounce' :
                mainScore >= 80 ? 'bg-blue-100' :
                'bg-gray-100'
              }`}>
                <Award className={`h-6 w-6 ${
                  mainScore >= 90 ? 'text-yellow-600' :
                  mainScore >= 80 ? 'text-blue-600' :
                  'text-gray-600'
                }`} />
              </div>
              <div>
                <h2 className="text-xl font-bold text-gray-800">Résumé quotidien</h2>
                <div className="mt-1">
                  {getScoreBadge(mainScore)}
                </div>
              </div>
            </CardTitle>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowDetails(!showDetails)}
              className="hover:bg-white/50 transition-all duration-200"
              aria-label={showDetails ? "Masquer les détails" : "Afficher les détails"}
            >
              {showDetails ? (
                <ChevronUp className="h-5 w-5" />
              ) : (
                <ChevronDown className="h-5 w-5" />
              )}
            </Button>
          </div>
        </CardHeader>
        
        <CardContent className="space-y-6">
          {/* Score global - Enhanced with celebration */}
          <div className="bg-white/60 rounded-lg p-4 backdrop-blur-sm">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-blue-500 animate-pulse"></div>
                <span className="font-semibold text-gray-700">Score nutritionnel global</span>
              </div>
              <div className="flex items-center gap-2">
                <span className={`text-3xl font-bold transition-all duration-300 ${
                  mainScore >= 90 ? 'text-green-600 animate-pulse' :
                  mainScore >= 80 ? 'text-blue-600' :
                  mainScore >= 70 ? 'text-yellow-600' :
                  'text-red-600'
                }`}>
                  {Math.round(mainScore)}%
                </span>
                {mainScore >= 90 && (
                  <div className="text-yellow-500 animate-bounce">🏆</div>
                )}
                {mainScore >= 80 && mainScore < 90 && (
                  <div className="text-blue-500">⭐</div>
                )}
              </div>
            </div>
            <div className="relative">
              <Progress 
                value={mainScore} 
                className="h-4 shadow-inner"
              />
              <div 
                className={`absolute top-0 h-4 rounded-full transition-all duration-1000 ${
                  mainScore >= 90 ? 'bg-gradient-to-r from-green-400 to-green-600 shadow-lg shadow-green-200' :
                  mainScore >= 80 ? 'bg-gradient-to-r from-blue-400 to-blue-600 shadow-lg shadow-blue-200' :
                  mainScore >= 70 ? 'bg-gradient-to-r from-yellow-400 to-yellow-600 shadow-lg shadow-yellow-200' :
                  'bg-gradient-to-r from-red-400 to-red-600 shadow-lg shadow-red-200'
                }`}
                style={{ width: `${mainScore}%` }}
              />
            </div>
            {mainScore >= 90 && (
              <div className="mt-3 text-center">
                <span className="text-green-600 font-semibold text-sm animate-pulse">
                  🎉 Performance exceptionnelle ! Continuez ainsi !
                </span>
              </div>
            )}
          </div>
          
          {/* Scores d'adhérence principaux */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <div className="text-sm text-muted-foreground mb-1">Adhérence au plan</div>
              <div className="flex items-center gap-2">
                <Progress value={planAdherence} className="flex-1 h-2" />
                <span className="text-sm font-medium min-w-[3rem]">
                  {Math.round(planAdherence)}%
                </span>
              </div>
            </div>
            
            <div>
              <div className="text-sm text-muted-foreground mb-1">Adhérence aux objectifs</div>
              <div className="flex items-center gap-2">
                <Progress value={targetAdherence} className="flex-1 h-2" />
                <span className="text-sm font-medium min-w-[3rem]">
                  {Math.round(targetAdherence)}%
                </span>
              </div>
            </div>
          </div>
          
          {/* Statistiques de repas */}
          <div className="flex items-center justify-between text-sm">
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-1">
                <CheckCircle className="h-4 w-4 text-green-600" />
                <span>{meal_stats.consumed || 0} consommés</span>
              </div>
              
              {meal_stats.skipped > 0 && (
                <div className="flex items-center gap-1">
                  <XCircle className="h-4 w-4 text-red-600" />
                  <span>{meal_stats.skipped} ignorés</span>
                </div>
              )}
              
              {(meal_stats.replaced > 0 || meal_stats.modified > 0) && (
                <div className="flex items-center gap-1">
                  <RotateCcw className="h-4 w-4 text-orange-600" />
                  <span>{(meal_stats.replaced || 0) + (meal_stats.modified || 0)} modifiés</span>
                </div>
              )}
            </div>
            
            <div className="text-muted-foreground">
              {Math.round(meal_stats.completion_rate || 0)}% terminés
            </div>
          </div>
        </CardContent>
      </Card>
      
      {/* Détails étendus */}
      {showDetails && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Bilan nutritionnel */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <Target className="h-4 w-4" />
                Bilan nutritionnel
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {[
                { key: 'calories', label: 'Calories', unit: 'kcal' },
                { key: 'protein', label: 'Protéines', unit: 'g' },
                { key: 'carbs', label: 'Glucides', unit: 'g' },
                { key: 'fat', label: 'Lipides', unit: 'g' }
              ].map(({ key, label, unit }) => {
                const deficit = deficit_surplus[`${key}_deficit_surplus`] || 0
                const isDeficit = deficit < 0
                
                return (
                  <div key={key} className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">{label}:</span>
                    <div className="flex items-center gap-2">
                      <span className="font-mono">
                        {formatNutrient(nutritionTotals[key] || 0)} {unit}
                      </span>
                      {Math.abs(deficit) > 1 && (
                        <Badge 
                          variant={isDeficit ? "destructive" : "secondary"}
                          className="text-xs"
                        >
                          {formatDeficitSurplus(deficit, unit)}
                        </Badge>
                      )}
                    </div>
                  </div>
                )
              })}
            </CardContent>
          </Card>
          
          {/* Qualité et timing */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <Clock className="h-4 w-4" />
                Qualité et timing
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {/* Satisfaction */}
              {quality.avg_satisfaction_rating && (
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Satisfaction:</span>
                  <div className="flex items-center gap-1">
                    {[1, 2, 3, 4, 5].map(star => (
                      <Star
                        key={star}
                        className={`h-3 w-3 ${
                          star <= quality.avg_satisfaction_rating
                            ? 'text-yellow-500 fill-current'
                            : 'text-gray-300'
                        }`}
                      />
                    ))}
                    <span className="text-sm ml-1">
                      {formatNutrient(quality.avg_satisfaction_rating)}/5
                    </span>
                  </div>
                </div>
              )}
              
              {/* Timing */}
              {timing.timing_adherence_rate > 0 && (
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Ponctualité:</span>
                  <span className="font-medium">
                    {Math.round(timing.timing_adherence_rate)}%
                  </span>
                </div>
              )}
              
              {timing.avg_variance_minutes && (
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Écart moyen:</span>
                  <span className="font-mono">
                    {Math.abs(Math.round(timing.avg_variance_minutes))} min
                  </span>
                </div>
              )}
              
              {/* Difficulté */}
              {quality.avg_difficulty_rating && (
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Difficulté moy.:</span>
                  <span className="font-medium">
                    {formatNutrient(quality.avg_difficulty_rating)}/5
                  </span>
                </div>
              )}
            </CardContent>
          </Card>
          
          {/* Achievements - Enhanced with celebrations */}
          {Object.keys(achievements).length > 0 && (
            <Card className="md:col-span-2 shadow-lg border-0 bg-gradient-to-br from-yellow-50 to-orange-50">
              <CardHeader className="pb-4">
                <CardTitle className="text-lg flex items-center gap-3 text-gray-800">
                  <div className="p-2 bg-yellow-100 rounded-full">
                    <Award className="h-5 w-5 text-yellow-600" />
                  </div>
                  <div>
                    <span className="font-bold">Objectifs atteints</span>
                    <p className="text-sm text-gray-600 mt-1 font-normal">
                      Vos réussites du jour
                    </p>
                  </div>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                  {[
                    { key: 'hit_calorie_target', label: 'Calories', icon: Target, color: 'blue' },
                    { key: 'hit_protein_target', label: 'Protéines', icon: TrendingUp, color: 'green' },
                    { key: 'hit_carbs_target', label: 'Glucides', icon: Target, color: 'yellow' },
                    { key: 'hit_fat_target', label: 'Lipides', icon: Target, color: 'purple' },
                    { key: 'hit_fiber_target', label: 'Fibres', icon: Target, color: 'green' },
                    { key: 'stayed_under_sodium_limit', label: 'Sodium', icon: CheckCircle, color: 'red' },
                    { key: 'stayed_under_sugar_limit', label: 'Sucre', icon: CheckCircle, color: 'pink' }
                  ].map(({ key, label, icon: Icon, color }, index) => {
                    const achieved = achievements[key]
                    if (achieved === undefined) return null
                    
                    return (
                      <div
                        key={key}
                        className={`flex items-center gap-3 p-3 rounded-lg transition-all duration-300 transform hover:scale-105 animate-in slide-in-from-bottom-4 ${
                          achieved 
                            ? `bg-green-100 text-green-800 border border-green-200 shadow-sm hover:shadow-md` 
                            : `bg-gray-100 text-gray-600 border border-gray-200`
                        }`}
                        style={{ animationDelay: `${index * 100}ms` }}
                      >
                        <div className={`p-2 rounded-full ${
                          achieved 
                            ? 'bg-green-200' 
                            : 'bg-gray-200'
                        }`}>
                          <Icon className={`h-4 w-4 ${
                            achieved 
                              ? 'text-green-700' 
                              : 'text-gray-500'
                          }`} />
                        </div>
                        <div className="flex-1">
                          <div className="font-medium text-sm">{label}</div>
                          <div className={`text-xs flex items-center gap-1 mt-1 ${
                            achieved ? 'font-semibold' : ''
                          }`}>
                            {achieved ? (
                              <>
                                <CheckCircle className="h-3 w-3" />
                                <span>Objectif atteint !</span>
                              </>
                            ) : (
                              <>
                                <div className="w-3 h-3 rounded-full border-2 border-gray-400"></div>
                                <span>Non atteint</span>
                              </>
                            )}
                          </div>
                        </div>
                        {achieved && (
                          <div className="text-green-600 animate-bounce">🎯</div>
                        )}
                      </div>
                    )
                  }).filter(Boolean)}
                </div>
                
                {/* Achievement summary */}
                <div className="mt-6 p-4 bg-white/70 rounded-lg backdrop-blur-sm">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Objectifs atteints aujourd'hui:</span>
                    <div className="flex items-center gap-2">
                      <span className="text-lg font-bold text-green-600">
                        {Object.values(achievements).filter(Boolean).length}
                      </span>
                      <span className="text-sm text-gray-500">
                        sur {Object.keys(achievements).length}
                      </span>
                      {Object.values(achievements).filter(Boolean).length === Object.keys(achievements).length && (
                        <div className="text-yellow-500 animate-spin">🌟</div>
                      )}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      )}
    </div>
  )
}

export default DailySummary