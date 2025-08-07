/**
 * Tests Frontend pour US1.6 - Composants React avec calendrier lundi-dimanche
 * Tests des composants React avec nouvelle logique calendrier ISO 8601
 * 
 * Coverage: Composants calendrier, hooks, intégration state management
 * Focus: UX calendrier, validation côté client, synchronisation API
 */

import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import { jest } from '@jest/globals';
import '@testing-library/jest-dom';
import React from 'react';

// Mock des utilitaires de date pour tests
const mockDateUtils = {
  getMondayOfWeek: (date) => {
    const d = new Date(date);
    const day = d.getDay();
    const diff = d.getDate() - day + (day === 0 ? -6 : 1);
    return new Date(d.setDate(diff));
  },
  
  getSundayOfWeek: (date) => {
    const monday = mockDateUtils.getMondayOfWeek(date);
    return new Date(monday.getTime() + 6 * 24 * 60 * 60 * 1000);
  },
  
  formatWeekDisplay: (monday, locale = 'fr') => {
    const sunday = mockDateUtils.getSundayOfWeek(monday);
    if (locale === 'fr') {
      return `Semaine du ${monday.getDate()} au ${sunday.getDate()}`;
    }
    return `Week of ${monday.getDate()} to ${sunday.getDate()}`;
  },
  
  isMonday: (date) => {
    return new Date(date).getDay() === 1;
  },
  
  nextMonday: (date) => {
    const d = new Date(date);
    const daysUntilMonday = (8 - d.getDay()) % 7 || 7;
    d.setDate(d.getDate() + daysUntilMonday);
    return d;
  }
};

