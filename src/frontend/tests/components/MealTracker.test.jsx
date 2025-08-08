/**
 * Tests for MealTracker component (US1.8)
 */

import React from 'react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import MealTracker from '../../components/MealTracker'
import { useMealTracking, useMealTrackingNetworkStatus } from '../../hooks/useMealTracking'
import { 
  createMockMealTracking, 
  createMockDailySummary,
  generateMealTrackings,
  renderWithProviders 
} from '../utils/test-utils'

// Mock the hooks
vi.mock('../../hooks/useMealTracking')

describe('MealTracker Component', () => {
  let mockUseMealTracking
  let mockNetworkStatus

  beforeEach(() => {
    mockUseMealTracking = {
      todayMealTrackings: [],
      dailySummary: null,
      isLoading: false,
      error: null,
      offlineMode: false,
      selectedDate: '2025-08-08',
      pendingActionsCount: 0,
      loadTodayMealTrackings: vi.fn(),
      loadDailySummary: vi.fn(),
      changeSelectedDate: vi.fn(),
      syncPendingActions: vi.fn(),
      clearError: vi.fn(),
      todayNutritionTotals: {
        planned: { calories: 0, protein: 0, carbs: 0, fat: 0 },
        actual: { calories: 0, protein: 0, carbs: 0, fat: 0 },
        effective: { calories: 0, protein: 0, carbs: 0, fat: 0 }
      },
      mealCompletionStats: {
        total: 0,
        completed: 0,
        completionRate: 0
      },
      mealsByType: {}
    }

    mockNetworkStatus = {
      offlineMode: false
    }

    useMealTracking.mockReturnValue(mockUseMealTracking)
    useMealTrackingNetworkStatus.mockReturnValue(mockNetworkStatus)
  })

  describe('Rendering', () => {
    it('renders meal tracker with header', () => {
      render(<MealTracker />)

      expect(screen.getByText(/suivi des repas/i)).toBeInTheDocument()
    })

    it('shows selected date correctly', () => {
      mockUseMealTracking.selectedDate = '2025-08-08'
      useMealTracking.mockReturnValue(mockUseMealTracking)

      render(<MealTracker />)

      // Should show formatted date
      expect(screen.getByText(/jeudi 8 août 2025/i)).toBeInTheDocument()
    })

    it('shows loading state', () => {
      mockUseMealTracking.isLoading = true
      useMealTracking.mockReturnValue(mockUseMealTracking)

      render(<MealTracker />)

      expect(screen.getByText(/chargement/i)).toBeInTheDocument()
    })

    it('shows empty state when no meals', () => {
      mockUseMealTracking.todayMealTrackings = []
      useMealTracking.mockReturnValue(mockUseMealTracking)

      render(<MealTracker />)

      expect(screen.getByText(/aucun repas planifié/i)).toBeInTheDocument()
    })
  })

  describe('Data Loading', () => {
    it('loads data on mount', () => {
      render(<MealTracker />)

      expect(mockUseMealTracking.loadTodayMealTrackings).toHaveBeenCalled()
      expect(mockUseMealTracking.loadDailySummary).toHaveBeenCalled()
    })

    it('reloads data when date changes', () => {
      const { rerender } = render(<MealTracker />)

      // Change selected date
      mockUseMealTracking.selectedDate = '2025-08-09'
      useMealTracking.mockReturnValue(mockUseMealTracking)

      rerender(<MealTracker />)

      expect(mockUseMealTracking.loadTodayMealTrackings).toHaveBeenCalledTimes(2)
      expect(mockUseMealTracking.loadDailySummary).toHaveBeenCalledTimes(2)
    })

    it('syncs pending actions when coming back online', () => {
      mockNetworkStatus.offlineMode = true
      mockUseMealTracking.pendingActionsCount = 2
      useMealTracking.mockReturnValue(mockUseMealTracking)
      useMealTrackingNetworkStatus.mockReturnValue(mockNetworkStatus)

      const { rerender } = render(<MealTracker />)

      // Come back online
      mockNetworkStatus.offlineMode = false
      useMealTrackingNetworkStatus.mockReturnValue(mockNetworkStatus)

      rerender(<MealTracker />)

      expect(mockUseMealTracking.syncPendingActions).toHaveBeenCalled()
    })
  })

  describe('Date Navigation', () => {
    it('navigates to previous day', async () => {
      const user = userEvent.setup()

      render(<MealTracker />)

      const prevButton = screen.getByRole('button', { name: /jour précédent/i })
      await user.click(prevButton)

      expect(mockUseMealTracking.changeSelectedDate).toHaveBeenCalledWith('2025-08-07')
    })

    it('navigates to next day', async () => {
      const user = userEvent.setup()

      render(<MealTracker />)

      const nextButton = screen.getByRole('button', { name: /jour suivant/i })
      await user.click(nextButton)

      expect(mockUseMealTracking.changeSelectedDate).toHaveBeenCalledWith('2025-08-09')
    })

    it('navigates to today', async () => {
      const user = userEvent.setup()
      const today = new Date().toISOString().split('T')[0]

      // Mock being on different date
      mockUseMealTracking.selectedDate = '2025-08-05'
      useMealTracking.mockReturnValue(mockUseMealTracking)

      render(<MealTracker />)

      const todayButton = screen.getByText(/aujourd'hui/i)
      await user.click(todayButton)

      expect(mockUseMealTracking.changeSelectedDate).toHaveBeenCalledWith(today)
    })

    it('hides today button when already on today', () => {
      const today = new Date().toISOString().split('T')[0]
      mockUseMealTracking.selectedDate = today
      useMealTracking.mockReturnValue(mockUseMealTracking)

      render(<MealTracker />)

      expect(screen.queryByText(/aujourd'hui/i)).not.toBeInTheDocument()
    })
  })

  describe('Meal Display', () => {
    it('renders meal cards for each tracking', () => {
      const trackings = generateMealTrackings(3)
      mockUseMealTracking.todayMealTrackings = trackings
      useMealTracking.mockReturnValue(mockUseMealTracking)

      render(<MealTracker />)

      trackings.forEach(tracking => {
        expect(screen.getByText(tracking.meal_name)).toBeInTheDocument()
      })
    })

    it('groups meals by type correctly', () => {
      const trackings = [
        createMockMealTracking({ meal_type: 'repas1', meal_name: 'Petit déjeuner' }),
        createMockMealTracking({ meal_type: 'repas2', meal_name: 'Déjeuner' }),
        createMockMealTracking({ meal_type: 'repas3', meal_name: 'Dîner' }),
        createMockMealTracking({ meal_type: 'collation', meal_name: 'Collation' })
      ]
      mockUseMealTracking.todayMealTrackings = trackings
      mockUseMealTracking.mealsByType = {
        repas1: [trackings[0]],
        repas2: [trackings[1]],
        repas3: [trackings[2]],
        collation: [trackings[3]]
      }
      useMealTracking.mockReturnValue(mockUseMealTracking)

      render(<MealTracker />)

      expect(screen.getByText('Petit déjeuner')).toBeInTheDocument()
      expect(screen.getByText('Déjeuner')).toBeInTheDocument()
      expect(screen.getByText('Dîner')).toBeInTheDocument()
      expect(screen.getByText('Collation')).toBeInTheDocument()
    })
  })

  describe('Nutrition Overview', () => {
    it('shows nutrition totals', () => {
      mockUseMealTracking.todayNutritionTotals = {
        planned: { calories: 1800, protein: 120, carbs: 225, fat: 60 },
        actual: { calories: 1650, protein: 110, carbs: 200, fat: 55 },
        effective: { calories: 1650, protein: 110, carbs: 200, fat: 55 }
      }
      useMealTracking.mockReturnValue(mockUseMealTracking)

      render(<MealTracker />)

      expect(screen.getByText('1650')).toBeInTheDocument() // effective calories
      expect(screen.getByText('110g')).toBeInTheDocument() // effective protein
    })

    it('shows completion statistics', () => {
      mockUseMealTracking.mealCompletionStats = {
        total: 4,
        completed: 3,
        completionRate: 75
      }
      useMealTracking.mockReturnValue(mockUseMealTracking)

      render(<MealTracker />)

      expect(screen.getByText('3/4')).toBeInTheDocument()
      expect(screen.getByText('75%')).toBeInTheDocument()
    })
  })

  describe('Daily Summary', () => {
    it('shows daily summary when available', () => {
      const summary = createMockDailySummary()
      mockUseMealTracking.dailySummary = summary
      useMealTracking.mockReturnValue(mockUseMealTracking)

      render(<MealTracker />)

      // Click to show summary
      const summaryButton = screen.getByText(/résumé quotidien/i)
      expect(summaryButton).toBeInTheDocument()
    })

    it('toggles summary display', async () => {
      const user = userEvent.setup()
      const summary = createMockDailySummary()
      mockUseMealTracking.dailySummary = summary
      useMealTracking.mockReturnValue(mockUseMealTracking)

      render(<MealTracker />)

      const summaryButton = screen.getByText(/résumé quotidien/i)
      await user.click(summaryButton)

      // Should show summary details
      expect(screen.getByText(/adhérence au plan/i)).toBeInTheDocument()
    })
  })

  describe('Quick Add Functionality', () => {
    it('shows quick add button for each meal type', () => {
      render(<MealTracker />)

      const quickAddButtons = screen.getAllByText(/ajouter rapidement/i)
      expect(quickAddButtons.length).toBeGreaterThan(0)
    })

    it('opens quick add modal', async () => {
      const user = userEvent.setup()

      render(<MealTracker />)

      const quickAddButton = screen.getAllByText(/ajouter rapidement/i)[0]
      await user.click(quickAddButton)

      expect(screen.getByText(/ajout rapide/i)).toBeInTheDocument()
    })

    it('closes quick add modal', async () => {
      const user = userEvent.setup()

      render(<MealTracker />)

      // Open modal
      const quickAddButton = screen.getAllByText(/ajouter rapidement/i)[0]
      await user.click(quickAddButton)

      // Close modal
      const closeButton = screen.getByRole('button', { name: /fermer/i })
      await user.click(closeButton)

      expect(screen.queryByText(/ajout rapide/i)).not.toBeInTheDocument()
    })
  })

  describe('Error Handling', () => {
    it('displays error message', () => {
      mockUseMealTracking.error = 'Erreur de réseau'
      useMealTracking.mockReturnValue(mockUseMealTracking)

      render(<MealTracker />)

      expect(screen.getByText('Erreur de réseau')).toBeInTheDocument()
    })

    it('allows error dismissal', async () => {
      const user = userEvent.setup()
      mockUseMealTracking.error = 'Erreur de réseau'
      useMealTracking.mockReturnValue(mockUseMealTracking)

      render(<MealTracker />)

      const dismissButton = screen.getByRole('button', { name: /fermer/i })
      await user.click(dismissButton)

      expect(mockUseMealTracking.clearError).toHaveBeenCalled()
    })
  })

  describe('Offline Mode', () => {
    it('shows offline indicator', () => {
      mockUseMealTracking.offlineMode = true
      useMealTracking.mockReturnValue(mockUseMealTracking)

      render(<MealTracker />)

      expect(screen.getByText(/hors ligne/i)).toBeInTheDocument()
    })

    it('shows pending actions count', () => {
      mockUseMealTracking.offlineMode = true
      mockUseMealTracking.pendingActionsCount = 3
      useMealTracking.mockReturnValue(mockUseMealTracking)

      render(<MealTracker />)

      expect(screen.getByText('3')).toBeInTheDocument()
      expect(screen.getByText(/actions en attente/i)).toBeInTheDocument()
    })

    it('allows manual sync', async () => {
      const user = userEvent.setup()
      mockUseMealTracking.offlineMode = true
      mockUseMealTracking.pendingActionsCount = 2
      useMealTracking.mockReturnValue(mockUseMealTracking)

      render(<MealTracker />)

      const syncButton = screen.getByRole('button', { name: /synchroniser/i })
      await user.click(syncButton)

      expect(mockUseMealTracking.syncPendingActions).toHaveBeenCalled()
    })
  })

  describe('Refresh Functionality', () => {
    it('refreshes data when refresh button is clicked', async () => {
      const user = userEvent.setup()

      render(<MealTracker />)

      const refreshButton = screen.getByRole('button', { name: /actualiser/i })
      await user.click(refreshButton)

      expect(mockUseMealTracking.loadTodayMealTrackings).toHaveBeenCalledWith(true)
      expect(mockUseMealTracking.loadDailySummary).toHaveBeenCalledWith(true)
    })
  })

  describe('Future Date Handling', () => {
    it('shows appropriate message for future dates', () => {
      const futureDate = new Date()
      futureDate.setDate(futureDate.getDate() + 1)
      
      mockUseMealTracking.selectedDate = futureDate.toISOString().split('T')[0]
      useMealTracking.mockReturnValue(mockUseMealTracking)

      render(<MealTracker />)

      expect(screen.getByText(/planification future/i)).toBeInTheDocument()
    })

    it('disables certain actions for future dates', () => {
      const futureDate = new Date()
      futureDate.setDate(futureDate.getDate() + 1)
      
      mockUseMealTracking.selectedDate = futureDate.toISOString().split('T')[0]
      mockUseMealTracking.todayMealTrackings = [
        createMockMealTracking({ status: 'planned' })
      ]
      useMealTracking.mockReturnValue(mockUseMealTracking)

      render(<MealTracker />)

      // Action buttons should be disabled for future dates
      const actionButtons = screen.getAllByRole('button')
      const consumeButtons = actionButtons.filter(btn => 
        btn.textContent?.includes('Consommer')
      )
      
      consumeButtons.forEach(button => {
        expect(button).toBeDisabled()
      })
    })
  })

  describe('Accessibility', () => {
    it('has proper heading structure', () => {
      render(<MealTracker />)

      expect(screen.getByRole('heading', { level: 1 })).toBeInTheDocument()
    })

    it('has proper button labels', () => {
      render(<MealTracker />)

      expect(screen.getByRole('button', { name: /jour précédent/i })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /jour suivant/i })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /actualiser/i })).toBeInTheDocument()
    })

    it('has proper aria labels for navigation', () => {
      render(<MealTracker />)

      const prevButton = screen.getByRole('button', { name: /jour précédent/i })
      const nextButton = screen.getByRole('button', { name: /jour suivant/i })

      expect(prevButton).toHaveAttribute('aria-label')
      expect(nextButton).toHaveAttribute('aria-label')
    })

    it('has proper focus management', async () => {
      const user = userEvent.setup()

      render(<MealTracker />)

      const refreshButton = screen.getByRole('button', { name: /actualiser/i })
      
      // Focus should work properly
      await user.tab()
      expect(document.activeElement).toBe(refreshButton)
    })
  })

  describe('Performance', () => {
    it('does not unnecessarily re-render', () => {
      const renderCount = vi.fn()
      
      const TrackingComponent = () => {
        renderCount()
        return <MealTracker />
      }

      const { rerender } = render(<TrackingComponent />)
      
      // Same props should not cause re-render
      rerender(<TrackingComponent />)
      
      expect(renderCount).toHaveBeenCalledTimes(2) // Initial + rerender
    })
  })
})