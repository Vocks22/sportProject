/**
 * Hook personnalisé pour la gestion du suivi des repas (US1.8)
 * Utilise Zustand pour l'état global et la persistance locale
 */

import React, { useState, useEffect } from 'react'
import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { apiRequest } from '../src/config/api'

/**
 * Store Zustand pour la gestion du suivi des repas
 */
export const useMealTrackingStore = create(
  persist(
    (set, get) => ({
      // État principal
      todayMealTrackings: [],
      dailySummary: null,
      isLoading: false,
      error: null,
      selectedDate: new Date().toISOString().split('T')[0],
      userId: 1, // Default user ID - should be set from auth context
      offlineMode: false,
      
      // Cache local pour les données
      cachedTrackings: {},
      cachedSummaries: {},
      lastSync: null,
      
      // Actions queue pour mode offline
      pendingActions: [],
      
      // Actions de base
      setUserId: (userId) => set({ userId }),
      
      setSelectedDate: (date) => set((state) => ({
        ...state,
        selectedDate: date,
        // Charger les données du cache si disponibles
        todayMealTrackings: state.cachedTrackings[date] || [],
        dailySummary: state.cachedSummaries[date] || null
      })),
      
      setTodayMealTrackings: (trackings) => set((state) => ({
        ...state,
        todayMealTrackings: trackings,
        cachedTrackings: {
          ...state.cachedTrackings,
          [state.selectedDate]: trackings
        }
      })),
      
      setDailySummary: (summary) => set((state) => ({
        ...state,
        dailySummary: summary,
        cachedSummaries: {
          ...state.cachedSummaries,
          [state.selectedDate]: summary
        }
      })),
      
      updateMealTracking: (trackingId, updatedData) => set((state) => {
        const updatedTrackings = state.todayMealTrackings.map(tracking =>
          tracking.id === trackingId 
            ? { ...tracking, ...updatedData }
            : tracking
        )
        
        return {
          ...state,
          todayMealTrackings: updatedTrackings,
          cachedTrackings: {
            ...state.cachedTrackings,
            [state.selectedDate]: updatedTrackings
          }
        }
      }),
      
      setLoading: (loading) => set({ isLoading: loading }),
      
      setError: (error) => set({ error }),
      
      clearError: () => set({ error: null }),
      
      setOfflineMode: (offline) => set({ offlineMode: offline }),
      
      addPendingAction: (action) => set((state) => ({
        ...state,
        pendingActions: [
          ...state.pendingActions,
          { ...action, timestamp: Date.now(), userId: state.userId }
        ]
      })),
      
      removePendingAction: (actionId) => set((state) => ({
        ...state,
        pendingActions: state.pendingActions.filter(action => action.id !== actionId)
      })),
      
      clearPendingActions: () => set({ pendingActions: [] }),
      
      updateLastSync: () => set({ lastSync: Date.now() }),
      
      // Getters calculés
      getTodayNutritionTotals: () => {
        const state = get()
        if (!state.todayMealTrackings.length) {
          return { calories: 0, protein: 0, carbs: 0, fat: 0, fiber: 0, sodium: 0, sugar: 0 }
        }
        
        return state.todayMealTrackings.reduce((totals, tracking) => {
          // Utiliser les valeurs effectives : actual si consommé/modifié, sinon planned
          const isConsumed = ['consumed', 'modified', 'replaced'].includes(tracking.status)
          
          const effectiveCalories = isConsumed && tracking.actual_calories !== null 
            ? tracking.actual_calories 
            : tracking.planned_calories || 0
            
          const effectiveProtein = isConsumed && tracking.actual_protein !== null 
            ? tracking.actual_protein 
            : tracking.planned_protein || 0
            
          const effectiveCarbs = isConsumed && tracking.actual_carbs !== null 
            ? tracking.actual_carbs 
            : tracking.planned_carbs || 0
            
          const effectiveFat = isConsumed && tracking.actual_fat !== null 
            ? tracking.actual_fat 
            : tracking.planned_fat || 0
            
          const effectiveFiber = isConsumed && tracking.actual_fiber !== null 
            ? tracking.actual_fiber 
            : tracking.planned_fiber || 0
            
          const effectiveSodium = isConsumed && tracking.actual_sodium !== null 
            ? tracking.actual_sodium 
            : tracking.planned_sodium || 0
            
          const effectiveSugar = isConsumed && tracking.actual_sugar !== null 
            ? tracking.actual_sugar 
            : tracking.planned_sugar || 0
          
          return {
            calories: totals.calories + effectiveCalories,
            protein: totals.protein + effectiveProtein,
            carbs: totals.carbs + effectiveCarbs,
            fat: totals.fat + effectiveFat,
            fiber: totals.fiber + effectiveFiber,
            sodium: totals.sodium + effectiveSodium,
            sugar: totals.sugar + effectiveSugar
          }
        }, { calories: 0, protein: 0, carbs: 0, fat: 0, fiber: 0, sodium: 0, sugar: 0 })
      },
      
      getMealCompletionStats: () => {
        const state = get()
        if (!state.todayMealTrackings.length) {
          return { total: 0, consumed: 0, skipped: 0, planned: 0, percentage: 0 }
        }
        
        const total = state.todayMealTrackings.length
        const consumed = state.todayMealTrackings.filter(t => 
          ['consumed', 'modified', 'replaced'].includes(t.status)
        ).length
        const skipped = state.todayMealTrackings.filter(t => t.status === 'skipped').length
        const planned = state.todayMealTrackings.filter(t => t.status === 'planned').length
        
        return {
          total,
          consumed,
          skipped,
          planned,
          percentage: total > 0 ? Math.round((consumed / total) * 100) : 0
        }
      },
      
      getMealsByType: () => {
        const state = get()
        const mealsByType = {
          repas1: null,
          repas2: null,
          repas3: null,
          collation: null
        }
        
        state.todayMealTrackings.forEach(tracking => {
          mealsByType[tracking.meal_type] = tracking
        })
        
        return mealsByType
      },
      
      getPendingActionsCount: () => {
        const state = get()
        return state.pendingActions.length
      }
    }),
    {
      name: 'meal-tracking-storage',
      partialize: (state) => ({
        cachedTrackings: state.cachedTrackings,
        cachedSummaries: state.cachedSummaries,
        lastSync: state.lastSync,
        pendingActions: state.pendingActions,
        userId: state.userId,
        selectedDate: state.selectedDate
      })
    }
  )
)

