import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from './ui/card'
import { Badge } from './ui/badge'
import { Progress } from './ui/progress'
import { 
  Scale, 
  TrendingDown, 
  TrendingUp, 
  Activity, 
  Flame, 
  Target,
  Calendar,
  ChefHat,
  ShoppingCart,
  Timer,
  Footprints,
  Moon,
  Heart,
  Minus
} from 'lucide-react'
import { Link } from 'react-router-dom'
import { WeightChartWithControls } from './WeightChart'
import { ProgressAlerts } from './ProgressAlerts'
import DietDashboard from './DietDashboard'

export function Dashboard() {
  const [measurements, setMeasurements] = useState([])
  const [profile, setProfile] = useState(null)
  const [weightHistory, setWeightHistory] = useState([])
  const [loading, setLoading] = useState(true)
  const userId = 1 // TODO: Récupérer depuis l'auth

  useEffect(() => {
    fetchData()
    
    // Rafraîchir quand on revient sur la page
    const handleFocus = () => {
      fetchData()
    }
    
    // Rafraîchir quand une mesure est ajoutée
    const handleMeasurementAdded = () => {
      fetchData()
    }
    
    window.addEventListener('focus', handleFocus)
    window.addEventListener('measurementAdded', handleMeasurementAdded)
    
    return () => {
      window.removeEventListener('focus', handleFocus)
      window.removeEventListener('measurementAdded', handleMeasurementAdded)
    }
  }, [])

  const fetchData = async () => {
    try {
      // Récupérer les mesures récentes
      const measResponse = await fetch(`${import.meta.env.VITE_API_URL || "http://localhost:5000/api"}/users/${userId}/measurements?days=365`)
      if (measResponse.ok) {
        const measData = await measResponse.json()
        setMeasurements(measData)
      }

      // Récupérer le profil
      const profileResponse = await fetch(`${import.meta.env.VITE_API_URL || "http://localhost:5000/api"}/users/${userId}/profile`)
      if (profileResponse.ok) {
        const profileData = await profileResponse.json()
        setProfile(profileData)
      }

      // Récupérer l'historique de poids
      const weightResponse = await fetch(`${import.meta.env.VITE_API_URL || "http://localhost:5000/api"}/users/${userId}/weight-history?days=365&limit=500`)
      if (weightResponse.ok) {
        const weightData = await weightResponse.json()
        setWeightHistory(weightData.weight_history || [])
      }
    } catch (error) {
      console.error('Erreur chargement données:', error)
    } finally {
      setLoading(false)
    }
  }

  // Obtenir la dernière mesure
  const latestMeasurement = measurements[0] || {}
  
  // Calculer les moyennes sur 7 jours
  const last7Days = measurements.slice(0, 7)
  const avgCaloriesBurned = last7Days.length > 0 
    ? Math.round(last7Days.reduce((sum, m) => sum + (m.calories_burned || 0), 0) / last7Days.length)
    : 0
  const avgSteps = last7Days.length > 0
    ? Math.round(last7Days.reduce((sum, m) => sum + (m.steps || 0), 0) / last7Days.length)
    : 0
  const avgSleep = last7Days.length > 0
    ? (last7Days.reduce((sum, m) => sum + (m.sleep_hours || 0), 0) / last7Days.length).toFixed(1)
    : 0

  // Calculer la progression du poids
  const weightProgress = profile && profile.current_weight && profile.target_weight
    ? Math.round(((profile.current_weight - profile.target_weight) / (100 - profile.target_weight)) * 100)
    : 0

  // Déterminer la tendance du poids
  const getWeightTrend = () => {
    if (measurements.length < 2) return { icon: Minus, color: 'text-gray-500', label: 'Pas de données' }
    const recent = measurements[0].weight
    const previous = measurements[6]?.weight || measurements[measurements.length - 1].weight
    const change = recent - previous
    
    if (change < -0.1) return { icon: TrendingDown, color: 'text-green-500', label: `${change.toFixed(1)} kg` }
    if (change > 0.1) return { icon: TrendingUp, color: 'text-red-500', label: `+${change.toFixed(1)} kg` }
    return { icon: Minus, color: 'text-gray-500', label: 'Stable' }
  }

  const weightTrend = getWeightTrend()
  const TrendIcon = weightTrend.icon

  // Date d'aujourd'hui
  const today = new Date()
  const dateOptions = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }
  const formattedDate = today.toLocaleDateString('fr-FR', dateOptions)

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {[1, 2, 3, 4].map(i => (
              <div key={i} className="h-32 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* En-tête */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600 capitalize">{formattedDate}</p>
        </div>
        <Link to="/measurements">
          <button className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center gap-2">
            <Activity className="h-4 w-4" />
            Ajouter mesure du jour
          </button>
        </Link>
      </div>

      {/* NOUVEAU : Dashboard de suivi de diète */}
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Suivi de Diète Quotidien</h2>
        <DietDashboard />
      </div>

      {/* Alertes et félicitations */}
      <ProgressAlerts measurements={measurements} profile={profile} />

      {/* Cartes de statistiques principales */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Poids actuel */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center justify-between">
              <span className="flex items-center gap-2">
                <Scale className="h-4 w-4" />
                Poids actuel
              </span>
              <TrendIcon className={`h-4 w-4 ${weightTrend.color}`} />
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {latestMeasurement.weight || profile?.current_weight || '--'} kg
            </div>
            <p className={`text-xs mt-1 ${weightTrend.color}`}>
              {weightTrend.label} sur 7 jours
            </p>
            <Progress 
              value={Math.max(0, Math.min(100, 100 - weightProgress))} 
              className="mt-2"
            />
          </CardContent>
        </Card>

        {/* Calories brûlées */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Flame className="h-4 w-4" />
              Calories brûlées
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {latestMeasurement.calories_burned || '--'} kcal
            </div>
            <p className="text-xs text-gray-600 mt-1">
              Moy. 7j: {avgCaloriesBurned} kcal
            </p>
            <div className="flex items-center gap-1 mt-2">
              {last7Days.slice(0, 7).map((m, i) => (
                <div
                  key={i}
                  className="flex-1 bg-gray-200 rounded-sm overflow-hidden"
                  style={{ height: '20px' }}
                >
                  <div
                    className="bg-orange-500"
                    style={{
                      height: '100%',
                      width: `${Math.min(100, (m.calories_burned || 0) / 30)}%`
                    }}
                  />
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Pas quotidiens */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Footprints className="h-4 w-4" />
              Pas aujourd'hui
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {latestMeasurement.steps || '--'}
            </div>
            <p className="text-xs text-gray-600 mt-1">
              Moy. 7j: {avgSteps} pas
            </p>
            <Progress 
              value={Math.min(100, ((latestMeasurement.steps || 0) / 10000) * 100)} 
              className="mt-2"
            />
            <p className="text-xs text-gray-500 mt-1">
              Objectif: 10,000 pas
            </p>
          </CardContent>
        </Card>

        {/* Sommeil */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Moon className="h-4 w-4" />
              Sommeil
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {latestMeasurement.sleep_hours || '--'} h
            </div>
            <p className="text-xs text-gray-600 mt-1">
              Moy. 7j: {avgSleep} h
            </p>
            <Badge 
              variant={latestMeasurement.sleep_quality >= 7 ? 'default' : 'secondary'}
              className="mt-2"
            >
              Qualité: {latestMeasurement.sleep_quality || '--'}/10
            </Badge>
          </CardContent>
        </Card>
      </div>

      {/* Graphique de progression du poids */}
      {weightHistory.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span className="flex items-center gap-2">
                <TrendingDown className="h-5 w-5" />
                Évolution du poids (30 derniers jours)
              </span>
              <Link to="/progress" className="text-sm text-blue-600 hover:text-blue-700">
                Voir plus →
              </Link>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <WeightChartWithControls 
              data={weightHistory}
              targetWeight={profile?.target_weight}
              height={250}
            />
          </CardContent>
        </Card>
      )}

      {/* Résumé de la journée */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Activité physique */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-5 w-5" />
              Activité du jour
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Exercice</span>
              <span className="font-medium">
                {latestMeasurement.exercise_hours || '0'} h - {latestMeasurement.exercise_type || 'Aucun'}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Distance parcourue</span>
              <span className="font-medium">{latestMeasurement.distance_walked || '0'} km</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Minutes actives</span>
              <span className="font-medium">{latestMeasurement.active_minutes || '0'} min</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Fréquence cardiaque</span>
              <span className="font-medium">
                <Heart className="h-4 w-4 inline mr-1 text-red-500" />
                {latestMeasurement.heart_rate_rest || '--'} bpm
              </span>
            </div>
          </CardContent>
        </Card>

        {/* Nutrition */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <ChefHat className="h-5 w-5" />
              Nutrition du jour
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Calories</span>
              <span className="font-medium">
                {latestMeasurement.calories_consumed || '--'} / {profile?.daily_calories_target || 1500} kcal
              </span>
            </div>
            <Progress 
              value={Math.min(100, ((latestMeasurement.calories_consumed || 0) / (profile?.daily_calories_target || 1500)) * 100)}
              className="h-2"
            />
            <div className="grid grid-cols-3 gap-2 text-center">
              <div>
                <div className="text-xs text-gray-600">Protéines</div>
                <div className="font-medium">{latestMeasurement.protein || '--'}g</div>
              </div>
              <div>
                <div className="text-xs text-gray-600">Glucides</div>
                <div className="font-medium">{latestMeasurement.carbs || '--'}g</div>
              </div>
              <div>
                <div className="text-xs text-gray-600">Lipides</div>
                <div className="font-medium">{latestMeasurement.fat || '--'}g</div>
              </div>
            </div>
            <div className="flex justify-between items-center pt-2 border-t">
              <span className="text-sm text-gray-600">Eau</span>
              <span className="font-medium">{latestMeasurement.water_intake || '--'} ml</span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Actions rapides */}
      <Card>
        <CardHeader>
          <CardTitle>Actions rapides</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <Link to="/measurements" className="block">
              <button className="w-full p-3 border rounded-lg hover:bg-gray-50 transition-colors flex flex-col items-center gap-2">
                <Scale className="h-5 w-5 text-blue-600" />
                <span className="text-sm">Ajouter pesée</span>
              </button>
            </Link>
            <Link to="/planning" className="block">
              <button className="w-full p-3 border rounded-lg hover:bg-gray-50 transition-colors flex flex-col items-center gap-2">
                <Calendar className="h-5 w-5 text-green-600" />
                <span className="text-sm">Planning repas</span>
              </button>
            </Link>
            <Link to="/recipes" className="block">
              <button className="w-full p-3 border rounded-lg hover:bg-gray-50 transition-colors flex flex-col items-center gap-2">
                <ChefHat className="h-5 w-5 text-orange-600" />
                <span className="text-sm">Recettes</span>
              </button>
            </Link>
            <Link to="/shopping" className="block">
              <button className="w-full p-3 border rounded-lg hover:bg-gray-50 transition-colors flex flex-col items-center gap-2">
                <ShoppingCart className="h-5 w-5 text-purple-600" />
                <span className="text-sm">Liste courses</span>
              </button>
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}