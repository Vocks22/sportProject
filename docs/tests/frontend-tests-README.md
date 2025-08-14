# Frontend Testing Documentation - US1.8 Meal Tracking

## Overview

This document outlines the frontend testing strategy and implementation for the US1.8 Meal Tracking feature. Our testing approach ensures reliable, maintainable, and user-friendly meal tracking functionality.

## Testing Philosophy

### User-Centric Testing
- Tests focus on user interactions and experiences
- Test behavior, not implementation details
- Verify accessibility and usability
- Cover real-world usage scenarios

### Component Testing Strategy
- Test components in isolation with mocked dependencies
- Test integration between components
- Verify state management and data flow
- Ensure error handling and loading states

## Test Structure

### Test Organization
```
src/frontend/tests/
├── setup.js                 # Test configuration
├── utils/
│   └── test-utils.jsx       # Test utilities and helpers
├── components/
│   ├── MealCard.test.jsx    # MealCard component tests
│   ├── MealTracker.test.jsx # MealTracker component tests
│   └── PortionAdjuster.test.jsx # PortionAdjuster tests
└── hooks/
    └── useMealTracking.test.js  # Hook and store tests
```

## Testing Tools and Libraries

### Core Testing Framework
- **Vitest**: Fast unit test runner with Jest compatibility
- **React Testing Library**: Component testing utilities
- **@testing-library/user-event**: User interaction simulation
- **@testing-library/jest-dom**: DOM assertions

### Mocking and Utilities
- **Vitest mocks**: Mock functions and modules
- **MSW (Future)**: API mocking for integration tests
- **Custom test utilities**: Reusable testing helpers

## Test Categories

### 1. Component Tests

#### MealCard Component Tests
**File**: `tests/components/MealCard.test.jsx`

**Test Coverage**:
- Rendering with different meal statuses
- Action button states and interactions
- Form validations and user input
- Status transitions (consume, skip, replace, adjust)
- Error handling and loading states
- Accessibility compliance

**Key Test Scenarios**:
```javascript
describe('MealCard Component', () => {
  it('renders meal information correctly')
  it('shows appropriate actions for each status')
  it('handles meal consumption workflow')
  it('validates portion adjustments')
  it('manages offline interactions')
  it('provides accessible user interface')
})
```

#### MealTracker Component Tests
**File**: `tests/components/MealTracker.test.jsx`

**Test Coverage**:
- Dashboard layout and navigation
- Date selection and navigation
- Meal overview and statistics
- Quick add functionality
- Error states and recovery
- Offline mode handling

**Key Test Scenarios**:
```javascript
describe('MealTracker Component', () => {
  it('displays daily meal overview')
  it('navigates between dates correctly')
  it('handles empty states gracefully')
  it('shows nutrition summaries')
  it('manages loading and error states')
  it('supports offline operations')
})
```

#### PortionAdjuster Component Tests
**File**: `tests/components/PortionAdjuster.test.jsx`

**Test Coverage**:
- Portion calculation accuracy
- Preset portion selections
- Real-time nutrition updates
- Input validation and constraints
- User experience flows

**Key Test Scenarios**:
```javascript
describe('PortionAdjuster Component', () => {
  it('calculates nutrition values correctly')
  it('applies preset portions accurately')
  it('validates user input properly')
  it('shows visual feedback for changes')
  it('handles edge cases gracefully')
})
```

### 2. Hook and Store Tests

#### useMealTracking Hook Tests
**File**: `tests/hooks/useMealTracking.test.js`

**Test Coverage**:
- Zustand store state management
- API integration and error handling
- Offline queue management
- Data synchronization
- Computed property calculations

**Key Test Scenarios**:
```javascript
describe('useMealTracking Hook', () => {
  it('manages meal tracking state correctly')
  it('handles API calls and responses')
  it('queues offline actions properly')
  it('calculates nutrition totals accurately')
  it('synchronizes data when online')
})
```

## Test Utilities and Helpers

### Custom Render Function
```javascript
// tests/utils/test-utils.jsx
export const renderWithProviders = (ui, options = {}) => {
  const Wrapper = ({ children }) => (
    <div>{children}</div>
  )
  return render(ui, { wrapper: Wrapper, ...options })
}
```

