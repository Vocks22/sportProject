import React from 'react'
import { useState, useEffect } from 'react'
import { 
  ChevronLeft, 
  ChevronRight, 
  Plus, 
  Shuffle,
  Calendar as CalendarIcon,
  AlertCircle,
  Clock,
  CheckCircle
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from './ui/card'
import { Button } from './ui/button'
import { Badge } from './ui/badge'
import { useMealPlanningWeek } from '../hooks/useISOWeek'
import MealTracker from './MealTracker'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000'

export function MealPlanning() {
  const {
    weekInfo,
    weekDays,
    planningMetrics,
    goToPreviousWeek,
    goToNextWeek,
    goToCurrentWeek,
    isWeekType
  } = useMealPlanningWeek()
  
  // État pour basculer entre Planning et Suivi
  const [activeView, setActiveView] = useState('planning') // 'planning' ou 'tracking'
  
  // État pour stocker les repas consommés (jour-repas : boolean)
  const [consumedMeals, setConsumedMeals] = useState({})
  const [todayMeals, setTodayMeals] = useState([])
  
  // Charger les données depuis l'API au montage
  useEffect(() => {
    fetchTodayMeals()
    
    // Écouter les changements depuis le Dashboard
    const handleMealStatusChange = (event) => {
      console.log('Planning: Événement reçu depuis Dashboard', event.detail)
      fetchTodayMeals()
    }
    window.addEventListener('mealStatusChanged', handleMealStatusChange)
    
    // Écouter le focus de la fenêtre pour rafraîchir
    const handleFocus = () => {
      console.log('Planning: Fenêtre en focus, rafraîchissement...')
      fetchTodayMeals()
    }
    window.addEventListener('focus', handleFocus)
    
    // Rafraîchir toutes les 5 minutes (300 secondes)
    const interval = setInterval(() => {
      fetchTodayMeals()
    }, 5 * 60 * 1000)
    
    return () => {
      clearInterval(interval)
      window.removeEventListener('mealStatusChanged', handleMealStatusChange)
      window.removeEventListener('focus', handleFocus)
    }
  }, [])
  
  // Recharger les repas depuis l'API à chaque changement de semaine
  useEffect(() => {
    const fetchWeekMeals = async () => {
      try {
        const apiUrl = API_URL.includes('/api') ? API_URL : `${API_URL}/api`
        const response = await fetch(`${apiUrl}/diet/week/${weekInfo.weekNumber}/${weekInfo.year}`)
        const data = await response.json()
        
        if (data.success && data.meals) {
          const weekMeals = {}
          
          // Convertir les données de l'API au format attendu
          Object.keys(data.meals).forEach(day => {
            Object.keys(data.meals[day]).forEach(mealType => {
              const key = `${day}-${mealType}`
              // data.meals[day][mealType] contient le statut boolean (completed)
              weekMeals[key] = data.meals[day][mealType]
            })
          })
          
          console.log('Planning: Données reçues de l\'API pour la semaine:', data.meals)
          console.log('Planning: État consumedMeals qui sera appliqué:', weekMeals)
          
          // Si on est sur la semaine courante, fusionner avec les données d'aujourd'hui
          if (weekInfo.isCurrentWeek) {
            fetchTodayMeals() // Rafraîchir les données d'aujourd'hui
          }
          
          setConsumedMeals(prevState => {
            // Pour toutes les semaines, fusionner les données de l'API avec l'état existant
            // en gardant priorité aux données les plus récentes d'aujourd'hui si on est sur la semaine courante
            if (weekInfo.isCurrentWeek) {
              const today = new Date().toLocaleDateString('en-US', { weekday: 'long' }).toLowerCase()
              const todayMealsFromState = {}
              
              // Garder les repas d'aujourd'hui de l'état actuel
              Object.keys(prevState).forEach(key => {
                if (key.startsWith(today + '-')) {
                  todayMealsFromState[key] = prevState[key]
                }
              })
              
              // Fusionner : d'abord les données de l'API, puis écraser avec les données d'aujourd'hui
              return {
                ...weekMeals,
                ...todayMealsFromState
              }
            }
            
            // Pour les autres semaines, utiliser les données de l'API
            return weekMeals
          })
        }
      } catch (err) {
        console.error('Erreur chargement semaine:', err)
      }
    }
    
    fetchWeekMeals()
    console.log(`Planning: Chargement des repas de la semaine ${weekInfo.weekNumber} depuis l'API`)
  }, [weekInfo.weekNumber, weekInfo.year]) // Se déclenche à chaque changement de semaine
  
  const fetchTodayMeals = async () => {
    try {
      const apiUrl = API_URL.includes('/api') ? API_URL : `${API_URL}/api`
      const response = await fetch(`${apiUrl}/diet/today`)
      const data = await response.json()
      
      if (data.success && data.meals) {
        const today = new Date().toLocaleDateString('en-US', { weekday: 'long' }).toLowerCase()
        
        // Préserver l'état existant des repas qui ne sont pas d'aujourd'hui
        setConsumedMeals(prevState => {
          const newState = { ...prevState }
          
          // Mettre à jour uniquement les repas d'aujourd'hui
          data.meals.forEach((meal) => {
            const mealTypeMap = {
              'repas1': 'repas1',
              'collation1': 'collation1',
              'repas2': 'repas2',
              'collation2': 'collation2',
              'repas3': 'repas3'
            }
            
            const mealTypeKey = mealTypeMap[meal.meal_type]
            if (mealTypeKey) {
              newState[`${today}-${mealTypeKey}`] = meal.completed
            }
          })
          
          return newState
        })
        
        setTodayMeals(data.meals)
      }
    } catch (err) {
      console.error('Erreur chargement repas:', err)
    }
  }
  
  // Données simulées du planning
  const weekPlan = {
    monday: {
      repas1: { id: 1, name: "Omelette aux blancs d'œufs", calories: 351, image: "🍳" },
      collation1: { id: 2, name: "Smoothie protéiné", calories: 300, image: "🥤" },
      repas2: { id: 3, name: "Poulet grillé aux brocolis", calories: 310, image: "🍗" },
      collation2: { id: 4, name: "Blancs d'œufs aux amandes", calories: 301, image: "🥜" },
      repas3: { id: 5, name: "Cabillaud en papillote", calories: 270, image: "🐟" }
    },
    tuesday: {
      repas1: { id: 1, name: "Omelette aux blancs d'œufs", calories: 351, image: "🍳" },
      collation1: { id: 2, name: "Smoothie protéiné", calories: 300, image: "🥤" },
      repas2: { id: 6, name: "Dinde sautée aux épinards", calories: 295, image: "🦃" },
      collation2: { id: 4, name: "Blancs d'œufs aux amandes", calories: 301, image: "🥜" },
      repas3: { id: 7, name: "Sole grillée à la salade", calories: 250, image: "🐟" }
    },
    wednesday: {
      repas1: { id: 1, name: "Omelette aux blancs d'œufs", calories: 351, image: "🍳" },
      collation1: { id: 2, name: "Smoothie protéiné", calories: 300, image: "🥤" },
      repas2: { id: 3, name: "Poulet grillé aux brocolis", calories: 310, image: "🍗" },
      collation2: { id: 4, name: "Blancs d'œufs aux amandes", calories: 301, image: "🥜" },
      repas3: { id: 5, name: "Cabillaud en papillote", calories: 270, image: "🐟" }
    },
    thursday: {
      repas1: { id: 1, name: "Omelette aux blancs d'œufs", calories: 351, image: "🍳" },
      collation1: { id: 2, name: "Smoothie protéiné", calories: 300, image: "🥤" },
      repas2: { id: 6, name: "Dinde sautée aux épinards", calories: 295, image: "🦃" },
      collation2: { id: 4, name: "Blancs d'œufs aux amandes", calories: 301, image: "🥜" },
      repas3: { id: 7, name: "Sole grillée à la salade", calories: 250, image: "🐟" }
    },
    friday: {
      repas1: { id: 1, name: "Omelette aux blancs d'œufs", calories: 351, image: "🍳" },
      collation1: { id: 2, name: "Smoothie protéiné", calories: 300, image: "🥤" },
      repas2: { id: 3, name: "Poulet grillé aux brocolis", calories: 310, image: "🍗" },
      collation2: { id: 4, name: "Blancs d'œufs aux amandes", calories: 301, image: "🥜" },
      repas3: { id: 5, name: "Cabillaud en papillote", calories: 270, image: "🐟" }
    },
    saturday: {
      repas1: { id: 1, name: "Omelette aux blancs d'œufs", calories: 351, image: "🍳" },
      collation1: { id: 2, name: "Smoothie protéiné", calories: 300, image: "🥤" },
      repas2: { id: 6, name: "Dinde sautée aux épinards", calories: 295, image: "🦃" },
      collation2: { id: 4, name: "Blancs d'œufs aux amandes", calories: 301, image: "🥜" },
      repas3: { id: 7, name: "Sole grillée à la salade", calories: 250, image: "🐟" }
    },
    sunday: {
      repas1: { id: 1, name: "Omelette aux blancs d'œufs", calories: 351, image: "🍳" },
      collation1: { id: 2, name: "Smoothie protéiné", calories: 300, image: "🥤" },
      repas2: { id: 3, name: "Poulet grillé aux brocolis", calories: 310, image: "🍗" },
      collation2: { id: 4, name: "Blancs d'œufs aux amandes", calories: 301, image: "🥜" },
      repas3: { id: 5, name: "Cabillaud en papillote", calories: 270, image: "🐟" }
    }
  }

  // Les jours sont maintenant fournis par le hook useISOWeek
  // et respectent automatiquement la norme ISO 8601 (lundi-dimanche)

  const mealTypes = [
    { key: 'repas1', label: 'Repas 1', color: 'bg-orange-100 text-orange-800' },
    { key: 'collation1', label: 'Collation', color: 'bg-blue-100 text-blue-800' },
    { key: 'repas2', label: 'Repas 2', color: 'bg-green-100 text-green-800' },
    { key: 'collation2', label: 'Collation', color: 'bg-blue-100 text-blue-800' },
    { key: 'repas3', label: 'Repas 3', color: 'bg-purple-100 text-purple-800' }
  ]

  const calculateDayTotal = (dayMeals) => {
    return Object.values(dayMeals).reduce((total, meal) => total + (meal?.calories || 0), 0)
  }

  const calculateWeekAverage = () => {
    const dailyTotals = Object.values(weekPlan).map(calculateDayTotal)
    return Math.round(dailyTotals.reduce((sum, total) => sum + total, 0) / dailyTotals.length)
  }
  
  // Fonction pour marquer un repas comme consommé ou non
  const toggleMealConsumed = async (dayKey, mealTypeKey) => {
    // Vérifier si c'est dans le passé, présent ou futur
    const today = new Date()
    const todayWeekday = today.toLocaleDateString('en-US', { weekday: 'long' }).toLowerCase()
    
    // Si on est sur une semaine future
    if (weekInfo.isFutureWeek) {
      alert("Vous ne pouvez pas cocher les repas des semaines futures")
      return
    }
    
    // Si on est sur la semaine courante
    if (weekInfo.isCurrentWeek) {
      // Obtenir l'index du jour actuel (0 = lundi, 6 = dimanche)
      const weekDaysOrder = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
      const todayIndex = weekDaysOrder.indexOf(todayWeekday)
      const selectedDayIndex = weekDaysOrder.indexOf(dayKey)
      
      // Si le jour sélectionné est après aujourd'hui dans la semaine courante
      if (selectedDayIndex > todayIndex) {
        alert("Vous ne pouvez pas cocher les repas futurs")
        return
      }
    }
    // Si on est sur une semaine passée, tout est permis
    
    const key = `${dayKey}-${mealTypeKey}`
    const newStatus = !consumedMeals[key]
    
    // Pour les jours passés, on doit créer/mettre à jour différemment
    // On utilise une approche simplifiée pour le moment
    if (dayKey === todayWeekday) {
      // Pour aujourd'hui, utiliser la logique existante
      const meal = todayMeals.find(m => m.meal_type === mealTypeKey)
      if (!meal) {
        console.error('Repas non trouvé:', mealTypeKey)
        return
      }
      
      try {
        const apiUrl = API_URL.includes('/api') ? API_URL : `${API_URL}/api`
        const response = await fetch(`${apiUrl}/diet/validate`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ 
            meal_id: meal.id, 
            completed: newStatus 
          })
        })
      
        const data = await response.json()
        if (data.success) {
          // Mettre à jour l'état local
          setConsumedMeals({
            ...consumedMeals,
            [key]: newStatus
          })
          
          // Déclencher un événement pour synchroniser avec Dashboard
          console.log('Planning: Émission événement mealStatusChanged', { mealId: meal.id, completed: newStatus })
          window.dispatchEvent(new CustomEvent('mealStatusChanged', { 
            detail: { mealId: meal.id, completed: newStatus } 
          }))
        }
      } catch (err) {
        console.error('Erreur validation:', err)
        alert('Erreur lors de la sauvegarde')
      }
    } else {
      // Pour les jours passés, on doit calculer la date et utiliser l'API
      try {
        // Utiliser les dates exactes fournies par weekDays qui contient les bonnes dates
        const selectedDay = weekDays.find(d => d.key === dayKey)
        if (!selectedDay || !selectedDay.dateISO) {
          console.error('Impossible de trouver la date pour', dayKey)
          return
        }
        
        // Utiliser directement la date ISO qui est au format YYYY-MM-DD
        const targetDateStr = selectedDay.dateISO
        
        // Trouver le meal_id en utilisant le meal_type
        // On suppose que les repas ont toujours les mêmes IDs (1-5)
        const mealTypeToId = {
          'repas1': 1,
          'collation1': 2,
          'repas2': 3,
          'collation2': 4,
          'repas3': 5
        }
        const mealId = mealTypeToId[mealTypeKey]
        
        if (!mealId) {
          console.error('Type de repas non reconnu:', mealTypeKey)
          return
        }
        
        const apiUrl = API_URL.includes('/api') ? API_URL : `${API_URL}/api`
        console.log(`Planning: Envoi validation pour repas passé - Date: ${targetDateStr}, Meal ID: ${mealId}, Status: ${newStatus}`)
        
        const response = await fetch(`${apiUrl}/diet/validate`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ 
            meal_id: mealId,
            completed: newStatus,
            date: targetDateStr // Format YYYY-MM-DD
          })
        })
        
        const data = await response.json()
        console.log('Planning: Réponse API validation:', data)
        
        if (data.success) {
          // Mettre à jour l'état local
          setConsumedMeals({
            ...consumedMeals,
            [key]: newStatus
          })
          
          console.log(`Planning: Repas passé ${targetDateStr} - ${dayKey} - ${mealTypeKey} sauvé avec succès`)
        }
      } catch (err) {
        console.error('Erreur sauvegarde repas passé:', err)
        alert('Erreur lors de la sauvegarde')
      }
    }
  }
  
  // Calculer les calories réellement consommées pour un jour
  const calculateConsumedDayTotal = (dayKey, dayMeals) => {
    let total = 0
    Object.entries(dayMeals).forEach(([mealTypeKey, meal]) => {
      const key = `${dayKey}-${mealTypeKey}`
      if (consumedMeals[key] && meal?.calories) {
        total += meal.calories
      }
    })
    return total
  }

  return (
    <div className="space-y-6">
      {/* Header avec boutons de bascule */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">
            {activeView === 'planning' ? 'Planification des Repas' : 'Suivi des Repas Consommés'}
          </h1>
          <p className="text-gray-600 text-sm sm:text-base">
            {activeView === 'planning' 
              ? planningMetrics.planningRecommendation 
              : 'Cochez les repas consommés et ajustez les portions'}
          </p>
          
          {weekInfo.isPastWeek && (
            <div className="flex items-center space-x-2 mt-2">
              <AlertCircle className="h-4 w-4 text-amber-600" />
              <span className="text-sm text-amber-700">
                Cette semaine est passée. Les modifications ne sont pas recommandées.
              </span>
            </div>
          )}
        </div>
        <div className="flex flex-wrap items-center gap-2">
          {/* Boutons de bascule entre Planning et Suivi */}
          <div className="flex items-center bg-gray-100 rounded-lg p-1">
            <Button
              size="sm"
              variant={activeView === 'planning' ? 'default' : 'ghost'}
              onClick={() => setActiveView('planning')}
              className="mr-1"
            >
              <CalendarIcon className="h-4 w-4 mr-2" />
              Planning
            </Button>
            <Button
              size="sm"
              variant={activeView === 'tracking' ? 'default' : 'ghost'}
              onClick={() => setActiveView('tracking')}
            >
              <CheckCircle className="h-4 w-4 mr-2" />
              Suivi Repas
            </Button>
          </div>
          
          {activeView === 'planning' && (
            <>
              {!isWeekType('current') && (
                <Button 
                  variant="outline" 
                  size="sm"
                  onClick={goToCurrentWeek}
                >
                  <Clock className="h-4 w-4 mr-2" />
                  Semaine courante
                </Button>
              )}
              <Button 
                variant="outline" 
                size="sm"
                disabled={!planningMetrics.canPlanMeals}
                title={planningMetrics.planningRecommendation}
              >
                <Shuffle className="h-4 w-4 mr-2" />
                Générer Plan Auto
              </Button>
              <Button 
                size="sm"
                disabled={!planningMetrics.canPlanMeals}
              >
                <Plus className="h-4 w-4 mr-2" />
                Nouvelle Recette
              </Button>
            </>
          )}
        </div>
      </div>

      {/* Affichage conditionnel Planning ou Tracking */}
      {activeView === 'tracking' ? (
        /* Composant de Suivi des Repas */
        <MealTracker />
      ) : (
        /* Vue Planning existante */
        <>
      {/* Week Navigation */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Button 
                variant="outline" 
                size="sm"
                onClick={goToPreviousWeek}
                title="Semaine précédente"
              >
                <ChevronLeft className="h-4 w-4" />
              </Button>
              <div className="flex items-center space-x-2">
                <CalendarIcon className="h-5 w-5 text-gray-500" />
                <span className="text-lg font-semibold">{weekInfo.displayRange}</span>
              </div>
              <Button 
                variant="outline" 
                size="sm"
                onClick={goToNextWeek}
                title="Semaine suivante"
              >
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
            <div className="flex items-center space-x-2">
              {/* Indicateurs de statut de la semaine */}
              {weekInfo.isCurrentWeek && (
                <Badge variant="default" className="flex items-center space-x-1">
                  <Clock className="h-3 w-3" />
                  <span>Semaine courante</span>
                </Badge>
              )}
              {weekInfo.isNextWeek && (
                <Badge variant="secondary" className="flex items-center space-x-1">
                  <CalendarIcon className="h-3 w-3" />
                  <span>Semaine prochaine</span>
                </Badge>
              )}
              {weekInfo.isPastWeek && (
                <Badge variant="outline" className="flex items-center space-x-1">
                  <span>Semaine passée</span>
                </Badge>
              )}
              <Badge variant="outline">
                Moyenne: {calculateWeekAverage()} kcal/jour
              </Badge>
            </div>
          </div>
        </CardHeader>
      </Card>

      {/* Meal Planning Grid */}
      <Card>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left p-4 font-medium text-gray-700 w-32">Repas</th>
                  {weekDays.map((day) => (
                    <th key={day.key} className="text-center p-4 font-medium text-gray-700 min-w-[140px]">
                      <div className={`${day.isToday ? 'font-bold text-blue-600' : ''}`}>
                        {day.label}
                      </div>
                      <div className={`text-sm ${day.isToday ? 'text-blue-500 font-medium' : 'text-gray-500'}`}>
                        {day.dayNumber}
                      </div>
                      {day.isToday && (
                        <div className="text-xs text-blue-600 font-medium">Aujourd'hui</div>
                      )}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {mealTypes.map((mealType) => (
                  <tr key={mealType.key} className="border-b hover:bg-gray-50">
                    <td className="p-4">
                      <Badge className={mealType.color}>
                        {mealType.label}
                      </Badge>
                    </td>
                    {weekDays.map((day) => {
                      const meal = weekPlan[day.key][mealType.key]
                      const isToday = day.isToday
                      const isWeekend = day.isWeekend
                      
                      // Déterminer si c'est passé, présent ou futur
                      let isPast = false
                      let isFuture = false
                      
                      if (weekInfo.isPastWeek) {
                        // Toute la semaine passée est dans le passé
                        isPast = true
                      } else if (weekInfo.isFutureWeek) {
                        // Toute la semaine future est dans le futur
                        isFuture = true
                      } else if (weekInfo.isCurrentWeek) {
                        // Pour la semaine courante, vérifier jour par jour
                        const weekDaysOrder = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
                        const todayWeekday = new Date().toLocaleDateString('en-US', { weekday: 'long' }).toLowerCase()
                        const todayIndex = weekDaysOrder.indexOf(todayWeekday)
                        const dayIndex = weekDaysOrder.indexOf(day.key)
                        isPast = dayIndex < todayIndex
                        isFuture = dayIndex > todayIndex
                      }
                      
                      const isConsumed = consumedMeals[`${day.key}-${mealType.key}`]
                      
                      return (
                        <td key={`${day.key}-${mealType.key}`} className={`p-2 ${isWeekend ? 'bg-gray-50' : ''} ${isPast ? 'bg-gray-50/50' : ''}`}>
                          {meal ? (
                            <div 
                              onClick={() => !isFuture && toggleMealConsumed(day.key, mealType.key)}
                              className={`bg-white border-2 rounded-lg p-3 transition-all ${
                                isFuture ? 'opacity-50 cursor-not-allowed' : 'hover:shadow-md cursor-pointer'
                              } ${
                                isToday ? 'border-blue-300 ring-1 ring-blue-200' : 'border-gray-200'
                              } ${isConsumed ? 'bg-green-100 border-green-400 shadow-md' : 'hover:border-gray-400'} ${
                                isPast && !isConsumed ? 'bg-orange-50 border-orange-200' : ''
                              }`}
                              title={
                                isFuture ? "Les repas futurs ne peuvent pas être cochés" :
                                isConsumed ? "Cliquez pour marquer comme non mangé" : 
                                isPast ? "Cliquez pour rattraper ce repas passé" :
                                "Cliquez pour marquer comme mangé"
                              }
                            >
                              <div className="text-center relative">
                                {/* Indicateur visuel de validation */}
                                {isConsumed && (
                                  <div className="absolute -top-2 -right-2 bg-green-500 rounded-full p-1">
                                    <CheckCircle className="h-4 w-4 text-white" />
                                  </div>
                                )}
                                <div className="text-2xl mb-1">{meal.image}</div>
                                <div className={`text-xs font-medium leading-tight ${
                                  isConsumed ? 'text-green-800 font-bold' : 'text-gray-900'
                                }`}>
                                  {meal.name.length > 20 ? meal.name.substring(0, 20) + '...' : meal.name}
                                </div>
                                <div className={`text-xs mt-1 ${
                                  isConsumed ? 'text-green-600 font-bold' : 'text-gray-500'
                                }`}>
                                  {meal.calories} kcal
                                  {isConsumed && ' ✓'}
                                </div>
                              </div>
                            </div>
                          ) : (
                            <div className={`border-2 border-dashed rounded-lg p-3 h-20 flex items-center justify-center hover:border-gray-400 transition-colors cursor-pointer ${
                              isToday ? 'bg-blue-50 border-blue-300' : 
                              isWeekend ? 'bg-gray-100 border-gray-300' : 'bg-gray-50 border-gray-300'
                            }`}>
                              <Plus className={`h-4 w-4 ${isToday ? 'text-blue-400' : 'text-gray-400'}`} />
                            </div>
                          )}
                        </td>
                      )
                    })}
                  </tr>
                ))}
                {/* Daily Totals Row */}
                <tr className="bg-gray-50 font-medium">
                  <td className="p-4 text-gray-700">Total</td>
                  {weekDays.map((day) => (
                    <td key={`${day.key}-total`} className={`p-4 text-center ${day.isWeekend ? 'bg-gray-100' : ''}`}>
                      <div className={`text-sm font-bold ${
                        day.isToday ? 'text-blue-600' : 'text-gray-900'
                      }`}>
                        {calculateDayTotal(weekPlan[day.key])} kcal
                      </div>
                    </td>
                  ))}
                </tr>
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Nutrition Summary */}
      <Card>
        <CardHeader>
          <CardTitle>Résumé Nutritionnel</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-900">{calculateWeekAverage()}</div>
              <div className="text-sm text-gray-500">Calories/jour</div>
              <div className="mt-2 h-2 bg-gray-200 rounded-full">
                <div 
                  className="h-2 bg-green-500 rounded-full" 
                  style={{ width: `${(calculateWeekAverage() / 1500) * 100}%` }}
                />
              </div>
              <div className="text-xs text-gray-500 mt-1">101% de l'objectif</div>
            </div>
            
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-900">145g</div>
              <div className="text-sm text-gray-500">Protéines/jour</div>
              <div className="mt-2 h-2 bg-gray-200 rounded-full">
                <div className="h-2 bg-purple-500 rounded-full" style={{ width: '97%' }} />
              </div>
              <div className="text-xs text-gray-500 mt-1">97% de l'objectif</div>
            </div>
            
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-900">85g</div>
              <div className="text-sm text-gray-500">Glucides/jour</div>
              <div className="mt-2 h-2 bg-gray-200 rounded-full">
                <div className="h-2 bg-orange-500 rounded-full" style={{ width: '85%' }} />
              </div>
              <div className="text-xs text-gray-500 mt-1">85% de l'objectif</div>
            </div>
            
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-900">75g</div>
              <div className="text-sm text-gray-500">Lipides/jour</div>
              <div className="mt-2 h-2 bg-gray-200 rounded-full">
                <div className="h-2 bg-red-500 rounded-full" style={{ width: '94%' }} />
              </div>
              <div className="text-xs text-gray-500 mt-1">94% de l'objectif</div>
            </div>
          </div>
        </CardContent>
      </Card>
        </>
      )}
    </div>
  )
}

