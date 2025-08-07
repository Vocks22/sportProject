// Configuration de l'API pour l'environnement

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

// Helper pour construire les URLs d'API
export const getApiUrl = (endpoint) => {
  // Enlever le slash initial si présent
  const cleanEndpoint = endpoint.startsWith('/') ? endpoint.slice(1) : endpoint;
  return `${API_URL}/${cleanEndpoint}`;
};

// Configuration par défaut pour fetch
export const fetchConfig = {
  headers: {
    'Content-Type': 'application/json',
  },
};

// Helper pour les requêtes API
export const apiRequest = async (endpoint, options = {}) => {
  const url = getApiUrl(endpoint);
  const config = {
    ...fetchConfig,
    ...options,
    headers: {
      ...fetchConfig.headers,
      ...options.headers,
    },
  };
  
  try {
    const response = await fetch(url, config);
    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('API Request failed:', error);
    throw error;
  }
};

export default API_URL;