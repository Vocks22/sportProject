import React from 'react'
import { Menu, User, Bell, LogOut } from 'lucide-react'
import { Button } from './ui/button'

export function Header({ sidebarOpen, setSidebarOpen, user, onLogout }) {
  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-white border-b border-gray-200 h-16">
      <div className="flex items-center justify-between h-full px-4">
        {/* Left side */}
        <div className="flex items-center space-x-4">
          {/* Bouton menu toujours visible */}
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setSidebarOpen(!sidebarOpen)}
          >
            <Menu className="h-5 w-5" />
          </Button>
          
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-green-500 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">DT</span>
            </div>
            <h1 className="text-xl font-bold text-gray-900 hidden sm:block">
              DietTracker
            </h1>
          </div>
        </div>

        {/* Right side */}
        <div className="flex items-center space-x-4">
          <Button variant="ghost" size="sm">
            <Bell className="h-5 w-5" />
          </Button>
          
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center">
              <User className="h-4 w-4 text-gray-600" />
            </div>
            <span className="text-sm font-medium text-gray-700 hidden sm:block">
              {user?.username || 'Utilisateur'}
            </span>
          </div>
          
          {/* Bouton de déconnexion */}
          <Button 
            variant="ghost" 
            size="sm"
            onClick={onLogout}
            title="Se déconnecter"
          >
            <LogOut className="h-5 w-5 text-red-500" />
          </Button>
        </div>
      </div>
    </header>
  )
}

