/**
 * Hook React pour la gestion des semaines ISO 8601 (lundi-dimanche)
 * US1.6 - Semaines Lundi-Dimanche
 * 
 * Ce hook fournit des utilitaires pour:
 * - Calculer les lundis et dimanche de semaines ISO 8601
 * - Naviguer entre les semaines
 * - Formater les affichages de semaines
 * - Identifier la semaine courante et prochaine
 */

import { useState, useCallback, useMemo } from 'react'

// Utilitaires ISO 8601
const getISOWeekMonday = (date) => {
  const d = new Date(date)
  const day = d.getDay()
  const diff = d.getDate() - day + (day === 0 ? -6 : 1) // Ajustement pour dimanche
  return new Date(d.setDate(diff))
}

const getISOWeekSunday = (date) => {
  const monday = getISOWeekMonday(date)
  return new Date(monday.getTime() + (6 * 24 * 60 * 60 * 1000))
}

const formatDateForAPI = (date) => {
  return date.toISOString().split('T')[0]
}

const formatDateForDisplay = (date, locale = 'fr') => {
  return date.toLocaleDateString(locale, {
    weekday: 'short',
    day: 'numeric',
    month: 'short'
  })
}

const formatWeekRange = (monday, locale = 'fr') => {
  const sunday = getISOWeekSunday(monday)
  
  if (locale === 'fr') {
    const monthNames = [
      'janvier', 'février', 'mars', 'avril', 'mai', 'juin',
      'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre'
    ]
    
    if (monday.getMonth() === sunday.getMonth()) {
      return `Semaine du ${monday.getDate()} au ${sunday.getDate()} ${monthNames[monday.getMonth()]} ${monday.getFullYear()}`
    } else {
      return `Semaine du ${monday.getDate()} ${monthNames[monday.getMonth()]} au ${sunday.getDate()} ${monthNames[sunday.getMonth()]} ${sunday.getFullYear()}`
    }
  }
  
  // English fallback
  if (monday.getMonth() === sunday.getMonth()) {
    return `Week of ${monday.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })} to ${sunday.getDate()}, ${monday.getFullYear()}`
  } else {
    return `Week of ${monday.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })} to ${sunday.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}`
  }
}

const isSameWeek = (date1, date2) => {
  const monday1 = getISOWeekMonday(date1)
  const monday2 = getISOWeekMonday(date2)
  return monday1.getTime() === monday2.getTime()
}

const isCurrentWeek = (date) => {
  return isSameWeek(date, new Date())
}

const isNextWeek = (date) => {
  const nextWeek = new Date()
  nextWeek.setDate(nextWeek.getDate() + 7)
  return isSameWeek(date, nextWeek)
}

const getWeekType = (date) => {
  if (isCurrentWeek(date)) return 'current'
  if (isNextWeek(date)) return 'next'
  
  const now = new Date()
  const monday = getISOWeekMonday(date)
  
  if (monday < getISOWeekMonday(now)) return 'past'
  return 'future'
}

/**
 * Hook principal useISOWeek
 * @param {Date|string} initialWeek - Semaine initiale (optionnelle, par défaut: semaine courante)
 * @returns {Object} Objet avec les propriétés et méthodes de gestion des semaines ISO 8601
 */
