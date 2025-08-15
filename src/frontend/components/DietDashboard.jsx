import React, { useState, useEffect } from 'react';
import { Check, Clock, Flame, Calendar, ChefHat, AlertCircle } from 'lucide-react';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

export default function DietDashboard() {
  const [todayDiet, setTodayDiet] = useState(null);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchTodayDiet();
    fetchStats();
    
    // Écouter les changements depuis Planning
    const handleMealStatusChange = (event) => {
      console.log('Dashboard: Événement reçu depuis Planning', event.detail);
      fetchTodayDiet();
      fetchStats();
    }
    window.addEventListener('mealStatusChanged', handleMealStatusChange);
    
    // Écouter le focus de la fenêtre pour rafraîchir
    const handleFocus = () => {
      console.log('Dashboard: Fenêtre en focus, rafraîchissement...');
      fetchTodayDiet();
      fetchStats();
    }
    window.addEventListener('focus', handleFocus);
    
    // Rafraîchir toutes les 5 minutes (300 secondes)
    const interval = setInterval(() => {
      fetchTodayDiet();
      fetchStats();
    }, 5 * 60 * 1000);
    
    return () => {
      clearInterval(interval);
      window.removeEventListener('mealStatusChanged', handleMealStatusChange);
      window.removeEventListener('focus', handleFocus);
    };
  }, []);

  const fetchTodayDiet = async () => {
    try {
      // Ajouter /api seulement si pas déjà présent dans l'URL
      const apiUrl = API_URL.includes('/api') ? API_URL : `${API_URL}/api`;
      const response = await fetch(`${apiUrl}/diet/today`);
      const data = await response.json();
      if (data.success) {
        setTodayDiet(data);
      }
    } catch (err) {
      setError('Erreur lors du chargement de la diète');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      // Ajouter /api seulement si pas déjà présent dans l'URL
      const apiUrl = API_URL.includes('/api') ? API_URL : `${API_URL}/api`;
      const response = await fetch(`${apiUrl}/diet/stats`);
      const data = await response.json();
      if (data.success) {
        setStats(data);
      }
    } catch (err) {
      console.error('Erreur stats:', err);
    }
  };

  const toggleMealCompleted = async (mealId, currentStatus) => {
    try {
      console.log('Dashboard: Toggle meal', { mealId, currentStatus, newStatus: !currentStatus });
      // Ajouter /api seulement si pas déjà présent dans l'URL
      const apiUrl = API_URL.includes('/api') ? API_URL : `${API_URL}/api`;
      const response = await fetch(`${apiUrl}/diet/validate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          meal_id: mealId, 
          completed: !currentStatus 
        })
      });
      const data = await response.json();
      console.log('Dashboard: Réponse API', data);
      if (data.success) {
        await fetchTodayDiet();
        await fetchStats();
        // Déclencher un événement pour synchroniser avec Planning
        console.log('Dashboard: Émission événement mealStatusChanged', { mealId, completed: !currentStatus });
        window.dispatchEvent(new CustomEvent('mealStatusChanged', { 
          detail: { mealId, completed: !currentStatus } 
        }));
      }
    } catch (err) {
      console.error('Erreur validation:', err);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
        <AlertCircle className="h-5 w-5 inline mr-2" />
        {error}
      </div>
    );
  }

  const currentMeal = todayDiet?.current_meal;
  const nextMeal = todayDiet?.next_meal;

  // Calculer les calories consommées
  const consumedCalories = todayDiet?.today_meals?.reduce((total, meal) => {
    if (meal.completed && meal.foods) {
      const mealCalories = meal.foods.reduce((sum, food) => sum + (food.calories || 0), 0);
      return total + mealCalories;
    }
    return total;
  }, 0) || 0;

  const totalPlannedCalories = todayDiet?.today_meals?.reduce((total, meal) => {
    if (meal.foods) {
      const mealCalories = meal.foods.reduce((sum, food) => sum + (food.calories || 0), 0);
      return total + mealCalories;
    }
    return total;
  }, 0) || 0;

  return (
    <div className="space-y-6">
      {/* Barre de progression des calories */}
      <div className="bg-white rounded-lg p-4 shadow-sm border">
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm font-medium text-gray-700">Calories consommées</span>
          <span className="text-sm font-bold">
            {consumedCalories} / {totalPlannedCalories} kcal
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-3">
          <div 
            className="bg-green-600 h-3 rounded-full transition-all duration-300"
            style={{ width: `${Math.min(100, (consumedCalories / totalPlannedCalories) * 100)}%` }}
          />
        </div>
      </div>

      {/* Zone 1: MAINTENANT - Le repas actuel */}
      <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-xl p-6 border-2 border-green-300">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-bold text-green-900 flex items-center">
            <Clock className="mr-2 h-6 w-6" />
            Maintenant
          </h2>
          {currentMeal && (
            <span className="bg-green-200 text-green-800 px-3 py-1 rounded-full text-sm font-medium">
              {currentMeal.time_slot}
            </span>
          )}
        </div>

        {currentMeal ? (
          <div className="bg-white rounded-lg p-4 shadow-sm">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-lg font-semibold text-gray-900">
                {currentMeal.meal_name}
              </h3>
              <button
                onClick={() => toggleMealCompleted(currentMeal.id, currentMeal.completed)}
                className={`p-3 rounded-lg transition-all ${
                  currentMeal.completed
                    ? 'bg-green-600 text-white hover:bg-green-700'
                    : 'bg-gray-200 hover:bg-green-500 hover:text-white'
                }`}
                title={currentMeal.completed ? "Marquer comme non mangé" : "Marquer comme mangé"}
              >
                <Check className="h-6 w-6" />
              </button>
            </div>

            <div className="space-y-2">
              {currentMeal.foods.map((food, index) => (
                <div key={index} className="flex items-center text-gray-700">
                  <span className="w-2 h-2 bg-green-400 rounded-full mr-3"></span>
                  <span className="font-medium">{food.name}</span>
                  <span className="ml-auto text-gray-500">
                    {food.quantity} {food.unit}
                  </span>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div className="bg-white rounded-lg p-4 text-center text-gray-500">
            Aucun repas prévu pour le moment
          </div>
        )}

        {/* Prochain repas */}
        {nextMeal && !currentMeal?.completed && (
          <div className="mt-4 p-3 bg-yellow-50 rounded-lg border border-yellow-200">
            <p className="text-sm text-yellow-800">
              <strong>Prochain repas :</strong> {nextMeal.meal_name} à {nextMeal.time_slot}
            </p>
          </div>
        )}
      </div>

      {/* Zone 2: STREAK & STATISTIQUES */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white rounded-xl p-6 border border-gray-200 shadow-sm">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-500 text-sm">Série actuelle</p>
              <p className="text-3xl font-bold text-orange-600 flex items-center">
                <Flame className="mr-2 h-8 w-8" />
                {stats?.streak?.current_streak || 0}
              </p>
              <p className="text-xs text-gray-500 mt-1">jours consécutifs</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl p-6 border border-gray-200 shadow-sm">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-500 text-sm">Aujourd'hui</p>
              <p className="text-3xl font-bold text-blue-600">
                {todayDiet?.stats?.completed || 0}/{todayDiet?.stats?.total || 5}
              </p>
              <p className="text-xs text-gray-500 mt-1">repas complétés</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl p-6 border border-gray-200 shadow-sm">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-500 text-sm">Cette semaine</p>
              <p className="text-3xl font-bold text-purple-600">
                {stats?.week_stats?.percentage || 0}%
              </p>
              <p className="text-xs text-gray-500 mt-1">de respect</p>
            </div>
          </div>
        </div>
      </div>

      {/* Zone 3: AUJOURD'HUI - Tous les repas */}
      <div className="bg-white rounded-xl p-6 border border-gray-200">
        <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
          <Calendar className="mr-2 h-5 w-5" />
          Programme du jour
        </h2>

        <div className="space-y-3">
          {todayDiet?.meals?.sort((a, b) => (a.order_index || 0) - (b.order_index || 0)).map((meal) => (
            <div
              key={meal.id}
              className={`flex items-center justify-between p-4 rounded-lg border ${
                meal.completed
                  ? 'bg-green-50 border-green-200'
                  : 'bg-gray-50 border-gray-200'
              }`}
            >
              <div className="flex-1">
                <div className="flex items-center">
                  <button
                    onClick={() => toggleMealCompleted(meal.id, meal.completed)}
                    className={`mr-3 p-2 rounded-full transition-all ${
                      meal.completed
                        ? 'bg-green-600 text-white'
                        : 'bg-gray-300 hover:bg-green-500 hover:text-white'
                    }`}
                  >
                    <Check className="h-4 w-4" />
                  </button>
                  <div className="flex-1">
                    <h4 className="font-semibold text-gray-900">{meal.meal_name}</h4>
                    <p className="text-sm text-gray-500">{meal.time_slot}</p>
                    {/* Afficher les aliments et calories */}
                    <div className="mt-1 text-xs text-gray-600">
                      {meal.foods && meal.foods.length > 0 && (
                        <span>
                          {meal.foods.reduce((sum, food) => sum + (food.calories || 0), 0)} kcal
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
              <div className="text-right">
                <p className="text-sm font-medium text-gray-700">
                  {meal.foods.length} aliments
                </p>
                {meal.completed && meal.completed_at && (
                  <p className="text-xs text-green-600">
                    ✓ {new Date(meal.completed_at).toLocaleTimeString('fr-FR', {
                      hour: '2-digit',
                      minute: '2-digit'
                    })}
                  </p>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* Barre de progression */}
        <div className="mt-6">
          <div className="flex justify-between text-sm text-gray-600 mb-2">
            <span>Progression du jour</span>
            <span>{todayDiet?.stats?.percentage || 0}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div
              className="bg-gradient-to-r from-green-400 to-green-600 h-3 rounded-full transition-all"
              style={{ width: `${todayDiet?.stats?.percentage || 0}%` }}
            />
          </div>
        </div>
      </div>

      {/* Zone 4: Rappels et conseils */}
      <div className="bg-blue-50 rounded-xl p-6 border border-blue-200">
        <h3 className="text-lg font-semibold text-blue-900 mb-3 flex items-center">
          <ChefHat className="mr-2 h-5 w-5" />
          Rappels du jour
        </h3>
        <ul className="space-y-2 text-blue-700">
          <li className="flex items-start">
            <span className="mr-2">💧</span>
            <span>Boire minimum 3,5L d'eau par jour</span>
          </li>
          <li className="flex items-start">
            <span className="mr-2">🧂</span>
            <span>1g de sel par repas solide (épices autorisées)</span>
          </li>
          <li className="flex items-start">
            <span className="mr-2">💊</span>
            <span>Multi-vitamines : 3000mg CLA matin et midi</span>
          </li>
        </ul>
      </div>
    </div>
  );
}