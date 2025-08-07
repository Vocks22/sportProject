import { useState, useEffect } from 'react'
import { 
  Clock, 
  ChefHat, 
  Users, 
  ArrowLeft, 
  Play, 
  Pause, 
  RotateCcw, 
  AlertTriangle,
  Lightbulb,
  Eye,
  Camera,
  CheckCircle,
  ArrowRight
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'

const DIFFICULTY_COLORS = {
  beginner: 'bg-green-100 text-green-800 border-green-200',
  intermediate: 'bg-yellow-100 text-yellow-800 border-yellow-200',
  advanced: 'bg-red-100 text-red-800 border-red-200'
}

const DIFFICULTY_LABELS = {
  beginner: 'Débutant',
  intermediate: 'Intermédiaire',
  advanced: 'Avancé'
}

const TIP_TYPES = {
  tip: { icon: Lightbulb, color: 'text-blue-500', bgColor: 'bg-blue-50', borderColor: 'border-blue-200' },
  warning: { icon: AlertTriangle, color: 'text-red-500', bgColor: 'bg-red-50', borderColor: 'border-red-200' },
  secret: { icon: ChefHat, color: 'text-purple-500', bgColor: 'bg-purple-50', borderColor: 'border-purple-200' },
  alternative: { icon: ArrowRight, color: 'text-green-500', bgColor: 'bg-green-50', borderColor: 'border-green-200' }
}

export function CookingGuide({ recipeId, onBack }) {
  const [cookingData, setCookingData] = useState(null)
  const [currentStep, setCurrentStep] = useState(0)
  const [timer, setTimer] = useState(0)
  const [isTimerRunning, setIsTimerRunning] = useState(false)
  const [completedSteps, setCompletedSteps] = useState(new Set())
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  // Charger les données de cuisson
  useEffect(() => {
    const fetchCookingGuide = async () => {
      try {
        const response = await fetch(`/api/recipes/${recipeId}/cooking-guide`)
        if (!response.ok) {
          throw new Error('Guide de cuisson non disponible')
        }
        const data = await response.json()
        setCookingData(data)
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }

    fetchCookingGuide()
  }, [recipeId])

  // Gestion du timer
  useEffect(() => {
    let interval = null
    if (isTimerRunning && timer > 0) {
      interval = setInterval(() => {
        setTimer(timer => timer - 1)
      }, 1000)
    } else if (timer === 0 && isTimerRunning) {
      setIsTimerRunning(false)
      // Notification sonore ou visuelle quand le timer se termine
      if ('Notification' in window && Notification.permission === 'granted') {
        new Notification('Étape terminée !', {
          body: 'Le temps pour cette étape est écoulé.',
          icon: '/favicon.ico'
        })
      }
    }
    return () => clearInterval(interval)
  }, [isTimerRunning, timer])

  const startTimer = (minutes) => {
    setTimer(minutes * 60)
    setIsTimerRunning(true)
  }

  const pauseTimer = () => {
    setIsTimerRunning(!isTimerRunning)
  }

  const resetTimer = () => {
    setIsTimerRunning(false)
    setTimer(0)
  }

  const markStepCompleted = (stepIndex) => {
    setCompletedSteps(prev => new Set([...prev, stepIndex]))
    if (stepIndex === currentStep && stepIndex < cookingData.cooking_steps.length - 1) {
      setCurrentStep(stepIndex + 1)
    }
  }

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <ChefHat className="w-12 h-12 text-gray-400 mx-auto mb-4 animate-pulse" />
          <p className="text-gray-600">Préparation du guide de cuisson...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <AlertTriangle className="w-12 h-12 text-red-400 mx-auto mb-4" />
          <p className="text-red-600 mb-4">{error}</p>
          <Button onClick={onBack} variant="outline">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Retour aux recettes
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen overflow-x-hidden">
      <div className="px-2 py-4 sm:px-4 sm:py-6">
        {/* Header */}
        <div className="mb-4 sm:mb-6">
          <div className="text-center">
            <h1 className="text-lg sm:text-xl lg:text-2xl font-bold text-gray-900 px-2">
              {cookingData.recipe_name}
            </h1>
            <div className="flex flex-wrap items-center justify-center gap-1 sm:gap-3 mt-2 sm:mt-3">
              <span className={`px-1.5 py-0.5 sm:px-2 sm:py-1 rounded-full text-xs font-medium border ${DIFFICULTY_COLORS[cookingData.difficulty_level]}`}>
                {DIFFICULTY_LABELS[cookingData.difficulty_level]}
              </span>
              <div className="flex items-center text-gray-600 text-xs sm:text-sm">
                <Clock className="w-3 h-3 sm:w-4 sm:h-4 mr-1" />
                <span>{cookingData.prep_time + cookingData.cook_time} min</span>
              </div>
              <div className="flex items-center text-gray-600 text-xs sm:text-sm">
                <Users className="w-3 h-3 sm:w-4 sm:h-4 mr-1" />
                <span>{cookingData.servings} portion{cookingData.servings > 1 ? 's' : ''}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Contenu principal - Responsive Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-2 sm:gap-4">
          {/* Colonne principale - Étapes de cuisson */}
          <div className="lg:col-span-2 space-y-2 sm:space-y-4">
            {/* Timer */}
            {timer > 0 && (
              <Card className="border-orange-200 bg-orange-50">
                <CardContent className="p-3 sm:p-4">
                  <div className="flex flex-col sm:flex-row items-center justify-between gap-2 sm:gap-3">
                    <div className="flex items-center gap-2 sm:gap-4">
                      <div className="text-2xl font-mono font-bold text-orange-600">
                        {formatTime(timer)}
                      </div>
                      <div className="flex space-x-2">
                        <Button 
                          size="sm" 
                          onClick={pauseTimer}
                          variant={isTimerRunning ? "default" : "outline"}
                        >
                          {isTimerRunning ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                        </Button>
                        <Button size="sm" onClick={resetTimer} variant="outline">
                          <RotateCcw className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                    <div className="text-sm text-orange-600 font-medium">
                      Timer actif
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Étapes de cuisson */}
            <div className="space-y-2 sm:space-y-4">
              {cookingData.cooking_steps.map((step, index) => (
                <Card 
                  key={index} 
                  className={`transition-all duration-200 ${
                    index === currentStep 
                      ? 'border-blue-500 shadow-lg' 
                      : completedSteps.has(index)
                      ? 'border-green-500 bg-green-50'
                      : 'border-gray-200'
                  }`}
                >
                  <CardHeader className="p-3 sm:p-4 lg:p-6">
                    <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-2 sm:gap-3">
                      <div className="flex items-start gap-2 flex-1 min-w-0">
                        <div className={`w-7 h-7 sm:w-9 sm:h-9 rounded-full flex items-center justify-center font-bold text-xs sm:text-sm flex-shrink-0 ${
                          completedSteps.has(index)
                            ? 'bg-green-500 text-white'
                            : index === currentStep
                            ? 'bg-blue-500 text-white'
                            : 'bg-gray-200 text-gray-600'
                        }`}>
                          {completedSteps.has(index) ? <CheckCircle className="w-4 h-4 sm:w-5 sm:h-5" /> : step.step}
                        </div>
                        <div className="flex-1 min-w-0">
                          <CardTitle className="text-sm sm:text-base lg:text-lg break-words">
                            {step.title}
                          </CardTitle>
                          <div className="flex flex-wrap items-center gap-1 text-xs text-gray-600 mt-1 sm:mt-2">
                            {step.duration_minutes && (
                              <span className="flex items-center">
                                <Clock className="w-3 h-3 sm:w-4 sm:h-4 mr-1" />
                                <span className="hidden sm:inline">{step.duration_minutes} min</span>
                                <span className="sm:hidden">{step.duration_minutes}m</span>
                              </span>
                            )}
                            {step.temperature && (
                              <span className="flex items-center max-w-[120px] sm:max-w-none">
                                <span className="mr-0.5">🌡️</span>
                                <span className="truncate">{step.temperature}</span>
                              </span>
                            )}
                            {step.technique && (
                              <span className="bg-gray-100 px-1.5 py-0.5 rounded text-xs truncate max-w-[100px] sm:max-w-none">
                                {step.technique}
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                      {index === currentStep && !completedSteps.has(index) && (
                        <div className="flex flex-row gap-1 w-full sm:w-auto">
                          {step.duration_minutes && (
                            <Button 
                              size="sm" 
                              onClick={() => startTimer(step.duration_minutes)}
                              className="flex-1 sm:flex-initial px-2 sm:px-3"
                            >
                              <Clock className="w-3 h-3 sm:w-4 sm:h-4 sm:mr-1" />
                              <span className="hidden sm:inline">Timer</span>
                            </Button>
                          )}
                          <Button 
                            size="sm" 
                            onClick={() => markStepCompleted(index)}
                            className="flex-1 sm:flex-initial px-2 sm:px-3"
                          >
                            <CheckCircle className="w-3 h-3 sm:w-4 sm:h-4 sm:mr-1" />
                            <span className="hidden sm:inline">Terminé</span>
                          </Button>
                        </div>
                      )}
                    </div>
                  </CardHeader>
                  <CardContent className="p-3 sm:p-4 lg:p-6 pt-0">
                    <p className="text-xs sm:text-sm lg:text-base text-gray-700 mb-3 break-words">
                      {step.description}
                    </p>
                    
                    {/* Indices visuels pour cette étape */}
                    {cookingData.visual_cues
                      .filter(cue => cue.step_number === step.step)
                      .map((cue, cueIndex) => (
                        <div key={cueIndex} className="bg-blue-50 border border-blue-200 rounded-lg p-2 sm:p-3 mb-2 sm:mb-3">
                          <div className="flex items-start gap-1.5 sm:gap-2">
                            <Eye className="w-3 h-3 sm:w-4 sm:h-4 text-blue-500 mt-0.5 flex-shrink-0" />
                            <div className="min-w-0 flex-1">
                              <p className="font-medium text-blue-900 text-xs sm:text-sm break-words">
                                {cue.description}
                              </p>
                              <p className="text-blue-700 text-xs mt-1 break-words">
                                {cue.what_to_look_for}
                              </p>
                            </div>
                          </div>
                        </div>
                      ))}
                    
                    {/* Media references pour cette étape */}
                    {cookingData.media_references
                      .filter(media => media.step_number === step.step)
                      .map((media, mediaIndex) => (
                        <div key={mediaIndex} className="mt-2 p-2 sm:p-3 bg-gray-50 rounded-lg">
                          <div className="flex items-center gap-1.5 sm:gap-2 text-xs text-gray-600">
                            <Camera className="w-3 h-3 sm:w-4 sm:h-4" />
                            <span>{media.description}</span>
                          </div>
                        </div>
                      ))}
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>

          {/* Sidebar - Conseils et ingrédients */}
          <div className="lg:col-span-1 space-y-2 sm:space-y-4">
            {/* Ingrédients */}
            <Card>
              <CardHeader className="p-3 sm:p-4">
                <CardTitle className="text-sm sm:text-base flex items-center">
                  <ChefHat className="w-4 h-4 sm:w-5 sm:h-5 mr-2" />
                  Ingrédients
                </CardTitle>
              </CardHeader>
              <CardContent className="p-3 sm:p-4 pt-0">
                <ul className="space-y-1 sm:space-y-2">
                  {cookingData.ingredients.map((ingredient, index) => (
                    <li key={index} className="text-xs sm:text-sm break-words">
                      <span className="font-medium">{ingredient.quantity} {ingredient.unit}</span>
                      <span className="text-gray-600 ml-1 sm:ml-2">{ingredient.name}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>

            {/* Conseils du Chef */}
            <Card>
              <CardHeader className="p-3 sm:p-4">
                <CardTitle className="text-sm sm:text-base">Conseils du Chef</CardTitle>
              </CardHeader>
              <CardContent className="p-3 sm:p-4 pt-0 space-y-2 sm:space-y-3">
                {cookingData.chef_tips.map((tip, index) => {
                  const tipType = TIP_TYPES[tip.type] || TIP_TYPES.tip
                  const Icon = tipType.icon
                  
                  return (
                    <div 
                      key={index} 
                      className={`p-2 sm:p-3 rounded-lg border ${tipType.bgColor} ${tipType.borderColor}`}
                    >
                      <div className="flex items-start gap-1.5 sm:gap-2">
                        <Icon className={`w-3 h-3 sm:w-4 sm:h-4 mt-0.5 flex-shrink-0 ${tipType.color}`} />
                        <div className="min-w-0 flex-1">
                          <p className="font-medium text-xs sm:text-sm break-words">{tip.title}</p>
                          <p className="text-xs mt-1 text-gray-700 break-words">
                            {tip.description}
                          </p>
                        </div>
                      </div>
                    </div>
                  )
                })}
              </CardContent>
            </Card>

            {/* Instructions du Chef */}
            {cookingData.chef_instructions && cookingData.chef_instructions.length > 0 && (
              <Card>
                <CardHeader className="p-3 sm:p-4">
                  <CardTitle className="text-sm sm:text-base">Instructions du Chef</CardTitle>
                </CardHeader>
                <CardContent className="p-3 sm:p-4 pt-0">
                  <ul className="space-y-1 sm:space-y-2">
                    {cookingData.chef_instructions.map((instruction, index) => (
                      <li key={index} className="text-xs sm:text-sm text-gray-700 break-words">
                        • {instruction}
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}