export const useISOWeek = (initialWeek = null) => {
  // État de la semaine courante sélectionnée
  const [selectedWeek, setSelectedWeek] = useState(() => {
    if (initialWeek) {
      return typeof initialWeek === 'string' ? new Date(initialWeek) : new Date(initialWeek)
    }
    return new Date()
  })

  // Calculer le lundi de la semaine sélectionnée
  const currentMonday = useMemo(() => {
    return getISOWeekMonday(selectedWeek)
  }, [selectedWeek])

  // Calculer le dimanche de la semaine sélectionnée
  const currentSunday = useMemo(() => {
    return getISOWeekSunday(selectedWeek)
  }, [selectedWeek])

  // Informations sur la semaine actuelle
  const weekInfo = useMemo(() => {
    const monday = currentMonday
    const sunday = currentSunday
    const type = getWeekType(monday)
    
    return {
      monday,
      sunday,
      mondayISO: formatDateForAPI(monday),
      sundayISO: formatDateForAPI(sunday),
      displayRange: formatWeekRange(monday),
      weekNumber: getISOWeekNumber(monday),
      year: getISOWeekYear(monday),
      type,
      isCurrentWeek: type === 'current',
      isNextWeek: type === 'next',
      isPastWeek: type === 'past',
      isFutureWeek: type === 'future'
    }
  }, [currentMonday, currentSunday])

  // Jours de la semaine avec informations détaillées
  const weekDays = useMemo(() => {
    const days = []
    const monday = currentMonday
    
    const dayLabels = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim']
    const dayKeys = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    
    for (let i = 0; i < 7; i++) {
      const dayDate = new Date(monday)
      dayDate.setDate(monday.getDate() + i)
      
      const isToday = dayDate.toDateString() === new Date().toDateString()
      
      days.push({
        key: dayKeys[i],
        label: dayLabels[i],
        date: dayDate,
        dateISO: formatDateForAPI(dayDate),
        dayNumber: dayDate.getDate(),
        displayDate: formatDateForDisplay(dayDate),
        isToday,
        isWeekend: i >= 5, // Samedi et dimanche
      })
    }
    
    return days
  }, [currentMonday])

  // Navigation entre les semaines
  const goToPreviousWeek = useCallback(() => {
    setSelectedWeek(prev => {
      const newDate = new Date(prev)
      newDate.setDate(newDate.getDate() - 7)
      return newDate
    })
  }, [])

  const goToNextWeek = useCallback(() => {
    setSelectedWeek(prev => {
      const newDate = new Date(prev)
      newDate.setDate(newDate.getDate() + 7)
      return newDate
    })
  }, [])

  const goToCurrentWeek = useCallback(() => {
    setSelectedWeek(new Date())
  }, [])

  const goToWeek = useCallback((date) => {
    setSelectedWeek(typeof date === 'string' ? new Date(date) : new Date(date))
  }, [])

  // Navigation spécifique
  const goToNextWeekFromToday = useCallback(() => {
    const nextWeek = new Date()
    nextWeek.setDate(nextWeek.getDate() + 7)
    setSelectedWeek(nextWeek)
  }, [])

  // Utilitaires de comparaison
  const isSameWeekAs = useCallback((otherDate) => {
    return isSameWeek(selectedWeek, otherDate)
  }, [selectedWeek])

  const isWeekType = useCallback((type) => {
    return weekInfo.type === type
  }, [weekInfo.type])

  return {
    // État de la semaine
    selectedWeek,
    weekInfo,
    weekDays,
    
    // Navigation
    goToPreviousWeek,
    goToNextWeek,
    goToCurrentWeek,
    goToWeek,
    goToNextWeekFromToday,
    
    // Comparaisons
    isSameWeekAs,
    isWeekType,
    
    // Utilitaires directs
    formatWeekRange: (date) => formatWeekRange(getISOWeekMonday(date)),
    getWeekMonday: getISOWeekMonday,
    getWeekSunday: getISOWeekSunday,
    formatDateForAPI,
    formatDateForDisplay,
    getWeekType,
    isCurrentWeek,
    isNextWeek,
  }
}

// Utilitaires ISO 8601 pour numéro de semaine
function getISOWeekNumber(date) {
  const d = new Date(date.getTime())
  d.setHours(0, 0, 0, 0)
  // Jeudi de cette semaine
  d.setDate(d.getDate() + 3 - (d.getDay() + 6) % 7)
  // 1er janvier
  const week1 = new Date(d.getFullYear(), 0, 4)
  // Calculer le numéro de semaine
  return 1 + Math.round(((d.getTime() - week1.getTime()) / 86400000 - 3 + (week1.getDay() + 6) % 7) / 7)
}

function getISOWeekYear(date) {
  const d = new Date(date.getTime())
  d.setDate(d.getDate() + 3 - (d.getDay() + 6) % 7)
  return d.getFullYear()
}

// Hook spécialisé pour les listes de courses "semaine prochaine"
export const useNextWeekShopping = () => {
  const { 
    weekInfo: nextWeekInfo, 
    weekDays: nextWeekDays,
    goToCurrentWeek: goBackToCurrentWeek
  } = useISOWeek(new Date(Date.now() + 7 * 24 * 60 * 60 * 1000))

  return {
    nextWeekInfo,
    nextWeekDays,
    goBackToCurrentWeek,
    displayText: `Liste pour ${nextWeekInfo.displayRange}`,
    isNextWeekFromToday: nextWeekInfo.isNextWeek
  }
}

// Hook pour la planification de repas avec navigation
export const useMealPlanningWeek = (initialWeek = null) => {
  const weekHook = useISOWeek(initialWeek)
  
  // Calculer les métriques de planification
  const planningMetrics = useMemo(() => {
    const { weekInfo } = weekHook
    
    return {
      canPlanMeals: weekInfo.type !== 'past',
      planningRecommendation: weekInfo.type === 'current' 
        ? 'Planification pour cette semaine' 
        : weekInfo.type === 'next'
        ? 'Planification pour la semaine prochaine'
        : weekInfo.type === 'future'
        ? 'Planification avancée'
        : 'Semaine passée (consultation uniquement)',
      urgencyLevel: weekInfo.type === 'current' ? 'high' : 
                    weekInfo.type === 'next' ? 'medium' : 'low'
    }
  }, [weekHook.weekInfo])

  return {
    ...weekHook,
    planningMetrics
  }
}

export default useISOWeek