/**
 * Hook principal pour les opérations de suivi des repas
 */
export const useMealTracking = () => {
  const store = useMealTrackingStore()
  
  // Charger les données du jour
  const loadTodayMealTrackings = async (forceRefresh = false) => {
    const { selectedDate, userId, cachedTrackings } = store
    
    // Utiliser le cache si disponible et pas de refresh forcé
    if (!forceRefresh && cachedTrackings[selectedDate] && cachedTrackings[selectedDate].length > 0) {
      store.setTodayMealTrackings(cachedTrackings[selectedDate])
      return
    }
    
    store.setLoading(true)
    store.clearError()
    
    try {
      const data = await apiRequest(`meal-tracking/today?user_id=${userId}`)
      
      store.setTodayMealTrackings(data.meal_trackings || [])
      store.setDailySummary(data.daily_summary)
      store.updateLastSync()
      
      return data
    } catch (error) {
      store.setError(`Erreur lors du chargement des repas: ${error.message}`)
      
      // Utiliser le cache en cas d'erreur réseau
      if (error.message.includes('fetch') || error.message.includes('network')) {
        store.setOfflineMode(true)
        const cachedData = cachedTrackings[selectedDate]
        if (cachedData) {
          store.setTodayMealTrackings(cachedData)
        }
      }
      
      return null
    } finally {
      store.setLoading(false)
    }
  }
  
  // Marquer un repas comme consommé
  const markMealConsumed = async (trackingId, consumptionData = {}) => {
    // Mise à jour optimiste
    store.updateMealTracking(trackingId, { 
      status: 'consumed',
      consumption_datetime: new Date().toISOString(),
      ...consumptionData
    })
    
    const actionId = `consume_${trackingId}_${Date.now()}`
    
    try {
      if (!store.offlineMode) {
        const data = await apiRequest(`meal-tracking/${trackingId}/consume`, {
          method: 'POST',
          body: JSON.stringify({
            user_id: store.userId,
            consumption_data: {
              consumption_time: new Date().toISOString(),
              ...consumptionData
            }
          })
        })
        
        if (data.success) {
          store.updateMealTracking(trackingId, data.meal_tracking)
          // Recalculer le résumé quotidien
          await loadDailySummary(true)
        }
      } else {
        // Mode offline - ajouter à la queue
        store.addPendingAction({
          id: actionId,
          type: 'consume_meal',
          trackingId,
          consumptionData,
          selectedDate: store.selectedDate
        })
      }
    } catch (error) {
      // Annuler la mise à jour optimiste
      store.updateMealTracking(trackingId, { status: 'planned' })
      store.setError(`Erreur lors de la confirmation du repas: ${error.message}`)
      
      if (error.message.includes('fetch')) {
        store.setOfflineMode(true)
        store.addPendingAction({
          id: actionId,
          type: 'consume_meal',
          trackingId,
          consumptionData,
          selectedDate: store.selectedDate
        })
        // Rétablir l'état souhaité
        store.updateMealTracking(trackingId, { 
          status: 'consumed',
          consumption_datetime: new Date().toISOString(),
          ...consumptionData
        })
      }
    }
  }
  
  // Ajuster les portions d'un repas
  const adjustMealPortions = async (trackingId, portionMultiplier, customNutrition = {}) => {
    const actionId = `adjust_${trackingId}_${Date.now()}`
    
    // Mise à jour optimiste
    store.updateMealTracking(trackingId, {
      status: 'modified',
      actual_portion_size: portionMultiplier
    })
    
    try {
      if (!store.offlineMode) {
        const data = await apiRequest(`meal-tracking/${trackingId}/adjust`, {
          method: 'PUT',
          body: JSON.stringify({
            user_id: store.userId,
            portion_multiplier: portionMultiplier,
            nutrition: customNutrition
          })
        })
        
        if (data.success) {
          store.updateMealTracking(trackingId, data.meal_tracking)
          await loadDailySummary(true)
        }
      } else {
        store.addPendingAction({
          id: actionId,
          type: 'adjust_portions',
          trackingId,
          portionMultiplier,
          customNutrition,
          selectedDate: store.selectedDate
        })
      }
    } catch (error) {
      // Annuler la mise à jour optimiste
      store.updateMealTracking(trackingId, { status: 'planned', actual_portion_size: null })
      store.setError(`Erreur lors de l'ajustement des portions: ${error.message}`)
      
      if (error.message.includes('fetch')) {
        store.setOfflineMode(true)
        store.addPendingAction({
          id: actionId,
          type: 'adjust_portions',
          trackingId,
          portionMultiplier,
          customNutrition,
          selectedDate: store.selectedDate
        })
        store.updateMealTracking(trackingId, {
          status: 'modified',
          actual_portion_size: portionMultiplier
        })
      }
    }
  }
  
  // Ignorer un repas
  const skipMeal = async (trackingId, reason = '') => {
    const actionId = `skip_${trackingId}_${Date.now()}`
    
    // Mise à jour optimiste
    store.updateMealTracking(trackingId, { 
      status: 'skipped',
      skip_reason: reason 
    })
    
    try {
      if (!store.offlineMode) {
        const data = await apiRequest(`meal-tracking/${trackingId}/skip`, {
          method: 'POST',
          body: JSON.stringify({
            user_id: store.userId,
            skip_data: { reason }
          })
        })
        
        if (data.success) {
          store.updateMealTracking(trackingId, data.meal_tracking)
          await loadDailySummary(true)
        }
      } else {
        store.addPendingAction({
          id: actionId,
          type: 'skip_meal',
          trackingId,
          reason,
          selectedDate: store.selectedDate
        })
      }
    } catch (error) {
      // Annuler la mise à jour optimiste
      store.updateMealTracking(trackingId, { status: 'planned', skip_reason: null })
      store.setError(`Erreur lors de l'omission du repas: ${error.message}`)
      
      if (error.message.includes('fetch')) {
        store.setOfflineMode(true)
        store.addPendingAction({
          id: actionId,
          type: 'skip_meal',
          trackingId,
          reason,
          selectedDate: store.selectedDate
        })
        store.updateMealTracking(trackingId, { 
          status: 'skipped',
          skip_reason: reason 
        })
      }
    }
  }
  
  // Remplacer un repas
  const replaceMeal = async (trackingId, replacementData = {}) => {
    const actionId = `replace_${trackingId}_${Date.now()}`
    
    // Mise à jour optimiste
    store.updateMealTracking(trackingId, { 
      status: 'replaced',
      replacement_name: replacementData.replacement_name,
      replacement_reason: replacementData.reason
    })
    
    try {
      if (!store.offlineMode) {
        const data = await apiRequest(`meal-tracking/${trackingId}/replace`, {
          method: 'POST',
          body: JSON.stringify({
            user_id: store.userId,
            replacement_data: replacementData
          })
        })
        
        if (data.success) {
          store.updateMealTracking(trackingId, data.meal_tracking)
          await loadDailySummary(true)
        }
      } else {
        store.addPendingAction({
          id: actionId,
          type: 'replace_meal',
          trackingId,
          replacementData,
          selectedDate: store.selectedDate
        })
      }
    } catch (error) {
      // Annuler la mise à jour optimiste
      store.updateMealTracking(trackingId, { 
        status: 'planned', 
        replacement_name: null,
        replacement_reason: null 
      })
      store.setError(`Erreur lors du remplacement du repas: ${error.message}`)
      
      if (error.message.includes('fetch')) {
        store.setOfflineMode(true)
        store.addPendingAction({
          id: actionId,
          type: 'replace_meal',
          trackingId,
          replacementData,
          selectedDate: store.selectedDate
        })
        store.updateMealTracking(trackingId, { 
          status: 'replaced',
          replacement_name: replacementData.replacement_name,
          replacement_reason: replacementData.reason
        })
      }
    }
  }
  
  // Charger le résumé quotidien
  const loadDailySummary = async (forceRefresh = false) => {
    const { selectedDate, userId, cachedSummaries } = store
    
    if (!forceRefresh && cachedSummaries[selectedDate]) {
      store.setDailySummary(cachedSummaries[selectedDate])
      return
    }
    
    try {
      const data = await apiRequest(`meal-tracking/summary/${selectedDate}?user_id=${userId}`)
      
      if (data.success) {
        store.setDailySummary(data.daily_summary)
      }
      
      return data
    } catch (error) {
      console.error('Erreur lors du chargement du résumé:', error)
      return null
    }
  }
  
  // Synchroniser les actions en attente
  const syncPendingActions = async () => {
    const { pendingActions } = store
    if (pendingActions.length === 0) return
    
    store.setLoading(true)
    
    const successfulActions = []
    
    try {
      for (const action of pendingActions) {
        try {
          switch (action.type) {
            case 'consume_meal':
              await apiRequest(`meal-tracking/${action.trackingId}/consume`, {
                method: 'POST',
                body: JSON.stringify({
                  user_id: action.userId,
                  consumption_data: action.consumptionData
                })
              })
              break
              
            case 'adjust_portions':
              await apiRequest(`meal-tracking/${action.trackingId}/adjust`, {
                method: 'PUT',
                body: JSON.stringify({
                  user_id: action.userId,
                  portion_multiplier: action.portionMultiplier,
                  nutrition: action.customNutrition
                })
              })
              break
              
            case 'skip_meal':
              await apiRequest(`meal-tracking/${action.trackingId}/skip`, {
                method: 'POST',
                body: JSON.stringify({
                  user_id: action.userId,
                  skip_data: { reason: action.reason }
                })
              })
              break
              
            case 'replace_meal':
              await apiRequest(`meal-tracking/${action.trackingId}/replace`, {
                method: 'POST',
                body: JSON.stringify({
                  user_id: action.userId,
                  replacement_data: action.replacementData
                })
              })
              break
          }
          
          successfulActions.push(action.id)
        } catch (actionError) {
          console.error(`Erreur lors de la synchronisation de l'action ${action.type}:`, actionError)
        }
      }
      
      // Supprimer les actions réussies
      successfulActions.forEach(actionId => {
        store.removePendingAction(actionId)
      })
      
      if (successfulActions.length > 0) {
        store.updateLastSync()
        store.setOfflineMode(false)
        // Recharger les données pour synchroniser
        await loadTodayMealTrackings(true)
      }
      
    } catch (error) {
      console.error('Erreur lors de la synchronisation globale:', error)
    } finally {
      store.setLoading(false)
    }
    
    return successfulActions.length
  }
  
  // Changer de date sélectionnée
  const changeSelectedDate = async (newDate) => {
    store.setSelectedDate(newDate)
    await loadTodayMealTrackings()
  }
  
  return {
    // État
    todayMealTrackings: store.todayMealTrackings,
    dailySummary: store.dailySummary,
    isLoading: store.isLoading,
    error: store.error,
    offlineMode: store.offlineMode,
    selectedDate: store.selectedDate,
    userId: store.userId,
    pendingActionsCount: store.getPendingActionsCount(),
    
    // Actions
    setUserId: store.setUserId,
    loadTodayMealTrackings,
    loadDailySummary,
    changeSelectedDate,
    markMealConsumed,
    adjustMealPortions,
    skipMeal,
    replaceMeal,
    syncPendingActions,
    clearError: store.clearError,
    
    // Getters calculés
    todayNutritionTotals: store.getTodayNutritionTotals(),
    mealCompletionStats: store.getMealCompletionStats(),
    mealsByType: store.getMealsByType()
  }
}

/**
 * Hook pour la détection du statut réseau (réutilise la logique existante)
 */
export const useMealTrackingNetworkStatus = () => {
  const setOfflineMode = useMealTrackingStore(state => state.setOfflineMode)
  const offlineMode = useMealTrackingStore(state => state.offlineMode)
  
  React.useEffect(() => {
    const isOffline = !navigator.onLine
    if (offlineMode !== isOffline) {
      setOfflineMode(isOffline)
    }
  }, [])
  
  React.useEffect(() => {
    const handleOnline = () => {
      setOfflineMode(false)
    }
    
    const handleOffline = () => {
      setOfflineMode(true)
    }
    
    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)
    
    return () => {
      window.removeEventListener('online', handleOnline)
      window.removeEventListener('offline', handleOffline)
    }
  }, [setOfflineMode])
  
  return { offlineMode }
}

export default useMealTracking