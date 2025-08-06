import { useState } from 'react'
import { 
  ChevronLeft, 
  ChevronRight, 
  Plus, 
  Shuffle,
  Calendar as CalendarIcon
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'

export function MealPlanning() {
  const [currentWeek, setCurrentWeek] = useState(new Date())
  
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

  const days = [
    { key: 'monday', label: 'Lun', date: '6' },
    { key: 'tuesday', label: 'Mar', date: '7' },
    { key: 'wednesday', label: 'Mer', date: '8' },
    { key: 'thursday', label: 'Jeu', date: '9' },
    { key: 'friday', label: 'Ven', date: '10' },
    { key: 'saturday', label: 'Sam', date: '11' },
    { key: 'sunday', label: 'Dim', date: '12' }
  ]

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

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Planification des Repas</h1>
          <p className="text-gray-600">Organisez vos repas pour la semaine</p>
        </div>
        <div className="flex items-center space-x-2">
          <Button variant="outline" size="sm">
            <Shuffle className="h-4 w-4 mr-2" />
            Générer Plan Auto
          </Button>
          <Button size="sm">
            <Plus className="h-4 w-4 mr-2" />
            Nouvelle Recette
          </Button>
        </div>
      </div>

      {/* Week Navigation */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Button variant="outline" size="sm">
                <ChevronLeft className="h-4 w-4" />
              </Button>
              <div className="flex items-center space-x-2">
                <CalendarIcon className="h-5 w-5 text-gray-500" />
                <span className="text-lg font-semibold">Semaine du 6-12 Août 2025</span>
              </div>
              <Button variant="outline" size="sm">
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
            <Badge variant="outline">
              Moyenne: {calculateWeekAverage()} kcal/jour
            </Badge>
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
                  {days.map((day) => (
                    <th key={day.key} className="text-center p-4 font-medium text-gray-700 min-w-[140px]">
                      <div>{day.label}</div>
                      <div className="text-sm text-gray-500">{day.date}</div>
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
                    {days.map((day) => {
                      const meal = weekPlan[day.key][mealType.key]
                      return (
                        <td key={`${day.key}-${mealType.key}`} className="p-2">
                          {meal ? (
                            <div className="bg-white border border-gray-200 rounded-lg p-3 hover:shadow-md transition-shadow cursor-pointer">
                              <div className="text-center">
                                <div className="text-2xl mb-1">{meal.image}</div>
                                <div className="text-xs font-medium text-gray-900 leading-tight">
                                  {meal.name.length > 20 ? meal.name.substring(0, 20) + '...' : meal.name}
                                </div>
                                <div className="text-xs text-gray-500 mt-1">
                                  {meal.calories} kcal
                                </div>
                              </div>
                            </div>
                          ) : (
                            <div className="bg-gray-50 border-2 border-dashed border-gray-300 rounded-lg p-3 h-20 flex items-center justify-center hover:border-gray-400 transition-colors cursor-pointer">
                              <Plus className="h-4 w-4 text-gray-400" />
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
                  {days.map((day) => (
                    <td key={`${day.key}-total`} className="p-4 text-center">
                      <div className="text-sm font-bold text-gray-900">
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
    </div>
  )
}

