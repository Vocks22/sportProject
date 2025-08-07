/**
 * Hook personnalisé pour la gestion des listes de courses interactives (US1.5)
 * Utilise Zustand pour l'état global et IndexedDB pour la persistance offline
 */

import React from 'react'
import { create } from 'zustand'
import { subscribeWithSelector, persist } from 'zustand/middleware'
import { immer } from 'zustand/middleware/immer'

// Configuration IndexedDB pour la persistance offline
const INDEXED_DB_CONFIG = {
  name: 'diettracker-shopping',
  version: 1,
  stores: {
    shoppingLists: 'id',
    checkedItems: 'listId',
    offlineActions: '++id'
  }
}

/**
 * Store Zustand pour la gestion des listes de courses
 */
export const useShoppingListStore = create(
  subscribeWithSelector(
    persist(
      immer((set, get) => ({
        // État principal
        currentList: null,
        checkedItems: {},
        isLoading: false,
        error: null,
        offlineMode: false,
        
        // Cache local
        cachedLists: {},
        lastSync: null,
        
        // Actions queue pour mode offline
        pendingActions: [],
        
        // Actions
        setCurrentList: (list) => set((state) => {
          state.currentList = list
          if (list) {
            state.cachedLists[list.id] = list
            // Initialiser l'état des cases cochées
            if (list.checked_items) {
              state.checkedItems = { ...state.checkedItems, ...list.checked_items }
            }
          }
        }),
        
        toggleItem: (itemId, checked, optimistic = true) => set((state) => {
          // Mise à jour optimiste
          if (optimistic) {
            state.checkedItems[itemId] = checked
            
            // Mettre à jour l'item dans la liste actuelle
            if (state.currentList?.items) {
              const item = state.currentList.items.find(item => 
                String(item.id) === String(itemId)
              )
              if (item) {
                item.checked = checked
              }
            }
          }
          
          // Ajouter l'action à la queue si offline
          if (state.offlineMode) {
            state.pendingActions.push({
              type: 'toggle_item',
              itemId,
              checked,
              timestamp: Date.now(),
              listId: state.currentList?.id
            })
          }
        }),
        
        bulkToggleItems: (itemUpdates, optimistic = true) => set((state) => {
          if (optimistic) {
            itemUpdates.forEach(({ itemId, checked }) => {
              state.checkedItems[itemId] = checked
              
              // Mettre à jour dans la liste actuelle
              if (state.currentList?.items) {
                const item = state.currentList.items.find(item => 
                  String(item.id) === String(itemId)
                )
                if (item) {
                  item.checked = checked
                }
              }
            })
          }
          
          // Ajouter à la queue si offline
          if (state.offlineMode) {
            state.pendingActions.push({
              type: 'bulk_toggle',
              items: itemUpdates,
              timestamp: Date.now(),
              listId: state.currentList?.id
            })
          }
        }),
        
        updateListData: (listData) => set((state) => {
          if (state.currentList && state.currentList.id === listData.id) {
            state.currentList = { ...state.currentList, ...listData }
            state.cachedLists[listData.id] = state.currentList
          }
        }),
        
        setLoading: (loading) => set((state) => {
          state.isLoading = loading
        }),
        
        setError: (error) => set((state) => {
          state.error = error
        }),
        
        clearError: () => set((state) => {
          state.error = null
        }),
        
        setOfflineMode: (offline) => set((state) => {
          state.offlineMode = offline
        }),
        
        addPendingAction: (action) => set((state) => {
          state.pendingActions.push({
            ...action,
            timestamp: Date.now()
          })
        }),
        
        clearPendingActions: () => set((state) => {
          state.pendingActions = []
        }),
        
        updateLastSync: () => set((state) => {
          state.lastSync = Date.now()
        }),
        
        // Getters calculés
        getCompletionStats: () => {
          const state = get()
          if (!state.currentList?.items) {
            return { total: 0, completed: 0, percentage: 0 }
          }
          
          const total = state.currentList.items.length
          const completed = state.currentList.items.filter(item => 
            state.checkedItems[String(item.id)]
          ).length
          
          return {
            total,
            completed,
            percentage: total > 0 ? Math.round((completed / total) * 100) : 0
          }
        },
        
        getItemsByCategory: () => {
          const state = get()
          if (!state.currentList?.items) return {}
          
          const categorized = {}
          state.currentList.items.forEach(item => {
            const category = item.category || 'other'
            if (!categorized[category]) {
              categorized[category] = []
            }
            categorized[category].push({
              ...item,
              checked: state.checkedItems[String(item.id)] || false
            })
          })
          
          return categorized
        },
        
        getPendingActionsCount: () => {
          const state = get()
          return state.pendingActions.length
        }
      })),
      {
        name: 'shopping-list-storage',
        partialize: (state) => ({
          checkedItems: state.checkedItems,
          cachedLists: state.cachedLists,
          lastSync: state.lastSync,
          pendingActions: state.pendingActions
        })
      }
    )
  )
)

