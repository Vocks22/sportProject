# US1.8 Meal Tracking - Comprehensive Test Suite

## Overview

This test suite provides comprehensive coverage for the US1.8 Meal Tracking feature in the DietTracker application. The tests are designed to ensure the reliability, performance, and correctness of all meal tracking functionality.

## Architecture

### Backend Testing Stack
- **Framework**: pytest
- **Database**: SQLite (in-memory for tests)
- **Mocking**: unittest.mock
- **Coverage**: pytest-cov
- **Performance**: Custom timing utilities

### Frontend Testing Stack
- **Framework**: Vitest + React Testing Library
- **Component Testing**: @testing-library/react
- **User Interactions**: @testing-library/user-event
- **Mocking**: Vitest mocks
- **Store Testing**: Direct Zustand store testing

## Test Structure

### Backend Tests

#### 1. Model Tests (`test_models.py`)
**Coverage**: 95%+ target

Tests for database models and business logic:

- **MealTracking Model**
  - Creation and validation
  - Status transitions and constraints
  - JSON field serialization/deserialization
  - Calculated properties (variance, effective nutrition)
  - Relationships with other models

- **DailyNutritionSummary Model**
  - Summary calculations and aggregations
  - Adherence score algorithms
  - Achievement flag logic
  - Temporal data handling

- **Data Integrity**
  - Unique constraints
  - Check constraints
  - Cascade deletes
  - Database indexes

#### 2. Service Tests (`test_meal_tracking_service.py`)
**Coverage**: 90%+ target

Tests for business logic layer:

- **Meal Plan Integration**
  - Creating trackings from meal plans
  - Handling missing or invalid plans
  - Recipe nutrition synchronization

- **Status Management**
  - Meal consumption workflows
  - Portion adjustments
  - Meal replacements and skipping
  - Offline action queuing

- **Summary Calculations**
  - Daily summary generation
  - Weekly and monthly aggregations
  - Adherence trend analysis
  - Performance with large datasets

#### 3. API Tests (`test_meal_tracking_api.py`)
**Coverage**: 85%+ target

Tests for REST API endpoints:

- **Endpoint Functionality**
  - All meal tracking routes
  - Request validation
  - Response formatting
  - Error handling

- **Security**
  - User authorization
  - Data isolation
  - Input sanitization

- **Integration**
  - Service layer integration
  - Database transaction handling
  - Concurrent request handling

#### 4. Integration Tests (`test_integration.py`)
**Coverage**: End-to-end workflows

Tests for complete user workflows:

- **Daily Workflows**
  - Complete meal tracking day
  - Mixed meal statuses
  - Summary generation

- **Long-term Patterns**
  - Weekly tracking patterns
  - Monthly reporting
  - Adherence trend analysis

- **Edge Cases**
  - Large datasets
  - Concurrent operations
  - Data migration scenarios

#### 5. Test Fixtures (`test_fixtures.py`)

Advanced data factories for complex testing scenarios:

- **Realistic Data Generation**
  - Week/month of meal data
  - User behavior patterns
  - Adherence progressions

- **Edge Case Data**
  - Extreme values
  - Missing data scenarios
  - Performance test datasets

### Frontend Tests

#### 1. Component Tests

**MealCard Component** (`MealCard.test.jsx`)
- Rendering with different meal states
- Action button functionality
- Status transitions (consume, skip, replace, adjust)
- Form validations and user interactions
- Error handling and loading states

**MealTracker Component** (`MealTracker.test.jsx`)
- Main dashboard functionality
- Date navigation
- Meal overview and statistics
- Offline mode handling
- Summary display

**PortionAdjuster Component** (`PortionAdjuster.test.jsx`)
- Portion calculation logic
- Preset portion selections
- Nutrition value updates
- Input validation
- User experience flows

#### 2. Hook Tests (`useMealTracking.test.js`)

**Zustand Store Testing**
- State management
- Action dispatching
- Persistence handling
- Cache management

**API Integration**
- Network request handling
- Error states
- Offline queue management
- Data synchronization

**Computed Properties**
- Nutrition totals
- Completion statistics
- Meal grouping

## Testing Strategy

### 1. Test Categories

#### Unit Tests (70% of tests)
- Isolated component/function testing
- Mock external dependencies
- Fast execution (<5ms per test)
- High code coverage target (90%+)

#### Integration Tests (25% of tests)
- Multi-layer interaction testing
- Database integration
- API contract testing
- Realistic data scenarios

#### End-to-End Tests (5% of tests)
- Complete user workflows
- Browser automation
- Performance benchmarking
- Edge case scenarios

