import { Link, useLocation } from 'react-router-dom'
import { 
  LayoutDashboard, 
  Calendar, 
  ChefHat, 
  ShoppingCart, 
  TrendingUp,
  X
} from 'lucide-react'
import { Button } from '@/components/ui/button'

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Planning', href: '/planning', icon: Calendar },
  { name: 'Recettes', href: '/recipes', icon: ChefHat },
  { name: 'Courses', href: '/shopping', icon: ShoppingCart },
  { name: 'Suivi', href: '/progress', icon: TrendingUp },
]

export function Sidebar({ isOpen, onClose }) {
  const location = useLocation()

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div 
          className="fixed inset-0 z-40 bg-black bg-opacity-50 lg:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <div className={`
        fixed top-16 left-0 z-50 h-[calc(100vh-4rem)] w-64 bg-white border-r border-gray-200
        transform transition-transform duration-300 ease-in-out
        ${isOpen ? 'translate-x-0' : '-translate-x-full'}
        lg:translate-x-0
      `}>
        {/* Mobile close button */}
        <div className="flex items-center justify-between p-4 lg:hidden">
          <span className="text-lg font-semibold text-gray-900">Menu</span>
          <Button variant="ghost" size="sm" onClick={onClose}>
            <X className="h-5 w-5" />
          </Button>
        </div>

        {/* Navigation */}
        <nav className="px-4 py-6 space-y-2">
          {navigation.map((item) => {
            const isActive = location.pathname === item.href
            return (
              <Link
                key={item.name}
                to={item.href}
                className={`
                  flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-colors
                  ${isActive 
                    ? 'bg-green-100 text-green-700' 
                    : 'text-gray-700 hover:bg-gray-100'
                  }
                `}
                onClick={() => window.innerWidth < 1024 && onClose()}
              >
                <item.icon className={`mr-3 h-5 w-5 ${
                  isActive ? 'text-green-700' : 'text-gray-400'
                }`} />
                {item.name}
              </Link>
            )
          })}
        </nav>

        {/* User info section */}
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-200">
          <div className="bg-green-50 rounded-lg p-3">
            <div className="text-sm font-medium text-green-800">
              Objectif du mois
            </div>
            <div className="text-xs text-green-600">
              -5kg • 2.3kg perdus
            </div>
            <div className="mt-2 bg-green-200 rounded-full h-2">
              <div 
                className="bg-green-500 h-2 rounded-full" 
                style={{ width: '46%' }}
              />
            </div>
          </div>
        </div>
      </div>
    </>
  )
}

