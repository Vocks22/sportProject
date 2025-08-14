import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { 
  LayoutDashboard, 
  Calendar, 
  ChefHat, 
  ShoppingCart, 
  TrendingUp,
  User,
  X,
  Activity
} from 'lucide-react'
import { Button } from './ui/button'

export function Sidebar({ isOpen, setIsOpen, isMobile }) {
  const location = useLocation()

  const navigation = [
    { name: 'Dashboard', href: '/', icon: LayoutDashboard },
    { name: 'Planning', href: '/planning', icon: Calendar },
    { name: 'Recettes', href: '/recipes', icon: ChefHat },
    { name: 'Courses', href: '/shopping', icon: ShoppingCart },
    { name: 'Suivi', href: '/progress', icon: TrendingUp },
    { name: 'Mesures', href: '/measurements', icon: Activity },
    { name: 'Profil', href: '/profile', icon: User },
    { name: '⚙️ Admin Repas', href: '/diet-admin', icon: LayoutDashboard },
  ]

  const handleLinkClick = () => {
    // Fermer automatiquement sur mobile après navigation
    if (isMobile) {
      setIsOpen(false)
    }
  }

  return (
    <aside 
      className={`
        fixed left-0 top-16 h-[calc(100vh-4rem)] bg-white border-r border-gray-200
        transition-transform duration-300 z-40
        ${isOpen ? 'translate-x-0' : '-translate-x-full'}
        w-64
      `}
    >
      {/* Header de la sidebar avec bouton fermer sur mobile */}
      {isMobile && (
        <div className="flex items-center justify-between p-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold">Menu</h2>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsOpen(false)}
          >
            <X className="h-5 w-5" />
          </Button>
        </div>
      )}

      {/* Menu items */}
      <nav className="p-4 space-y-2">
        {navigation.map((item) => {
          const Icon = item.icon
          const isActive = location.pathname === item.href
          
          return (
            <Link
              key={item.name}
              to={item.href}
              onClick={handleLinkClick}
              className={`
                flex items-center space-x-3 px-4 py-3 rounded-lg
                transition-colors duration-200
                ${isActive 
                  ? 'bg-indigo-50 text-indigo-600 font-medium' 
                  : 'text-gray-700 hover:bg-gray-100'
                }
              `}
            >
              <Icon className={`h-5 w-5 ${isActive ? 'text-indigo-600' : 'text-gray-500'}`} />
              <span>{item.name}</span>
            </Link>
          )
        })}
      </nav>

      {/* Footer avec infos utilisateur */}
      <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-200">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-gray-300 rounded-full flex items-center justify-center">
            <User className="h-5 w-5 text-gray-600" />
          </div>
          <div>
            <p className="text-sm font-medium text-gray-900">Fabien</p>
            <p className="text-xs text-gray-500">-2.3kg ce mois</p>
          </div>
        </div>
      </div>
    </aside>
  )
}