/**
 * Test utilities for meal tracking components
 * Provides custom render functions and mock data
 */

import React from 'react'
import { render } from '@testing-library/react'
import { vi } from 'vitest'

// Mock data factories
export const createMockMealTracking = (overrides = {}) => ({
  id: 1,
  user_id: 1,
  meal_date: '2025-08-08',
  meal_type: 'repas1',
  meal_name: 'Test Breakfast',
  status: 'planned',
  planned_nutrition: {
    calories: 400,
    protein: 25,
    carbs: 45,
    fat: 15,
    fiber: 5,
    sodium: 200,
    sugar: 10
  },
  actual_nutrition: null,
  effective_nutrition: {
    calories: 400,
    protein: 25,
    carbs: 45,
    fat: 15,
    fiber: 5,
    sodium: 200,
    sugar: 10
  },
  planned_portion_size: 1.0,
  actual_portion_size: null,
  consumption_datetime: null,
  user_notes: null,
  satisfaction_rating: null,
  difficulty_rating: null,
  photo_urls: [],
  modifications: {},
  substitutions: {},
  timing_variance_minutes: null,
  is_consumed: false,
  created_at: '2025-08-08T08:00:00Z',
  updated_at: '2025-08-08T08:00:00Z',
  ...overrides
})

export const createMockDailySummary = (overrides = {}) => ({
  id: 1,
  user_id: 1,
  summary_date: '2025-08-08',
  planned_nutrition: {
    calories: 1800,
    protein: 120,
    carbs: 225,
    fat: 60,
    fiber: 25,
    sodium: 2000,
    sugar: 50
  },
  actual_nutrition: {
    calories: 1750,
    protein: 115,
    carbs: 220,
    fat: 58,
    fiber: 23,
    sodium: 1900,
    sugar: 45
  },
  target_nutrition: {
    calories: 1800,
    protein: 120,
    carbs: 225,
    fat: 60,
    fiber: 25,
    sodium: 2000,
    sugar: 50
  },
  adherence_scores: {
    plan_adherence: 97.2,
    target_adherence: 97.2,
    calorie_adherence: 97.2,
    protein_adherence: 92.3,
    overall_nutrition: 94.8,
    balance_score: 95.1
  },
  meal_stats: {
    planned: 3,
    consumed: 2,
    skipped: 1,
    replaced: 0,
    modified: 0,
    completion_rate: 66.7,
    skip_rate: 33.3,
    modification_rate: 0.0
  },
  deficit_surplus: {
    calories: 50,
    protein: -5,
    carbs: -5,
    fat: -2,
    fiber: -2,
    sodium: -100,
    sugar: -5
  },
  timing: {
    avg_variance_minutes: null,
    on_time_meals: 0,
    timing_adherence_rate: 0
  },
  quality: {
    avg_satisfaction_rating: null,
    avg_difficulty_rating: null
  },
  achievements: {
    hit_calorie_target: true,
    hit_protein_target: false,
    hit_carbs_target: true,
    hit_fat_target: true,
    hit_fiber_target: false,
    stayed_under_sodium_limit: true,
    stayed_under_sugar_limit: true
  },
  week_start: '2025-08-04',
  month_year: '2025-08',
  ...overrides
})

export const createMockUser = (overrides = {}) => ({
  id: 1,
  name: 'Test User',
  email: 'test@example.com',
  age: 30,
  sex: 'M',
  height: 175,
  weight: 75,
  activity_level: 'moderate',
  goal: 'maintenance',
  ...overrides
})

// Mock API responses
export const mockApiResponse = (data, status = 200) => ({
  ok: status >= 200 && status < 300,
  status,
  json: vi.fn().mockResolvedValue(data),
  text: vi.fn().mockResolvedValue(JSON.stringify(data))
})

export const mockSuccessResponse = (data) => mockApiResponse(data, 200)
export const mockErrorResponse = (error, status = 500) => mockApiResponse({ error }, status)

