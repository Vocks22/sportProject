import React from 'react'
import { 
  AlertCircle, 
  TrendingDown, 
  TrendingUp, 
  Trophy, 
  Target,
  Zap,
  Award,
  Heart,
  CheckCircle,
  XCircle
} from 'lucide-react'
import { Alert, AlertDescription, AlertTitle } from './ui/alert'

export function ProgressAlerts({ measurements, profile }) {
  if (!measurements || measurements.length < 2 || !profile) {
    return null
  }

  const alerts = []
  
  // Analyser la progression récente
  const latestWeight = measurements[0]?.weight
  const previousWeight = measurements[1]?.weight
  const weekAgoWeight = measurements[6]?.weight || measurements[measurements.length - 1]?.weight
  const monthAgoWeight = measurements[29]?.weight || measurements[measurements.length - 1]?.weight
  
  const dailyChange = latestWeight - previousWeight
  const weeklyChange = latestWeight - weekAgoWeight
  const monthlyChange = latestWeight - monthAgoWeight
  
  const targetWeight = profile.target_weight || 70
  const remainingToGoal = latestWeight - targetWeight
  
  // Générer les alertes basées sur la progression
  
  // Alerte si prise de poids
  if (dailyChange > 0.3) {
    alerts.push({
      type: 'warning',
      icon: TrendingUp,
      title: 'Attention - Prise de poids',
      description: `Vous avez pris ${dailyChange.toFixed(1)}kg depuis hier. Vérifiez votre alimentation et hydratation.`,
      color: 'border-orange-500 bg-orange-50'
    })
  }
  
  // Félicitations pour perte de poids
  if (dailyChange < -0.1) {
    alerts.push({
      type: 'success',
      icon: TrendingDown,
      title: 'Excellente progression !',
      description: `Vous avez perdu ${Math.abs(dailyChange).toFixed(1)}kg depuis hier. Continuez ainsi !`,
      color: 'border-green-500 bg-green-50'
    })
  }
  
  // Progrès hebdomadaire
  if (weeklyChange < -0.5) {
    alerts.push({
      type: 'success',
      icon: Trophy,
      title: 'Semaine exceptionnelle !',
      description: `${Math.abs(weeklyChange).toFixed(1)}kg perdus cette semaine. Vous êtes sur la bonne voie !`,
      color: 'border-green-500 bg-green-50'
    })
  } else if (weeklyChange > 0.5) {
    alerts.push({
      type: 'warning',
      icon: AlertCircle,
      title: 'Semaine difficile',
      description: `Prise de ${weeklyChange.toFixed(1)}kg cette semaine. Analysez vos habitudes et ajustez si nécessaire.`,
      color: 'border-red-500 bg-red-50'
    })
  }
  
  // Proche de l'objectif
  if (remainingToGoal <= 2 && remainingToGoal > 0) {
    alerts.push({
      type: 'info',
      icon: Target,
      title: 'Objectif en vue !',
      description: `Plus que ${remainingToGoal.toFixed(1)}kg avant d'atteindre votre objectif de ${targetWeight}kg !`,
      color: 'border-blue-500 bg-blue-50'
    })
  }
  
  // Objectif atteint !
  if (latestWeight <= targetWeight) {
    alerts.push({
      type: 'success',
      icon: Award,
      title: '🎉 FÉLICITATIONS - Objectif atteint !',
      description: `Vous avez atteint votre objectif de ${targetWeight}kg ! Pensez à définir un nouvel objectif.`,
      color: 'border-yellow-500 bg-yellow-50'
    })
  }
  
  // Vérifier l'activité récente
  const todayMeasurement = measurements[0]
  if (todayMeasurement) {
    // Alerte si pas d'exercice
    if (!todayMeasurement.exercise_hours || todayMeasurement.exercise_hours === 0) {
      alerts.push({
        type: 'info',
        icon: Zap,
        title: 'Pensez à bouger',
        description: "Aucune activité physique enregistrée aujourd'hui. Même 30 minutes de marche peuvent faire la différence !",
        color: 'border-blue-500 bg-blue-50'
      })
    }
    
    // Félicitations pour bonne activité
    if (todayMeasurement.steps >= 10000) {
      alerts.push({
        type: 'success',
        icon: CheckCircle,
        title: 'Objectif pas atteint !',
        description: `${todayMeasurement.steps} pas aujourd'hui. Excellent travail !`,
        color: 'border-green-500 bg-green-50'
      })
    }
    
    // Alerte sommeil insuffisant
    if (todayMeasurement.sleep_hours && todayMeasurement.sleep_hours < 6) {
      alerts.push({
        type: 'warning',
        icon: AlertCircle,
        title: 'Sommeil insuffisant',
        description: `Seulement ${todayMeasurement.sleep_hours}h de sommeil. Le repos est crucial pour la perte de poids.`,
        color: 'border-orange-500 bg-orange-50'
      })
    }
    
    // Alerte hydratation
    if (todayMeasurement.water_intake && todayMeasurement.water_intake < 1500) {
      alerts.push({
        type: 'info',
        icon: AlertCircle,
        title: 'Hydratation insuffisante',
        description: `Seulement ${(todayMeasurement.water_intake / 1000).toFixed(1)}L d'eau aujourd'hui. Visez au moins 2L par jour.`,
        color: 'border-blue-500 bg-blue-50'
      })
    }
  }
  
  // Analyser la tendance mensuelle
  if (monthlyChange < -2) {
    alerts.push({
      type: 'success',
      icon: Award,
      title: 'Mois remarquable !',
      description: `Vous avez perdu ${Math.abs(monthlyChange).toFixed(1)}kg ce mois-ci. Votre régularité paie !`,
      color: 'border-green-500 bg-green-50'
    })
  }
  
  // Limiter à 3 alertes maximum
  const displayAlerts = alerts.slice(0, 3)
  
  if (displayAlerts.length === 0) {
    return null
  }
  
  return (
    <div className="space-y-3">
      {displayAlerts.map((alert, index) => {
        const Icon = alert.icon
        return (
          <Alert key={index} className={`${alert.color} border-l-4`}>
            <Icon className="h-4 w-4" />
            <AlertTitle>{alert.title}</AlertTitle>
            <AlertDescription>{alert.description}</AlertDescription>
          </Alert>
        )
      })}
    </div>
  )
}