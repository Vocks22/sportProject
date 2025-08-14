import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Trash2, Edit, Plus, Save, X, RefreshCw, ChefHat, Clock, Utensils, PlusCircle, Upload } from 'lucide-react';
import TimeRangePicker from './ui/TimeRangePicker';
import FoodSelector from './FoodSelector';

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
  const [showCustomFood, setShowCustomFood] = useState(false);
  const [customFood, setCustomFood] = useState({ name: '', defaultUnit: 'g', caloriesPerUnit: 0 });
  const [syncing, setSyncing] = useState(false);

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

  const handleFoodsChange = (mealId, newFoods) => {
    const meal = meals.find(m => m.id === mealId);
    if (meal) {
      const formattedFoods = newFoods.map(f => ({
        name: f.name,
        quantity: f.quantity.toString(),
        unit: f.unit,
        calories: f.calories
      }));
      const updatedMeal = {
        ...meal,
        foods: formattedFoods
      };
      handleUpdateMeal(updatedMeal);
    }
  };

  const handleAddCustomFood = () => {
    if (!customFood.name || !customFood.defaultUnit || !customFood.caloriesPerUnit) {
      alert('Veuillez remplir tous les champs');
      return;
    }
    
    // Ici on pourrait sauvegarder l'aliment personnalisé dans le localStorage
    // ou l'envoyer au backend
    const customFoods = JSON.parse(localStorage.getItem('customFoods') || '[]');
    const newCustomFood = {
      id: `custom_${Date.now()}`,
      name: customFood.name,
      category: 'custom',
      defaultUnit: customFood.defaultUnit,
      units: {
        [customFood.defaultUnit]: { 
          calories: parseFloat(customFood.caloriesPerUnit),
          protein: 0,
          carbs: 0,
          fat: 0
        }
      }
    };
    customFoods.push(newCustomFood);
    localStorage.setItem('customFoods', JSON.stringify(customFoods));
    
    alert(`Aliment "${customFood.name}" ajouté avec succès !`);
    setCustomFood({ name: '', defaultUnit: 'g', caloriesPerUnit: 0 });
    setShowCustomFood(false);
  };

  const handleSyncToProduction = async () => {
    if (!confirm('⚠️ Êtes-vous sûr de vouloir synchroniser vos repas vers la production ?\n\nCela remplacera TOUS les repas en production par ceux de votre environnement actuel.')) {
      return;
    }

    setSyncing(true);
    try {
      const response = await fetch(`${API_URL}/diet/admin/meals/sync-to-production`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          secret_key: 'sync2024-diet-tracker',
          production_url: 'https://diettracker-backend.onrender.com'
        })
      });

      const data = await response.json();
      
      if (data.success) {
        alert(`✅ Synchronisation réussie !\n\n${data.details.updated} repas mis à jour\n${data.details.imported} nouveaux repas créés\n\nVérifiez sur https://diettracker.netlify.app`);
      } else {
        alert(`❌ Erreur de synchronisation: ${data.error}`);
      }
    } catch (error) {
      console.error('Erreur sync:', error);
      alert(`❌ Erreur de connexion: ${error.message}`);
    } finally {
      setSyncing(false);
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
                onClick={handleSyncToProduction}
                className="bg-purple-600 hover:bg-purple-700"
                disabled={meals.length === 0 || syncing}
              >
                <Upload className="w-4 h-4 mr-2" />
                {syncing ? 'Synchronisation...' : 'Synchroniser vers Production'}
              </Button>
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
                      
                      {/* Section aliments avec sélecteur et calcul des calories */}
                      {expandedMeal === meal.id && (
                        <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                          <h5 className="font-semibold mb-3">🍽️ Gestion des aliments</h5>
                          
                          {/* Utilisation du nouveau sélecteur d'aliments */}
                          <FoodSelector
                            foods={meal.foods?.map(f => ({
                              foodId: f.foodId || `legacy_${f.name}`,
                              name: f.name,
                              quantity: parseFloat(f.quantity) || 1,
                              unit: f.unit || 'g',
                              calories: f.calories || 0
                            })) || []}
                            onChange={(newFoods) => handleFoodsChange(meal.id, newFoods)}
                            mealName={meal.meal_name}
                          />
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ))
            )}
          </div>

          {/* Section pour ajouter des aliments personnalisés */}
          <div className="mt-6 p-4 bg-purple-50 border border-purple-200 rounded-lg">
            <div className="flex justify-between items-center mb-3">
              <h4 className="font-bold text-purple-800">🍴 Aliments personnalisés</h4>
              <Button
                onClick={() => setShowCustomFood(!showCustomFood)}
                className="bg-purple-600 hover:bg-purple-700"
                size="sm"
              >
                <PlusCircle className="w-4 h-4 mr-2" />
                Ajouter un aliment
              </Button>
            </div>
            
            {showCustomFood && (
              <div className="mt-3 p-3 bg-white rounded border">
                <p className="text-sm font-medium mb-2">Nouvel aliment personnalisé :</p>
                <div className="grid grid-cols-3 gap-2 mb-2">
                  <Input
                    placeholder="Nom de l'aliment"
                    value={customFood.name}
                    onChange={(e) => setCustomFood({...customFood, name: e.target.value})}
                  />
                  <Input
                    placeholder="Unité (g, ml, unité...)"
                    value={customFood.defaultUnit}
                    onChange={(e) => setCustomFood({...customFood, defaultUnit: e.target.value})}
                  />
                  <Input
                    type="number"
                    placeholder="Calories par unité"
                    value={customFood.caloriesPerUnit}
                    onChange={(e) => setCustomFood({...customFood, caloriesPerUnit: e.target.value})}
                  />
                </div>
                <div className="flex gap-2">
                  <Button
                    onClick={handleAddCustomFood}
                    className="bg-green-600 hover:bg-green-700"
                    size="sm"
                  >
                    <Save className="w-4 h-4 mr-2" />
                    Enregistrer
                  </Button>
                  <Button
                    onClick={() => {
                      setShowCustomFood(false);
                      setCustomFood({ name: '', defaultUnit: 'g', caloriesPerUnit: 0 });
                    }}
                    variant="outline"
                    size="sm"
                  >
                    <X className="w-4 h-4 mr-2" />
                    Annuler
                  </Button>
                </div>
              </div>
            )}
            
            <p className="text-xs text-purple-600 mt-2">
              💡 Vous pouvez ajouter vos propres aliments avec leurs calories pour un suivi personnalisé
            </p>
          </div>

          {/* Instructions */}
          <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
            <h4 className="font-bold text-yellow-800 mb-2">📝 Instructions :</h4>
            <ul className="text-sm text-yellow-700 space-y-1">
              <li>• Sélectionnez les aliments dans la liste prédéfinie</li>
              <li>• Les calories sont calculées automatiquement</li>
              <li>• Vous pouvez ajouter des aliments personnalisés</li>
              <li>• Les modifications sont appliquées immédiatement</li>
            </ul>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default DietAdmin;