// Mock fetch for specific endpoints
export const mockFetchEndpoint = (endpoint, response) => {
  global.fetch.mockImplementation((url) => {
    if (url.includes(endpoint)) {
      return Promise.resolve(response)
    }
    return Promise.reject(new Error(`Unmocked endpoint: ${url}`))
  })
}

// Mock multiple endpoints
export const mockFetchEndpoints = (endpoints) => {
  global.fetch.mockImplementation((url) => {
    for (const [pattern, response] of Object.entries(endpoints)) {
      if (url.includes(pattern)) {
        return Promise.resolve(response)
      }
    }
    return Promise.reject(new Error(`Unmocked endpoint: ${url}`))
  })
}

// Create mock store state
export const createMockStoreState = (overrides = {}) => ({
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
  pendingActions: [],
  ...overrides
})

// Mock hooks
export const createMockMealTrackingHook = (overrides = {}) => ({
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
  markMealConsumed: vi.fn(),
  adjustMealPortions: vi.fn(),
  skipMeal: vi.fn(),
  replaceMeal: vi.fn(),
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
  mealsByType: {},
  ...overrides
})

// Custom render function with providers
export const renderWithProviders = (ui, options = {}) => {
  const Wrapper = ({ children }) => {
    return (
      <div>
        {children}
      </div>
    )
  }

  return render(ui, {
    wrapper: Wrapper,
    ...options
  })
}

// Wait for async operations
export const waitForAsyncOperations = () => new Promise(resolve => setTimeout(resolve, 0))

// Simulate user interactions
export const simulateNetworkDelay = (ms = 100) => 
  new Promise(resolve => setTimeout(resolve, ms))

// Test data generators
export const generateMealTrackings = (count = 3) => {
  const mealTypes = ['repas1', 'repas2', 'repas3', 'collation']
  const statuses = ['planned', 'consumed', 'modified', 'skipped', 'replaced']
  
  return Array.from({ length: count }, (_, index) => 
    createMockMealTracking({
      id: index + 1,
      meal_type: mealTypes[index % mealTypes.length],
      status: statuses[index % statuses.length],
      meal_name: `Test Meal ${index + 1}`
    })
  )
}

export const generateWeekOfTrackings = (startDate = '2025-08-04') => {
  const trackings = {}
  const start = new Date(startDate)
  
  for (let i = 0; i < 7; i++) {
    const date = new Date(start)
    date.setDate(start.getDate() + i)
    const dateStr = date.toISOString().split('T')[0]
    
    trackings[dateStr] = generateMealTrackings(3)
  }
  
  return trackings
}

// Error handling test utilities
export const expectAsyncError = async (asyncFn, expectedError) => {
  try {
    await asyncFn()
    throw new Error('Expected function to throw an error')
  } catch (error) {
    expect(error.message).toContain(expectedError)
  }
}

// DOM testing utilities
export const getByTestId = (container, testId) => 
  container.querySelector(`[data-testid="${testId}"]`)

export const getAllByTestId = (container, testId) => 
  container.querySelectorAll(`[data-testid="${testId}"]`)

// Form testing utilities
export const fillForm = async (user, formData) => {
  for (const [field, value] of Object.entries(formData)) {
    const input = screen.getByRole('textbox', { name: new RegExp(field, 'i') })
    await user.clear(input)
    await user.type(input, value)
  }
}

// Mock component props
export const createMockComponentProps = (component, overrides = {}) => {
  const defaultProps = {
    MealCard: {
      mealTracking: createMockMealTracking(),
      onStatusChange: vi.fn(),
      disabled: false
    },
    MealTracker: {
      className: ''
    },
    PortionAdjuster: {
      mealTracking: createMockMealTracking(),
      onAdjust: vi.fn(),
      onCancel: vi.fn()
    },
    DailySummary: {
      summary: createMockDailySummary(),
      className: ''
    }
  }
  
  return {
    ...defaultProps[component],
    ...overrides
  }
}