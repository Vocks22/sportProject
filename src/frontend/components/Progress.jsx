import React, { useState, useEffect } from 'react'
import { 
  TrendingDown, 
  Target, 
  Calendar,
  Utensils,
  Dumbbell,
  Droplets,
  Award,
  Flame,
  Activity,
  Scale,
  Timer,
  ChevronLeft,
  ChevronRight,
  Trophy,
  Footprints
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from './ui/card'
import { Progress as ProgressBar } from './ui/progress'
import { Badge } from './ui/badge'
import { WeightChartWithControls } from './WeightChart'
import { ProgressAlerts } from './ProgressAlerts'

export function ProgressPage() {
  const [measurements, setMeasurements] = useState([])
  const [profile, setProfile] = useState(null)
  const [weightHistory, setWeightHistory] = useState([])
  const [selectedPeriod, setSelectedPeriod] = useState(30) // 30 jours par défaut
  const [loading, setLoading] = useState(true)
  const userId = 1

  useEffect(() => {
    fetchProgressData()
    
    // Rafraîchir quand une mesure est ajoutée
    const handleMeasurementAdded = () => {
      fetchProgressData()
    }
    
    window.addEventListener('measurementAdded', handleMeasurementAdded)
    
    return () => {
      window.removeEventListener('measurementAdded', handleMeasurementAdded)
    }
  }, [selectedPeriod])

  const fetchProgressData = async () => {
    setLoading(true)
    try {
      // Récupérer TOUTES les mesures
      const measResponse = await fetch(`http://localhost:5000/api/users/${userId}/measurements?days=365&limit=100`)
      if (measResponse.ok) {
        const measData = await measResponse.json()
        // Filtrer côté client selon la période sélectionnée
        const cutoffDate = new Date()
        cutoffDate.setDate(cutoffDate.getDate() - selectedPeriod)
        
        const filteredMeasurements = measData.filter(m => {
          const measureDate = new Date(m.date)
          return measureDate >= cutoffDate
        })
        
        setMeasurements(filteredMeasurements)
      }

      // Récupérer le profil
      const profileResponse = await fetch(`http://localhost:5000/api/users/${userId}/profile`)
      if (profileResponse.ok) {
        const profileData = await profileResponse.json()
        setProfile(profileData)
      }

      // Récupérer l'historique de poids
      const weightResponse = await fetch(`http://localhost:5000/api/users/${userId}/weight-history?days=365&limit=500`)
      if (weightResponse.ok) {
        const weightData = await weightResponse.json()
        // Filtrer selon la période sélectionnée
        const allWeights = weightData.weight_history || []
        const cutoffDate = new Date()
        cutoffDate.setDate(cutoffDate.getDate() - selectedPeriod)
        
        const filteredWeights = allWeights.filter(w => {
          const weightDate = new Date(w.recorded_date)
          return weightDate >= cutoffDate
        })
        
        setWeightHistory(filteredWeights)
      }
    } catch (error) {
      console.error('Erreur chargement données:', error)
    } finally {
      setLoading(false)
    }
  }

  // Calculs de progression
  const latestMeasurement = measurements[0] || {}
  const oldestMeasurement = measurements[measurements.length - 1] || {}
  
  const currentWeight = latestMeasurement.weight || profile?.current_weight || 0
  const startWeight = oldestMeasurement.weight || currentWeight
  const targetWeight = profile?.target_weight || 70
  
  const totalWeightLoss = startWeight - currentWeight
  const remainingWeight = currentWeight - targetWeight
  const progressPercentage = startWeight > targetWeight 
    ? Math.min(100, Math.max(0, ((startWeight - currentWeight) / (startWeight - targetWeight)) * 100))
    : 0

  // Moyennes et statistiques
  const calculateStats = () => {
    if (measurements.length === 0) return {
      avgCalories: 0,
      avgSteps: 0,
      avgExercise: 0,
      avgSleep: 0,
      avgWater: 0,
      totalCaloriesBurned: 0,
      totalSteps: 0,
      totalExerciseHours: 0,
      activeDays: 0
    }

    const stats = measurements.reduce((acc, m) => ({
      calories: acc.calories + (m.calories_consumed || 0),
      caloriesBurned: acc.caloriesBurned + (m.calories_burned || 0),
      steps: acc.steps + (m.steps || 0),
      exercise: acc.exercise + (m.exercise_hours || 0),
      sleep: acc.sleep + (m.sleep_hours || 0),
      water: acc.water + (m.water_intake || 0),
      activeDays: acc.activeDays + (m.exercise_hours > 0 ? 1 : 0)
    }), { calories: 0, caloriesBurned: 0, steps: 0, exercise: 0, sleep: 0, water: 0, activeDays: 0 })

    const count = measurements.length
    return {
      avgCalories: Math.round(stats.calories / count),
      avgCaloriesBurned: Math.round(stats.caloriesBurned / count),
      avgSteps: Math.round(stats.steps / count),
      avgExercise: (stats.exercise / count).toFixed(1),
      avgSleep: (stats.sleep / count).toFixed(1),
      avgWater: Math.round(stats.water / count),
      totalCaloriesBurned: stats.caloriesBurned,
      totalSteps: stats.steps,
      totalExerciseHours: stats.exercise.toFixed(1),
      activeDays: stats.activeDays
    }
  }

  const stats = calculateStats()

  // Calcul de la vitesse de perte
  const daysElapsed = measurements.length
  const averageLossPerDay = daysElapsed > 0 ? (totalWeightLoss / daysElapsed).toFixed(3) : 0
  const projectedDaysToGoal = averageLossPerDay > 0 ? Math.ceil(remainingWeight / averageLossPerDay) : 0

  // Badges et achievements
  const achievements = []
  if (totalWeightLoss >= 1) achievements.push({ icon: Trophy, text: "1kg perdu !", color: "bg-yellow-500" })
  if (totalWeightLoss >= 2) achievements.push({ icon: Trophy, text: "2kg perdus !", color: "bg-yellow-500" })
  if (stats.activeDays >= 20) achievements.push({ icon: Dumbbell, text: "20 jours actifs", color: "bg-blue-500" })
  if (stats.totalSteps >= 100000) achievements.push({ icon: Footprints, text: "100k pas !", color: "bg-green-500" })
  if (stats.avgSleep >= 7) achievements.push({ icon: Award, text: "Bon dormeur", color: "bg-purple-500" })

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[1, 2, 3].map(i => (
              <div key={i} className="h-32 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Suivi & Progression</h1>
          <p className="text-gray-600">Analysez vos progrès sur {selectedPeriod} jours</p>
        </div>
        <div className="flex gap-2">
          {[7, 30, 90].map(days => (
            <button
              key={days}
              onClick={() => setSelectedPeriod(days)}
              className={`px-4 py-2 rounded-lg transition-colors ${
                selectedPeriod === days 
                  ? 'bg-green-600 text-white' 
                  : 'bg-gray-100 hover:bg-gray-200'
              }`}
            >
              {days}j
            </button>
          ))}
        </div>
      </div>

      {/* Alertes et félicitations */}
      <ProgressAlerts measurements={measurements} profile={profile} />

      {/* Cartes de progression principales */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Poids Actuel</CardTitle>
            <Scale className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{currentWeight.toFixed(1)} kg</div>
            <div className="flex items-center space-x-2 mt-2">
              <span className={`text-sm ${totalWeightLoss > 0 ? 'text-green-600' : 'text-gray-500'}`}>
                {totalWeightLoss > 0 ? '⬇️' : '➡️'} {totalWeightLoss > 0 ? '-' : ''}{Math.abs(totalWeightLoss).toFixed(1)} kg
              </span>
              <span className="text-xs text-gray-500">sur {selectedPeriod}j</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Objectif</CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{targetWeight} kg</div>
            <div className="text-sm text-gray-600">Reste: {remainingWeight.toFixed(1)} kg</div>
            <div className="mt-2">
              <div className="text-xs font-medium text-blue-600">
                ~{projectedDaysToGoal} jours restants
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Progression</CardTitle>
            <Award className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{progressPercentage.toFixed(0)}%</div>
            <ProgressBar value={progressPercentage} className="mt-2" />
            <div className="text-xs text-gray-600 mt-1">
              {averageLossPerDay > 0 ? `${(averageLossPerDay * 1000).toFixed(0)}g/jour` : 'Stable'}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Jours Actifs</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.activeDays}/{daysElapsed}</div>
            <ProgressBar value={(stats.activeDays / daysElapsed) * 100} className="mt-2" />
            <div className="text-xs text-gray-600 mt-1">
              {((stats.activeDays / daysElapsed) * 100).toFixed(0)}% d'assiduité
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Graphique de poids */}
      {weightHistory.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingDown className="h-5 w-5" />
              Évolution du poids
            </CardTitle>
          </CardHeader>
          <CardContent>
            <WeightChartWithControls 
              data={weightHistory}
              targetWeight={targetWeight}
              height={300}
            />
          </CardContent>
        </Card>
      )}

      {/* Statistiques détaillées */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Activité physique */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-5 w-5" />
              Activité Physique
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span>Calories brûlées (moy.)</span>
                <span className="font-medium">{stats.avgCaloriesBurned} kcal/jour</span>
              </div>
              <ProgressBar value={Math.min(100, (stats.avgCaloriesBurned / 2500) * 100)} />
            </div>
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span>Pas quotidiens (moy.)</span>
                <span className="font-medium">{stats.avgSteps}</span>
              </div>
              <ProgressBar value={Math.min(100, (stats.avgSteps / 10000) * 100)} />
            </div>
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span>Exercice (moy.)</span>
                <span className="font-medium">{stats.avgExercise} h/jour</span>
              </div>
              <ProgressBar value={Math.min(100, (stats.avgExercise / 2) * 100)} />
            </div>
            <div className="pt-3 border-t">
              <div className="grid grid-cols-2 gap-2 text-center">
                <div>
                  <div className="text-2xl font-bold text-orange-600">
                    {(stats.totalCaloriesBurned / 1000).toFixed(1)}k
                  </div>
                  <div className="text-xs text-gray-600">Calories brûlées</div>
                </div>
                <div>
                  <div className="text-2xl font-bold text-blue-600">
                    {stats.totalExerciseHours}h
                  </div>
                  <div className="text-xs text-gray-600">Heures d'exercice</div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Habitudes */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Utensils className="h-5 w-5" />
              Nutrition & Habitudes
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span>Calories consommées (moy.)</span>
                <span className="font-medium">{stats.avgCalories} kcal</span>
              </div>
              <ProgressBar value={Math.min(100, (stats.avgCalories / (profile?.daily_calories_target || 1500)) * 100)} />
            </div>
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span>Hydratation (moy.)</span>
                <span className="font-medium">{(stats.avgWater / 1000).toFixed(1)} L</span>
              </div>
              <ProgressBar value={Math.min(100, (stats.avgWater / 2500) * 100)} />
            </div>
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span>Sommeil (moy.)</span>
                <span className="font-medium">{stats.avgSleep} h</span>
              </div>
              <ProgressBar value={Math.min(100, (stats.avgSleep / 8) * 100)} />
            </div>
            <div className="pt-3 border-t">
              <p className="text-sm text-gray-600">
                Déficit calorique moyen: 
                <span className="font-medium text-green-600 ml-1">
                  {stats.avgCaloriesBurned - stats.avgCalories} kcal/jour
                </span>
              </p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Achievements */}
      {achievements.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Trophy className="h-5 w-5" />
              Achievements débloqués
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {achievements.map((achievement, index) => {
                const Icon = achievement.icon
                return (
                  <Badge key={index} className={`${achievement.color} text-white`}>
                    <Icon className="h-3 w-3 mr-1" />
                    {achievement.text}
                  </Badge>
                )
              })}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Analyse détaillée */}
      <Card>
        <CardHeader>
          <CardTitle>Analyse de la période</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2 text-sm">
            <p>
              Sur les <span className="font-medium">{selectedPeriod} derniers jours</span>, vous avez perdu{' '}
              <span className="font-medium text-green-600">{totalWeightLoss.toFixed(1)} kg</span> 
              {averageLossPerDay > 0 && (
                <span> avec une moyenne de <span className="font-medium">{(averageLossPerDay * 1000).toFixed(0)}g/jour</span></span>
              )}.
            </p>
            {projectedDaysToGoal > 0 && (
              <p>
                À ce rythme, vous atteindrez votre objectif de <span className="font-medium">{targetWeight} kg</span> dans environ{' '}
                <span className="font-medium text-blue-600">{projectedDaysToGoal} jours</span>.
              </p>
            )}
            <p>
              Vous avez été actif <span className="font-medium">{stats.activeDays} jours sur {daysElapsed}</span>,
              brûlant en moyenne <span className="font-medium">{stats.avgCaloriesBurned} calories par jour</span>.
            </p>
            {stats.avgSleep < 7 && (
              <p className="text-orange-600">
                ⚠️ Votre sommeil moyen ({stats.avgSleep}h) est inférieur aux 7h recommandées.
              </p>
            )}
            {stats.avgWater < 2000 && (
              <p className="text-orange-600">
                ⚠️ Pensez à augmenter votre hydratation (actuellement {(stats.avgWater / 1000).toFixed(1)}L/jour).
              </p>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}