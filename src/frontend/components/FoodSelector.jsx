import React, { useState, useEffect } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Plus, X, Calculator } from 'lucide-react';
import { FOOD_DATABASE } from '../data/foodDatabase';

// Fonction pour obtenir tous les aliments (base + personnalisés)
const getAllFoods = () => {
  const customFoods = JSON.parse(localStorage.getItem('customFoods') || '[]');
  return [...FOOD_DATABASE, ...customFoods];
};

// Fonction pour obtenir un aliment par son ID (base + personnalisés)
const getFoodById = (id) => {
  return getAllFoods().find(food => food.id === id);
};

// Fonction pour calculer les calories
const calculateCalories = (foodId, quantity, unit) => {
  const food = getFoodById(foodId);
  if (!food || !food.units[unit]) return 0;
  
  return Math.round(food.units[unit].calories * quantity);
};

// Obtenir les unités disponibles pour un aliment
const getFoodUnits = (foodId) => {
  const food = getFoodById(foodId);
  if (!food) return [];
  return Object.keys(food.units);
};

const FoodSelector = ({ foods = [], onChange, mealName = '' }) => {
  const [selectedFood, setSelectedFood] = useState('');
  const [quantity, setQuantity] = useState(1);
  const [unit, setUnit] = useState('');
  const [availableUnits, setAvailableUnits] = useState([]);
  const [totalCalories, setTotalCalories] = useState(0);

  // Calculer le total des calories à chaque changement
  useEffect(() => {
    const total = foods.reduce((sum, food) => {
      // Si l'aliment a déjà des calories calculées, les utiliser
      if (food.calories) {
        return sum + food.calories;
      }
      // Sinon, calculer à partir de foodId
      const foodData = getFoodById(food.foodId);
      if (foodData && foodData.units[food.unit]) {
        return sum + (foodData.units[food.unit].calories * food.quantity);
      }
      return sum;
    }, 0);
    setTotalCalories(Math.round(total));
  }, [foods]);

  // Mettre à jour les unités disponibles quand on sélectionne un aliment
  useEffect(() => {
    if (selectedFood) {
      const units = getFoodUnits(selectedFood);
      setAvailableUnits(units);
      const food = getFoodById(selectedFood);
      if (food && units.length > 0) {
        setUnit(food.defaultUnit || units[0]);
      }
    }
  }, [selectedFood]);

  const handleAddFood = () => {
    if (!selectedFood || !quantity || !unit) {
      alert('Veuillez sélectionner un aliment, une quantité et une unité');
      return;
    }

    const food = getFoodById(selectedFood);
    const calories = calculateCalories(selectedFood, quantity, unit);

    const newFood = {
      foodId: selectedFood,
      name: food.name,
      quantity: parseFloat(quantity),
      unit: unit,
      calories: calories
    };

    onChange([...foods, newFood]);
    
    // Réinitialiser
    setSelectedFood('');
    setQuantity(1);
    setUnit('');
  };

  const handleRemoveFood = (index) => {
    const newFoods = [...foods];
    newFoods.splice(index, 1);
    onChange(newFoods);
  };

  // Grouper les aliments par catégorie
  const allFoods = getAllFoods();
  const foodsByCategory = allFoods.reduce((acc, food) => {
    if (!acc[food.category]) acc[food.category] = [];
    acc[food.category].push(food);
    return acc;
  }, {});

  const categoryLabels = {
    'proteine': '🥚 Protéines',
    'glucide': '🌾 Glucides',
    'lipide': '🥜 Lipides',
    'fruit': '🍎 Fruits',
    'legume': '🥬 Légumes',
    'boisson': '☕ Boissons',
    'supplement': '💊 Suppléments',
    'autre': '🍫 Autres',
    'custom': '⭐ Personnalisés'
  };

  return (
    <div className="space-y-4">
      {/* Total des calories */}
      <div className="bg-blue-50 p-3 rounded-lg flex items-center justify-between">
        <span className="font-semibold text-blue-900">
          {mealName && `${mealName} - `}Total calories:
        </span>
        <span className="text-2xl font-bold text-blue-600 flex items-center">
          <Calculator className="w-5 h-5 mr-2" />
          {totalCalories} kcal
        </span>
      </div>

      {/* Liste des aliments actuels */}
      <div className="space-y-2">
        {foods.map((food, index) => {
          const foodData = getFoodById(food.foodId);
          return (
            <div key={index} className="flex items-center justify-between bg-white p-2 rounded border">
              <div className="flex-1">
                <span className="font-medium">{food.name}</span>
                <span className="text-gray-600 ml-2">
                  {food.quantity} {food.unit}
                </span>
              </div>
              <div className="flex items-center space-x-2">
                <span className="text-sm text-gray-500">
                  {food.calories} kcal
                </span>
                <Button
                  onClick={() => handleRemoveFood(index)}
                  size="sm"
                  variant="destructive"
                >
                  <X className="w-3 h-3" />
                </Button>
              </div>
            </div>
          );
        })}
        
        {foods.length === 0 && (
          <p className="text-gray-500 italic text-center py-2">
            Aucun aliment sélectionné
          </p>
        )}
      </div>

      {/* Formulaire d'ajout */}
      <div className="border-t pt-3">
        <p className="text-sm font-medium mb-2">Ajouter un aliment :</p>
        <div className="space-y-3">
          {/* Sélecteur d'aliment par catégorie */}
          <select
            value={selectedFood}
            onChange={(e) => setSelectedFood(e.target.value)}
            className="w-full px-3 py-2 border rounded-md"
          >
            <option value="">-- Choisir un aliment --</option>
            {Object.entries(foodsByCategory).map(([category, foods]) => (
              <optgroup key={category} label={categoryLabels[category] || category}>
                {foods.map(food => (
                  <option key={food.id} value={food.id}>
                    {food.name}
                  </option>
                ))}
              </optgroup>
            ))}
          </select>

          {/* Quantité et unité */}
          {selectedFood && (
            <div className="flex gap-2">
              <Input
                type="number"
                placeholder="Quantité"
                value={quantity}
                onChange={(e) => setQuantity(e.target.value)}
                className="w-24"
                min="0.1"
                step="0.1"
              />
              <select
                value={unit}
                onChange={(e) => setUnit(e.target.value)}
                className="px-3 py-2 border rounded-md"
              >
                {availableUnits.map(u => (
                  <option key={u} value={u}>{u}</option>
                ))}
              </select>
              
              {/* Aperçu des calories */}
              {selectedFood && quantity && unit && (
                <div className="flex items-center px-3 text-sm text-gray-600">
                  = {calculateCalories(selectedFood, quantity, unit)} kcal
                </div>
              )}
              
              <Button
                onClick={handleAddFood}
                className="bg-green-600 hover:bg-green-700"
                size="sm"
              >
                <Plus className="w-4 h-4" />
              </Button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default FoodSelector;