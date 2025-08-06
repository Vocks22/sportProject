import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { Header } from './components/Header'
import { Sidebar } from './components/Sidebar'
import { MobileHeader } from './components/MobileHeader'
import { Dashboard } from './components/Dashboard'
import { MobileDashboard } from './components/MobileDashboard'
import { MealPlanning } from './components/MealPlanning'
import { Recipes } from './components/Recipes'
import { Shopping } from './components/Shopping'
import { MobileShopping } from './components/MobileShopping'
import { ProgressPage } from './components/Progress'
import './App.css'

function App() {
  const [currentPage, setCurrentPage] = useState('dashboard')

  // Mettre à jour currentPage quand l'URL change
  useEffect(() => {
    const path = window.location.pathname
    const pageMap = {
      '/': 'dashboard',
      '/planning': 'planning',
      '/recipes': 'recipes',
      '/shopping': 'shopping',
      '/progress': 'progress'
    }
    setCurrentPage(pageMap[path] || 'dashboard')
  }, [])

  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        {/* Header Desktop */}
        <div className="hidden lg:block">
          <Header />
        </div>
        
        {/* Header Mobile */}
        <div className="lg:hidden">
          <MobileHeader 
            currentPage={currentPage}
          />
        </div>
        
        <div className="flex">
          {/* Sidebar Desktop */}
          <div className="hidden lg:block">
            <Sidebar />
          </div>
          
          <main className="flex-1 lg:ml-64 p-4 lg:p-6">
            <Routes>
              <Route path="/" element={
                <>
                  <div className="lg:hidden">
                    <MobileDashboard />
                  </div>
                  <div className="hidden lg:block">
                    <Dashboard />
                  </div>
                </>
              } />
              <Route path="/dashboard" element={
                <>
                  <div className="lg:hidden">
                    <MobileDashboard />
                  </div>
                  <div className="hidden lg:block">
                    <Dashboard />
                  </div>
                </>
              } />
              <Route path="/planning" element={<MealPlanning />} />
              <Route path="/recipes" element={<Recipes />} />
              <Route path="/shopping" element={
                <>
                  <div className="lg:hidden">
                    <MobileShopping />
                  </div>
                  <div className="hidden lg:block">
                    <Shopping />
                  </div>
                </>
              } />
              <Route path="/progress" element={<ProgressPage />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>
        </div>
      </div>
    </Router>
  )
}

export default App

