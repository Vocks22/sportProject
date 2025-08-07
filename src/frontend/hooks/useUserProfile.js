/**
 * Hook personnalisé pour la gestion du profil utilisateur - US1.7
 * Gère l'état, les API calls et le cache local pour le profil utilisateur complet
 */

import { useState, useEffect, useCallback, useRef } from 'react';

// Configuration des endpoints
const API_BASE = '/api';
const ENDPOINTS = {
  profile: (userId) => `${API_BASE}/users/${userId}/profile`,
  weightHistory: (userId) => `${API_BASE}/users/${userId}/weight-history`,
  nutritionProfile: (userId) => `${API_BASE}/users/${userId}/nutrition-profile`,
  goals: (userId) => `${API_BASE}/users/${userId}/goals`,
  nutritionValidation: (userId) => `${API_BASE}/users/${userId}/nutrition-validation`
};

// Configuration du cache local
const CACHE_CONFIG = {
  profile: { key: 'userProfile', ttl: 300000 }, // 5 minutes
  weightHistory: { key: 'weightHistory', ttl: 60000 }, // 1 minute
  nutritionProfile: { key: 'nutritionProfile', ttl: 3600000 } // 1 heure
};

/**
 * Utilitaire de cache local avec TTL
 */
class LocalCache {
  static set(key, data, ttl = 300000) {
    const cacheData = {
      data,
      timestamp: Date.now(),
      ttl
    };
    localStorage.setItem(key, JSON.stringify(cacheData));
  }

  static get(key) {
    try {
      const cached = localStorage.getItem(key);
      if (!cached) return null;

      const { data, timestamp, ttl } = JSON.parse(cached);
      const isExpired = Date.now() - timestamp > ttl;
      
      if (isExpired) {
        localStorage.removeItem(key);
        return null;
      }
      
      return data;
    } catch {
      return null;
    }
  }

  static remove(key) {
    localStorage.removeItem(key);
  }

  static clear() {
    const keys = Object.keys(localStorage);
    keys.forEach(key => {
      if (key.startsWith('userProfile') || key.startsWith('weightHistory') || key.startsWith('nutritionProfile')) {
        localStorage.removeItem(key);
      }
    });
  }
}

/**
 * Hook principal pour la gestion du profil utilisateur
 */