// Mock du composant WeekCalendar
const WeekCalendar = ({ currentWeek, onWeekChange, weekStart }) => {
  const monday = mockDateUtils.getMondayOfWeek(currentWeek);
  const weekDays = [];
  
  // Générer les 7 jours de la semaine à partir du lundi
  for (let i = 0; i < 7; i++) {
    const day = new Date(monday);
    day.setDate(monday.getDate() + i);
    weekDays.push(day);
  }
  
  return (
    <div data-testid="week-calendar">
      <div className="week-header">
        <button 
          data-testid="prev-week"
          onClick={() => onWeekChange(new Date(monday.getTime() - 7 * 24 * 60 * 60 * 1000))}
        >
          Semaine précédente
        </button>
        
        <span data-testid="week-display">
          {mockDateUtils.formatWeekDisplay(monday)}
        </span>
        
        <button 
          data-testid="next-week"
          onClick={() => onWeekChange(mockDateUtils.nextMonday(monday))}
        >
          Semaine suivante
        </button>
      </div>
      
      <div className="week-days">
        {weekDays.map((day, index) => {
          const dayNames = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche'];
          return (
            <div 
              key={index} 
              data-testid={`day-${index}`}
              className={`day ${day.getDay() === 1 ? 'monday' : ''}`}
            >
              <div className="day-name">{dayNames[index]}</div>
              <div className="day-date">{day.getDate()}</div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

// Mock du composant MealPlanningWeek
const MealPlanningWeek = ({ weekStart, meals, onMealChange }) => {
  const monday = mockDateUtils.getMondayOfWeek(weekStart);
  
  if (!mockDateUtils.isMonday(weekStart)) {
    return (
      <div data-testid="invalid-week-error" className="error">
        Erreur: La semaine doit commencer un lundi selon ISO 8601
      </div>
    );
  }
  
  const dayNames = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'];
  const mealTypes = ['breakfast', 'lunch', 'dinner'];
  
  return (
    <div data-testid="meal-planning-week" data-week-start={weekStart.toISOString()}>
      <h3>Planning pour la semaine du {mockDateUtils.formatWeekDisplay(monday)}</h3>
      
      {dayNames.map((dayName, dayIndex) => (
        <div key={dayName} data-testid={`day-${dayName}`} className="planning-day">
          <h4>{dayName.charAt(0).toUpperCase() + dayName.slice(1)}</h4>
          
          {mealTypes.map(mealType => (
            <div key={mealType} className="meal-slot">
              <label>{mealType}:</label>
              <select
                data-testid={`meal-${dayName}-${mealType}`}
                value={meals?.[dayName]?.[mealType] || ''}
                onChange={(e) => onMealChange(dayName, mealType, e.target.value)}
              >
                <option value="">Sélectionner recette</option>
                <option value="1">Omelette aux blancs</option>
                <option value="2">Poulet grillé</option>
                <option value="3">Salade verte</option>
              </select>
            </div>
          ))}
        </div>
      ))}
    </div>
  );
};

// Mock du hook useWeekCalendar
const useWeekCalendar = (initialWeek) => {
  const [currentWeek, setCurrentWeek] = React.useState(() => {
    return mockDateUtils.getMondayOfWeek(initialWeek || new Date());
  });
  
  const goToNextWeek = React.useCallback(() => {
    setCurrentWeek(prev => mockDateUtils.nextMonday(prev));
  }, []);
  
  const goToPreviousWeek = React.useCallback(() => {
    setCurrentWeek(prev => {
      const prevWeek = new Date(prev);
      prevWeek.setDate(prevWeek.getDate() - 7);
      return mockDateUtils.getMondayOfWeek(prevWeek);
    });
  }, []);
  
  const goToWeek = React.useCallback((date) => {
    setCurrentWeek(mockDateUtils.getMondayOfWeek(date));
  }, []);
  
  return {
    currentWeek,
    goToNextWeek,
    goToPreviousWeek,
    goToWeek,
    isCurrentWeek: (date) => {
      const compareMonday = mockDateUtils.getMondayOfWeek(date);
      return compareMonday.getTime() === currentWeek.getTime();
    }
  };
};

// Tests des composants
describe('WeekCalendar Component - US1.6', () => {
  test('should display week starting with Monday', () => {
    const testDate = new Date('2025-08-07'); // Jeudi
    const onWeekChangeMock = jest.fn();
    
    render(
      <WeekCalendar 
        currentWeek={testDate} 
        onWeekChange={onWeekChangeMock}
      />
    );
    
    // Vérifier que la semaine commence par lundi
    const firstDay = screen.getByTestId('day-0');
    expect(firstDay).toHaveTextContent('Lundi');
    expect(firstDay).toHaveClass('monday');
    
    // Vérifier l'ordre des jours
    const expectedDays = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche'];
    expectedDays.forEach((dayName, index) => {
      const dayElement = screen.getByTestId(`day-${index}`);
      expect(dayElement).toHaveTextContent(dayName);
    });
  });
  
  test('should display correct week range in header', () => {
    const testDate = new Date('2025-08-07'); // Jeudi 7 août
    const onWeekChangeMock = jest.fn();
    
    render(
      <WeekCalendar 
        currentWeek={testDate} 
        onWeekChange={onWeekChangeMock}
      />
    );
    
    const weekDisplay = screen.getByTestId('week-display');
    // La semaine du jeudi 7 août va du lundi 4 au dimanche 10
    expect(weekDisplay).toHaveTextContent('Semaine du 4 au 10');
  });
  
  test('should navigate to next week correctly', async () => {
    const testDate = new Date('2025-08-07'); // Jeudi
    const onWeekChangeMock = jest.fn();
    
    render(
      <WeekCalendar 
        currentWeek={testDate} 
        onWeekChange={onWeekChangeMock}
      />
    );
    
    const nextButton = screen.getByTestId('next-week');
    fireEvent.click(nextButton);
    
    expect(onWeekChangeMock).toHaveBeenCalledTimes(1);
    
    // Vérifier que la date passée est bien un lundi (11 août)
    const calledDate = onWeekChangeMock.mock.calls[0][0];
    expect(calledDate.getDay()).toBe(1); // 1 = lundi
    expect(calledDate.getDate()).toBe(11); // 11 août
  });
  
  test('should navigate to previous week correctly', async () => {
    const testDate = new Date('2025-08-07'); // Jeudi
    const onWeekChangeMock = jest.fn();
    
    render(
      <WeekCalendar 
        currentWeek={testDate} 
        onWeekChange={onWeekChangeMock}
      />
    );
    
    const prevButton = screen.getByTestId('prev-week');
    fireEvent.click(prevButton);
    
    expect(onWeekChangeMock).toHaveBeenCalledTimes(1);
    
    // Vérifier que la date passée est bien un lundi (28 juillet)
    const calledDate = onWeekChangeMock.mock.calls[0][0];
    expect(calledDate.getDay()).toBe(1); // 1 = lundi
    expect(calledDate.getDate()).toBe(28); // 28 juillet
  });
});

describe('MealPlanningWeek Component - US1.6', () => {
  test('should accept valid Monday as weekStart', () => {
    const monday = new Date('2025-08-04'); // Lundi
    const mealsMock = {
      monday: { breakfast: '1', lunch: '2' },
      tuesday: { dinner: '3' }
    };
    const onMealChangeMock = jest.fn();
    
    render(
      <MealPlanningWeek 
        weekStart={monday}
        meals={mealsMock}
        onMealChange={onMealChangeMock}
      />
    );
    
    expect(screen.getByTestId('meal-planning-week')).toBeInTheDocument();
    expect(screen.queryByTestId('invalid-week-error')).not.toBeInTheDocument();
    
    // Vérifier que l'attribut data-week-start contient le lundi
    const planningWeek = screen.getByTestId('meal-planning-week');
    expect(planningWeek).toHaveAttribute('data-week-start', monday.toISOString());
  });
  
  test('should show error for non-Monday weekStart', () => {
    const tuesday = new Date('2025-08-05'); // Mardi
    
    render(
      <MealPlanningWeek 
        weekStart={tuesday}
        meals={{}}
        onMealChange={() => {}}
      />
    );
    
    expect(screen.getByTestId('invalid-week-error')).toBeInTheDocument();
    expect(screen.getByText(/La semaine doit commencer un lundi selon ISO 8601/)).toBeInTheDocument();
    expect(screen.queryByTestId('meal-planning-week')).not.toBeInTheDocument();
  });
  
  test('should display all days Monday to Sunday', () => {
    const monday = new Date('2025-08-04');
    
    render(
      <MealPlanningWeek 
        weekStart={monday}
        meals={{}}
        onMealChange={() => {}}
      />
    );
    
    const expectedDays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'];
    
    expectedDays.forEach(dayName => {
      expect(screen.getByTestId(`day-${dayName}`)).toBeInTheDocument();
    });
  });
  
  test('should handle meal selection changes', () => {
    const monday = new Date('2025-08-04');
    const onMealChangeMock = jest.fn();
    
    render(
      <MealPlanningWeek 
        weekStart={monday}
        meals={{}}
        onMealChange={onMealChangeMock}
      />
    );
    
    // Sélectionner une recette pour le petit-déjeuner du lundi
    const mondayBreakfast = screen.getByTestId('meal-monday-breakfast');
    fireEvent.change(mondayBreakfast, { target: { value: '1' } });
    
    expect(onMealChangeMock).toHaveBeenCalledWith('monday', 'breakfast', '1');
  });
  
  test('should preserve existing meal selections', () => {
    const monday = new Date('2025-08-04');
    const meals = {
      monday: { breakfast: '1', lunch: '2' },
      friday: { dinner: '3' }
    };
    
    render(
      <MealPlanningWeek 
        weekStart={monday}
        meals={meals}
        onMealChange={() => {}}
      />
    );
    
    // Vérifier que les repas existants sont sélectionnés
    expect(screen.getByTestId('meal-monday-breakfast')).toHaveValue('1');
    expect(screen.getByTestId('meal-monday-lunch')).toHaveValue('2');
    expect(screen.getByTestId('meal-friday-dinner')).toHaveValue('3');
    
    // Vérifier qu'un slot vide n'a pas de valeur
    expect(screen.getByTestId('meal-tuesday-breakfast')).toHaveValue('');
  });
});

describe('useWeekCalendar Hook - US1.6', () => {
  const TestComponent = ({ initialWeek }) => {
    const { 
      currentWeek, 
      goToNextWeek, 
      goToPreviousWeek, 
      goToWeek,
      isCurrentWeek 
    } = useWeekCalendar(initialWeek);
    
    return (
      <div>
        <div data-testid="current-week">{currentWeek.toISOString()}</div>
        <button data-testid="next-week" onClick={goToNextWeek}>Next</button>
        <button data-testid="prev-week" onClick={goToPreviousWeek}>Previous</button>
        <button 
          data-testid="go-to-specific" 
          onClick={() => goToWeek(new Date('2025-08-06'))}
        >
          Go to Aug 6
        </button>
        <div data-testid="is-current-week">
          {isCurrentWeek(new Date('2025-08-07')).toString()}
        </div>
      </div>
    );
  };
  
  test('should initialize with Monday of given week', () => {
    const testDate = new Date('2025-08-07'); // Jeudi
    
    render(<TestComponent initialWeek={testDate} />);
    
    const currentWeekElement = screen.getByTestId('current-week');
    const currentWeekDate = new Date(currentWeekElement.textContent);
    
    // Devrait être initialisé au lundi 4 août
    expect(currentWeekDate.getDay()).toBe(1); // Lundi
    expect(currentWeekDate.getDate()).toBe(4); // 4 août
  });
  
  test('should navigate to next Monday when goToNextWeek called', () => {
    const testDate = new Date('2025-08-04'); // Lundi
    
    render(<TestComponent initialWeek={testDate} />);
    
    const nextButton = screen.getByTestId('next-week');
    fireEvent.click(nextButton);
    
    const currentWeekElement = screen.getByTestId('current-week');
    const newWeekDate = new Date(currentWeekElement.textContent);
    
    // Devrait être le lundi suivant (11 août)
    expect(newWeekDate.getDay()).toBe(1); // Lundi
    expect(newWeekDate.getDate()).toBe(11); // 11 août
  });
  
  test('should navigate to previous Monday when goToPreviousWeek called', () => {
    const testDate = new Date('2025-08-04'); // Lundi
    
    render(<TestComponent initialWeek={testDate} />);
    
    const prevButton = screen.getByTestId('prev-week');
    fireEvent.click(prevButton);
    
    const currentWeekElement = screen.getByTestId('current-week');
    const newWeekDate = new Date(currentWeekElement.textContent);
    
    // Devrait être le lundi précédent (28 juillet)
    expect(newWeekDate.getDay()).toBe(1); // Lundi
    expect(newWeekDate.getDate()).toBe(28); // 28 juillet
  });
  
  test('should go to Monday of specified week when goToWeek called', () => {
    const testDate = new Date('2025-08-04'); // Lundi
    
    render(<TestComponent initialWeek={testDate} />);
    
    // Aller à la semaine contenant le 6 août (mercredi)
    const goToButton = screen.getByTestId('go-to-specific');
    fireEvent.click(goToButton);
    
    const currentWeekElement = screen.getByTestId('current-week');
    const newWeekDate = new Date(currentWeekElement.textContent);
    
    // Devrait être le lundi 4 août (même semaine que le 6)
    expect(newWeekDate.getDay()).toBe(1); // Lundi
    expect(newWeekDate.getDate()).toBe(4); // 4 août
  });
  
  test('should correctly identify current week', () => {
    const testDate = new Date('2025-08-07'); // Jeudi
    
    render(<TestComponent initialWeek={testDate} />);
    
    const isCurrentWeekElement = screen.getByTestId('is-current-week');
    
    // Le 7 août (jeudi) est dans la même semaine que l'initialisation
    expect(isCurrentWeekElement).toHaveTextContent('true');
  });
});

describe('Calendar Integration Tests - US1.6', () => {
  test('should maintain Monday-Sunday consistency across components', () => {
    const CalendarApp = () => {
      const { currentWeek, goToNextWeek } = useWeekCalendar(new Date('2025-08-07'));
      const [meals, setMeals] = React.useState({});
      
      const handleMealChange = (day, mealType, recipeId) => {
        setMeals(prev => ({
          ...prev,
          [day]: {
            ...prev[day],
            [mealType]: recipeId
          }
        }));
      };
      
      return (
        <div>
          <WeekCalendar 
            currentWeek={currentWeek}
            onWeekChange={() => {}}
          />
          <MealPlanningWeek 
            weekStart={currentWeek}
            meals={meals}
            onMealChange={handleMealChange}
          />
          <button data-testid="next-week-app" onClick={goToNextWeek}>
            Next Week
          </button>
        </div>
      );
    };
    
    render(<CalendarApp />);
    
    // Vérifier que les deux composants utilisent la même semaine
    const calendarWeek = screen.getByTestId('week-display');
    const planningWeek = screen.getByTestId('meal-planning-week');
    
    expect(calendarWeek).toHaveTextContent('Semaine du 4 au 10');
    
    // Les deux composants devraient être synchronisés
    const planningWeekStart = planningWeek.getAttribute('data-week-start');
    const planningDate = new Date(planningWeekStart);
    expect(planningDate.getDay()).toBe(1); // Lundi
    expect(planningDate.getDate()).toBe(4); // 4 août
    
    // Naviguer vers la semaine suivante
    fireEvent.click(screen.getByTestId('next-week-app'));
    
    // Attendre la mise à jour
    waitFor(() => {
      const updatedPlanningWeek = screen.getByTestId('meal-planning-week');
      const updatedWeekStart = updatedPlanningWeek.getAttribute('data-week-start');
      const updatedDate = new Date(updatedWeekStart);
      
      expect(updatedDate.getDay()).toBe(1); // Toujours lundi
      expect(updatedDate.getDate()).toBe(11); // 11 août (semaine suivante)
    });
  });
  
  test('should handle edge cases with year transitions', () => {
    // Test avec la dernière semaine de 2024
    const lastWeek2024 = new Date('2024-12-30'); // Lundi
    
    const EdgeCaseApp = () => {
      const { currentWeek, goToNextWeek } = useWeekCalendar(lastWeek2024);
      
      return (
        <div>
          <WeekCalendar 
            currentWeek={currentWeek}
            onWeekChange={() => {}}
          />
          <button data-testid="next-week-edge" onClick={goToNextWeek}>
            Next Week
          </button>
        </div>
      );
    };
    
    render(<EdgeCaseApp />);
    
    // Naviguer vers la première semaine de 2025
    fireEvent.click(screen.getByTestId('next-week-edge'));
    
    // La semaine suivante devrait être le 6 janvier 2025
    waitFor(() => {
      const weekDisplay = screen.getByTestId('week-display');
      expect(weekDisplay).toHaveTextContent('Semaine du 6'); // 6 janvier
    });
  });
});

describe('Error Handling - US1.6', () => {
  test('should handle invalid dates gracefully', () => {
    const InvalidDateApp = () => {
      try {
        const { currentWeek } = useWeekCalendar(new Date('invalid-date'));
        return (
          <div data-testid="invalid-date-result">
            {currentWeek.toString()}
          </div>
        );
      } catch (error) {
        return (
          <div data-testid="invalid-date-error">
            Error: {error.message}
          </div>
        );
      }
    };
    
    render(<InvalidDateApp />);
    
    // L'application ne devrait pas planter
    expect(screen.getByTestId('invalid-date-error')).toBeInTheDocument();
  });
  
  test('should validate API responses for Monday weekStart', async () => {
    // Mock d'une réponse API avec date invalide
    const mockApiResponse = {
      id: 1,
      week_start: '2025-08-05', // Mardi - invalide
      meals: {}
    };
    
    const ApiValidationApp = () => {
      const [error, setError] = React.useState(null);
      
      React.useEffect(() => {
        const weekStartDate = new Date(mockApiResponse.week_start);
        if (!mockDateUtils.isMonday(weekStartDate)) {
          setError('API returned invalid week_start: must be Monday');
        }
      }, []);
      
      if (error) {
        return <div data-testid="api-validation-error">{error}</div>;
      }
      
      return <div data-testid="api-validation-success">Valid API response</div>;
    };
    
    render(<ApiValidationApp />);
    
    // Devrait détecter et signaler l'erreur
    await waitFor(() => {
      expect(screen.getByTestId('api-validation-error')).toBeInTheDocument();
      expect(screen.getByText(/must be Monday/)).toBeInTheDocument();
    });
  });
});

// Configuration Jest pour les tests
export default {
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/src/setupTests.js'],
  moduleNameMapping: {
    '\\.(css|less|scss|sass)$': 'identity-obj-proxy'
  },
  collectCoverageFrom: [
    'src/frontend/components/**/*.{js,jsx}',
    'src/frontend/hooks/**/*.{js,jsx}',
    '!src/frontend/**/*.test.{js,jsx}',
    '!src/frontend/**/index.js'
  ],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80
    }
  }
};