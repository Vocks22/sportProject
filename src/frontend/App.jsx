import React, { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { Login } from './components/Login'
import { Header } from './components/Header'
import { Sidebar } from './components/Sidebar'
import { Dashboard } from './components/Dashboard'
import { MealPlanning } from './components/MealPlanning'
import { Recipes } from './components/Recipes'
import { Shopping } from './components/Shopping'
import { ProgressPage } from './components/Progress'
import ProfilePage from './pages/ProfilePage'
import MeasurementsPage from './pages/MeasurementsPage'
import DietAdmin from './components/DietAdmin'
import { DatabaseViewer } from './components/DatabaseViewer'
import './App.css'

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [isMobile, setIsMobile] = useState(window.innerWidth < 1024)
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  // Vérifier l'authentification au chargement
  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('auth_token')
      const storedUser = localStorage.getItem('user')
      
      if (token && storedUser) {
        try {
          // Vérifier que le token est toujours valide
          const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000'
          const apiUrl = API_URL.includes('/api') ? API_URL : `${API_URL}/api`
          
          const response = await fetch(`${apiUrl}/auth/verify`, {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          })
          
          if (response.ok) {
            const data = await response.json()
            if (data.success) {
              setIsAuthenticated(true)
              setUser(data.user)
            } else {
              // Token invalide, nettoyer le localStorage
              localStorage.removeItem('auth_token')
              localStorage.removeItem('user')
            }
          }
        } catch (err) {
          console.error('Erreur vérification auth:', err)
        }
      }
      setLoading(false)
    }
    
    checkAuth()
  }, [])
  
  // Détecter les changements de taille d'écran
  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth < 1024)
      // Fermer automatiquement sur mobile
      if (window.innerWidth < 1024) {
        setSidebarOpen(false)
      }
    }
    
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [])

  const handleLogin = (userData, token) => {
    setIsAuthenticated(true)
    setUser(userData)
  }

  const handleLogout = () => {
    localStorage.removeItem('auth_token')
    localStorage.removeItem('user')
    setIsAuthenticated(false)
    setUser(null)
  }

  // Affichage loading pendant la vérification auth
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <svg className="animate-spin h-12 w-12 text-blue-500 mx-auto mb-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <p className="text-gray-600">Chargement...</p>
        </div>
      </div>
    )
  }

  // Si non authentifié, afficher la page de login
  if (!isAuthenticated) {
    return (
      <Router>
        <Routes>
          <Route path="*" element={<Login onLogin={handleLogin} />} />
        </Routes>
      </Router>
    )
  }

  // Application principale (utilisateur authentifié)
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        {/* Header unifié avec bouton menu et logout */}
        <Header 
          sidebarOpen={sidebarOpen} 
          setSidebarOpen={setSidebarOpen}
          user={user}
          onLogout={handleLogout}
        />
        
        {/* Conteneur principal */}
        <div className="flex pt-16 relative">
          {/* Overlay pour mobile quand sidebar est ouvert */}
          {sidebarOpen && isMobile && (
            <div 
              className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
              onClick={() => setSidebarOpen(false)}
            />
          )}
          
          {/* Sidebar rétractable unifié */}
          <Sidebar 
            isOpen={sidebarOpen} 
            setIsOpen={setSidebarOpen}
            isMobile={isMobile}
          />
          
          {/* Contenu principal avec marge dynamique */}
          <main className={`
            flex-1 p-4 lg:p-6 transition-all duration-300
            ${sidebarOpen && !isMobile ? 'ml-64' : 'ml-0'}
          `}>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/planning" element={<MealPlanning />} />
              <Route path="/recipes" element={<Recipes />} />
              <Route path="/shopping" element={<Shopping />} />
              <Route path="/progress" element={<ProgressPage />} />
              <Route path="/profile" element={<ProfilePage />} />
              <Route path="/measurements" element={<MeasurementsPage />} />
              <Route path="/diet-admin" element={<DietAdmin />} />
              <Route path="/database" element={<DatabaseViewer />} />
            </Routes>
          </main>
        </div>
      </div>
    </Router>
  )
}

export default App