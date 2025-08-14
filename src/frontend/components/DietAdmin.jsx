import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Trash2, Edit, Plus, Save, X, RefreshCw, ChefHat, Clock, Utensils } from 'lucide-react';
import TimeRangePicker from './ui/TimeRangePicker';

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';
const API_URL = BASE_URL.includes('/api') ? BASE_URL : `${BASE_URL}/api`;

const DietAdmin = () => {
  const [meals, setMeals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editingMeal, setEditingMeal] = useState(null);
  const [newMeal, setNewMeal] = useState({
    meal_type: '',
    meal_name: '',
    time_slot: '',
    order_index: 1,
    foods: []
  });
  const [showNewForm, setShowNewForm] = useState(false);
  const [expandedMeal, setExpandedMeal] = useState(null);
  const [newFood, setNewFood] = useState({ name: '', quantity: '', unit: '' });

  useEffect(() => {
    fetchMeals();
  }, []);

  const fetchMeals = async () => {
    try {
      const response = await fetch(`${API_URL}/diet/admin/meals`);
      const data = await response.json();
      if (data.success) {
        // Trier par order_index pour afficher dans le bon ordre
        const sortedMeals = data.meals.sort((a, b) => a.order_index - b.order_index);
        setMeals(sortedMeals);
      }
    } catch (error) {
      console.error('Erreur chargement repas:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleInitDefault = async () => {
    if (!confirm('Initialiser les 5 repas par défaut ? (Les repas existants doivent être supprimés d\'abord)')) {
      return;
    }

    try {
      const response = await fetch(`${API_URL}/diet/admin/meals/init`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      const data = await response.json();
      
      if (data.success) {
        alert('5 repas par défaut créés avec succès !');
        fetchMeals();
      } else {
        alert(`Erreur: ${data.error}`);
      }
    } catch (error) {
      console.error('Erreur:', error);
      alert('Erreur lors de l\'initialisation');
    }
  };

  const handleInitFoods = async () => {
    if (!confirm('Initialiser les aliments par défaut pour tous les repas ? Cela remplacera les aliments existants.')) {
      return;
    }

    try {
      const response = await fetch(`${API_URL}/diet/admin/meals/init-foods`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      const data = await response.json();
      
      if (data.success) {
        alert(`✅ ${data.message}\n\nDétails:\n${data.updated_meals.map(m => `- ${m.name}: ${m.foods_count} aliments`).join('\n')}`);
        fetchMeals();
      } else {
        alert(`❌ Erreur: ${data.error}`);
      }
    } catch (error) {
      console.error('Erreur:', error);
      alert('❌ Erreur lors de l\'initialisation des aliments');
    }
  };

  const handleClearAll = async () => {
    if (!confirm('⚠️ ATTENTION: Supprimer TOUS les repas ? Cette action est irréversible !')) {
      return;
    }

    try {
      const response = await fetch(`${API_URL}/diet/admin/meals/clear?confirm=yes`, {
        method: 'DELETE'
      });
      const data = await response.json();
      
      if (data.success) {
        alert(`${data.count} repas supprimés`);
        setMeals([]);
      }
    } catch (error) {
      console.error('Erreur:', error);
    }
  };

  const handleCreateMeal = async () => {
    try {
      const response = await fetch(`${API_URL}/diet/admin/meals`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newMeal)
      });
      const data = await response.json();
      
      if (data.success) {
        alert('Repas créé avec succès !');
        setShowNewForm(false);
        setNewMeal({ meal_type: '', meal_name: '', time_slot: '', order_index: 1, foods: [] });
        fetchMeals();
      } else {
        alert(`Erreur: ${data.error}`);
      }
    } catch (error) {
      console.error('Erreur:', error);
    }
  };

  const handleUpdateMeal = async (meal) => {
    try {
      const response = await fetch(`${API_URL}/diet/admin/meals/${meal.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(meal)
      });
      const data = await response.json();
      
      if (data.success) {
        alert('Repas modifié avec succès !');
        setEditingMeal(null);
        fetchMeals();
      }
    } catch (error) {
      console.error('Erreur:', error);
    }
  };

  const handleDeleteMeal = async (id) => {
    if (!confirm('Supprimer ce repas ?')) return;

    try {
      const response = await fetch(`${API_URL}/diet/admin/meals/${id}`, {
        method: 'DELETE'
      });
      const data = await response.json();
      
      if (data.success) {
        alert('Repas supprimé');
        fetchMeals();
      }
    } catch (error) {
      console.error('Erreur:', error);
    }
  };

  const handleAddFood = (mealId) => {
    if (!newFood.name || !newFood.quantity || !newFood.unit) {
      alert('Veuillez remplir tous les champs');
      return;
    }

    const meal = meals.find(m => m.id === mealId);
    if (meal) {
      const updatedMeal = {
        ...meal,
        foods: [...(meal.foods || []), { ...newFood }]
      };
      handleUpdateMeal(updatedMeal);
      setNewFood({ name: '', quantity: '', unit: '' });
    }
  };

  const handleRemoveFood = (mealId, foodIndex) => {
    const meal = meals.find(m => m.id === mealId);
    if (meal) {
      const updatedFoods = [...(meal.foods || [])];
      updatedFoods.splice(foodIndex, 1);
      const updatedMeal = { ...meal, foods: updatedFoods };
      handleUpdateMeal(updatedMeal);
    }
  };

  if (loading) {
    return <div className="p-8">Chargement...</div>;
  }

  return (
    <div className="p-4 max-w-6xl mx-auto">
      <Card>
        <CardHeader>
          <CardTitle className="flex justify-between items-center">
            <span>🛠️ Administration des Repas</span>
            <div className="space-x-2">
              <Button 
                onClick={handleInitDefault}
                className="bg-green-600 hover:bg-green-700"
                disabled={meals.length > 0}
              >
                <RefreshCw className="w-4 h-4 mr-2" />
                Initialiser 5 repas
              </Button>
              <Button 
                onClick={handleInitFoods}
                className="bg-orange-600 hover:bg-orange-700"
                disabled={meals.length === 0}
              >
                <Utensils className="w-4 h-4 mr-2" />
                Initialiser aliments
              </Button>
              <Button 
                onClick={handleClearAll}
                variant="destructive"
                disabled={meals.length === 0}
              >
                <Trash2 className="w-4 h-4 mr-2" />
                Tout supprimer
              </Button>
              <Button 
                onClick={() => setShowNewForm(true)}
                className="bg-blue-600 hover:bg-blue-700"
              >
                <Plus className="w-4 h-4 mr-2" />
                Nouveau repas
              </Button>
            </div>
          </CardTitle>
        </CardHeader>
        <CardContent>
          {/* Formulaire nouveau repas */}
          {showNewForm && (
            <div className="mb-6 p-4 border rounded-lg bg-blue-50">
              <h3 className="font-bold mb-3">Nouveau repas</h3>
              <div className="space-y-3">
                <div className="grid grid-cols-3 gap-2">
                  <Input
                    placeholder="Type (ex: repas1)"
                    value={newMeal.meal_type}
                    onChange={(e) => setNewMeal({...newMeal, meal_type: e.target.value})}
                  />
                  <Input
                    placeholder="Nom du repas"
                    value={newMeal.meal_name}
                    onChange={(e) => setNewMeal({...newMeal, meal_name: e.target.value})}
                  />
                  <Input
                    type="number"
                    placeholder="Ordre"
                    value={newMeal.order_index}
                    onChange={(e) => setNewMeal({...newMeal, order_index: parseInt(e.target.value)})}
                  />
                </div>
                <div className="flex items-center gap-2">
                  <Clock className="w-4 h-4 text-gray-500" />
                  <span className="text-sm text-gray-600">Horaire:</span>
                  <TimeRangePicker
                    value={newMeal.time_slot}
                    onChange={(value) => setNewMeal({...newMeal, time_slot: value})}
                  />
                </div>
              </div>
              <div className="mt-2 space-x-2">
                <Button onClick={handleCreateMeal} className="bg-green-600 hover:bg-green-700">
                  <Save className="w-4 h-4 mr-2" />
                  Créer
                </Button>
                <Button onClick={() => setShowNewForm(false)} variant="outline">
                  <X className="w-4 h-4 mr-2" />
                  Annuler
                </Button>
              </div>
            </div>
          )}

          {/* Liste des repas */}
          <div className="space-y-3">
            {meals.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                Aucun repas configuré. Cliquez sur "Initialiser 5 repas" pour commencer.
              </div>
            ) : (
              meals.map(meal => (
                <div key={meal.id} className="border rounded-lg p-4 hover:bg-gray-50">
                  {editingMeal?.id === meal.id ? (
                    // Mode édition
                    <div className="space-y-3">
                      <div className="grid grid-cols-4 gap-2">
                        <Input
                          value={editingMeal.meal_type}
                          onChange={(e) => setEditingMeal({...editingMeal, meal_type: e.target.value})}
                        />
                        <Input
                          value={editingMeal.meal_name}
                          onChange={(e) => setEditingMeal({...editingMeal, meal_name: e.target.value})}
                        />
                        <Input
                          type="number"
                          value={editingMeal.order_index}
                          onChange={(e) => setEditingMeal({...editingMeal, order_index: parseInt(e.target.value)})}
                        />
                        <div className="flex space-x-1">
                          <Button 
                            onClick={() => handleUpdateMeal(editingMeal)}
                            className="bg-green-600 hover:bg-green-700"
                            size="sm"
                          >
                            <Save className="w-4 h-4" />
                          </Button>
                          <Button 
                            onClick={() => setEditingMeal(null)}
                            variant="outline"
                            size="sm"
                          >
                            <X className="w-4 h-4" />
                          </Button>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Clock className="w-4 h-4 text-gray-500" />
                        <TimeRangePicker
                          value={editingMeal.time_slot}
                          onChange={(value) => setEditingMeal({...editingMeal, time_slot: value})}
                        />
                      </div>
                    </div>
                  ) : (
                    // Mode affichage
                    <div>
                      <div className="flex justify-between items-center">
                        <div className="flex-1 grid grid-cols-4 gap-4">
                          <div>
                            <span className="text-xs text-gray-500">Type:</span>
                            <p className="font-mono">{meal.meal_type}</p>
                          </div>
                          <div>
                            <span className="text-xs text-gray-500">Nom:</span>
                            <p className="font-semibold">{meal.meal_name}</p>
                          </div>
                          <div>
                            <span className="text-xs text-gray-500">Horaire:</span>
                            <p>{meal.time_slot}</p>
                          </div>
                          <div>
                            <span className="text-xs text-gray-500">Ordre:</span>
                            <p className="text-center">{meal.order_index}</p>
                          </div>
                        </div>
                        <div className="flex space-x-2">
                          <Button 
                            onClick={() => setExpandedMeal(expandedMeal === meal.id ? null : meal.id)}
                            variant="outline"
                            size="sm"
                          >
                            <ChefHat className="w-4 h-4" />
                          </Button>
                          <Button 
                            onClick={() => setEditingMeal(meal)}
                            variant="outline"
                            size="sm"
                          >
                            <Edit className="w-4 h-4" />
                          </Button>
                          <Button 
                            onClick={() => handleDeleteMeal(meal.id)}
                            variant="destructive"
                            size="sm"
                          >
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </div>
                      </div>
                      
                      {/* Section aliments */}
                      {expandedMeal === meal.id && (
                        <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                          <h5 className="font-semibold mb-3">🍽️ Aliments du repas</h5>
                          
                          {/* Liste des aliments existants */}
                          <div className="space-y-2 mb-4">
                            {meal.foods && meal.foods.length > 0 ? (
                              meal.foods.map((food, index) => (
                                <div key={index} className="flex items-center justify-between bg-white p-2 rounded border">
                                  <span className="font-medium">{food.name}</span>
                                  <div className="flex items-center space-x-2">
                                    <span className="text-gray-600">{food.quantity} {food.unit}</span>
                                    <Button
                                      onClick={() => handleRemoveFood(meal.id, index)}
                                      size="sm"
                                      variant="destructive"
                                    >
                                      <X className="w-3 h-3" />
                                    </Button>
                                  </div>
                                </div>
                              ))
                            ) : (
                              <p className="text-gray-500 italic">Aucun aliment défini</p>
                            )}
                          </div>
                          
                          {/* Formulaire ajout aliment */}
                          <div className="border-t pt-3">
                            <p className="text-sm font-medium mb-2">Ajouter un aliment :</p>
                            <div className="flex gap-2">
                              <Input
                                placeholder="Nom de l'aliment"
                                value={newFood.name}
                                onChange={(e) => setNewFood({...newFood, name: e.target.value})}
                                className="flex-1"
                              />
                              <Input
                                placeholder="Quantité"
                                value={newFood.quantity}
                                onChange={(e) => setNewFood({...newFood, quantity: e.target.value})}
                                className="w-24"
                              />
                              <Input
                                placeholder="Unité"
                                value={newFood.unit}
                                onChange={(e) => setNewFood({...newFood, unit: e.target.value})}
                                className="w-24"
                              />
                              <Button
                                onClick={() => handleAddFood(meal.id)}
                                className="bg-green-600 hover:bg-green-700"
                                size="sm"
                              >
                                <Plus className="w-4 h-4" />
                              </Button>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ))
            )}
          </div>

          {/* Instructions */}
          <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
            <h4 className="font-bold text-yellow-800 mb-2">📝 Instructions :</h4>
            <ul className="text-sm text-yellow-700 space-y-1">
              <li>• Les types de repas doivent être uniques (repas1, collation1, etc.)</li>
              <li>• L'ordre détermine l'affichage dans le suivi quotidien</li>
              <li>• Les modifications sont appliquées immédiatement</li>
              <li>• Utilisez "Initialiser 5 repas" pour une configuration rapide</li>
            </ul>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default DietAdmin;