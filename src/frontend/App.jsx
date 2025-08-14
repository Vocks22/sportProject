import React, { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
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
import './App.css'

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [isMobile, setIsMobile] = useState(window.innerWidth < 1024)

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

  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        {/* Header unifié avec bouton menu */}
        <Header 
          sidebarOpen={sidebarOpen} 
          setSidebarOpen={setSidebarOpen}
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
            </Routes>
          </main>
        </div>
      </div>
    </Router>
  )
}

export default App