### 2. Coverage Requirements

#### Backend Coverage Targets
- Models: 95%+
- Services: 90%+
- API Routes: 85%+
- Overall: 90%+

#### Frontend Coverage Targets
- Components: 85%+
- Hooks: 90%+
- Utilities: 95%+
- Overall: 85%+

### 3. Test Data Strategy

#### Realistic Test Data
- Based on actual user behavior patterns
- Varied nutrition values and portions
- Realistic timing and adherence patterns
- Edge cases and boundary conditions

#### Data Factories
- Parameterized data generation
- Consistent but varied test data
- Performance-optimized creation
- Clean-up and isolation

### 4. Performance Testing

#### Load Testing
- Large dataset handling (10K+ meals)
- Concurrent user simulation
- Memory usage monitoring
- Database query optimization

#### Response Time Targets
- API endpoints: <200ms average
- Database queries: <100ms
- Frontend renders: <16ms (60fps)
- Summary calculations: <500ms

## Running Tests

### Backend Tests

```bash
# Run all backend tests
cd src/backend
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=. --cov-report=html

# Run specific test files
python -m pytest tests/test_models.py -v
python -m pytest tests/test_meal_tracking_service.py -v
python -m pytest tests/test_meal_tracking_api.py -v

# Run integration tests
python -m pytest tests/test_integration.py -v

# Performance tests
python -m pytest tests/test_integration.py::TestMealTrackingIntegration::test_performance_with_large_datasets -v
```

### Frontend Tests

```bash
# Run all frontend tests
cd src/frontend
npm test

# Run with coverage
npm run test:coverage

# Run specific test files
npm test -- --run tests/components/MealCard.test.jsx
npm test -- --run tests/components/MealTracker.test.jsx
npm test -- --run tests/hooks/useMealTracking.test.js

# Watch mode for development
npm run test:watch
```

### Full Test Suite

```bash
# Run complete test suite
npm run test:full

# Generate coverage reports
npm run test:coverage:full
```

## Test Environment Configuration

### Backend Configuration

```python
# pytest.ini or pyproject.toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --tb=short --strict-markers"
markers = [
    "unit: Unit tests",
    "integration: Integration tests",
    "performance: Performance tests",
    "slow: Slow-running tests"
]
```

### Frontend Configuration

```javascript
// vitest.config.js
export default {
  test: {
    environment: 'jsdom',
    setupFiles: ['./tests/setup.js'],
    coverage: {
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'tests/',
        '**/*.d.ts',
      ]
    }
  }
}
```

## Continuous Integration

### GitHub Actions Workflow

```yaml
name: US1.8 Meal Tracking Tests

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          cd src/backend
          pip install -r requirements.txt
          pip install pytest pytest-cov
      - name: Run tests
        run: |
          cd src/backend
          python -m pytest tests/ --cov=. --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      - name: Install dependencies
        run: |
          cd src/frontend
          npm ci
      - name: Run tests
        run: |
          cd src/frontend
          npm run test:ci
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

## Quality Gates

### Automated Checks
- All tests must pass
- Coverage thresholds must be met
- No linting errors
- Performance benchmarks within limits

### Code Review Checklist
- [ ] New features have corresponding tests
- [ ] Tests cover both happy path and error cases
- [ ] Integration tests verify end-to-end functionality
- [ ] Performance implications are considered
- [ ] Test data is realistic and comprehensive

## Troubleshooting

### Common Issues

#### Backend
- **Database lock errors**: Ensure proper test isolation
- **Import errors**: Check Python path and module structure
- **Fixture conflicts**: Use unique fixture names and proper scoping

#### Frontend
- **Mock issues**: Verify mock setup in beforeEach/afterEach
- **Async test problems**: Use proper await and waitFor patterns
- **Component rendering**: Ensure proper provider setup

### Debug Mode

```bash
# Backend debug mode
python -m pytest tests/test_models.py::TestMealTrackingModel::test_meal_tracking_creation -v -s --pdb

# Frontend debug mode
npm test -- --reporter=verbose tests/components/MealCard.test.jsx
```

## Maintenance

### Regular Tasks
- Update test data to reflect real-world patterns
- Review and optimize slow tests
- Maintain test documentation
- Update coverage targets as code evolves

### Test Metrics Monitoring
- Track test execution time trends
- Monitor coverage changes
- Identify flaky tests
- Performance regression detection

This comprehensive test suite ensures the reliability and maintainability of the US1.8 Meal Tracking feature, providing confidence in the system's behavior across all scenarios and edge cases.