import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Menu, X, User, Target } from 'lucide-react'
import { Button } from '@/components/ui/button'

export function MobileHeader({ currentPage }) {
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const navigate = useNavigate()

  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: '📊', color: 'bg-blue-500', path: '/' },
    { id: 'planning', label: 'Planning', icon: '📅', color: 'bg-orange-500', path: '/planning' },
    { id: 'recipes', label: 'Recettes', icon: '🍽️', color: 'bg-purple-500', path: '/recipes' },
    { id: 'shopping', label: 'Courses', icon: '🛒', color: 'bg-teal-500', path: '/shopping' },
    { id: 'progress', label: 'Suivi', icon: '📈', color: 'bg-pink-500', path: '/progress' }
  ]

  const handleNavigate = (item) => {
    navigate(item.path)
    setIsMenuOpen(false)
  }

  return (
    <>
      {/* Header Mobile */}
      <div className="lg:hidden bg-white border-b border-gray-200 px-4 py-3 flex items-center justify-between sticky top-0 z-50">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-green-500 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-sm">DT</span>
          </div>
          <h1 className="text-lg font-bold text-gray-900">DietTracker</h1>
        </div>
        
        <div className="flex items-center space-x-3">
          {/* Objectif du mois - Version mobile compacte */}
          <div className="text-right">
            <div className="text-xs text-gray-500">Objectif</div>
            <div className="text-sm font-bold text-green-600">-2.3kg</div>
          </div>
          
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsMenuOpen(!isMenuOpen)}
            className="p-2"
          >
            {isMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </Button>
        </div>
      </div>

      {/* Menu Mobile Overlay */}
      {isMenuOpen && (
        <div className="lg:hidden fixed inset-0 z-40 bg-black bg-opacity-50" onClick={() => setIsMenuOpen(false)}>
          <div className="absolute top-16 right-0 left-0 bg-white border-b border-gray-200 shadow-lg">
            <div className="p-4">
              {/* Profil utilisateur */}
              <div className="flex items-center space-x-3 mb-6 p-3 bg-gray-50 rounded-lg">
                <div className="w-10 h-10 bg-green-500 rounded-full flex items-center justify-center">
                  <User className="h-5 w-5 text-white" />
                </div>
                <div>
                  <div className="font-semibold text-gray-900">Fabien</div>
                  <div className="text-sm text-gray-500">Objectif: -5kg ce mois</div>
                </div>
              </div>

              {/* Navigation */}
              <div className="space-y-2">
                {menuItems.map((item) => (
                  <button
                    key={item.id}
                    onClick={() => handleNavigate(item)}
                    className={`w-full flex items-center space-x-3 p-3 rounded-lg transition-colors ${
                      currentPage === item.id 
                        ? 'bg-blue-50 border border-blue-200' 
                        : 'hover:bg-gray-50'
                    }`}
                  >
                    <div className={`w-8 h-8 ${item.color} rounded-lg flex items-center justify-center`}>
                      <span className="text-white text-sm">{item.icon}</span>
                    </div>
                    <span className="font-medium text-gray-900">{item.label}</span>
                    {currentPage === item.id && (
                      <div className="ml-auto w-2 h-2 bg-blue-500 rounded-full"></div>
                    )}
                  </button>
                ))}
              </div>

              {/* Objectif détaillé */}
              <div className="mt-6 p-3 bg-green-50 rounded-lg border border-green-200">
                <div className="flex items-center space-x-2 mb-2">
                  <Target className="h-4 w-4 text-green-600" />
                  <span className="text-sm font-medium text-green-800">Objectif du mois</span>
                </div>
                <div className="text-lg font-bold text-green-600">-5kg • 2.3kg perdus</div>
                <div className="w-full bg-green-200 rounded-full h-2 mt-2">
                  <div className="bg-green-500 h-2 rounded-full" style={{ width: '46%' }}></div>
                </div>
                <div className="text-xs text-green-600 mt-1">46% de l'objectif atteint</div>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  )
}