/**
 * Hook pour les opérations de liste de courses
 */
export const useShoppingList = () => {
  const store = useShoppingListStore()
  
  const toggleItemStatus = async (itemId, checked) => {
    // Mise à jour optimiste
    store.toggleItem(itemId, checked, true)
    
    try {
      if (!store.offlineMode && store.currentList) {
        // Appel API
        const response = await fetch(
          `/api/shopping-lists/${store.currentList.id}/items/${itemId}/toggle`,
          {
            method: 'PATCH',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ checked })
          }
        )
        
        if (!response.ok) {
          throw new Error('Échec de la mise à jour')
        }
        
        const result = await response.json()
        store.updateListData(result.shopping_list)
        
      }
    } catch (error) {
      // Annuler la mise à jour optimiste en cas d'erreur
      store.toggleItem(itemId, !checked, true)
      store.setError(`Erreur lors de la mise à jour: ${error.message}`)
      
      // Passer en mode offline si erreur réseau
      if (error.message.includes('fetch')) {
        store.setOfflineMode(true)
        store.toggleItem(itemId, checked, true) // Rétablir l'état souhaité
      }
    }
  }
  
  const bulkToggleItems = async (itemUpdates) => {
    // Mise à jour optimiste
    store.bulkToggleItems(itemUpdates, true)
    
    try {
      if (!store.offlineMode && store.currentList) {
        const response = await fetch(
          `/api/shopping-lists/${store.currentList.id}/bulk-toggle`,
          {
            method: 'PATCH',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
              items: itemUpdates.map(({ itemId, checked }) => ({
                item_id: itemId,
                checked
              }))
            })
          }
        )
        
        if (!response.ok) {
          throw new Error('Échec de la mise à jour groupée')
        }
        
        const result = await response.json()
        store.updateListData(result.shopping_list)
      }
    } catch (error) {
      // Annuler les mises à jour optimistes
      const revertUpdates = itemUpdates.map(({ itemId, checked }) => ({
        itemId,
        checked: !checked
      }))
      store.bulkToggleItems(revertUpdates, true)
      store.setError(`Erreur lors de la mise à jour groupée: ${error.message}`)
      
      if (error.message.includes('fetch')) {
        store.setOfflineMode(true)
        store.bulkToggleItems(itemUpdates, true) // Rétablir l'état souhaité
      }
    }
  }
  
  const regenerateList = async (preserveChecked = true) => {
    if (!store.currentList) return
    
    store.setLoading(true)
    
    try {
      const response = await fetch(
        `/api/shopping-lists/${store.currentList.id}/regenerate`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            preserve_checked_items: preserveChecked
          })
        }
      )
      
      if (!response.ok) {
        throw new Error('Échec de la régénération')
      }
      
      const result = await response.json()
      if (result.success) {
        store.setCurrentList(result.shopping_list)
        
        // Enregistrer l'action dans l'historique local
        store.addPendingAction({
          type: 'regenerated',
          preserve_checked_items: preserveChecked,
          listId: store.currentList.id
        })
      } else {
        throw new Error(result.error || 'Erreur inconnue')
      }
      
    } catch (error) {
      store.setError(`Erreur lors de la régénération: ${error.message}`)
      
      // Passer en mode offline si erreur réseau
      if (error.message.includes('fetch')) {
        store.setOfflineMode(true)
      }
    } finally {
      store.setLoading(false)
    }
  }
  
  const syncPendingActions = async () => {
    const pendingActions = store.pendingActions
    if (pendingActions.length === 0) return
    
    store.setLoading(true)
    
    try {
      // Traiter les actions en batch
      const bulkItems = []
      
      pendingActions.forEach(action => {
        if (action.type === 'toggle_item') {
          bulkItems.push({
            item_id: action.itemId,
            checked: action.checked
          })
        } else if (action.type === 'bulk_toggle') {
          bulkItems.push(...action.items.map(item => ({
            item_id: item.itemId,
            checked: item.checked
          })))
        }
      })
      
      if (bulkItems.length > 0 && store.currentList) {
        const response = await fetch(
          `/api/shopping-lists/${store.currentList.id}/bulk-toggle`,
          {
            method: 'PATCH',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ items: bulkItems })
          }
        )
        
        if (response.ok) {
          const result = await response.json()
          store.updateListData(result.shopping_list)
          store.clearPendingActions()
          store.updateLastSync()
          store.setOfflineMode(false)
        }
      }
    } catch (error) {
      console.error('Erreur lors de la synchronisation:', error)
    } finally {
      store.setLoading(false)
    }
  }
  
  // Nouvelles fonctions US1.5
  const getListStatistics = async () => {
    if (!store.currentList) return null
    
    try {
      const response = await fetch(`/api/shopping-lists/${store.currentList.id}/statistics`)
      
      if (!response.ok) {
        throw new Error('Échec de récupération des statistiques')
      }
      
      return await response.json()
      
    } catch (error) {
      store.setError(`Erreur lors de la récupération des statistiques: ${error.message}`)
      return null
    }
  }
  
  const exportList = async (format = 'json', options = {}) => {
    if (!store.currentList) return null
    
    try {
      const response = await fetch(
        `/api/shopping-lists/${store.currentList.id}/export-data`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            format,
            include_metadata: options.includeMetadata !== false,
            include_checked_items: options.includeCheckedItems !== false
          })
        }
      )
      
      if (!response.ok) {
        throw new Error('Échec de l\'export')
      }
      
      return await response.json()
      
    } catch (error) {
      store.setError(`Erreur lors de l'export: ${error.message}`)
      return null
    }
  }
  
  const getListHistory = async (page = 1, perPage = 20) => {
    if (!store.currentList) return null
    
    try {
      const response = await fetch(
        `/api/shopping-lists/${store.currentList.id}/history?page=${page}&per_page=${perPage}`
      )
      
      if (!response.ok) {
        throw new Error('Échec de récupération de l\'historique')
      }
      
      return await response.json()
      
    } catch (error) {
      store.setError(`Erreur lors de la récupération de l'historique: ${error.message}`)
      return null
    }
  }
  
  const loadShoppingList = async (listId) => {
    store.setLoading(true)
    
    try {
      const response = await fetch(`/api/shopping-lists/${listId}`)
      
      if (!response.ok) {
        throw new Error('Liste de courses non trouvée')
      }
      
      const shoppingList = await response.json()
      store.setCurrentList(shoppingList)
      
      return shoppingList
      
    } catch (error) {
      store.setError(`Erreur lors du chargement: ${error.message}`)
      return null
    } finally {
      store.setLoading(false)
    }
  }

  return {
    // État
    currentList: store.currentList,
    checkedItems: store.checkedItems,
    isLoading: store.isLoading,
    error: store.error,
    offlineMode: store.offlineMode,
    pendingActionsCount: store.getPendingActionsCount(),
    
    // Actions principales
    setCurrentList: store.setCurrentList,
    toggleItemStatus,
    bulkToggleItems,
    regenerateList,
    syncPendingActions,
    clearError: store.clearError,
    
    // Nouvelles actions US1.5
    loadShoppingList,
    getListStatistics,
    exportList,
    getListHistory,
    
    // Getters
    completionStats: store.getCompletionStats(),
    itemsByCategory: store.getItemsByCategory()
  }
}

/**
 * Hook pour la détection du statut réseau
 */
export const useNetworkStatus = () => {
  const setOfflineMode = useShoppingListStore(state => state.setOfflineMode)
  const syncPendingActions = useShoppingList().syncPendingActions
  
  React.useEffect(() => {
    const handleOnline = () => {
      setOfflineMode(false)
      // Déclencher la sync automatique après un délai
      setTimeout(syncPendingActions, 1000)
    }
    
    const handleOffline = () => {
      setOfflineMode(true)
    }
    
    // État initial
    setOfflineMode(!navigator.onLine)
    
    // Écouter les changements
    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)
    
    return () => {
      window.removeEventListener('online', handleOnline)
      window.removeEventListener('offline', handleOffline)
    }
  }, [setOfflineMode, syncPendingActions])
}

export default useShoppingList