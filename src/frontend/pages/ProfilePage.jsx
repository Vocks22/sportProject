/**
 * Page de profil utilisateur - US1.7 : Profil Utilisateur Réel
 * Interface complète avec métriques, formulaire et graphique de progression
 */

import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Progress } from '../components/ui/progress';
import { useUserProfile } from '../hooks/useUserProfile';
import WeightChart from '../components/WeightChart';
import {
  User,
  Target,
  TrendingUp,
  TrendingDown,
  Minus,
  Scale,
  Activity,
  Heart,
  AlertCircle,
  CheckCircle,
  Calendar,
  Edit,
  Save,
  X,
  Plus
} from 'lucide-react';

// Composant pour les métriques de santé
const HealthMetricsCard = ({ profile, nutritionProfile }) => {
  const metrics = [
    {
      label: 'IMC',
      value: profile?.calculated_values?.bmi,
      unit: '',
      category: profile?.calculated_values?.bmi_category,
      icon: Scale
    },
    {
      label: 'BMR',
      value: nutritionProfile?.bmr,
      unit: 'kcal/jour',
      description: 'Métabolisme de base',
      icon: Activity
    },
    {
      label: 'TDEE',
      value: nutritionProfile?.tdee,
      unit: 'kcal/jour',
      description: 'Dépense énergétique totale',
      icon: Heart
    }
  ];

  const getBmiColor = (category) => {
    switch (category) {
      case 'underweight': return 'text-blue-600';
      case 'normal': return 'text-green-600';
      case 'overweight': return 'text-yellow-600';
      case 'obese': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  const getBmiLabel = (category) => {
    switch (category) {
      case 'underweight': return 'Insuffisance pondérale';
      case 'normal': return 'Normal';
      case 'overweight': return 'Surpoids';
      case 'obese': return 'Obésité';
      default: return 'Non calculé';
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Activity className="h-5 w-5" />
          Métriques de santé
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {metrics.map((metric, index) => {
            const Icon = metric.icon;
            return (
              <div key={index} className="p-4 bg-gray-50 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <Icon className="h-4 w-4 text-gray-500" />
                  <span className="text-sm text-gray-600">{metric.label}</span>
                </div>
                <div className="space-y-1">
                  <div className="text-2xl font-bold">
                    {metric.value ? metric.value.toFixed(1) : '--'}
                    <span className="text-sm font-normal text-gray-500 ml-1">
                      {metric.unit}
                    </span>
                  </div>
                  {metric.category && (
                    <Badge 
                      className={`text-xs ${getBmiColor(metric.category)}`}
                      variant="outline"
                    >
                      {getBmiLabel(metric.category)}
                    </Badge>
                  )}
                  {metric.description && (
                    <p className="text-xs text-gray-500">{metric.description}</p>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
};

// Composant pour les objectifs nutritionnels
const NutritionTargetsCard = ({ nutritionProfile, onEdit }) => {
  if (!nutritionProfile) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center py-8">
          <div className="text-center">
            <AlertCircle className="h-12 w-12 text-gray-400 mx-auto mb-2" />
            <p className="text-gray-600">Calculs nutritionnels en cours...</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  const targets = [
    { label: 'Calories', value: nutritionProfile.adjusted_calories, unit: 'kcal', color: 'bg-blue-500' },
    { label: 'Protéines', value: nutritionProfile.protein_target, unit: 'g', color: 'bg-red-500' },
    { label: 'Glucides', value: nutritionProfile.carbs_target, unit: 'g', color: 'bg-green-500' },
    { label: 'Lipides', value: nutritionProfile.fat_target, unit: 'g', color: 'bg-yellow-500' },
    { label: 'Fibres', value: nutritionProfile.fiber_target, unit: 'g', color: 'bg-purple-500' },
    { label: 'Eau', value: nutritionProfile.water_target, unit: 'ml', color: 'bg-cyan-500' }
  ];

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Target className="h-5 w-5" />
            Objectifs nutritionnels
          </CardTitle>
          <Button variant="outline" size="sm" onClick={onEdit}>
            <Edit className="h-4 w-4 mr-2" />
            Modifier
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          {targets.map((target, index) => (
            <div key={index} className="text-center p-3 bg-gray-50 rounded-lg">
              <div className={`w-3 h-3 ${target.color} rounded-full mx-auto mb-2`}></div>
              <div className="text-lg font-semibold">
                {target.value.toFixed(0)}
                <span className="text-sm font-normal text-gray-500 ml-1">
                  {target.unit}
                </span>
              </div>
              <div className="text-sm text-gray-600">{target.label}</div>
            </div>
          ))}
        </div>
        
        {nutritionProfile.calculation_method === 'mifflin_st_jeor' && (
          <div className="mt-4 p-3 bg-green-50 rounded-lg">
            <div className="flex items-center gap-2 text-sm text-green-700">
              <CheckCircle className="h-4 w-4" />
              Calculé avec la formule Mifflin-St Jeor (recommandée)
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

// Composant pour la progression du poids
const WeightProgressCard = ({ profile, weightHistory, onAddWeight }) => {
  const progress = profile?.progress || {};
  const currentWeight = profile?.current_weight;
  const targetWeight = profile?.target_weight;
  
  const getTrendIcon = (trend) => {
    switch (trend) {
      case 'increasing': return <TrendingUp className="h-4 w-4 text-red-500" />;
      case 'decreasing': return <TrendingDown className="h-4 w-4 text-green-500" />;
      case 'stable': return <Minus className="h-4 w-4 text-gray-500" />;
      default: return null;
    }
  };

  const getTrendLabel = (trend) => {
    switch (trend) {
      case 'increasing': return 'En hausse';
      case 'decreasing': return 'En baisse';
      case 'stable': return 'Stable';
      default: return 'Pas de données';
    }
  };

  const getTrendColor = (trend) => {
    switch (trend) {
      case 'increasing': return 'text-red-600';
      case 'decreasing': return 'text-green-600';
      case 'stable': return 'text-gray-600';
      default: return 'text-gray-400';
    }
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Scale className="h-5 w-5" />
            Progression du poids
          </CardTitle>
          <Button variant="outline" size="sm" onClick={onAddWeight}>
            <Plus className="h-4 w-4 mr-2" />
            Ajouter pesée
          </Button>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Poids actuel et objectif */}
        <div className="grid grid-cols-2 gap-4">
          <div className="text-center p-3 bg-blue-50 rounded-lg">
            <div className="text-2xl font-bold text-blue-700">
              {currentWeight ? `${currentWeight} kg` : '--'}
            </div>
            <div className="text-sm text-blue-600">Poids actuel</div>
          </div>
          <div className="text-center p-3 bg-green-50 rounded-lg">
            <div className="text-2xl font-bold text-green-700">
              {targetWeight ? `${targetWeight} kg` : '--'}
            </div>
            <div className="text-sm text-green-600">Objectif</div>
          </div>
        </div>

        {/* Progression */}
        {progress.progress_percentage !== undefined && (
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span>Progression vers l'objectif</span>
              <span className="font-medium">
                {Math.round(progress.progress_percentage)}%
              </span>
            </div>
            <Progress value={Math.max(0, Math.min(100, progress.progress_percentage))} />
          </div>
        )}

        {/* Tendance */}
        <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
          <span className="text-sm text-gray-600">Tendance (30 jours)</span>
          <div className={`flex items-center gap-2 ${getTrendColor(progress.weight_trend)}`}>
            {getTrendIcon(progress.weight_trend)}
            <span className="font-medium">{getTrendLabel(progress.weight_trend)}</span>
          </div>
        </div>

        {/* Alerte dernière pesée */}
        {progress.days_since_last_weigh_in > 7 && (
          <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
            <div className="flex items-center gap-2 text-yellow-700">
              <AlertCircle className="h-4 w-4" />
              <span className="text-sm">
                Dernière pesée il y a {progress.days_since_last_weigh_in} jours
              </span>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

// Formulaire modal pour ajouter une pesée
const AddWeightModal = ({ isOpen, onClose, onSubmit, loading }) => {
  const [formData, setFormData] = useState({
    weight: '',
    recorded_date: new Date().toISOString().split('T')[0],
    body_fat_percentage: '',
    notes: ''
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    const data = {
      ...formData,
      weight: parseFloat(formData.weight),
      body_fat_percentage: formData.body_fat_percentage ? parseFloat(formData.body_fat_percentage) : null
    };
    onSubmit(data);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold">Ajouter une pesée</h3>
          <Button variant="ghost" size="sm" onClick={onClose}>
            <X className="h-4 w-4" />
          </Button>
        </div>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Poids (kg)</label>
            <input
              type="number"
              step="0.1"
              min="20"
              max="500"
              value={formData.weight}
              onChange={(e) => setFormData(prev => ({ ...prev, weight: e.target.value }))}
              className="w-full p-2 border border-gray-300 rounded-md"
              required
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">Date</label>
            <input
              type="date"
              value={formData.recorded_date}
              onChange={(e) => setFormData(prev => ({ ...prev, recorded_date: e.target.value }))}
              className="w-full p-2 border border-gray-300 rounded-md"
              required
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">
              Masse grasse (%) <span className="text-gray-400">optionnel</span>
            </label>
            <input
              type="number"
              step="0.1"
              min="0"
              max="100"
              value={formData.body_fat_percentage}
              onChange={(e) => setFormData(prev => ({ ...prev, body_fat_percentage: e.target.value }))}
              className="w-full p-2 border border-gray-300 rounded-md"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">
              Notes <span className="text-gray-400">optionnel</span>
            </label>
            <textarea
              value={formData.notes}
              onChange={(e) => setFormData(prev => ({ ...prev, notes: e.target.value }))}
              className="w-full p-2 border border-gray-300 rounded-md"
              rows="2"
            />
          </div>
          
          <div className="flex gap-2 pt-4">
            <Button type="button" variant="outline" onClick={onClose} className="flex-1">
              Annuler
            </Button>
            <Button type="submit" disabled={loading} className="flex-1">
              {loading ? 'Enregistrement...' : 'Enregistrer'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};

// Composant principal
const ProfilePage = () => {
  const userId = 1; // TODO: Récupérer depuis le contexte d'authentification
  
  const {
    profile,
    weightHistory,
    nutritionProfile,
    loading,
    errors,
    hasCompleteProfile,
    fetchProfile,
    addWeightEntry,
    refreshAll
  } = useUserProfile(userId);

  const [showAddWeight, setShowAddWeight] = useState(false);
  const [editingProfile, setEditingProfile] = useState(false);

  // Handlers
  const handleAddWeight = useCallback(async (weightData) => {
    try {
      await addWeightEntry(weightData);
      setShowAddWeight(false);
      // Rafraîchir les données après ajout
      setTimeout(() => refreshAll(), 500);
    } catch (error) {
      console.error('Erreur ajout pesée:', error);
    }
  }, [addWeightEntry, refreshAll]);

  const handleEditProfile = useCallback(() => {
    setEditingProfile(true);
  }, []);

  const handleEditNutrition = useCallback(() => {
    // TODO: Ouvrir modal d'édition des objectifs nutritionnels
    console.log('Édition objectifs nutritionnels');
  }, []);

  // Chargement initial
  useEffect(() => {
    if (userId) {
      refreshAll();
    }
  }, [userId, refreshAll]);

  if (loading.profile && !profile) {
    return (
      <div className="max-w-6xl mx-auto p-6">
        <div className="animate-pulse space-y-6">
          <div className="h-8 bg-gray-200 rounded w-1/3"></div>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {[1, 2, 3].map(i => (
              <div key={i} className="h-64 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Mon Profil</h1>
          <p className="text-gray-600 mt-1">
            Gérez votre profil et suivez votre progression
          </p>
        </div>
        <div className="flex items-center gap-2">
          {!hasCompleteProfile && (
            <Badge variant="outline" className="text-yellow-600 border-yellow-300">
              <AlertCircle className="h-3 w-3 mr-1" />
              Profil incomplet
            </Badge>
          )}
          <Button onClick={refreshAll} variant="outline">
            Actualiser
          </Button>
        </div>
      </div>

      {/* Erreurs */}
      {Object.values(errors).some(Boolean) && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center gap-2 text-red-700 mb-2">
            <AlertCircle className="h-4 w-4" />
            <span className="font-medium">Erreurs détectées</span>
          </div>
          <ul className="text-sm text-red-600 space-y-1">
            {Object.entries(errors).map(([key, error]) => 
              error && <li key={key}>• {error}</li>
            )}
          </ul>
        </div>
      )}

      {/* Grille principale */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Colonne gauche */}
        <div className="lg:col-span-2 space-y-6">
          {/* Métriques de santé */}
          <HealthMetricsCard 
            profile={profile} 
            nutritionProfile={nutritionProfile} 
          />
          
          {/* Graphique de progression */}
          {weightHistory.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TrendingUp className="h-5 w-5" />
                  Évolution du poids
                </CardTitle>
              </CardHeader>
              <CardContent>
                <WeightChart 
                  data={weightHistory}
                  targetWeight={profile?.target_weight}
                  height={300}
                />
              </CardContent>
            </Card>
          )}
          
          {/* Objectifs nutritionnels */}
          <NutritionTargetsCard 
            nutritionProfile={nutritionProfile}
            onEdit={handleEditNutrition}
          />
        </div>

        {/* Colonne droite */}
        <div className="space-y-6">
          {/* Progression du poids */}
          <WeightProgressCard 
            profile={profile}
            weightHistory={weightHistory}
            onAddWeight={() => setShowAddWeight(true)}
          />
          
          {/* Informations du profil */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center gap-2">
                  <User className="h-5 w-5" />
                  Informations personnelles
                </CardTitle>
                <Button variant="outline" size="sm" onClick={handleEditProfile}>
                  <Edit className="h-4 w-4 mr-2" />
                  Modifier
                </Button>
              </div>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Nom d'utilisateur</span>
                <span className="font-medium">{profile?.username || '--'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Âge</span>
                <span className="font-medium">{profile?.age || '--'} ans</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Genre</span>
                <span className="font-medium capitalize">
                  {profile?.gender === 'male' ? 'Homme' : 
                   profile?.gender === 'female' ? 'Femme' : '--'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Taille</span>
                <span className="font-medium">
                  {profile?.height ? `${profile.height} cm` : '--'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Niveau d'activité</span>
                <span className="font-medium capitalize">
                  {profile?.activity_level?.replace('_', ' ') || '--'}
                </span>
              </div>
              {profile?.last_profile_update && (
                <div className="pt-2 border-t">
                  <div className="flex items-center gap-2 text-xs text-gray-500">
                    <Calendar className="h-3 w-3" />
                    Dernière mise à jour : {new Date(profile.last_profile_update).toLocaleDateString('fr-FR')}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Modal ajout pesée */}
      <AddWeightModal
        isOpen={showAddWeight}
        onClose={() => setShowAddWeight(false)}
        onSubmit={handleAddWeight}
        loading={loading.weightEntry}
      />
    </div>
  );
};

export default ProfilePage;