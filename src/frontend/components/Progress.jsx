import { 
  TrendingDown, 
  Target, 
  Calendar,
  Utensils,
  Dumbbell,
  Droplets,
  Award
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Progress as ProgressBar } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'

export function ProgressPage() {
  // Données simulées de progression
  const weightData = [
    { date: '1/8', weight: 75.0 },
    { date: '2/8', weight: 74.6 },
    { date: '3/8', weight: 74.2 },
    { date: '4/8', weight: 73.8 },
    { date: '5/8', weight: 73.4 },
    { date: '6/8', weight: 73.1 },
    { date: '7/8', weight: 72.7 }
  ]

  const currentWeight = 72.7
  const startWeight = 75.0
  const targetWeight = 70.0
  const weightLoss = startWeight - currentWeight
  const remainingWeight = currentWeight - targetWeight
  const progressPercentage = ((startWeight - currentWeight) / (startWeight - targetWeight)) * 100

  const nutritionData = {
    protein: { current: 145, target: 150, percentage: 97 },
    carbs: { current: 85, target: 100, percentage: 85 },
    fat: { current: 75, target: 80, percentage: 94 },
    calories: { current: 1515, target: 1500, percentage: 101 }
  }

  const habits = {
    meals: { completed: 18, total: 21, percentage: 86 },
    sport: { completed: 2, total: 3, percentage: 67 },
    hydration: { current: 3.2, target: 3.5, percentage: 91 }
  }

  const nextGoals = [
    { icon: Target, text: "Atteindre 70kg", deadline: "dans 7 jours", color: "text-green-600" },
    { icon: Dumbbell, text: "Maintenir 3 séances/semaine", deadline: "en cours", color: "text-blue-600" },
    { icon: Droplets, text: "Augmenter hydratation à 4L", deadline: "cette semaine", color: "text-cyan-600" },
    { icon: TrendingDown, text: "Stabiliser à -0.3kg/jour", deadline: "objectif mensuel", color: "text-purple-600" }
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Suivi & Progression</h1>
          <p className="text-gray-600">Analysez vos progrès et objectifs</p>
        </div>
        <Badge variant="outline" className="text-lg px-3 py-1">
          Jour 6/30
        </Badge>
      </div>

      {/* Weight Progress Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Poids Actuel</CardTitle>
            <TrendingDown className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{currentWeight} kg</div>
            <div className="flex items-center space-x-2 mt-2">
              <span className="text-sm text-green-600">⬇️ -0.4 kg</span>
              <span className="text-xs text-gray-500">depuis hier</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Objectif</CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">-5 kg</div>
            <div className="text-sm text-gray-600">ce mois</div>
            <div className="mt-2">
              <div className="text-sm font-medium text-blue-600">🎯 Reste: -{remainingWeight.toFixed(1)} kg</div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Progression</CardTitle>
            <Award className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">-{weightLoss.toFixed(1)} kg</div>
            <div className="text-sm text-gray-600">en 6 jours</div>
            <div className="mt-2">
              <div className="text-sm font-medium">📈 Rythme: -0.38kg/jour</div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Weight Chart */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <TrendingDown className="h-5 w-5" />
            <span>Évolution du Poids</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-64 flex items-end justify-between space-x-2">
            {weightData.map((data, index) => {
              const height = ((76 - data.weight) / (76 - 72)) * 100
              return (
                <div key={index} className="flex-1 flex flex-col items-center">
                  <div className="text-xs text-gray-600 mb-2">{data.weight}kg</div>
                  <div 
                    className="w-full bg-green-500 rounded-t"
                    style={{ height: `${height}%` }}
                  />
                  <div className="text-xs text-gray-500 mt-2">{data.date}</div>
                </div>
              )
            })}
          </div>
          <div className="mt-4 text-center">
            <ProgressBar value={progressPercentage} className="h-3" />
            <div className="text-sm text-gray-600 mt-2">
              {Math.round(progressPercentage)}% de l'objectif mensuel atteint
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Nutrition Progress */}
      <Card>
        <CardHeader>
          <CardTitle>Répartition Nutritionnelle</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="text-lg font-bold text-purple-600">Protéines</div>
              <div className="text-2xl font-bold">{nutritionData.protein.percentage}%</div>
              <div className="text-sm text-gray-600">{nutritionData.protein.current}g/{nutritionData.protein.target}g</div>
              <ProgressBar value={nutritionData.protein.percentage} className="h-2 mt-2" />
              <div className="text-xs text-green-600 mt-1">Optimal</div>
            </div>
            
            <div className="text-center">
              <div className="text-lg font-bold text-orange-600">Glucides</div>
              <div className="text-2xl font-bold">{nutritionData.carbs.percentage}%</div>
              <div className="text-sm text-gray-600">{nutritionData.carbs.current}g/{nutritionData.carbs.target}g</div>
              <ProgressBar value={nutritionData.carbs.percentage} className="h-2 mt-2" />
              <div className="text-xs text-yellow-600 mt-1">Correct</div>
            </div>
            
            <div className="text-center">
              <div className="text-lg font-bold text-red-600">Lipides</div>
              <div className="text-2xl font-bold">{nutritionData.fat.percentage}%</div>
              <div className="text-sm text-gray-600">{nutritionData.fat.current}g/{nutritionData.fat.target}g</div>
              <ProgressBar value={nutritionData.fat.percentage} className="h-2 mt-2" />
              <div className="text-xs text-green-600 mt-1">Optimal</div>
            </div>
            
            <div className="text-center">
              <div className="text-lg font-bold text-green-600">Calories</div>
              <div className="text-2xl font-bold">{nutritionData.calories.percentage}%</div>
              <div className="text-sm text-gray-600">{nutritionData.calories.current}/{nutritionData.calories.target}</div>
              <ProgressBar value={nutritionData.calories.percentage} className="h-2 mt-2" />
              <div className="text-xs text-green-600 mt-1">Parfait</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Habits & Goals */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Habits */}
        <Card>
          <CardHeader>
            <CardTitle>Habitudes</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center space-x-2">
                  <Utensils className="h-4 w-4 text-gray-500" />
                  <span className="text-sm font-medium">Repas pris cette semaine</span>
                </div>
                <span className="text-sm text-gray-600">{habits.meals.completed}/{habits.meals.total}</span>
              </div>
              <ProgressBar value={habits.meals.percentage} className="h-2" />
              <div className="text-xs text-gray-500 mt-1">{habits.meals.percentage}%</div>
            </div>
            
            <div>
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center space-x-2">
                  <Dumbbell className="h-4 w-4 text-gray-500" />
                  <span className="text-sm font-medium">Sport</span>
                </div>
                <span className="text-sm text-gray-600">{habits.sport.completed}/{habits.sport.total}</span>
              </div>
              <ProgressBar value={habits.sport.percentage} className="h-2" />
              <div className="text-xs text-gray-500 mt-1">{habits.sport.percentage}%</div>
            </div>
            
            <div>
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center space-x-2">
                  <Droplets className="h-4 w-4 text-gray-500" />
                  <span className="text-sm font-medium">Hydratation</span>
                </div>
                <span className="text-sm text-gray-600">{habits.hydration.current}L/{habits.hydration.target}L</span>
              </div>
              <ProgressBar value={habits.hydration.percentage} className="h-2" />
              <div className="text-xs text-gray-500 mt-1">{habits.hydration.percentage}%</div>
            </div>
          </CardContent>
        </Card>

        {/* Next Goals */}
        <Card>
          <CardHeader>
            <CardTitle>Prochains Objectifs</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {nextGoals.map((goal, index) => (
              <div key={index} className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                <goal.icon className={`h-5 w-5 ${goal.color}`} />
                <div className="flex-1">
                  <div className="font-medium text-sm">{goal.text}</div>
                  <div className="text-xs text-gray-500">{goal.deadline}</div>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>

      {/* Weekly Summary */}
      <Card>
        <CardHeader>
          <CardTitle>Résumé de la Semaine</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 text-center">
            <div className="p-4 bg-green-50 rounded-lg">
              <div className="text-2xl font-bold text-green-600">-2.3kg</div>
              <div className="text-sm text-gray-600">Perte de poids</div>
            </div>
            <div className="p-4 bg-blue-50 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">86%</div>
              <div className="text-sm text-gray-600">Repas suivis</div>
            </div>
            <div className="p-4 bg-purple-50 rounded-lg">
              <div className="text-2xl font-bold text-purple-600">2/3</div>
              <div className="text-sm text-gray-600">Séances sport</div>
            </div>
            <div className="p-4 bg-cyan-50 rounded-lg">
              <div className="text-2xl font-bold text-cyan-600">3.2L</div>
              <div className="text-sm text-gray-600">Hydratation moy.</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

