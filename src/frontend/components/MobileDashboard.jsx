import { useState } from 'react'
import { 
  CheckCircle2, 
  Circle, 
  Utensils, 
  Droplets, 
  Dumbbell,
  Calendar,
  ShoppingCart,
  Pill,
  TrendingDown,
  Target
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Progress as ProgressBar } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'
import { TutorialSystem } from './TutorialSystem'

export function MobileDashboard() {
  const [completedMeals, setCompletedMeals] = useState([false, false, false, false, false])

  const meals = [
    { id: 0, name: "Repas 1", time: "8h00", calories: 351, emoji: "🍳", description: "Omelette aux blancs d'œufs" },
    { id: 1, name: "Collation 1", time: "10h30", calories: 300, emoji: "🥤", description: "Smoothie protéiné" },
    { id: 2, name: "Repas 2", time: "13h00", calories: 310, emoji: "🍗", description: "Poulet grillé aux brocolis" },
    { id: 3, name: "Collation 2", time: "16h00", calories: 301, emoji: "🥜", description: "Blancs d'œufs aux amandes" },
    { id: 4, name: "Repas 3", time: "19h30", calories: 270, emoji: "🐟", description: "Cabillaud en papillote" }
  ]

  const toggleMeal = (index) => {
    const newCompleted = [...completedMeals]
    newCompleted[index] = !newCompleted[index]
    setCompletedMeals(newCompleted)
  }

  const completedCount = completedMeals.filter(Boolean).length
  const totalCalories = meals.reduce((sum, meal, index) => 
    sum + (completedMeals[index] ? meal.calories : 0), 0
  )
  const targetCalories = 1532
  const caloriesProgress = (totalCalories / targetCalories) * 100

  return (
    <div className="min-h-screen bg-gray-50">
      <TutorialSystem currentPage="dashboard" />
      
      {/* Vue d'ensemble - Version mobile */}
      <div className="dashboard-overview p-4 space-y-4">
        {/* Carte principale du jour */}
        <Card className="bg-gradient-to-r from-blue-500 to-blue-600 text-white">
          <CardContent className="p-4">
            <div className="flex items-center justify-between mb-3">
              <div>
                <h2 className="text-lg font-bold">Mardi 6 Août 2025</h2>
                <p className="text-blue-100 text-sm">Jour 6 de votre programme</p>
              </div>
              <div className="text-right">
                <div className="text-2xl font-bold">{completedCount}/5</div>
                <div className="text-blue-100 text-xs">repas</div>
              </div>
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-white bg-opacity-20 rounded-lg p-3">
                <div className="text-xs text-blue-100">Calories</div>
                <div className="text-lg font-bold">{totalCalories}/{targetCalories}</div>
                <ProgressBar value={caloriesProgress} className="h-1 mt-1 bg-blue-400" />
              </div>
              <div className="bg-white bg-opacity-20 rounded-lg p-3">
                <div className="text-xs text-blue-100">Objectif</div>
                <div className="text-lg font-bold">-0.4kg</div>
                <div className="text-xs text-blue-100">aujourd'hui</div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Progression des repas */}
        <Card className="meals-progress">
          <CardHeader className="pb-3">
            <CardTitle className="text-lg flex items-center">
              <Utensils className="h-5 w-5 mr-2 text-orange-500" />
              Vos repas du jour
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {meals.map((meal, index) => (
              <div 
                key={meal.id}
                className={`flex items-center space-x-3 p-3 rounded-lg border transition-all ${
                  completedMeals[index] 
                    ? 'bg-green-50 border-green-200' 
                    : 'bg-white border-gray-200 hover:border-gray-300'
                }`}
              >
                <button
                  onClick={() => toggleMeal(index)}
                  className="flex-shrink-0"
                >
                  {completedMeals[index] ? (
                    <CheckCircle2 className="h-6 w-6 text-green-500" />
                  ) : (
                    <Circle className="h-6 w-6 text-gray-400" />
                  )}
                </button>
                
                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-2">
                    <span className="text-lg">{meal.emoji}</span>
                    <div className="flex-1">
                      <div className={`font-medium ${
                        completedMeals[index] ? 'text-green-800' : 'text-gray-900'
                      }`}>{meal.name}</div>
                      <div className={`text-sm truncate ${
                        completedMeals[index] ? 'text-green-600' : 'text-gray-500'
                      }`}>{meal.description}</div>
                    </div>
                  </div>
                </div>
                
                <div className="text-right flex-shrink-0">
                  <div className="text-sm font-medium text-gray-900">{meal.time}</div>
                  <div className="text-xs text-gray-500">{meal.calories} kcal</div>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>

        {/* Rappels importants */}
        <Card className="reminders">
          <CardHeader className="pb-3">
            <CardTitle className="text-lg flex items-center">
              <Calendar className="h-5 w-5 mr-2 text-purple-500" />
              Rappels du jour
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-center space-x-3 p-3 bg-yellow-50 rounded-lg border border-yellow-200">
              <Pill className="h-5 w-5 text-yellow-600" />
              <div className="flex-1">
                <div className="font-medium text-yellow-800">Vitamines</div>
                <div className="text-sm text-yellow-600">Multi-vitamine + CLA 3000mg</div>
              </div>
              <Badge variant="outline" className="text-yellow-600 border-yellow-300">
                2x/jour
              </Badge>
            </div>

            <div className="flex items-center space-x-3 p-3 bg-blue-50 rounded-lg border border-blue-200">
              <Dumbbell className="h-5 w-5 text-blue-600" />
              <div className="flex-1">
                <div className="font-medium text-blue-800">Sport aujourd'hui</div>
                <div className="text-sm text-blue-600">Séance 1h en salle</div>
              </div>
              <Badge variant="outline" className="text-blue-600 border-blue-300">
                Mardi
              </Badge>
            </div>

            <div className="flex items-center space-x-3 p-3 bg-teal-50 rounded-lg border border-teal-200">
              <Droplets className="h-5 w-5 text-teal-600" />
              <div className="flex-1">
                <div className="font-medium text-teal-800">Hydratation</div>
                <div className="text-sm text-teal-600">Objectif: 3,5L d'eau</div>
              </div>
              <Badge variant="outline" className="text-teal-600 border-teal-300">
                2,1L/3,5L
              </Badge>
            </div>
          </CardContent>
        </Card>

        {/* Progression hebdomadaire */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-lg flex items-center">
              <TrendingDown className="h-5 w-5 mr-2 text-green-500" />
              Progression cette semaine
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-7 gap-1 mb-4">
              {['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim'].map((day, index) => (
                <div key={day} className="text-center">
                  <div className="text-xs text-gray-500 mb-1">{day}</div>
                  <div className={`h-8 rounded ${
                    index <= 1 ? 'bg-green-500' : 'bg-gray-200'
                  } flex items-center justify-center`}>
                    {index <= 1 && <span className="text-white text-xs">✓</span>}
                  </div>
                </div>
              ))}
            </div>
            
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600 mb-1">-2.3kg</div>
              <div className="text-sm text-gray-600">perdus en 6 jours</div>
              <ProgressBar value={46} className="h-2 mt-2" />
              <div className="text-xs text-gray-500 mt-1">46% de l'objectif mensuel</div>
            </div>
          </CardContent>
        </Card>

        {/* Actions rapides */}
        <div className="grid grid-cols-2 gap-3">
          <Button variant="outline" className="h-16 flex flex-col items-center justify-center space-y-1">
            <ShoppingCart className="h-5 w-5" />
            <span className="text-sm">Liste courses</span>
          </Button>
          <Button variant="outline" className="h-16 flex flex-col items-center justify-center space-y-1">
            <Target className="h-5 w-5" />
            <span className="text-sm">Voir progression</span>
          </Button>
        </div>
      </div>
    </div>
  )
}

