/**
 * Composant principal de suivi des repas (US1.8)
 * Affiche les repas du jour avec possibilité de les marquer comme consommés,
 * ajuster les portions, ignorer ou remplacer
 */

import React, { useEffect, useState } from 'react'
import { useMealTracking, useMealTrackingNetworkStatus } from '../hooks/useMealTracking'
import MealCard from './MealCard'
import NutritionComparison from './NutritionComparison'
import DailySummary from './DailySummary'
import QuickAddModal from './QuickAddModal'
import { Card, CardContent, CardHeader, CardTitle } from './ui/card'
import { Button } from './ui/button'
import { Badge } from './ui/badge'
import { Alert } from './ui/alert'
import { Progress } from './ui/progress'
import { Calendar, Plus, RefreshCw, Wifi, WifiOff, Sync, ChevronLeft, ChevronRight, BarChart3 } from 'lucide-react'

const MealTracker = ({ className = '' }) => {
  const {
    todayMealTrackings,
    dailySummary,
    isLoading,
    error,
    offlineMode,
    selectedDate,
    pendingActionsCount,
    loadTodayMealTrackings,
    loadDailySummary,
    changeSelectedDate,
    syncPendingActions,
    clearError,
    todayNutritionTotals,
    mealCompletionStats,
    mealsByType
  } = useMealTracking()
  
  const { offlineMode: networkOffline } = useMealTrackingNetworkStatus()
  
  const [showQuickAdd, setShowQuickAdd] = useState(false)
  const [selectedMealType, setSelectedMealType] = useState(null)
  const [showSummary, setShowSummary] = useState(false)
  
  // Charger les données au montage et quand la date change
  useEffect(() => {
    loadTodayMealTrackings()
    loadDailySummary()
  }, [selectedDate])
  
  // Auto-sync quand on revient online
  useEffect(() => {
    if (!networkOffline && pendingActionsCount > 0) {
      syncPendingActions()
    }
  }, [networkOffline, pendingActionsCount])
  
  // Handlers pour la navigation de dates
  const goToPreviousDay = () => {
    const currentDate = new Date(selectedDate)
    currentDate.setDate(currentDate.getDate() - 1)
    changeSelectedDate(currentDate.toISOString().split('T')[0])
  }
  
  const goToNextDay = () => {
    const currentDate = new Date(selectedDate)
    currentDate.setDate(currentDate.getDate() + 1)
    changeSelectedDate(currentDate.toISOString().split('T')[0])
  }
  
  const goToToday = () => {
    const today = new Date().toISOString().split('T')[0]
    changeSelectedDate(today)
  }
  
  const isToday = selectedDate === new Date().toISOString().split('T')[0]
  const isInFuture = new Date(selectedDate) > new Date()
  
  // Formatage de la date pour l'affichage
  const formatSelectedDate = () => {
    const date = new Date(selectedDate)
    const options = { 
      weekday: 'long', 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    }
    return date.toLocaleDateString('fr-FR', options)
  }
  
  const handleQuickAdd = (mealType) => {
    setSelectedMealType(mealType)
    setShowQuickAdd(true)
  }
  
  const handleRefresh = () => {
    loadTodayMealTrackings(true)
    loadDailySummary(true)
  }
  
  const handleSync = async () => {
    const syncedCount = await syncPendingActions()
    if (syncedCount > 0) {
      // Optionnel: afficher un message de succès
      console.log(`${syncedCount} actions synchronisées`)
    }
  }
  
  // Types de repas avec leurs labels
  const mealTypes = {
    repas1: 'Petit-déjeuner',
    repas2: 'Déjeuner',
    repas3: 'Dîner',
    collation: 'Collation'
  }
  
  return (
    <div className={`meal-tracker transition-all duration-300 ${className}`}>
      {/* Header avec navigation de dates */}
      <Card className="mb-6 shadow-lg border-0 bg-gradient-to-r from-white via-blue-50/30 to-purple-50/30">
        <CardHeader className="pb-4">
          {/* Mobile-first header layout */}
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div className="flex flex-col sm:flex-row items-start sm:items-center gap-2 sm:gap-4">
              <CardTitle className="text-xl sm:text-2xl font-bold flex items-center gap-2 text-gray-800">
                <Calendar className="h-5 w-5 sm:h-6 sm:w-6 text-blue-600" />
                Suivi des repas
              </CardTitle>
              
              {/* Indicateur de statut - mobile optimized */}
              <div className="flex items-center gap-2 flex-wrap">
                {offlineMode || networkOffline ? (
                  <Badge 
                    variant="secondary" 
                    className="flex items-center gap-1 bg-orange-100 text-orange-800 border-orange-200 animate-pulse"
                  >
                    <WifiOff className="h-3 w-3" />
                    <span className="hidden sm:inline">Hors ligne</span>
                  </Badge>
                ) : (
                  <Badge 
                    variant="outline" 
                    className="flex items-center gap-1 bg-green-50 text-green-700 border-green-200"
                  >
                    <Wifi className="h-3 w-3" />
                    <span className="hidden sm:inline">En ligne</span>
                  </Badge>
                )}
                
                {pendingActionsCount > 0 && (
                  <Badge 
                    variant="destructive" 
                    className="flex items-center gap-1 bg-red-100 text-red-800 animate-bounce"
                  >
                    <Sync className="h-3 w-3 animate-spin" />
                    <span className="sm:hidden">{pendingActionsCount}</span>
                    <span className="hidden sm:inline">{pendingActionsCount} en attente</span>
                  </Badge>
                )}
              </div>
            </div>
            
            {/* Action buttons - mobile optimized */}
            <div className="flex items-center gap-2 w-full sm:w-auto">
              {/* Synchronisation manuelle */}
              {pendingActionsCount > 0 && !offlineMode && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleSync}
                  disabled={isLoading}
                  className="flex items-center gap-1 transition-all duration-200 hover:bg-blue-50 hover:border-blue-300 flex-1 sm:flex-none"
                  aria-label="Synchroniser les actions en attente"
                >
                  <Sync className="h-4 w-4" />
                  <span className="hidden sm:inline">Synchroniser</span>
                </Button>
              )}
              
              {/* Rafraîchir */}
              <Button
                variant="outline"
                size="sm"
                onClick={handleRefresh}
                disabled={isLoading}
                className="flex items-center gap-1 transition-all duration-200 hover:bg-green-50 hover:border-green-300 flex-1 sm:flex-none"
                aria-label="Actualiser les données"
              >
                <RefreshCw className={`h-4 w-4 transition-transform duration-500 ${isLoading ? 'animate-spin' : ''}`} />
                <span className="hidden sm:inline">Actualiser</span>
              </Button>
              
              {/* Voir résumé */}
              <Button
                variant={showSummary ? "default" : "outline"}
                size="sm"
                onClick={() => setShowSummary(!showSummary)}
                className={`flex items-center gap-1 transition-all duration-200 flex-1 sm:flex-none ${
                  showSummary 
                    ? 'bg-blue-600 hover:bg-blue-700 text-white shadow-md' 
                    : 'hover:bg-blue-50 hover:border-blue-300'
                }`}
                aria-label={showSummary ? "Masquer le résumé" : "Afficher le résumé"}
              >
                <BarChart3 className="h-4 w-4" />
                <span className="hidden sm:inline">Résumé</span>
              </Button>
            </div>
          </div>
          
          {/* Navigation de dates - Enhanced mobile-first */}
          <div className="flex flex-col sm:flex-row items-center justify-between mt-6 gap-4">
            <div className="flex items-center gap-3 w-full sm:w-auto">
              <Button
                variant="outline"
                size="sm"
                onClick={goToPreviousDay}
                className="p-3 rounded-full hover:bg-blue-50 hover:border-blue-300 transition-all duration-200 shadow-sm"
                aria-label="Jour précédent"
              >
                <ChevronLeft className="h-4 w-4" />
              </Button>
              
              <div className="text-center flex-1 sm:min-w-[280px] bg-white/60 rounded-lg p-3 backdrop-blur-sm">
                <h3 className="font-semibold text-lg text-gray-800 mb-1">
                  {formatSelectedDate()}
                </h3>
                <div className="flex justify-center gap-2">
                  {isToday && (
                    <Badge className="bg-blue-100 text-blue-800 border-blue-200 shadow-sm animate-pulse">
                      Aujourd'hui
                    </Badge>
                  )}
                  {isInFuture && (
                    <Badge variant="outline" className="bg-purple-50 text-purple-700 border-purple-200">
                      À venir
                    </Badge>
                  )}
                </div>
              </div>
              
              <Button
                variant="outline"
                size="sm"
                onClick={goToNextDay}
                className="p-3 rounded-full hover:bg-blue-50 hover:border-blue-300 transition-all duration-200 shadow-sm"
                aria-label="Jour suivant"
              >
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
            
            {!isToday && (
              <Button
                variant="outline"
                size="sm"
                onClick={goToToday}
                className="flex items-center gap-2 px-4 py-2 hover:bg-blue-50 hover:border-blue-300 transition-all duration-200 shadow-sm w-full sm:w-auto justify-center"
                aria-label="Revenir à aujourd'hui"
              >
                <Calendar className="h-4 w-4" />
                <span>Aujourd'hui</span>
              </Button>
            )}
          </div>
          
          {/* Barre de progression quotidienne - Enhanced */}
          <div className="mt-6 bg-white/70 rounded-lg p-4 backdrop-blur-sm">
            <div className="flex justify-between items-center mb-3">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
                <span className="text-sm font-semibold text-gray-700">
                  Progression des repas
                </span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-sm font-mono bg-blue-100 text-blue-800 px-2 py-1 rounded">
                  {mealCompletionStats.consumed}/{mealCompletionStats.total}
                </span>
                <span className="text-xs text-gray-500">repas</span>
              </div>
            </div>
            <div className="space-y-2">
              <Progress 
                value={mealCompletionStats.percentage} 
                className="h-3 shadow-inner"
              />
              <div className="flex justify-between text-xs text-gray-600">
                <span>0%</span>
                <span className="font-semibold text-blue-600">
                  {Math.round(mealCompletionStats.percentage)}%
                </span>
                <span>100%</span>
              </div>
              {mealCompletionStats.percentage === 100 && (
                <div className="text-center">
                  <span className="text-green-600 text-sm font-semibold animate-bounce">
                    🎉 Tous les repas terminés !
                  </span>
                </div>
              )}
            </div>
          </div>
        </CardHeader>
      </Card>
      
      {/* Messages d'erreur - Enhanced */}
      {error && (
        <Alert 
          className="mb-6 border-red-200 bg-red-50 animate-in slide-in-from-top-2 duration-300" 
          variant="destructive"
        >
          <div className="flex justify-between items-start gap-3">
            <div className="flex-1">
              <p className="text-red-800 font-medium">Une erreur est survenue</p>
              <p className="text-red-700 text-sm mt-1">{error}</p>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={clearError}
              className="text-red-600 hover:text-red-800 hover:bg-red-100 transition-colors duration-200"
              aria-label="Fermer le message d'erreur"
            >
              ✕
            </Button>
          </div>
        </Alert>
      )}
      
      {/* Résumé quotidien - Enhanced */}
      {showSummary && (
        <div className="mb-6 animate-in slide-in-from-top-4 duration-300">
          <DailySummary 
            summary={dailySummary}
            nutritionTotals={todayNutritionTotals}
            completionStats={mealCompletionStats}
          />
        </div>
      )}
      
      {/* Comparaison nutritionnelle - Enhanced */}
      <div className="mb-6 animate-in slide-in-from-left-4 duration-300">
        <NutritionComparison
          actualNutrition={todayNutritionTotals}
          targetNutrition={dailySummary?.target_nutrition}
          plannedNutrition={dailySummary?.planned_nutrition}
        />
      </div>
      
      {/* Liste des repas - Enhanced mobile-first */}
      <div className="space-y-6">
        {Object.entries(mealTypes).map(([mealType, label], index) => {
          const mealTracking = mealsByType[mealType]
          
          return (
            <div 
              key={mealType} 
              className={`animate-in slide-in-from-bottom-4 duration-300`}
              style={{ animationDelay: `${index * 100}ms` }}
            >
              <div className="flex items-center justify-between mb-3 px-1">
                <div className="flex items-center gap-3">
                  <div className="w-1 h-6 bg-gradient-to-b from-blue-400 to-purple-500 rounded-full"></div>
                  <h3 className="font-semibold text-lg text-gray-800">{label}</h3>
                  {mealTracking?.status && (
                    <div className="ml-auto sm:ml-0">
                      {mealTracking.status === 'consumed' && (
                        <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                      )}
                      {mealTracking.status === 'skipped' && (
                        <div className="w-2 h-2 bg-red-500 rounded-full"></div>
                      )}
                      {mealTracking.status === 'planned' && (
                        <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
                      )}
                    </div>
                  )}
                </div>
                {!mealTracking && !isInFuture && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleQuickAdd(mealType)}
                    className="flex items-center gap-1 hover:bg-blue-50 hover:border-blue-300 transition-all duration-200 shadow-sm"
                    aria-label={`Ajouter ${label.toLowerCase()}`}
                  >
                    <Plus className="h-4 w-4" />
                    <span className="hidden sm:inline">Ajouter</span>
                  </Button>
                )}
              </div>
              
              {mealTracking ? (
                <MealCard
                  mealTracking={mealTracking}
                  onStatusChange={loadTodayMealTrackings}
                  disabled={isInFuture}
                />
              ) : (
                <Card className="border-dashed border-2 border-gray-200 hover:border-blue-300 transition-colors duration-200 bg-gray-50/30">
                  <CardContent className="flex items-center justify-center py-8">
                    <div className="text-center">
                      <div className="w-12 h-12 rounded-full bg-gray-100 flex items-center justify-center mx-auto mb-3">
                        <Plus className="h-6 w-6 text-gray-400" />
                      </div>
                      <p className="text-gray-600 mb-3 font-medium">
                        Aucun {label.toLowerCase()} planifié
                      </p>
                      <p className="text-gray-500 text-sm mb-4">
                        Ajoutez un repas pour commencer le suivi
                      </p>
                      {!isInFuture && (
                        <Button
                          variant="outline"
                          onClick={() => handleQuickAdd(mealType)}
                          className="flex items-center gap-2 hover:bg-blue-50 hover:border-blue-300 transition-all duration-200 shadow-sm"
                        >
                          <Plus className="h-4 w-4" />
                          <span>Ajouter un {label.toLowerCase()}</span>
                        </Button>
                      )}
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          )
        })}
      </div>
      
      {/* État de chargement - Enhanced */}
      {isLoading && todayMealTrackings.length === 0 && (
        <Card className="shadow-lg border-0 bg-gradient-to-br from-blue-50 to-indigo-50">
          <CardContent className="flex items-center justify-center py-12">
            <div className="text-center">
              <div className="relative mb-4">
                <div className="w-16 h-16 rounded-full bg-blue-100 flex items-center justify-center mx-auto">
                  <RefreshCw className="h-8 w-8 animate-spin text-blue-600" />
                </div>
                <div className="absolute inset-0 rounded-full border-2 border-blue-200 animate-ping"></div>
              </div>
              <p className="text-gray-700 font-medium mb-2">Chargement des repas...</p>
              <p className="text-gray-500 text-sm">Récupération de vos données nutritionnelles</p>
            </div>
          </CardContent>
        </Card>
      )}
      
      {/* État vide - Enhanced */}
      {!isLoading && todayMealTrackings.length === 0 && !error && (
        <Card className="shadow-lg border-0 bg-gradient-to-br from-gray-50 to-blue-50">
          <CardContent className="flex items-center justify-center py-16">
            <div className="text-center max-w-md">
              <div className="relative mb-6">
                <div className="w-20 h-20 rounded-full bg-gray-100 flex items-center justify-center mx-auto">
                  <Calendar className="h-10 w-10 text-gray-400" />
                </div>
                <div className="absolute -top-1 -right-1 w-6 h-6 rounded-full bg-blue-100 flex items-center justify-center">
                  <Plus className="h-4 w-4 text-blue-600" />
                </div>
              </div>
              <h3 className="font-bold text-xl mb-3 text-gray-800">
                Aucun repas pour cette date
              </h3>
              <p className="text-gray-600 mb-6 leading-relaxed">
                {isInFuture 
                  ? "Les repas futurs ne sont pas encore disponibles. Revenez à une date antérieure pour voir vos plans."
                  : "Aucun plan de repas trouvé pour cette date. Commencez par ajouter votre premier repas !"
                }
              </p>
              {!isInFuture && (
                <div className="space-y-3">
                  <Button
                    onClick={() => setShowQuickAdd(true)}
                    className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white shadow-md hover:shadow-lg transition-all duration-200 px-6 py-3"
                    size="lg"
                  >
                    <Plus className="h-5 w-5" />
                    <span>Ajouter un repas</span>
                  </Button>
                  <p className="text-gray-500 text-sm">
                    Vous pouvez ajouter des repas personnalisés ou rechercher dans notre base de recettes
                  </p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}
      
      {/* Modal d'ajout rapide */}
      <QuickAddModal
        isOpen={showQuickAdd}
        onClose={() => {
          setShowQuickAdd(false)
          setSelectedMealType(null)
        }}
        mealType={selectedMealType}
        selectedDate={selectedDate}
        onMealAdded={() => {
          loadTodayMealTrackings(true)
          setShowQuickAdd(false)
          setSelectedMealType(null)
        }}
      />
    </div>
  )
}

export default MealTracker