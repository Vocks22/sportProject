/**
 * Tests for useMealTracking hook and Zustand store (US1.8)
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { useMealTracking, useMealTrackingStore } from '../../hooks/useMealTracking'
import { 
  createMockMealTracking, 
  createMockDailySummary,
  mockSuccessResponse,
  mockErrorResponse,
  mockFetchEndpoint,
  waitForAsyncOperations,
  simulateNetworkDelay
} from '../utils/test-utils'

// Mock API
vi.mock('../../src/config/api', () => ({
  apiRequest: vi.fn()
}))

describe('useMealTrackingStore', () => {
  beforeEach(() => {
    // Reset store state
    useMealTrackingStore.setState({
      todayMealTrackings: [],
      dailySummary: null,
      isLoading: false,
      error: null,
      selectedDate: '2025-08-08',
      userId: 1,
      offlineMode: false,
      cachedTrackings: {},
      cachedSummaries: {},
      lastSync: null,
      pendingActions: []
    })
    
    // Clear localStorage
    localStorage.clear()
  })

  describe('Basic State Management', () => {
    it('initializes with default state', () => {
      const { result } = renderHook(() => useMealTrackingStore())
      
      expect(result.current.todayMealTrackings).toEqual([])
      expect(result.current.dailySummary).toBeNull()
      expect(result.current.isLoading).toBe(false)
      expect(result.current.error).toBeNull()
      expect(result.current.offlineMode).toBe(false)
      expect(result.current.pendingActions).toEqual([])
    })

    it('updates user ID', () => {
      const { result } = renderHook(() => useMealTrackingStore())
      
      act(() => {
        result.current.setUserId(123)
      })
      
      expect(result.current.userId).toBe(123)
    })

    it('updates selected date', () => {
      const { result } = renderHook(() => useMealTrackingStore())
      
      act(() => {
        result.current.setSelectedDate('2025-08-09')
      })
      
      expect(result.current.selectedDate).toBe('2025-08-09')
    })

    it('updates meal trackings', () => {
      const { result } = renderHook(() => useMealTrackingStore())
      const mockTrackings = [createMockMealTracking()]
      
      act(() => {
        result.current.setTodayMealTrackings(mockTrackings)
      })
      
      expect(result.current.todayMealTrackings).toEqual(mockTrackings)
    })

    it('updates daily summary', () => {
      const { result } = renderHook(() => useMealTrackingStore())
      const mockSummary = createMockDailySummary()
      
      act(() => {
        result.current.setDailySummary(mockSummary)
      })
      
      expect(result.current.dailySummary).toEqual(mockSummary)
    })
  })

  describe('Caching', () => {
    it('caches meal trackings by date', () => {
      const { result } = renderHook(() => useMealTrackingStore())
      const mockTrackings = [createMockMealTracking()]
      
      act(() => {
        result.current.setTodayMealTrackings(mockTrackings)
      })
      
      expect(result.current.cachedTrackings[result.current.selectedDate])
        .toEqual(mockTrackings)
    })

    it('caches daily summaries by date', () => {
      const { result } = renderHook(() => useMealTrackingStore())
      const mockSummary = createMockDailySummary()
      
      act(() => {
        result.current.setDailySummary(mockSummary)
      })
      
      expect(result.current.cachedSummaries[result.current.selectedDate])
        .toEqual(mockSummary)
    })

    it('loads data from cache when date changes', () => {
      const { result } = renderHook(() => useMealTrackingStore())
      const mockTrackings = [createMockMealTracking()]
      const mockSummary = createMockDailySummary()
      
      // Set data for current date
      act(() => {
        result.current.setTodayMealTrackings(mockTrackings)
        result.current.setDailySummary(mockSummary)
      })
      
      // Change to different date
      act(() => {
        result.current.setSelectedDate('2025-08-09')
      })
      
      // Should clear current data
      expect(result.current.todayMealTrackings).toEqual([])
      expect(result.current.dailySummary).toBeNull()
      
      // Change back to original date
      act(() => {
        result.current.setSelectedDate('2025-08-08')
      })
      
      // Should load from cache
      expect(result.current.todayMealTrackings).toEqual(mockTrackings)
      expect(result.current.dailySummary).toEqual(mockSummary)
    })
  })

  describe('Error Handling', () => {
    it('sets and clears errors', () => {
      const { result } = renderHook(() => useMealTrackingStore())
      
      act(() => {
        result.current.setError('Test error')
      })
      
      expect(result.current.error).toBe('Test error')
      
      act(() => {
        result.current.clearError()
      })
      
      expect(result.current.error).toBeNull()
    })
  })

  describe('Loading State', () => {
    it('manages loading state', () => {
      const { result } = renderHook(() => useMealTrackingStore())
      
      act(() => {
        result.current.setLoading(true)
      })
      
      expect(result.current.isLoading).toBe(true)
      
      act(() => {
        result.current.setLoading(false)
      })
      
      expect(result.current.isLoading).toBe(false)
    })
  })

  describe('Offline Mode', () => {
    it('manages offline mode', () => {
      const { result } = renderHook(() => useMealTrackingStore())
      
      act(() => {
        result.current.setOfflineMode(true)
      })
      
      expect(result.current.offlineMode).toBe(true)
    })

    it('queues actions when offline', () => {
      const { result } = renderHook(() => useMealTrackingStore())
      
      act(() => {
        result.current.setOfflineMode(true)
        result.current.queueOfflineAction({
          type: 'MARK_CONSUMED',
          trackingId: 1,
          data: { satisfaction_rating: 5 }
        })
      })
      
      expect(result.current.pendingActions).toHaveLength(1)
      expect(result.current.pendingActions[0].type).toBe('MARK_CONSUMED')
    })

    it('clears pending actions', () => {
      const { result } = renderHook(() => useMealTrackingStore())
      
      act(() => {
        result.current.queueOfflineAction({ type: 'TEST' })
        result.current.clearPendingActions()
      })
      
      expect(result.current.pendingActions).toHaveLength(0)
    })
  })

  describe('Persistence', () => {
    it('persists state to localStorage', () => {
      const { result } = renderHook(() => useMealTrackingStore())
      const mockTrackings = [createMockMealTracking()]
      
      act(() => {
        result.current.setTodayMealTrackings(mockTrackings)
      })
      
      // Check if data was persisted
      const persistedData = localStorage.getItem('meal-tracking-storage')
      expect(persistedData).toBeTruthy()
      
      const parsed = JSON.parse(persistedData)
      expect(parsed.state.cachedTrackings).toBeDefined()
    })

    it('restores state from localStorage', () => {
      // Set initial data in localStorage
      const initialData = {
        state: {
          userId: 123,
          selectedDate: '2025-08-09',
          cachedTrackings: {
            '2025-08-09': [createMockMealTracking()]
          }
        }
      }
      localStorage.setItem('meal-tracking-storage', JSON.stringify(initialData))
      
      const { result } = renderHook(() => useMealTrackingStore())
      
      expect(result.current.userId).toBe(123)
      expect(result.current.selectedDate).toBe('2025-08-09')
    })
  })
})

describe('useMealTracking hook', () => {
  let mockApiRequest

  beforeEach(() => {
    const { apiRequest } = require('../../src/config/api')
    mockApiRequest = apiRequest
    mockApiRequest.mockClear()

    // Reset store
    useMealTrackingStore.setState({
      todayMealTrackings: [],
      dailySummary: null,
      isLoading: false,
      error: null,
      selectedDate: '2025-08-08',
      userId: 1,
      offlineMode: false,
      cachedTrackings: {},
      cachedSummaries: {},
      lastSync: null,
      pendingActions: []
    })
  })

  describe('Data Loading', () => {
    it('loads today meal trackings successfully', async () => {
      const mockTrackings = [createMockMealTracking()]
      mockApiRequest.mockResolvedValueOnce({
        meal_trackings: mockTrackings,
        total_trackings: 1
      })

      const { result } = renderHook(() => useMealTracking())

      await act(async () => {
        await result.current.loadTodayMealTrackings()
      })

      expect(mockApiRequest).toHaveBeenCalledWith('/meal-tracking/today?user_id=1')
      expect(result.current.todayMealTrackings).toEqual(mockTrackings)
      expect(result.current.isLoading).toBe(false)
    })

    it('handles API errors when loading trackings', async () => {
      mockApiRequest.mockRejectedValueOnce(new Error('Network error'))

      const { result } = renderHook(() => useMealTracking())

      await act(async () => {
        await result.current.loadTodayMealTrackings()
      })

      expect(result.current.error).toBe('Erreur lors du chargement des repas')
      expect(result.current.isLoading).toBe(false)
    })

    it('loads daily summary successfully', async () => {
      const mockSummary = createMockDailySummary()
      mockApiRequest.mockResolvedValueOnce({
        success: true,
        daily_summary: mockSummary
      })

      const { result } = renderHook(() => useMealTracking())

      await act(async () => {
        await result.current.loadDailySummary()
      })

      expect(mockApiRequest).toHaveBeenCalledWith(
        '/meal-tracking/summary/2025-08-08?user_id=1'
      )
      expect(result.current.dailySummary).toEqual(mockSummary)
    })

    it('forces refresh when specified', async () => {
      const mockTrackings = [createMockMealTracking()]
      mockApiRequest.mockResolvedValueOnce({
        meal_trackings: mockTrackings
      })

      const { result } = renderHook(() => useMealTracking())

      await act(async () => {
        await result.current.loadTodayMealTrackings(true) // Force refresh
      })

      expect(mockApiRequest).toHaveBeenCalledWith('/meal-tracking/today?user_id=1')
    })
  })

  describe('Meal Actions', () => {
    it('marks meal as consumed successfully', async () => {
      const updatedTracking = createMockMealTracking({ status: 'consumed' })
      mockApiRequest.mockResolvedValueOnce({
        success: true,
        meal_tracking: updatedTracking
      })

      const { result } = renderHook(() => useMealTracking())

      await act(async () => {
        await result.current.markMealConsumed(1, {
          satisfaction_rating: 5,
          notes: 'Délicieux!'
        })
      })

      expect(mockApiRequest).toHaveBeenCalledWith(
        '/meal-tracking/1/consume',
        'POST',
        {
          user_id: 1,
          consumption_data: {
            satisfaction_rating: 5,
            notes: 'Délicieux!'
          }
        }
      )
    })

    it('adjusts meal portions successfully', async () => {
      const adjustedTracking = createMockMealTracking({
        status: 'modified',
        actual_portion_size: 1.5
      })
      mockApiRequest.mockResolvedValueOnce({
        success: true,
        meal_tracking: adjustedTracking
      })

      const { result } = renderHook(() => useMealTracking())

      await act(async () => {
        await result.current.adjustMealPortions(1, {
          portion_multiplier: 1.5,
          nutrition: { calories: 600 }
        })
      })

      expect(mockApiRequest).toHaveBeenCalledWith(
        '/meal-tracking/1/adjust',
        'PUT',
        {
          user_id: 1,
          portion_multiplier: 1.5,
          nutrition: { calories: 600 }
        }
      )
    })

    it('skips meal successfully', async () => {
      const skippedTracking = createMockMealTracking({ status: 'skipped' })
      mockApiRequest.mockResolvedValueOnce({
        success: true,
        meal_tracking: skippedTracking
      })

      const { result } = renderHook(() => useMealTracking())

      await act(async () => {
        await result.current.skipMeal(1, 'Pas faim')
      })

      expect(mockApiRequest).toHaveBeenCalledWith(
        '/meal-tracking/1/skip',
        'POST',
        {
          user_id: 1,
          skip_data: { reason: 'Pas faim' }
        }
      )
    })

    it('replaces meal successfully', async () => {
      const replacedTracking = createMockMealTracking({ status: 'replaced' })
      mockApiRequest.mockResolvedValueOnce({
        success: true,
        meal_tracking: replacedTracking
      })

      const { result } = renderHook(() => useMealTracking())

      await act(async () => {
        await result.current.replaceMeal(1, {
          replacement_name: 'Salade César',
          reason: 'Plus léger'
        })
      })

      expect(mockApiRequest).toHaveBeenCalledWith(
        '/meal-tracking/1/replace',
        'POST',
        {
          user_id: 1,
          replacement_data: {
            replacement_name: 'Salade César',
            reason: 'Plus léger'
          }
        }
      )
    })
  })

  describe('Offline Mode Handling', () => {
    it('queues actions when offline', async () => {
      const { result } = renderHook(() => useMealTracking())

      // Set offline mode
      act(() => {
        useMealTrackingStore.setState({ offlineMode: true })
      })

      await act(async () => {
        await result.current.markMealConsumed(1, { satisfaction_rating: 5 })
      })

      // Should not make API call
      expect(mockApiRequest).not.toHaveBeenCalled()
      
      // Should queue the action
      const state = useMealTrackingStore.getState()
      expect(state.pendingActions).toHaveLength(1)
      expect(state.pendingActions[0].type).toBe('MARK_CONSUMED')
    })

    it('syncs pending actions when coming online', async () => {
      const { result } = renderHook(() => useMealTracking())
      
      // Set some pending actions
      act(() => {
        useMealTrackingStore.setState({
          pendingActions: [
            {
              id: '1',
              type: 'MARK_CONSUMED',
              trackingId: 1,
              data: { satisfaction_rating: 5 },
              timestamp: Date.now()
            }
          ]
        })
      })

      mockApiRequest.mockResolvedValueOnce({
        success: true,
        meal_tracking: createMockMealTracking({ status: 'consumed' })
      })

      await act(async () => {
        await result.current.syncPendingActions()
      })

      expect(mockApiRequest).toHaveBeenCalled()
      
      const state = useMealTrackingStore.getState()
      expect(state.pendingActions).toHaveLength(0)
    })

    it('handles sync failures gracefully', async () => {
      const { result } = renderHook(() => useMealTracking())
      
      act(() => {
        useMealTrackingStore.setState({
          pendingActions: [
            { id: '1', type: 'MARK_CONSUMED', trackingId: 1, data: {} }
          ]
        })
      })

      mockApiRequest.mockRejectedValueOnce(new Error('Sync failed'))

      await act(async () => {
        await result.current.syncPendingActions()
      })

      // Should not clear actions if sync failed
      const state = useMealTrackingStore.getState()
      expect(state.pendingActions).toHaveLength(1)
      expect(result.current.error).toContain('synchronisation')
    })
  })

  describe('Date Management', () => {
    it('changes selected date', () => {
      const { result } = renderHook(() => useMealTracking())

      act(() => {
        result.current.changeSelectedDate('2025-08-09')
      })

      expect(result.current.selectedDate).toBe('2025-08-09')
    })

    it('loads cached data when changing dates', () => {
      const { result } = renderHook(() => useMealTracking())
      const mockTrackings = [createMockMealTracking()]

      // Set data for current date
      act(() => {
        useMealTrackingStore.setState({
          cachedTrackings: {
            '2025-08-09': mockTrackings
          }
        })
        result.current.changeSelectedDate('2025-08-09')
      })

      expect(result.current.todayMealTrackings).toEqual(mockTrackings)
    })
  })

  describe('Computed Properties', () => {
    it('calculates today nutrition totals', () => {
      const trackings = [
        createMockMealTracking({
          planned_nutrition: { calories: 400, protein: 25, carbs: 45, fat: 15 },
          status: 'consumed'
        }),
        createMockMealTracking({
          planned_nutrition: { calories: 600, protein: 35, carbs: 60, fat: 20 },
          status: 'planned'
        })
      ]

      act(() => {
        useMealTrackingStore.setState({ todayMealTrackings: trackings })
      })

      const { result } = renderHook(() => useMealTracking())

      expect(result.current.todayNutritionTotals.planned.calories).toBe(1000)
      expect(result.current.todayNutritionTotals.planned.protein).toBe(60)
      expect(result.current.todayNutritionTotals.effective.calories).toBe(1000)
    })

    it('calculates meal completion stats', () => {
      const trackings = [
        createMockMealTracking({ status: 'consumed' }),
        createMockMealTracking({ status: 'consumed' }),
        createMockMealTracking({ status: 'planned' }),
        createMockMealTracking({ status: 'skipped' })
      ]

      act(() => {
        useMealTrackingStore.setState({ todayMealTrackings: trackings })
      })

      const { result } = renderHook(() => useMealTracking())

      expect(result.current.mealCompletionStats.total).toBe(4)
      expect(result.current.mealCompletionStats.completed).toBe(2)
      expect(result.current.mealCompletionStats.completionRate).toBe(50)
    })

    it('groups meals by type', () => {
      const trackings = [
        createMockMealTracking({ meal_type: 'repas1' }),
        createMockMealTracking({ meal_type: 'repas2' }),
        createMockMealTracking({ meal_type: 'repas1' })
      ]

      act(() => {
        useMealTrackingStore.setState({ todayMealTrackings: trackings })
      })

      const { result } = renderHook(() => useMealTracking())

      expect(result.current.mealsByType.repas1).toHaveLength(2)
      expect(result.current.mealsByType.repas2).toHaveLength(1)
    })
  })

  describe('Error Handling', () => {
    it('handles network errors gracefully', async () => {
      mockApiRequest.mockRejectedValueOnce(new Error('Network error'))

      const { result } = renderHook(() => useMealTracking())

      await act(async () => {
        await result.current.markMealConsumed(1, {})
      })

      expect(result.current.error).toContain('Erreur')
    })

    it('clears errors', () => {
      const { result } = renderHook(() => useMealTracking())

      act(() => {
        useMealTrackingStore.setState({ error: 'Test error' })
      })

      expect(result.current.error).toBe('Test error')

      act(() => {
        result.current.clearError()
      })

      expect(result.current.error).toBeNull()
    })
  })

  describe('Loading States', () => {
    it('manages loading state during API calls', async () => {
      let resolvePromise
      const promise = new Promise(resolve => {
        resolvePromise = resolve
      })
      mockApiRequest.mockReturnValueOnce(promise)

      const { result } = renderHook(() => useMealTracking())

      // Start loading
      act(() => {
        result.current.loadTodayMealTrackings()
      })

      expect(result.current.isLoading).toBe(true)

      // Resolve promise
      await act(async () => {
        resolvePromise({ meal_trackings: [] })
        await promise
      })

      expect(result.current.isLoading).toBe(false)
    })
  })

  describe('Edge Cases', () => {
    it('handles empty API responses', async () => {
      mockApiRequest.mockResolvedValueOnce({ meal_trackings: [] })

      const { result } = renderHook(() => useMealTracking())

      await act(async () => {
        await result.current.loadTodayMealTrackings()
      })

      expect(result.current.todayMealTrackings).toEqual([])
      expect(result.current.error).toBeNull()
    })

    it('handles malformed API responses', async () => {
      mockApiRequest.mockResolvedValueOnce(null)

      const { result } = renderHook(() => useMealTracking())

      await act(async () => {
        await result.current.loadTodayMealTrackings()
      })

      expect(result.current.error).toBeTruthy()
    })

    it('handles missing user ID', async () => {
      act(() => {
        useMealTrackingStore.setState({ userId: null })
      })

      const { result } = renderHook(() => useMealTracking())

      await act(async () => {
        await result.current.loadTodayMealTrackings()
      })

      expect(result.current.error).toContain('utilisateur')
    })
  })
})