export const useUserProfile = (userId) => {
  // États principaux
  const [profile, setProfile] = useState(null);
  const [weightHistory, setWeightHistory] = useState([]);
  const [nutritionProfile, setNutritionProfile] = useState(null);
  const [goals, setGoals] = useState([]);
  
  // États de chargement
  const [loading, setLoading] = useState({
    profile: false,
    weightHistory: false,
    nutritionProfile: false,
    goals: false,
    update: false,
    weightEntry: false
  });
  
  // États d'erreur
  const [errors, setErrors] = useState({
    profile: null,
    weightHistory: null,
    nutritionProfile: null,
    goals: null,
    update: null,
    weightEntry: null
  });

  // Références pour éviter les appels multiples
  const abortControllerRef = useRef();
  const lastFetchRef = useRef({});

  // Fonction utilitaire pour gérer les erreurs
  const handleError = useCallback((errorType, error) => {
    console.error(`Erreur ${errorType}:`, error);
    setErrors(prev => ({ ...prev, [errorType]: error.message || 'Une erreur est survenue' }));
  }, []);

  // Fonction utilitaire pour les appels API
  const apiCall = useCallback(async (url, options = {}) => {
    try {
      const controller = new AbortController();
      abortControllerRef.current = controller;

      const response = await fetch(url, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers
        },
        signal: controller.signal
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `HTTP Error ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      if (error.name === 'AbortError') {
        throw new Error('Requête annulée');
      }
      throw error;
    }
  }, []);

  /**
   * Récupère le profil utilisateur complet
   */
  const fetchProfile = useCallback(async (forceRefresh = false) => {
    if (!userId) return;

    const cacheKey = `${CACHE_CONFIG.profile.key}_${userId}`;
    
    // Vérifier le cache si pas de refresh forcé
    if (!forceRefresh) {
      const cachedProfile = LocalCache.get(cacheKey);
      if (cachedProfile) {
        setProfile(cachedProfile);
        return cachedProfile;
      }
    }

    // Éviter les appels multiples
    const now = Date.now();
    if (!forceRefresh && lastFetchRef.current.profile && (now - lastFetchRef.current.profile) < 1000) {
      return profile;
    }
    lastFetchRef.current.profile = now;

    setLoading(prev => ({ ...prev, profile: true }));
    setErrors(prev => ({ ...prev, profile: null }));

    try {
      const profileData = await apiCall(ENDPOINTS.profile(userId));
      
      setProfile(profileData);
      LocalCache.set(cacheKey, profileData, CACHE_CONFIG.profile.ttl);
      
      // Mettre à jour les données liées
      if (profileData.recent_weight_history) {
        setWeightHistory(profileData.recent_weight_history);
      }
      if (profileData.nutrition_profile) {
        setNutritionProfile(profileData.nutrition_profile);
      }
      if (profileData.active_goals) {
        setGoals(profileData.active_goals);
      }

      return profileData;
    } catch (error) {
      handleError('profile', error);
      return null;
    } finally {
      setLoading(prev => ({ ...prev, profile: false }));
    }
  }, [userId, apiCall, handleError, profile]);

  /**
   * Met à jour le profil utilisateur
   */
  const updateProfile = useCallback(async (updates) => {
    if (!userId) return null;

    setLoading(prev => ({ ...prev, update: true }));
    setErrors(prev => ({ ...prev, update: null }));

    try {
      const updatedProfile = await apiCall(ENDPOINTS.profile(userId), {
        method: 'PUT',
        body: JSON.stringify(updates)
      });

      setProfile(updatedProfile);
      
      // Mettre à jour le cache
      const cacheKey = `${CACHE_CONFIG.profile.key}_${userId}`;
      LocalCache.set(cacheKey, updatedProfile, CACHE_CONFIG.profile.ttl);

      // Invalider les caches liés
      LocalCache.remove(`${CACHE_CONFIG.nutritionProfile.key}_${userId}`);
      
      return updatedProfile;
    } catch (error) {
      handleError('update', error);
      throw error;
    } finally {
      setLoading(prev => ({ ...prev, update: false }));
    }
  }, [userId, apiCall, handleError]);

  /**
   * Récupère l'historique des pesées
   */
  const fetchWeightHistory = useCallback(async (params = {}) => {
    if (!userId) return [];

    const queryParams = new URLSearchParams({
      days: params.days || 90,
      limit: params.limit || 100
    });

    const cacheKey = `${CACHE_CONFIG.weightHistory.key}_${userId}_${queryParams.toString()}`;
    
    // Vérifier le cache
    if (!params.forceRefresh) {
      const cachedHistory = LocalCache.get(cacheKey);
      if (cachedHistory) {
        setWeightHistory(cachedHistory.weight_history || []);
        return cachedHistory;
      }
    }

    setLoading(prev => ({ ...prev, weightHistory: true }));
    setErrors(prev => ({ ...prev, weightHistory: null }));

    try {
      const url = `${ENDPOINTS.weightHistory(userId)}?${queryParams}`;
      const historyData = await apiCall(url);
      
      setWeightHistory(historyData.weight_history || []);
      LocalCache.set(cacheKey, historyData, CACHE_CONFIG.weightHistory.ttl);
      
      return historyData;
    } catch (error) {
      handleError('weightHistory', error);
      return { weight_history: [], statistics: {}, period_info: {} };
    } finally {
      setLoading(prev => ({ ...prev, weightHistory: false }));
    }
  }, [userId, apiCall, handleError]);

  /**
   * Ajoute une nouvelle pesée
   */
  const addWeightEntry = useCallback(async (weightData) => {
    if (!userId) return null;

    setLoading(prev => ({ ...prev, weightEntry: true }));
    setErrors(prev => ({ ...prev, weightEntry: null }));

    try {
      const result = await apiCall(ENDPOINTS.weightHistory(userId), {
        method: 'POST',
        body: JSON.stringify(weightData)
      });

      // Mettre à jour l'historique local
      setWeightHistory(prev => [result.weight_entry, ...prev.slice(0, 99)]);
      
      // Invalider les caches
      const cacheKeys = Object.keys(localStorage).filter(key => 
        key.startsWith(`${CACHE_CONFIG.weightHistory.key}_${userId}`) ||
        key.startsWith(`${CACHE_CONFIG.profile.key}_${userId}`)
      );
      cacheKeys.forEach(key => localStorage.removeItem(key));

      // Recharger le profil si le poids actuel a changé
      if (weightData.recorded_date === new Date().toISOString().split('T')[0]) {
        setTimeout(() => fetchProfile(true), 500);
      }

      return result;
    } catch (error) {
      handleError('weightEntry', error);
      throw error;
    } finally {
      setLoading(prev => ({ ...prev, weightEntry: false }));
    }
  }, [userId, apiCall, handleError, fetchProfile]);

  /**
   * Récupère le profil nutritionnel
   */
  const fetchNutritionProfile = useCallback(async (params = {}) => {
    if (!userId) return null;

    const queryParams = new URLSearchParams();
    if (params.goalType) queryParams.append('goal_type', params.goalType);
    if (params.forceRecalculate) queryParams.append('force_recalculate', 'true');

    const cacheKey = `${CACHE_CONFIG.nutritionProfile.key}_${userId}_${queryParams.toString()}`;
    
    // Vérifier le cache
    if (!params.forceRecalculate) {
      const cachedNutrition = LocalCache.get(cacheKey);
      if (cachedNutrition) {
        setNutritionProfile(cachedNutrition);
        return cachedNutrition;
      }
    }

    setLoading(prev => ({ ...prev, nutritionProfile: true }));
    setErrors(prev => ({ ...prev, nutritionProfile: null }));

    try {
      const url = `${ENDPOINTS.nutritionProfile(userId)}?${queryParams}`;
      const nutritionData = await apiCall(url);
      
      setNutritionProfile(nutritionData);
      LocalCache.set(cacheKey, nutritionData, CACHE_CONFIG.nutritionProfile.ttl);
      
      return nutritionData;
    } catch (error) {
      handleError('nutritionProfile', error);
      return null;
    } finally {
      setLoading(prev => ({ ...prev, nutritionProfile: false }));
    }
  }, [userId, apiCall, handleError]);

  /**
   * Valide les objectifs nutritionnels
   */
  const validateNutritionGoals = useCallback(async () => {
    if (!userId) return null;

    try {
      return await apiCall(ENDPOINTS.nutritionValidation(userId), {
        method: 'POST'
      });
    } catch (error) {
      handleError('nutritionProfile', error);
      throw error;
    }
  }, [userId, apiCall, handleError]);

  /**
   * Récupère les objectifs de l'utilisateur
   */
  const fetchGoals = useCallback(async (status = 'active') => {
    if (!userId) return [];

    setLoading(prev => ({ ...prev, goals: true }));
    setErrors(prev => ({ ...prev, goals: null }));

    try {
      const url = `${ENDPOINTS.goals(userId)}?status=${status}`;
      const goalsData = await apiCall(url);
      
      setGoals(goalsData.goals || []);
      return goalsData;
    } catch (error) {
      handleError('goals', error);
      return { goals: [], count: 0 };
    } finally {
      setLoading(prev => ({ ...prev, goals: false }));
    }
  }, [userId, apiCall, handleError]);

  /**
   * Crée un nouvel objectif
   */
  const createGoal = useCallback(async (goalData) => {
    if (!userId) return null;

    try {
      const result = await apiCall(ENDPOINTS.goals(userId), {
        method: 'POST',
        body: JSON.stringify(goalData)
      });

      // Mettre à jour la liste des objectifs
      setGoals(prev => [result, ...prev]);
      
      return result;
    } catch (error) {
      handleError('goals', error);
      throw error;
    }
  }, [userId, apiCall, handleError]);

  /**
   * Efface tous les caches
   */
  const clearCache = useCallback(() => {
    LocalCache.clear();
  }, []);

  /**
   * Rafraîchit toutes les données
   */
  const refreshAll = useCallback(async () => {
    clearCache();
    
    const promises = [
      fetchProfile(true),
      fetchWeightHistory({ forceRefresh: true }),
      fetchNutritionProfile({ forceRecalculate: true }),
      fetchGoals()
    ];

    try {
      await Promise.allSettled(promises);
    } catch (error) {
      console.error('Erreur lors du rafraîchissement:', error);
    }
  }, [fetchProfile, fetchWeightHistory, fetchNutritionProfile, fetchGoals, clearCache]);

  // Chargement initial
  useEffect(() => {
    if (userId) {
      fetchProfile();
    }

    // Cleanup
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, [userId, fetchProfile]);

  // Données dérivées
  const derivedData = {
    // Indicateurs de progression
    hasCompleteProfile: profile?.profile_completed || false,
    weightTrend: profile?.progress?.weight_trend || null,
    progressPercentage: profile?.progress?.progress_percentage || 0,
    daysSinceLastWeighIn: profile?.progress?.days_since_last_weigh_in || null,
    
    // Métriques calculées
    bmi: profile?.calculated_values?.bmi || null,
    bmiCategory: profile?.calculated_values?.bmi_category || null,
    bmr: nutritionProfile?.bmr || profile?.calculated_values?.bmr || null,
    tdee: nutritionProfile?.tdee || profile?.calculated_values?.tdee || null,
    
    // Statuts
    needsWeightUpdate: (profile?.progress?.days_since_last_weigh_in || 0) > 7,
    hasActiveGoals: goals.length > 0,
    isLoading: Object.values(loading).some(Boolean),
    hasErrors: Object.values(errors).some(Boolean)
  };

  return {
    // Données
    profile,
    weightHistory,
    nutritionProfile,
    goals,
    
    // États
    loading,
    errors,
    
    // Données dérivées
    ...derivedData,
    
    // Actions
    fetchProfile,
    updateProfile,
    fetchWeightHistory,
    addWeightEntry,
    fetchNutritionProfile,
    validateNutritionGoals,
    fetchGoals,
    createGoal,
    refreshAll,
    clearCache
  };
};

/**
 * Hook simplifié pour les données de base du profil
 */
export const useBasicProfile = (userId) => {
  const {
    profile,
    loading,
    errors,
    fetchProfile,
    updateProfile,
    hasCompleteProfile,
    bmi,
    bmiCategory
  } = useUserProfile(userId);

  return {
    profile,
    loading: loading.profile,
    error: errors.profile,
    fetchProfile,
    updateProfile,
    hasCompleteProfile,
    bmi,
    bmiCategory
  };
};

/**
 * Hook spécialisé pour l'historique des poids
 */
export const useWeightTracking = (userId) => {
  const {
    weightHistory,
    loading,
    errors,
    fetchWeightHistory,
    addWeightEntry,
    weightTrend,
    daysSinceLastWeighIn,
    needsWeightUpdate
  } = useUserProfile(userId);

  return {
    weightHistory,
    loading: loading.weightHistory || loading.weightEntry,
    error: errors.weightHistory || errors.weightEntry,
    fetchWeightHistory,
    addWeightEntry,
    weightTrend,
    daysSinceLastWeighIn,
    needsWeightUpdate
  };
};

/**
 * Hook spécialisé pour la nutrition
 */
export const useNutritionTracking = (userId) => {
  const {
    nutritionProfile,
    loading,
    errors,
    fetchNutritionProfile,
    validateNutritionGoals,
    bmr,
    tdee
  } = useUserProfile(userId);

  return {
    nutritionProfile,
    loading: loading.nutritionProfile,
    error: errors.nutritionProfile,
    fetchNutritionProfile,
    validateNutritionGoals,
    bmr,
    tdee
  };
};

export default useUserProfile;