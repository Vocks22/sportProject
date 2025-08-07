import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import {
  Scale,
  Activity,
  Flame,
  Timer,
  TrendingUp,
  TrendingDown,
  Plus,
  Calendar,
  Target,
  Dumbbell,
  Heart,
  Footprints,
  Moon,
  Droplets,
  Apple,
  Save,
  X,
  ChevronDown,
  ChevronUp
} from 'lucide-react';

const MeasurementsPage = () => {
  const userId = 1; // À remplacer par l'auth réelle plus tard
  const [measurements, setMeasurements] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);
  const [expandedSections, setExpandedSections] = useState({
    weight: true,
    activity: true,
    nutrition: true,
    health: true
  });

  // État pour le nouveau formulaire de mesure
  const [newMeasurement, setNewMeasurement] = useState({
    date: new Date().toISOString().split('T')[0],
    // Poids et composition
    weight: '',
    body_fat: '',
    muscle_mass: '',
    water_percentage: '',
    // Activité
    calories_burned: '',
    steps: '',
    exercise_hours: '',
    exercise_type: '',
    // Nutrition
    calories_consumed: '',
    protein: '',
    carbs: '',
    fat: '',
    water_intake: '',
    // Santé
    sleep_hours: '',
    heart_rate_rest: '',
    blood_pressure_sys: '',
    blood_pressure_dia: '',
    notes: ''
  });

  // Catégories de mesures
  const measurementCategories = {
    weight: {
      title: 'Poids & Composition',
      icon: Scale,
      color: 'blue',
      fields: [
        { key: 'weight', label: 'Poids (kg)', type: 'number', step: '0.1', required: true },
        { key: 'body_fat', label: 'Masse grasse (%)', type: 'number', step: '0.1' },
        { key: 'muscle_mass', label: 'Masse musculaire (%)', type: 'number', step: '0.1' },
        { key: 'water_percentage', label: 'Eau corporelle (%)', type: 'number', step: '0.1' }
      ]
    },
    activity: {
      title: 'Activité Physique',
      icon: Activity,
      color: 'green',
      fields: [
        { key: 'calories_burned', label: 'Calories dépensées', type: 'number' },
        { key: 'steps', label: 'Nombre de pas', type: 'number' },
        { key: 'exercise_hours', label: 'Heures d\'exercice', type: 'number', step: '0.5' },
        { key: 'exercise_type', label: 'Type d\'exercice', type: 'text', placeholder: 'Ex: Musculation, Course, Vélo...' }
      ]
    },
    nutrition: {
      title: 'Nutrition',
      icon: Apple,
      color: 'orange',
      fields: [
        { key: 'calories_consumed', label: 'Calories consommées', type: 'number' },
        { key: 'protein', label: 'Protéines (g)', type: 'number' },
        { key: 'carbs', label: 'Glucides (g)', type: 'number' },
        { key: 'fat', label: 'Lipides (g)', type: 'number' },
        { key: 'water_intake', label: 'Eau bue (ml)', type: 'number', step: '250' }
      ]
    },
    health: {
      title: 'Santé & Bien-être',
      icon: Heart,
      color: 'red',
      fields: [
        { key: 'sleep_hours', label: 'Heures de sommeil', type: 'number', step: '0.5' },
        { key: 'heart_rate_rest', label: 'Fréquence cardiaque au repos', type: 'number' },
        { key: 'blood_pressure_sys', label: 'Tension systolique', type: 'number' },
        { key: 'blood_pressure_dia', label: 'Tension diastolique', type: 'number' }
      ]
    }
  };

  // Charger les mesures
  useEffect(() => {
    fetchMeasurements();
  }, []);

  const fetchMeasurements = async () => {
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL || "http://localhost:5000"}/api/users/${userId}/measurements?days=365&limit=100`);
      if (response.ok) {
        const data = await response.json();
        setMeasurements(data);
      }
    } catch (error) {
      console.error('Erreur chargement mesures:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Filtrer les champs vides
    const dataToSend = {};
    Object.keys(newMeasurement).forEach(key => {
      if (newMeasurement[key] !== '') {
        dataToSend[key] = key === 'date' || key === 'exercise_type' || key === 'notes' 
          ? newMeasurement[key] 
          : parseFloat(newMeasurement[key]);
      }
    });

    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL || "http://localhost:5000"}/api/users/${userId}/measurements`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(dataToSend)
      });

      if (response.ok) {
        // Réinitialiser le formulaire
        setNewMeasurement({
          date: new Date().toISOString().split('T')[0],
          weight: '', body_fat: '', muscle_mass: '', water_percentage: '',
          calories_burned: '', steps: '', exercise_hours: '', exercise_type: '',
          calories_consumed: '', protein: '', carbs: '', fat: '', water_intake: '',
          sleep_hours: '', heart_rate_rest: '', blood_pressure_sys: '', blood_pressure_dia: '',
          notes: ''
        });
        setShowAddForm(false);
        fetchMeasurements(); // Recharger les mesures
        
        // Forcer le rafraîchissement des autres pages quand on revient dessus
        window.dispatchEvent(new Event('measurementAdded'));
      }
    } catch (error) {
      console.error('Erreur sauvegarde mesure:', error);
      alert('Erreur lors de la sauvegarde');
    }
  };

  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  // Calculer les tendances sur les 7 derniers jours
  const calculateTrend = (field) => {
    const recentMeasurements = measurements
      .filter(m => m[field])
      .sort((a, b) => new Date(b.date) - new Date(a.date))
      .slice(0, 7);
    
    if (recentMeasurements.length < 2) return null;
    
    const latest = recentMeasurements[0][field];
    const previous = recentMeasurements[recentMeasurements.length - 1][field];
    const change = latest - previous;
    const percentChange = ((change / previous) * 100).toFixed(1);
    
    return { change, percentChange, trend: change > 0 ? 'up' : 'down' };
  };

  // Obtenir la dernière valeur d'un champ
  const getLatestValue = (field) => {
    const measurement = measurements.find(m => m[field]);
    return measurement ? measurement[field] : null;
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded w-1/3"></div>
          <div className="h-64 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-6">
      {/* En-tête */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Mes Mesures</h1>
          <p className="text-gray-600 mt-1">
            Suivez toutes vos métriques de santé et de performance
          </p>
        </div>
        <Button 
          onClick={() => setShowAddForm(!showAddForm)}
          className="flex items-center gap-2"
        >
          {showAddForm ? <X className="h-4 w-4" /> : <Plus className="h-4 w-4" />}
          {showAddForm ? 'Annuler' : 'Nouvelle mesure'}
        </Button>
      </div>

      {/* Formulaire d'ajout */}
      {showAddForm && (
        <Card>
          <CardHeader>
            <CardTitle>Ajouter une nouvelle mesure</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Date */}
              <div>
                <label className="block text-sm font-medium mb-2">
                  Date de la mesure
                </label>
                <input
                  type="date"
                  value={newMeasurement.date}
                  onChange={(e) => setNewMeasurement({...newMeasurement, date: e.target.value})}
                  className="w-full p-2 border rounded-md"
                  required
                />
              </div>

              {/* Catégories de mesures */}
              {Object.entries(measurementCategories).map(([key, category]) => (
                <div key={key} className="space-y-3">
                  <div 
                    className="flex items-center justify-between cursor-pointer"
                    onClick={() => toggleSection(key)}
                  >
                    <h3 className="text-lg font-semibold flex items-center gap-2">
                      <category.icon className="h-5 w-5" />
                      {category.title}
                    </h3>
                    {expandedSections[key] ? 
                      <ChevronUp className="h-4 w-4" /> : 
                      <ChevronDown className="h-4 w-4" />
                    }
                  </div>
                  
                  {expandedSections[key] && (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pl-7">
                      {category.fields.map(field => (
                        <div key={field.key}>
                          <label className="block text-sm font-medium mb-1">
                            {field.label} {field.required && <span className="text-red-500">*</span>}
                          </label>
                          <input
                            type={field.type}
                            step={field.step}
                            placeholder={field.placeholder}
                            value={newMeasurement[field.key]}
                            onChange={(e) => setNewMeasurement({
                              ...newMeasurement, 
                              [field.key]: e.target.value
                            })}
                            className="w-full p-2 border rounded-md"
                            required={field.required}
                          />
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ))}

              {/* Notes */}
              <div>
                <label className="block text-sm font-medium mb-2">
                  Notes (optionnel)
                </label>
                <textarea
                  value={newMeasurement.notes}
                  onChange={(e) => setNewMeasurement({...newMeasurement, notes: e.target.value})}
                  className="w-full p-2 border rounded-md"
                  rows="3"
                  placeholder="Ajoutez des notes sur votre journée, votre forme, etc."
                />
              </div>

              {/* Boutons */}
              <div className="flex gap-3">
                <Button type="submit" className="flex items-center gap-2">
                  <Save className="h-4 w-4" />
                  Enregistrer
                </Button>
                <Button 
                  type="button" 
                  variant="outline"
                  onClick={() => setShowAddForm(false)}
                >
                  Annuler
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      {/* Cartes de résumé */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Poids */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium flex items-center justify-between">
              <span className="flex items-center gap-2">
                <Scale className="h-4 w-4" />
                Poids
              </span>
              {calculateTrend('weight') && (
                calculateTrend('weight').trend === 'down' ? 
                  <TrendingDown className="h-4 w-4 text-green-500" /> :
                  <TrendingUp className="h-4 w-4 text-red-500" />
              )}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {getLatestValue('weight') || '—'} kg
            </div>
            {calculateTrend('weight') && (
              <p className="text-xs text-gray-600 mt-1">
                {calculateTrend('weight').change > 0 ? '+' : ''}
                {calculateTrend('weight').change.toFixed(1)} kg ({calculateTrend('weight').percentChange}%)
              </p>
            )}
          </CardContent>
        </Card>

        {/* Calories dépensées */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Flame className="h-4 w-4" />
              Calories dépensées
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {getLatestValue('calories_burned') || '—'} kcal
            </div>
            <p className="text-xs text-gray-600 mt-1">Aujourd'hui</p>
          </CardContent>
        </Card>

        {/* Exercice */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Dumbbell className="h-4 w-4" />
              Exercice
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {getLatestValue('exercise_hours') || '—'} h
            </div>
            <p className="text-xs text-gray-600 mt-1">
              {getLatestValue('exercise_type') || 'Aucun exercice'}
            </p>
          </CardContent>
        </Card>

        {/* Sommeil */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Moon className="h-4 w-4" />
              Sommeil
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {getLatestValue('sleep_hours') || '—'} h
            </div>
            <p className="text-xs text-gray-600 mt-1">Dernière nuit</p>
          </CardContent>
        </Card>
      </div>

      {/* Historique des mesures */}
      <Card>
        <CardHeader>
          <CardTitle>Historique des mesures</CardTitle>
        </CardHeader>
        <CardContent>
          {measurements.length === 0 ? (
            <p className="text-gray-500 text-center py-8">
              Aucune mesure enregistrée. Commencez par ajouter votre première mesure !
            </p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left p-2">Date</th>
                    <th className="text-right p-2">Poids</th>
                    <th className="text-right p-2">Calories dép.</th>
                    <th className="text-right p-2">Exercice</th>
                    <th className="text-right p-2">Sommeil</th>
                    <th className="text-left p-2">Notes</th>
                  </tr>
                </thead>
                <tbody>
                  {measurements.map((measurement, index) => (
                    <tr key={index} className="border-b hover:bg-gray-50">
                      <td className="p-2">
                        {new Date(measurement.date).toLocaleDateString('fr-FR')}
                      </td>
                      <td className="text-right p-2">
                        {measurement.weight ? `${measurement.weight} kg` : '—'}
                      </td>
                      <td className="text-right p-2">
                        {measurement.calories_burned ? `${measurement.calories_burned} kcal` : '—'}
                      </td>
                      <td className="text-right p-2">
                        {measurement.exercise_hours ? `${measurement.exercise_hours} h` : '—'}
                      </td>
                      <td className="text-right p-2">
                        {measurement.sleep_hours ? `${measurement.sleep_hours} h` : '—'}
                      </td>
                      <td className="p-2">
                        {measurement.notes ? 
                          <span className="text-sm text-gray-600 truncate max-w-xs block">
                            {measurement.notes}
                          </span> : '—'
                        }
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default MeasurementsPage;