/**
 * Tests for MealCard component (US1.8)
 */

import React from 'react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import MealCard from '../../components/MealCard'
import { useMealTracking } from '../../hooks/useMealTracking'
import { 
  createMockMealTracking, 
  createMockComponentProps,
  renderWithProviders,
  waitForAsyncOperations 
} from '../utils/test-utils'

// Mock the hook
vi.mock('../../hooks/useMealTracking')

describe('MealCard Component', () => {
  let mockUseMealTracking

  beforeEach(() => {
    mockUseMealTracking = {
      markMealConsumed: vi.fn(),
      adjustMealPortions: vi.fn(),
      skipMeal: vi.fn(),
      replaceMeal: vi.fn(),
      isLoading: false
    }
    
    useMealTracking.mockReturnValue(mockUseMealTracking)
  })

  describe('Rendering', () => {
    it('renders meal card with basic information', () => {
      const mealTracking = createMockMealTracking({
        meal_name: 'Healthy Breakfast',
        status: 'planned'
      })

      render(<MealCard mealTracking={mealTracking} onStatusChange={vi.fn()} />)

      expect(screen.getByText('Healthy Breakfast')).toBeInTheDocument()
      expect(screen.getByText('Planifié')).toBeInTheDocument()
      expect(screen.getByText('400')).toBeInTheDocument() // calories
      expect(screen.getByText('25g')).toBeInTheDocument() // protein
    })

    it('renders nutrition information correctly', () => {
      const mealTracking = createMockMealTracking({
        planned_nutrition: {
          calories: 500,
          protein: 30,
          carbs: 60,
          fat: 20,
          fiber: 8,
          sodium: 300,
          sugar: 15
        }
      })

      render(<MealCard mealTracking={mealTracking} onStatusChange={vi.fn()} />)

      expect(screen.getByText('500')).toBeInTheDocument()
      expect(screen.getByText('30g')).toBeInTheDocument()
    })

    it('shows correct status badge for each status', () => {
      const statuses = [
        { status: 'planned', label: 'Planifié' },
        { status: 'consumed', label: 'Consommé' },
        { status: 'modified', label: 'Modifié' },
        { status: 'skipped', label: 'Ignoré' },
        { status: 'replaced', label: 'Remplacé' }
      ]

      statuses.forEach(({ status, label }) => {
        const { rerender } = render(
          <MealCard 
            mealTracking={createMockMealTracking({ status })} 
            onStatusChange={vi.fn()} 
          />
        )
        
        expect(screen.getByText(label)).toBeInTheDocument()
        
        // Cleanup for next iteration
        rerender(<div />)
      })
    })

    it('does not render when mealTracking is null', () => {
      const { container } = render(
        <MealCard mealTracking={null} onStatusChange={vi.fn()} />
      )
      
      expect(container.firstChild).toBeNull()
    })
  })

  describe('Status Actions', () => {
    it('shows action buttons for planned meals', () => {
      const mealTracking = createMockMealTracking({ status: 'planned' })

      render(<MealCard mealTracking={mealTracking} onStatusChange={vi.fn()} />)

      expect(screen.getByText('Consommer')).toBeInTheDocument()
      expect(screen.getByText('Ajuster')).toBeInTheDocument()
      expect(screen.getByText('Ignorer')).toBeInTheDocument()
      expect(screen.getByText('Remplacer')).toBeInTheDocument()
    })

    it('hides action buttons for consumed meals', () => {
      const mealTracking = createMockMealTracking({ status: 'consumed' })

      render(<MealCard mealTracking={mealTracking} onStatusChange={vi.fn()} />)

      expect(screen.queryByText('Consommer')).not.toBeInTheDocument()
      expect(screen.queryByText('Ajuster')).not.toBeInTheDocument()
      expect(screen.queryByText('Ignorer')).not.toBeInTheDocument()
      expect(screen.queryByText('Remplacer')).not.toBeInTheDocument()
    })

    it('disables buttons when disabled prop is true', () => {
      const mealTracking = createMockMealTracking({ status: 'planned' })

      render(
        <MealCard 
          mealTracking={mealTracking} 
          onStatusChange={vi.fn()} 
          disabled={true} 
        />
      )

      const consumeButton = screen.getByText('Consommer')
      const adjustButton = screen.getByText('Ajuster')
      
      expect(consumeButton).toBeDisabled()
      expect(adjustButton).toBeDisabled()
    })

    it('disables buttons when loading', () => {
      mockUseMealTracking.isLoading = true
      useMealTracking.mockReturnValue(mockUseMealTracking)

      const mealTracking = createMockMealTracking({ status: 'planned' })

      render(<MealCard mealTracking={mealTracking} onStatusChange={vi.fn()} />)

      const consumeButton = screen.getByText('Consommer')
      expect(consumeButton).toBeDisabled()
    })
  })

  describe('Consume Meal Functionality', () => {
    it('calls markMealConsumed when consume button is clicked', async () => {
      const user = userEvent.setup()
      const mealTracking = createMockMealTracking({ id: 123, status: 'planned' })
      const onStatusChange = vi.fn()

      mockUseMealTracking.markMealConsumed.mockResolvedValue({ success: true })

      render(<MealCard mealTracking={mealTracking} onStatusChange={onStatusChange} />)

      const consumeButton = screen.getByText('Consommer')
      await user.click(consumeButton)

      expect(mockUseMealTracking.markMealConsumed).toHaveBeenCalledWith(123, {})
      
      await waitFor(() => {
        expect(onStatusChange).toHaveBeenCalled()
      })
    })

    it('shows rating interface when consume button is clicked', async () => {
      const user = userEvent.setup()
      const mealTracking = createMockMealTracking({ status: 'planned' })

      render(<MealCard mealTracking={mealTracking} onStatusChange={vi.fn()} />)

      const consumeButton = screen.getByText('Consommer')
      await user.click(consumeButton)

      // Should show rating stars
      const stars = screen.getAllByRole('button', { name: /étoile/i })
      expect(stars).toHaveLength(5)
    })

    it('submits consumption with rating and notes', async () => {
      const user = userEvent.setup()
      const mealTracking = createMockMealTracking({ id: 123, status: 'planned' })

      mockUseMealTracking.markMealConsumed.mockResolvedValue({ success: true })

      render(<MealCard mealTracking={mealTracking} onStatusChange={vi.fn()} />)

      // Click consume to show rating interface
      await user.click(screen.getByText('Consommer'))

      // Rate 4 stars
      const fourthStar = screen.getAllByRole('button', { name: /étoile/i })[3]
      await user.click(fourthStar)

      // Add notes
      const notesInput = screen.getByPlaceholderText(/notes/i)
      await user.type(notesInput, 'Délicieux repas!')

      // Confirm consumption
      const confirmButton = screen.getByText('Confirmer')
      await user.click(confirmButton)

      expect(mockUseMealTracking.markMealConsumed).toHaveBeenCalledWith(123, {
        satisfaction_rating: 4,
        notes: 'Délicieux repas!'
      })
    })
  })

  describe('Skip Meal Functionality', () => {
    it('shows skip reason form when skip button is clicked', async () => {
      const user = userEvent.setup()
      const mealTracking = createMockMealTracking({ status: 'planned' })

      render(<MealCard mealTracking={mealTracking} onStatusChange={vi.fn()} />)

      const skipButton = screen.getByText('Ignorer')
      await user.click(skipButton)

      expect(screen.getByPlaceholderText(/raison/i)).toBeInTheDocument()
      expect(screen.getByText('Confirmer l\'ignorance')).toBeInTheDocument()
    })

    it('calls skipMeal with reason', async () => {
      const user = userEvent.setup()
      const mealTracking = createMockMealTracking({ id: 123, status: 'planned' })

      mockUseMealTracking.skipMeal.mockResolvedValue({ success: true })

      render(<MealCard mealTracking={mealTracking} onStatusChange={vi.fn()} />)

      // Click skip
      await user.click(screen.getByText('Ignorer'))

      // Enter reason
      const reasonInput = screen.getByPlaceholderText(/raison/i)
      await user.type(reasonInput, 'Pas faim')

      // Confirm skip
      const confirmButton = screen.getByText('Confirmer l\'ignorance')
      await user.click(confirmButton)

      expect(mockUseMealTracking.skipMeal).toHaveBeenCalledWith(123, 'Pas faim')
    })
  })

  describe('Replace Meal Functionality', () => {
    it('shows replacement form when replace button is clicked', async () => {
      const user = userEvent.setup()
      const mealTracking = createMockMealTracking({ status: 'planned' })

      render(<MealCard mealTracking={mealTracking} onStatusChange={vi.fn()} />)

      const replaceButton = screen.getByText('Remplacer')
      await user.click(replaceButton)

      expect(screen.getByPlaceholderText(/nouveau repas/i)).toBeInTheDocument()
      expect(screen.getByPlaceholderText(/raison du remplacement/i)).toBeInTheDocument()
      expect(screen.getByText('Confirmer le remplacement')).toBeInTheDocument()
    })

    it('calls replaceMeal with replacement data', async () => {
      const user = userEvent.setup()
      const mealTracking = createMockMealTracking({ id: 123, status: 'planned' })

      mockUseMealTracking.replaceMeal.mockResolvedValue({ success: true })

      render(<MealCard mealTracking={mealTracking} onStatusChange={vi.fn()} />)

      // Click replace
      await user.click(screen.getByText('Remplacer'))

      // Fill replacement form
      const nameInput = screen.getByPlaceholderText(/nouveau repas/i)
      const reasonInput = screen.getByPlaceholderText(/raison du remplacement/i)
      
      await user.type(nameInput, 'Salade César')
      await user.type(reasonInput, 'Plus léger')

      // Confirm replacement
      const confirmButton = screen.getByText('Confirmer le remplacement')
      await user.click(confirmButton)

      expect(mockUseMealTracking.replaceMeal).toHaveBeenCalledWith(123, {
        replacement_name: 'Salade César',
        reason: 'Plus léger'
      })
    })
  })

  describe('Portion Adjustment', () => {
    it('shows portion adjuster when adjust button is clicked', async () => {
      const user = userEvent.setup()
      const mealTracking = createMockMealTracking({ status: 'planned' })

      render(<MealCard mealTracking={mealTracking} onStatusChange={vi.fn()} />)

      const adjustButton = screen.getByText('Ajuster')
      await user.click(adjustButton)

      expect(screen.getByText('Ajustement des portions')).toBeInTheDocument()
    })

    it('hides portion adjuster when cancelled', async () => {
      const user = userEvent.setup()
      const mealTracking = createMockMealTracking({ status: 'planned' })

      render(<MealCard mealTracking={mealTracking} onStatusChange={vi.fn()} />)

      // Show adjuster
      await user.click(screen.getByText('Ajuster'))
      expect(screen.getByText('Ajustement des portions')).toBeInTheDocument()

      // Cancel
      const cancelButton = screen.getByText('Annuler')
      await user.click(cancelButton)

      expect(screen.queryByText('Ajustement des portions')).not.toBeInTheDocument()
    })
  })

  describe('Details Toggle', () => {
    it('shows details when toggle is clicked', async () => {
      const user = userEvent.setup()
      const mealTracking = createMockMealTracking({
        planned_nutrition: {
          calories: 400,
          protein: 25,
          carbs: 45,
          fat: 15,
          fiber: 8,
          sodium: 300,
          sugar: 12
        }
      })

      render(<MealCard mealTracking={mealTracking} onStatusChange={vi.fn()} />)

      // Click details toggle
      const toggleButton = screen.getByRole('button', { name: /détails/i })
      await user.click(toggleButton)

      // Check if detailed nutrition is shown
      expect(screen.getByText(/glucides/i)).toBeInTheDocument()
      expect(screen.getByText(/lipides/i)).toBeInTheDocument()
      expect(screen.getByText(/fibres/i)).toBeInTheDocument()
    })

    it('hides details when toggle is clicked again', async () => {
      const user = userEvent.setup()
      const mealTracking = createMockMealTracking()

      render(<MealCard mealTracking={mealTracking} onStatusChange={vi.fn()} />)

      const toggleButton = screen.getByRole('button', { name: /détails/i })
      
      // Show details
      await user.click(toggleButton)
      expect(screen.getByText(/glucides/i)).toBeInTheDocument()

      // Hide details
      await user.click(toggleButton)
      expect(screen.queryByText(/glucides/i)).not.toBeInTheDocument()
    })
  })

  describe('Status Display', () => {
    it('shows consumption time for consumed meals', () => {
      const mealTracking = createMockMealTracking({
        status: 'consumed',
        consumption_datetime: '2025-08-08T08:30:00Z'
      })

      render(<MealCard mealTracking={mealTracking} onStatusChange={vi.fn()} />)

      expect(screen.getByText(/08:30/)).toBeInTheDocument()
    })

    it('shows satisfaction rating for consumed meals', () => {
      const mealTracking = createMockMealTracking({
        status: 'consumed',
        satisfaction_rating: 5
      })

      render(<MealCard mealTracking={mealTracking} onStatusChange={vi.fn()} />)

      // Should show 5 filled stars
      const filledStars = screen.getAllByText('★')
      expect(filledStars).toHaveLength(5)
    })

    it('shows user notes for consumed meals', () => {
      const mealTracking = createMockMealTracking({
        status: 'consumed',
        user_notes: 'Très bon repas!'
      })

      render(<MealCard mealTracking={mealTracking} onStatusChange={vi.fn()} />)

      expect(screen.getByText('Très bon repas!')).toBeInTheDocument()
    })

    it('shows skip reason for skipped meals', () => {
      const mealTracking = createMockMealTracking({
        status: 'skipped',
        skip_reason: 'Pas le temps'
      })

      render(<MealCard mealTracking={mealTracking} onStatusChange={vi.fn()} />)

      expect(screen.getByText('Pas le temps')).toBeInTheDocument()
    })

    it('shows replacement info for replaced meals', () => {
      const mealTracking = createMockMealTracking({
        status: 'replaced',
        replacement_name: 'Salade verte',
        replacement_reason: 'Plus sain'
      })

      render(<MealCard mealTracking={mealTracking} onStatusChange={vi.fn()} />)

      expect(screen.getByText('Salade verte')).toBeInTheDocument()
      expect(screen.getByText('Plus sain')).toBeInTheDocument()
    })
  })

  describe('Accessibility', () => {
    it('has proper button labels', () => {
      const mealTracking = createMockMealTracking({ status: 'planned' })

      render(<MealCard mealTracking={mealTracking} onStatusChange={vi.fn()} />)

      expect(screen.getByRole('button', { name: 'Consommer' })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: 'Ajuster' })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: 'Ignorer' })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: 'Remplacer' })).toBeInTheDocument()
    })

    it('has proper aria labels for interactive elements', () => {
      const mealTracking = createMockMealTracking({ status: 'planned' })

      render(<MealCard mealTracking={mealTracking} onStatusChange={vi.fn()} />)

      const detailsButton = screen.getByRole('button', { name: /détails/i })
      expect(detailsButton).toHaveAttribute('aria-expanded', 'false')
    })
  })

  describe('Error Handling', () => {
    it('handles API errors gracefully', async () => {
      const user = userEvent.setup()
      const mealTracking = createMockMealTracking({ id: 123, status: 'planned' })

      mockUseMealTracking.markMealConsumed.mockRejectedValue(
        new Error('Network error')
      )

      render(<MealCard mealTracking={mealTracking} onStatusChange={vi.fn()} />)

      const consumeButton = screen.getByText('Consommer')
      await user.click(consumeButton)

      // Should not crash the component
      expect(screen.getByText('Healthy Breakfast')).toBeInTheDocument()
    })

    it('shows loading state during operations', async () => {
      const user = userEvent.setup()
      const mealTracking = createMockMealTracking({ status: 'planned' })

      // Mock loading state
      mockUseMealTracking.isLoading = true
      useMealTracking.mockReturnValue(mockUseMealTracking)

      render(<MealCard mealTracking={mealTracking} onStatusChange={vi.fn()} />)

      const consumeButton = screen.getByText('Consommer')
      expect(consumeButton).toBeDisabled()
    })
  })
})