### Mock Data Factories
```javascript
export const createMockMealTracking = (overrides = {}) => ({
  id: 1,
  meal_name: 'Test Meal',
  status: 'planned',
  planned_nutrition: { calories: 400, protein: 25 },
  // ... other properties
  ...overrides
})
```

### Test Configuration
```javascript
// tests/setup.js
import '@testing-library/jest-dom'
import { cleanup } from '@testing-library/react'

beforeEach(() => {
  // Reset mocks and state
})

afterEach(() => {
  cleanup()
  vi.clearAllMocks()
})
```

## Testing Best Practices

### 1. Test Naming and Organization

#### Descriptive Test Names
```javascript
// Good
it('shows error message when API call fails')
it('disables submit button during loading state')

// Bad
it('works correctly')
it('handles errors')
```

#### Logical Test Grouping
```javascript
describe('MealCard Component', () => {
  describe('Rendering', () => {
    it('renders basic meal information')
    it('shows correct status badge')
  })
  
  describe('User Interactions', () => {
    it('handles consume button click')
    it('validates portion input')
  })
})
```

### 2. User-Centric Testing Approach

#### Query by Role and Label
```javascript
// Good - queries like a user would
expect(screen.getByRole('button', { name: 'Consommer' }))
expect(screen.getByLabelText('Portion size'))

// Bad - queries by implementation details
expect(container.querySelector('.consume-btn'))
expect(getByTestId('portion-input'))
```

#### Test User Interactions
```javascript
it('allows user to consume meal with rating', async () => {
  const user = userEvent.setup()
  
  render(<MealCard mealTracking={mockMeal} />)
  
  // User clicks consume button
  await user.click(screen.getByRole('button', { name: 'Consommer' }))
  
  // User rates the meal
  await user.click(screen.getByRole('button', { name: '5 étoiles' }))
  
  // User confirms
  await user.click(screen.getByRole('button', { name: 'Confirmer' }))
  
  // Verify outcome
  expect(mockOnStatusChange).toHaveBeenCalledWith(...)
})
```

### 3. Async Testing Patterns

#### Waiting for Changes
```javascript
it('shows loading state during API call', async () => {
  mockApiCall.mockImplementation(() => new Promise(resolve => 
    setTimeout(() => resolve(mockData), 100)
  ))
  
  render(<MealTracker />)
  
  // Trigger API call
  fireEvent.click(screen.getByText('Refresh'))
  
  // Wait for loading state
  expect(screen.getByText('Chargement...')).toBeInTheDocument()
  
  // Wait for completion
  await waitFor(() => {
    expect(screen.queryByText('Chargement...')).not.toBeInTheDocument()
  })
})
```

### 4. Error Testing

#### Network Errors
```javascript
it('displays error when network fails', async () => {
  mockFetch.mockRejectedValueOnce(new Error('Network error'))
  
  render(<MealTracker />)
  
  await waitFor(() => {
    expect(screen.getByText(/erreur de réseau/i)).toBeInTheDocument()
  })
})
```

#### Validation Errors
```javascript
it('shows validation error for invalid input', async () => {
  const user = userEvent.setup()
  
  render(<PortionAdjuster {...props} />)
  
  await user.clear(screen.getByLabelText('Portion'))
  await user.type(screen.getByLabelText('Portion'), '-50')
  
  expect(screen.getByText('Valeur invalide')).toBeInTheDocument()
})
```

## Mocking Strategies

### 1. API Mocking

#### Simple Fetch Mock
```javascript
beforeEach(() => {
  global.fetch = vi.fn()
})

afterEach(() => {
  global.fetch.mockRestore()
})

it('loads meal data successfully', async () => {
  global.fetch.mockResolvedValueOnce({
    ok: true,
    json: async () => ({ meal_trackings: [mockMeal] })
  })
  
  render(<MealTracker />)
  
  await waitFor(() => {
    expect(screen.getByText('Test Meal')).toBeInTheDocument()
  })
})
```

#### Module Mocking
```javascript
vi.mock('../../hooks/useMealTracking', () => ({
  useMealTracking: () => ({
    todayMealTrackings: [mockMeal],
    loadTodayMealTrackings: vi.fn(),
    markMealConsumed: vi.fn()
  })
}))
```

