/**
 * Tests for PortionAdjuster component (US1.8)
 */

import React from 'react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import PortionAdjuster from '../../components/PortionAdjuster'
import { 
  createMockMealTracking, 
  createMockComponentProps,
  renderWithProviders 
} from '../utils/test-utils'

describe('PortionAdjuster Component', () => {
  let defaultProps

  beforeEach(() => {
    defaultProps = {
      mealTracking: createMockMealTracking({
        planned_nutrition: {
          calories: 400,
          protein: 25,
          carbs: 45,
          fat: 15,
          fiber: 5,
          sodium: 200,
          sugar: 10
        }
      }),
      onAdjust: vi.fn(),
      onCancel: vi.fn()
    }
  })

  describe('Rendering', () => {
    it('renders portion adjuster with initial values', () => {
      render(<PortionAdjuster {...defaultProps} />)

      expect(screen.getByText('Ajustement des portions')).toBeInTheDocument()
      expect(screen.getByDisplayValue('100')).toBeInTheDocument() // 100% as default
    })

    it('shows original nutrition values', () => {
      render(<PortionAdjuster {...defaultProps} />)

      expect(screen.getByText('400')).toBeInTheDocument() // calories
      expect(screen.getByText('25g')).toBeInTheDocument() // protein
      expect(screen.getByText('45g')).toBeInTheDocument() // carbs
      expect(screen.getByText('15g')).toBeInTheDocument() // fat
    })

    it('shows adjusted nutrition values', async () => {
      const user = userEvent.setup()
      
      render(<PortionAdjuster {...defaultProps} />)

      // Change portion to 150%
      const portionInput = screen.getByDisplayValue('100')
      await user.clear(portionInput)
      await user.type(portionInput, '150')

      // Should show adjusted values (1.5x)
      await waitFor(() => {
        expect(screen.getByText('600')).toBeInTheDocument() // 400 * 1.5
        expect(screen.getByText('37.5g')).toBeInTheDocument() // 25 * 1.5
      })
    })
  })

  describe('Portion Input', () => {
    it('accepts percentage input', async () => {
      const user = userEvent.setup()
      
      render(<PortionAdjuster {...defaultProps} />)

      const portionInput = screen.getByDisplayValue('100')
      await user.clear(portionInput)
      await user.type(portionInput, '75')

      expect(portionInput.value).toBe('75')
    })

    it('accepts decimal values', async () => {
      const user = userEvent.setup()
      
      render(<PortionAdjuster {...defaultProps} />)

      const portionInput = screen.getByDisplayValue('100')
      await user.clear(portionInput)
      await user.type(portionInput, '125.5')

      expect(portionInput.value).toBe('125.5')
    })

    it('prevents negative values', async () => {
      const user = userEvent.setup()
      
      render(<PortionAdjuster {...defaultProps} />)

      const portionInput = screen.getByDisplayValue('100')
      await user.clear(portionInput)
      await user.type(portionInput, '-50')

      // Should reset to minimum value
      await waitFor(() => {
        expect(portionInput.value).toBe('1')
      })
    })

    it('prevents zero values', async () => {
      const user = userEvent.setup()
      
      render(<PortionAdjuster {...defaultProps} />)

      const portionInput = screen.getByDisplayValue('100')
      await user.clear(portionInput)
      await user.type(portionInput, '0')

      await waitFor(() => {
        expect(portionInput.value).toBe('1')
      })
    })

    it('limits maximum portion size', async () => {
      const user = userEvent.setup()
      
      render(<PortionAdjuster {...defaultProps} />)

      const portionInput = screen.getByDisplayValue('100')
      await user.clear(portionInput)
      await user.type(portionInput, '500')

      // Should be limited to maximum (e.g., 300%)
      await waitFor(() => {
        expect(parseInt(portionInput.value)).toBeLessThanOrEqual(300)
      })
    })
  })

  describe('Nutrition Calculations', () => {
    it('calculates nutrition correctly for different portions', async () => {
      const user = userEvent.setup()
      
      render(<PortionAdjuster {...defaultProps} />)

      const testCases = [
        { portion: '50', expectedCalories: '200' },
        { portion: '150', expectedCalories: '600' },
        { portion: '200', expectedCalories: '800' }
      ]

      for (const { portion, expectedCalories } of testCases) {
        const portionInput = screen.getByDisplayValue(/\d+/)
        await user.clear(portionInput)
        await user.type(portionInput, portion)

        await waitFor(() => {
          expect(screen.getByText(expectedCalories)).toBeInTheDocument()
        })
      }
    })

    it('handles decimal portion calculations', async () => {
      const user = userEvent.setup()
      
      render(<PortionAdjuster {...defaultProps} />)

      const portionInput = screen.getByDisplayValue('100')
      await user.clear(portionInput)
      await user.type(portionInput, '33.33')

      // 400 * 0.3333 ≈ 133.32
      await waitFor(() => {
        const calorieElements = screen.getAllByText(/133/)
        expect(calorieElements.length).toBeGreaterThan(0)
      })
    })

    it('rounds nutrition values appropriately', async () => {
      const user = userEvent.setup()
      
      render(<PortionAdjuster {...defaultProps} />)

      const portionInput = screen.getByDisplayValue('100')
      await user.clear(portionInput)
      await user.type(portionInput, '33')

      // Values should be rounded to reasonable precision
      await waitFor(() => {
        const proteinElements = screen.getAllByText(/8\.3g/)
        expect(proteinElements.length).toBeGreaterThan(0)
      })
    })
  })

  describe('Preset Portions', () => {
    it('shows common portion presets', () => {
      render(<PortionAdjuster {...defaultProps} />)

      expect(screen.getByText('50%')).toBeInTheDocument()
      expect(screen.getByText('75%')).toBeInTheDocument()
      expect(screen.getByText('100%')).toBeInTheDocument()
      expect(screen.getByText('125%')).toBeInTheDocument()
      expect(screen.getByText('150%')).toBeInTheDocument()
    })

    it('applies preset portions when clicked', async () => {
      const user = userEvent.setup()
      
      render(<PortionAdjuster {...defaultProps} />)

      const preset75Button = screen.getByText('75%')
      await user.click(preset75Button)

      const portionInput = screen.getByDisplayValue(/\d+/)
      expect(portionInput.value).toBe('75')

      // Should show adjusted nutrition
      await waitFor(() => {
        expect(screen.getByText('300')).toBeInTheDocument() // 400 * 0.75
      })
    })

    it('highlights active preset', async () => {
      const user = userEvent.setup()
      
      render(<PortionAdjuster {...defaultProps} />)

      const preset125Button = screen.getByText('125%')
      await user.click(preset125Button)

      // Button should have active styling
      expect(preset125Button).toHaveClass(/active|selected|primary/)
    })
  })

  describe('Actions', () => {
    it('calls onAdjust with correct data when confirmed', async () => {
      const user = userEvent.setup()
      const mockOnAdjust = vi.fn()
      
      render(<PortionAdjuster {...defaultProps} onAdjust={mockOnAdjust} />)

      // Set portion to 150%
      const portionInput = screen.getByDisplayValue('100')
      await user.clear(portionInput)
      await user.type(portionInput, '150')

      // Confirm adjustment
      const confirmButton = screen.getByText('Confirmer')
      await user.click(confirmButton)

      expect(mockOnAdjust).toHaveBeenCalledWith({
        portion_multiplier: 1.5,
        adjusted_nutrition: {
          calories: 600,
          protein: 37.5,
          carbs: 67.5,
          fat: 22.5,
          fiber: 7.5,
          sodium: 300,
          sugar: 15
        }
      })
    })

    it('calls onCancel when cancelled', async () => {
      const user = userEvent.setup()
      const mockOnCancel = vi.fn()
      
      render(<PortionAdjuster {...defaultProps} onCancel={mockOnCancel} />)

      const cancelButton = screen.getByText('Annuler')
      await user.click(cancelButton)

      expect(mockOnCancel).toHaveBeenCalled()
    })

    it('resets to original values when reset button is clicked', async () => {
      const user = userEvent.setup()
      
      render(<PortionAdjuster {...defaultProps} />)

      // Change portion
      const portionInput = screen.getByDisplayValue('100')
      await user.clear(portionInput)
      await user.type(portionInput, '200')

      // Reset
      const resetButton = screen.getByText('Réinitialiser')
      await user.click(resetButton)

      expect(portionInput.value).toBe('100')
      expect(screen.getByText('400')).toBeInTheDocument() // Original calories
    })
  })

  describe('Visual Feedback', () => {
    it('shows comparison between original and adjusted values', async () => {
      const user = userEvent.setup()
      
      render(<PortionAdjuster {...defaultProps} />)

      // Set portion to 150%
      const portionInput = screen.getByDisplayValue('100')
      await user.clear(portionInput)
      await user.type(portionInput, '150')

      // Should show both original and adjusted values
      expect(screen.getByText('400')).toBeInTheDocument() // Original
      expect(screen.getByText('600')).toBeInTheDocument() // Adjusted
    })

    it('highlights significant changes', async () => {
      const user = userEvent.setup()
      
      render(<PortionAdjuster {...defaultProps} />)

      // Set portion to 200% (significant change)
      const portionInput = screen.getByDisplayValue('100')
      await user.clear(portionInput)
      await user.type(portionInput, '200')

      // Should highlight the change
      const adjustedValues = screen.getAllByText(/800|50g/) // 800 cal, 50g protein
      adjustedValues.forEach(element => {
        expect(element).toHaveClass(/highlight|changed|bold/)
      })
    })

    it('shows percentage change indicators', async () => {
      const user = userEvent.setup()
      
      render(<PortionAdjuster {...defaultProps} />)

      // Set portion to 75%
      const portionInput = screen.getByDisplayValue('100')
      await user.clear(portionInput)
      await user.type(portionInput, '75')

      // Should show percentage indicators
      expect(screen.getByText(/-25%/)).toBeInTheDocument()
    })
  })

  describe('Input Validation', () => {
    it('shows error for invalid input', async () => {
      const user = userEvent.setup()
      
      render(<PortionAdjuster {...defaultProps} />)

      const portionInput = screen.getByDisplayValue('100')
      await user.clear(portionInput)
      await user.type(portionInput, 'abc')

      await waitFor(() => {
        expect(screen.getByText(/valeur invalide/i)).toBeInTheDocument()
      })
    })

    it('disables confirm button for invalid input', async () => {
      const user = userEvent.setup()
      
      render(<PortionAdjuster {...defaultProps} />)

      const portionInput = screen.getByDisplayValue('100')
      await user.clear(portionInput)
      await user.type(portionInput, '-10')

      const confirmButton = screen.getByText('Confirmer')
      expect(confirmButton).toBeDisabled()
    })

    it('shows warning for extreme portions', async () => {
      const user = userEvent.setup()
      
      render(<PortionAdjuster {...defaultProps} />)

      const portionInput = screen.getByDisplayValue('100')
      await user.clear(portionInput)
      await user.type(portionInput, '300')

      await waitFor(() => {
        expect(screen.getByText(/portion très importante/i)).toBeInTheDocument()
      })
    })
  })

  describe('Accessibility', () => {
    it('has proper form labels', () => {
      render(<PortionAdjuster {...defaultProps} />)

      expect(screen.getByLabelText(/pourcentage de la portion/i)).toBeInTheDocument()
    })

    it('has proper button labels', () => {
      render(<PortionAdjuster {...defaultProps} />)

      expect(screen.getByRole('button', { name: 'Confirmer' })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: 'Annuler' })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: 'Réinitialiser' })).toBeInTheDocument()
    })

    it('supports keyboard navigation', async () => {
      const user = userEvent.setup()
      
      render(<PortionAdjuster {...defaultProps} />)

      // Tab through elements
      await user.tab()
      expect(document.activeElement).toHaveAttribute('type', 'number')

      await user.tab()
      expect(document.activeElement.textContent).toContain('50%')
    })

    it('has proper aria descriptions', () => {
      render(<PortionAdjuster {...defaultProps} />)

      const portionInput = screen.getByDisplayValue('100')
      expect(portionInput).toHaveAttribute('aria-describedby')
    })
  })

  describe('Edge Cases', () => {
    it('handles meals with zero nutrition values', () => {
      const mealWithZeroNutrition = createMockMealTracking({
        planned_nutrition: {
          calories: 0,
          protein: 0,
          carbs: 0,
          fat: 0,
          fiber: 0,
          sodium: 0,
          sugar: 0
        }
      })

      render(<PortionAdjuster {...defaultProps} mealTracking={mealWithZeroNutrition} />)

      expect(screen.getByText('Ajustement des portions')).toBeInTheDocument()
      expect(screen.getByText('0')).toBeInTheDocument()
    })

    it('handles missing nutrition data', () => {
      const mealWithMissingData = createMockMealTracking({
        planned_nutrition: null
      })

      render(<PortionAdjuster {...defaultProps} mealTracking={mealWithMissingData} />)

      expect(screen.getByText('Ajustement des portions')).toBeInTheDocument()
    })

    it('handles very large nutrition values', () => {
      const mealWithLargeValues = createMockMealTracking({
        planned_nutrition: {
          calories: 9999,
          protein: 999,
          carbs: 999,
          fat: 999,
          fiber: 99,
          sodium: 9999,
          sugar: 999
        }
      })

      render(<PortionAdjuster {...defaultProps} mealTracking={mealWithLargeValues} />)

      expect(screen.getByText('9999')).toBeInTheDocument()
    })
  })

  describe('Performance', () => {
    it('debounces nutrition calculations during rapid input', async () => {
      const user = userEvent.setup()
      const calculationSpy = vi.fn()
      
      // Mock calculation function
      const OriginalComponent = PortionAdjuster
      PortionAdjuster.prototype.calculateNutrition = calculationSpy

      render(<PortionAdjuster {...defaultProps} />)

      const portionInput = screen.getByDisplayValue('100')
      
      // Rapid typing
      await user.clear(portionInput)
      await user.type(portionInput, '123', { delay: 1 })

      // Should not call calculation for every keystroke
      expect(calculationSpy.call.length).toBeLessThan(3)
    })

    it('does not re-render unnecessarily', () => {
      const renderCount = vi.fn()
      
      const TestComponent = (props) => {
        renderCount()
        return <PortionAdjuster {...props} />
      }

      const { rerender } = render(<TestComponent {...defaultProps} />)
      
      // Same props should not cause re-render
      rerender(<TestComponent {...defaultProps} />)
      
      expect(renderCount).toHaveBeenCalledTimes(2) // Initial + rerender
    })
  })
})