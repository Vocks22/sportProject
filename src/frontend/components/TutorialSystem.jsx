import { useState, useEffect } from 'react'
import { X, ChevronRight, ChevronLeft, HelpCircle, Lightbulb } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'

export function TutorialSystem({ currentPage }) {
  const [isFirstVisit, setIsFirstVisit] = useState(false)
  const [currentStep, setCurrentStep] = useState(0)
  const [showTutorial, setShowTutorial] = useState(false)
  const [showHelpButton, setShowHelpButton] = useState(true)

  // Guides pour chaque page
  const tutorials = {
    dashboard: {
      title: "Bienvenue sur votre Dashboard !",
      steps: [
        {
          title: "Vue d'ensemble quotidienne",
          content: "Ici vous voyez vos repas du jour, vos calories consommées et vos objectifs. C'est votre point de départ chaque matin !",
          highlight: ".dashboard-overview"
        },
        {
          title: "Progression des repas",
          content: "Cochez vos repas au fur et à mesure de la journée. L'application calcule automatiquement vos calories et nutriments.",
          highlight: ".meals-progress"
        },
        {
          title: "Rappels importants",
          content: "N'oubliez pas vos vitamines, vos séances de sport (Mar/Jeu/Ven) et de préparer votre liste de courses le samedi !",
          highlight: ".reminders"
        }
      ]
    },
    planning: {
      title: "Planification de vos repas",
      steps: [
        {
          title: "Votre semaine de repas",
          content: "Voici votre planning hebdomadaire basé sur votre programme personnalisé. Chaque jour contient 5 repas équilibrés.",
          highlight: ".meal-planning-table"
        },
        {
          title: "Génération automatique",
          content: "Cliquez sur 'Générer Plan Auto' pour créer automatiquement une nouvelle semaine de repas variés.",
          highlight: ".auto-generate-btn"
        },
        {
          title: "Modification des repas",
          content: "Cliquez sur n'importe quel repas pour le modifier ou le remplacer par une autre recette compatible.",
          highlight: ".meal-card"
        },
        {
          title: "Résumé nutritionnel",
          content: "En bas, vous voyez le résumé de vos apports quotidiens : calories, protéines, glucides et lipides.",
          highlight: ".nutrition-summary"
        }
      ]
    },
    recipes: {
      title: "Votre bibliothèque de recettes",
      steps: [
        {
          title: "Recettes personnalisées",
          content: "Toutes ces recettes sont basées sur votre programme alimentaire. Elles respectent vos objectifs de perte de poids.",
          highlight: ".recipes-grid"
        },
        {
          title: "Filtres pratiques",
          content: "Utilisez les filtres pour trouver rapidement des recettes par type de repas : petit-déjeuner, déjeuner, dîner ou collations.",
          highlight: ".recipe-filters"
        },
        {
          title: "Informations détaillées",
          content: "Chaque recette indique les calories, protéines, temps de préparation et ustensiles nécessaires.",
          highlight: ".recipe-card"
        },
        {
          title: "Ajouter au planning",
          content: "Cliquez sur 'Ajouter' pour intégrer directement une recette dans votre planning hebdomadaire.",
          highlight: ".add-recipe-btn"
        }
      ]
    },
    shopping: {
      title: "Votre liste de courses intelligente",
      steps: [
        {
          title: "Génération automatique",
          content: "Cette liste est générée automatiquement chaque samedi en fonction de votre planning de repas de la semaine suivante.",
          highlight: ".shopping-header"
        },
        {
          title: "Organisation par catégories",
          content: "Les articles sont organisés par rayons (protéines, légumes, fruits...) pour faciliter vos courses au supermarché.",
          highlight: ".shopping-categories"
        },
        {
          title: "Quantités précises",
          content: "Chaque article indique la quantité exacte nécessaire pour la semaine, calculée selon vos portions.",
          highlight: ".item-quantities"
        },
        {
          title: "Suivi des achats",
          content: "Cochez les articles au fur et à mesure de vos courses. La barre de progression vous indique votre avancement.",
          highlight: ".shopping-progress"
        },
        {
          title: "Budget estimé",
          content: "En bas, vous voyez le budget estimé pour vos courses de la semaine (85-95€).",
          highlight: ".budget-estimate"
        },
        {
          title: "Régénérer la liste",
          content: "Si vous voulez modifier votre planning, cliquez sur 'Régénérer' pour mettre à jour automatiquement votre liste.",
          highlight: ".regenerate-btn"
        }
      ]
    },
    progress: {
      title: "Suivi de votre progression",
      steps: [
        {
          title: "Évolution de votre poids",
          content: "Suivez jour après jour votre progression vers l'objectif de -5kg ce mois. Pesez-vous chaque matin !",
          highlight: ".weight-progress"
        },
        {
          title: "Objectifs nutritionnels",
          content: "Vérifiez que vous respectez vos apports en protéines (150g), glucides (100g) et lipides (80g) chaque jour.",
          highlight: ".nutrition-targets"
        },
        {
          title: "Suivi des habitudes",
          content: "Suivez vos habitudes : repas pris, séances de sport (Mar/Jeu/Ven) et hydratation (3,5L minimum par jour).",
          highlight: ".habits-tracking"
        },
        {
          title: "Objectifs futurs",
          content: "Consultez vos prochains objectifs et recommandations pour maintenir votre rythme de perte de poids.",
          highlight: ".future-goals"
        }
      ]
    }
  }

  // Vérifier si c'est la première visite
  useEffect(() => {
    const hasVisited = localStorage.getItem(`tutorial-${currentPage}-completed`)
    if (!hasVisited) {
      setIsFirstVisit(true)
      setShowTutorial(true)
    }
  }, [currentPage])

  const currentTutorial = tutorials[currentPage]
  const totalSteps = currentTutorial?.steps.length || 0

  const nextStep = () => {
    if (currentStep < totalSteps - 1) {
      setCurrentStep(currentStep + 1)
    } else {
      completeTutorial()
    }
  }

  const prevStep = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1)
    }
  }

  const completeTutorial = () => {
    localStorage.setItem(`tutorial-${currentPage}-completed`, 'true')
    setShowTutorial(false)
    setCurrentStep(0)
    setIsFirstVisit(false)
  }

  const skipTutorial = () => {
    localStorage.setItem(`tutorial-${currentPage}-completed`, 'true')
    setShowTutorial(false)
    setCurrentStep(0)
  }

  const restartTutorial = () => {
    setCurrentStep(0)
    setShowTutorial(true)
  }

  if (!currentTutorial) return null

  return (
    <>
      {/* Bouton d'aide flottant */}
      {showHelpButton && !showTutorial && (
        <Button
          onClick={restartTutorial}
          className="fixed bottom-6 right-6 z-50 w-14 h-14 rounded-full bg-blue-500 hover:bg-blue-600 shadow-lg"
          size="sm"
        >
          <HelpCircle className="h-6 w-6 text-white" />
        </Button>
      )}

      {/* Overlay du tutoriel */}
      {showTutorial && (
        <div className="fixed inset-0 z-50 bg-black bg-opacity-50 flex items-center justify-center p-4">
          <Card className="w-full max-w-md mx-auto">
            <CardContent className="p-6">
              {/* Header */}
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-2">
                  <Lightbulb className="h-5 w-5 text-yellow-500" />
                  <h3 className="text-lg font-semibold">{currentTutorial.title}</h3>
                </div>
                <Button variant="ghost" size="sm" onClick={skipTutorial}>
                  <X className="h-4 w-4" />
                </Button>
              </div>

              {/* Indicateur de progression */}
              <div className="mb-4">
                <div className="flex justify-between text-sm text-gray-500 mb-2">
                  <span>Étape {currentStep + 1} sur {totalSteps}</span>
                  <span>{Math.round(((currentStep + 1) / totalSteps) * 100)}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${((currentStep + 1) / totalSteps) * 100}%` }}
                  ></div>
                </div>
              </div>

              {/* Contenu de l'étape */}
              <div className="mb-6">
                <h4 className="font-semibold text-gray-900 mb-2">
                  {currentTutorial.steps[currentStep]?.title}
                </h4>
                <p className="text-gray-600 leading-relaxed">
                  {currentTutorial.steps[currentStep]?.content}
                </p>
              </div>

              {/* Boutons de navigation */}
              <div className="flex justify-between">
                <div className="flex space-x-2">
                  <Button 
                    variant="outline" 
                    size="sm" 
                    onClick={prevStep}
                    disabled={currentStep === 0}
                  >
                    <ChevronLeft className="h-4 w-4 mr-1" />
                    Précédent
                  </Button>
                </div>

                <div className="flex space-x-2">
                  <Button variant="ghost" size="sm" onClick={skipTutorial}>
                    Passer
                  </Button>
                  <Button size="sm" onClick={nextStep}>
                    {currentStep === totalSteps - 1 ? 'Terminer' : 'Suivant'}
                    {currentStep !== totalSteps - 1 && <ChevronRight className="h-4 w-4 ml-1" />}
                  </Button>
                </div>
              </div>

              {/* Message de première visite */}
              {isFirstVisit && currentStep === 0 && (
                <div className="mt-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
                  <p className="text-sm text-blue-800">
                    👋 Bienvenue ! Ce guide vous explique comment utiliser cette section. 
                    Vous pouvez le relancer à tout moment avec le bouton d'aide.
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}
    </>
  )
}

