// Utilitaire pour les requêtes API avec authentification

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000'

// Fonction pour obtenir les headers avec le token JWT
export const getAuthHeaders = () => {
  const token = localStorage.getItem('auth_token')
  const headers = {
    'Content-Type': 'application/json'
  }
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }
  
  return headers
}

// Fonction pour faire une requête API authentifiée
export const apiRequest = async (endpoint, options = {}) => {
  const url = `${API_URL}${endpoint}`
  
  const config = {
    ...options,
    headers: {
      ...getAuthHeaders(),
      ...(options.headers || {})
    }
  }
  
  try {
    const response = await fetch(url, config)
    
    // Si non authentifié, rediriger vers login
    if (response.status === 401) {
      localStorage.removeItem('auth_token')
      localStorage.removeItem('user')
      window.location.href = '/login'
      return null
    }
    
    return response
  } catch (error) {
    console.error('API Request Error:', error)
    throw error
  }
}

// Requêtes GET
export const apiGet = (endpoint) => {
  return apiRequest(endpoint, { method: 'GET' })
}

// Requêtes POST
export const apiPost = (endpoint, data) => {
  return apiRequest(endpoint, {
    method: 'POST',
    body: JSON.stringify(data)
  })
}

// Requêtes PUT
export const apiPut = (endpoint, data) => {
  return apiRequest(endpoint, {
    method: 'PUT',
    body: JSON.stringify(data)
  })
}

// Requêtes DELETE
export const apiDelete = (endpoint) => {
  return apiRequest(endpoint, { method: 'DELETE' })
}