### 2. Store Mocking

#### Zustand Store Testing
```javascript
describe('useMealTrackingStore', () => {
  beforeEach(() => {
    useMealTrackingStore.setState({
      todayMealTrackings: [],
      isLoading: false,
      error: null
    })
  })
  
  it('updates meal trackings', () => {
    const { result } = renderHook(() => useMealTrackingStore())
    
    act(() => {
      result.current.setTodayMealTrackings([mockMeal])
    })
    
    expect(result.current.todayMealTrackings).toEqual([mockMeal])
  })
})
```

## Performance Testing

### Render Performance
```javascript
it('renders large meal lists efficiently', () => {
  const largeMealList = Array.from({ length: 100 }, (_, i) => 
    createMockMealTracking({ id: i })
  )
  
  const startTime = performance.now()
  render(<MealTracker todayMealTrackings={largeMealList} />)
  const renderTime = performance.now() - startTime
  
  expect(renderTime).toBeLessThan(100) // 100ms threshold
})
```

### Memory Leak Detection
```javascript
it('cleans up properly on unmount', () => {
  const { unmount } = render(<MealTracker />)
  
  // Verify no memory leaks
  unmount()
  
  // Check that event listeners are cleaned up
  // Check that timers are cleared
  // Check that subscriptions are cancelled
})
```

## Accessibility Testing

### Screen Reader Support
```javascript
it('provides proper screen reader support', () => {
  render(<MealCard mealTracking={mockMeal} />)
  
  expect(screen.getByRole('article')).toHaveAccessibleName()
  expect(screen.getByRole('button', { name: 'Consommer' }))
    .toHaveAttribute('aria-describedby')
})
```

### Keyboard Navigation
```javascript
it('supports keyboard navigation', async () => {
  const user = userEvent.setup()
  render(<MealTracker />)
  
  // Tab through interactive elements
  await user.tab()
  expect(document.activeElement).toHaveAttribute('role', 'button')
  
  // Activate with Enter/Space
  await user.keyboard('{Enter}')
  expect(mockAction).toHaveBeenCalled()
})
```

## Coverage Requirements

### Component Coverage Targets
- **Statements**: 85%+
- **Branches**: 80%+
- **Functions**: 90%+
- **Lines**: 85%+

### Coverage Exclusions
```javascript
// vitest.config.js
export default {
  test: {
    coverage: {
      exclude: [
        'tests/**',
        '**/*.d.ts',
        '**/node_modules/**',
        '**/*.config.js'
      ]
    }
  }
}
```

## Running Tests

### Development Workflow
```bash
# Install dependencies
npm install

# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run with coverage
npm run test:coverage

# Run specific test file
npm test -- MealCard.test.jsx

# Debug mode
npm test -- --reporter=verbose MealCard.test.jsx
```

### CI/CD Integration
```bash
# CI test command
npm run test:ci

# Generate coverage reports
npm run test:coverage:ci
```

## Debugging Tests

### Debug Test Failures
```javascript
it('debugs component state', () => {
  render(<MealCard mealTracking={mockMeal} />)
  
  // Debug DOM structure
  screen.debug()
  
  // Debug specific element
  screen.debug(screen.getByRole('button'))
  
  // Log component props
  console.log('Props:', mockMeal)
})
```

### Isolate Test Issues
```bash
# Run single test
npm test -- --run tests/components/MealCard.test.jsx -t "specific test name"

# Run with verbose output
npm test -- --reporter=verbose
```

## Maintenance and Updates

### Regular Maintenance Tasks
- Update test data to match real-world scenarios
- Review and remove obsolete tests
- Optimize slow-running tests
- Update dependencies and testing tools

### Test Quality Checklist
- [ ] Tests are independent and isolated
- [ ] Tests use realistic data
- [ ] Error cases are covered
- [ ] Accessibility is tested
- [ ] Performance is considered
- [ ] Tests are maintainable and readable

This comprehensive testing strategy ensures the frontend meal tracking functionality is robust, user-friendly, and maintainable across all scenarios and user interactions.