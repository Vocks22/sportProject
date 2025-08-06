import { useState } from 'react'
import { 
  ShoppingCart, 
  Check, 
  RefreshCw, 
  Mail, 
  Printer,
  ChevronDown,
  ChevronUp
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Checkbox } from '@/components/ui/checkbox'
import { Badge } from '@/components/ui/badge'
import { Progress as ProgressBar } from '@/components/ui/progress'
import { TutorialSystem } from './TutorialSystem'

export function MobileShopping() {
  const [shoppingList, setShoppingList] = useState({
    proteins: [
      { id: 1, name: "Blanc de poulet", quantity: "1080 g", detail: "(6 portions de 180g)", checked: false },
      { id: 2, name: "Escalope de dinde", quantity: "540 g", detail: "(3 portions de 180g)", checked: false },
      { id: 3, name: "Filet de cabillaud", quantity: "800 g", detail: "(4 portions de 200g)", checked: false },
      { id: 4, name: "Filet de sole", quantity: "600 g", detail: "(3 portions de 200g)", checked: false },
      { id: 5, name: "Œufs frais", quantity: "42 unités", detail: "(6 par jour)", checked: false }
    ],
    nuts: [
      { id: 6, name: "Noix de cajou", quantity: "280 g", detail: "(7 portions de 40g)", checked: false },
      { id: 7, name: "Amandes", quantity: "280 g", detail: "(7 portions de 40g)", checked: false }
    ],
    vegetables: [
      { id: 8, name: "Brocolis", quantity: "525 g", detail: "(3.5 portions de 150g)", checked: false },
      { id: 9, name: "Épinards frais", quantity: "525 g", detail: "(3.5 portions de 150g)", checked: false },
      { id: 10, name: "Salade verte (mélange)", quantity: "700 g", detail: "", checked: false },
      { id: 11, name: "Ail", quantity: "1 tête", detail: "", checked: false }
    ],
    fruits: [
      { id: 12, name: "Ananas frais", quantity: "350 g", detail: "(7 portions de 50g)", checked: false },
      { id: 13, name: "Fruits rouges mélangés", quantity: "350 g", detail: "", checked: false },
      { id: 14, name: "Pamplemousse", quantity: "7 unités", detail: "", checked: false }
    ],
    dairy: [
      { id: 15, name: "Lait d'amande", quantity: "1.4 L", detail: "(200ml par jour)", checked: false }
    ],
    cereals: [
      { id: 16, name: "Flocons d'avoine", quantity: "420 g", detail: "(7 portions de 60g)", checked: false }
    ],
    condiments: [
      { id: 17, name: "Huile d'olive extra vierge", quantity: "70 ml", detail: "", checked: false },
      { id: 18, name: "Sel de mer", quantity: "1 paquet", detail: "", checked: false },
      { id: 19, name: "Herbes de Provence", quantity: "1 pot", detail: "", checked: false },
      { id: 20, name: "Paprika", quantity: "1 pot", detail: "", checked: false },
      { id: 21, name: "Chocolat noir 70%", quantity: "1 tablette", detail: "", checked: false }
    ],
    supplements: [
      { id: 22, name: "Multi-vitamines", quantity: "1 boîte", detail: "", checked: false },
      { id: 23, name: "CLA 3000mg", quantity: "1 boîte", detail: "", checked: false }
    ]
  })

  const [expandedCategories, setExpandedCategories] = useState({
    proteins: true,
    nuts: false,
    vegetables: false,
    fruits: false,
    dairy: false,
    cereals: false,
    condiments: false,
    supplements: false
  })

  const categories = [
    { key: 'proteins', name: 'PROTÉINES', emoji: '🥩', color: 'bg-red-500' },
    { key: 'nuts', name: 'OLÉAGINEUX', emoji: '🥜', color: 'bg-orange-500' },
    { key: 'vegetables', name: 'LÉGUMES', emoji: '🥬', color: 'bg-green-500' },
    { key: 'fruits', name: 'FRUITS', emoji: '🍓', color: 'bg-pink-500' },
    { key: 'dairy', name: 'PRODUITS LAITIERS', emoji: '🥛', color: 'bg-blue-500' },
    { key: 'cereals', name: 'CÉRÉALES', emoji: '🌾', color: 'bg-yellow-500' },
    { key: 'condiments', name: 'CONDIMENTS & ÉPICES', emoji: '🫒', color: 'bg-purple-500' },
    { key: 'supplements', name: 'COMPLÉMENTS', emoji: '💊', color: 'bg-indigo-500' }
  ]

  const toggleItem = (categoryKey, itemId) => {
    setShoppingList(prev => ({
      ...prev,
      [categoryKey]: prev[categoryKey].map(item =>
        item.id === itemId ? { ...item, checked: !item.checked } : item
      )
    }))
  }

  const toggleCategory = (categoryKey) => {
    setExpandedCategories(prev => ({
      ...prev,
      [categoryKey]: !prev[categoryKey]
    }))
  }

  const checkAllItems = () => {
    setShoppingList(prev => {
      const newList = {}
      Object.keys(prev).forEach(categoryKey => {
        newList[categoryKey] = prev[categoryKey].map(item => ({ ...item, checked: true }))
      })
      return newList
    })
  }

  const regenerateList = () => {
    // Réinitialiser tous les items
    setShoppingList(prev => {
      const newList = {}
      Object.keys(prev).forEach(categoryKey => {
        newList[categoryKey] = prev[categoryKey].map(item => ({ ...item, checked: false }))
      })
      return newList
    })
    
    // Afficher un message de confirmation
    alert("Liste de courses régénérée ! Tous les articles ont été décochés.")
  }

  // Calculer les statistiques
  const totalItems = Object.values(shoppingList).flat().length
  const checkedItems = Object.values(shoppingList).flat().filter(item => item.checked).length
  const progressPercentage = totalItems > 0 ? (checkedItems / totalItems) * 100 : 0

  const getCategoryStats = (categoryKey) => {
    const items = shoppingList[categoryKey]
    const checked = items.filter(item => item.checked).length
    return { checked, total: items.length }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <TutorialSystem currentPage="shopping" />
      
      <div className="p-4 space-y-4">
        {/* Header */}
        <Card className="shopping-header">
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="text-lg flex items-center">
                  <ShoppingCart className="h-5 w-5 mr-2 text-teal-500" />
                  Liste de Courses
                </CardTitle>
                <p className="text-sm text-gray-600">Semaine du 6-12 Août 2025</p>
              </div>
              <div className="flex space-x-2">
                <Button variant="outline" size="sm">
                  <Mail className="h-4 w-4" />
                </Button>
                <Button variant="outline" size="sm">
                  <Printer className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="shopping-progress space-y-3">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-sm text-gray-600">Générée le 3 août 2025</div>
                  <div className="text-sm text-gray-600">Budget estimé: 85-95€</div>
                </div>
                <Badge variant="outline" className="text-lg px-3 py-1">
                  {checkedItems}/{totalItems}
                </Badge>
              </div>
              
              <ProgressBar value={progressPercentage} className="h-3" />
              
              <div className="flex justify-between items-center">
                <span className="text-sm font-medium">
                  {Math.round(progressPercentage)}% terminé
                </span>
                <div className="flex space-x-2">
                  <Button 
                    variant="outline" 
                    size="sm" 
                    onClick={checkAllItems}
                    className="text-xs"
                  >
                    <Check className="h-3 w-3 mr-1" />
                    Tout cocher
                  </Button>
                  <Button 
                    variant="outline" 
                    size="sm" 
                    onClick={regenerateList}
                    className="text-xs regenerate-btn"
                  >
                    <RefreshCw className="h-3 w-3 mr-1" />
                    Régénérer
                  </Button>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Catégories */}
        <div className="shopping-categories space-y-3">
          {categories.map((category) => {
            const stats = getCategoryStats(category.key)
            const isExpanded = expandedCategories[category.key]
            
            return (
              <Card key={category.key}>
                <CardHeader 
                  className="pb-2 cursor-pointer"
                  onClick={() => toggleCategory(category.key)}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className={`w-8 h-8 ${category.color} rounded-lg flex items-center justify-center`}>
                        <span className="text-white text-sm">{category.emoji}</span>
                      </div>
                      <div>
                        <h3 className="font-semibold text-gray-900">{category.name}</h3>
                        <p className="text-sm text-gray-500">{stats.checked}/{stats.total} articles</p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Badge variant="outline">
                        {stats.checked}/{stats.total}
                      </Badge>
                      {isExpanded ? (
                        <ChevronUp className="h-4 w-4 text-gray-400" />
                      ) : (
                        <ChevronDown className="h-4 w-4 text-gray-400" />
                      )}
                    </div>
                  </div>
                </CardHeader>
                
                {isExpanded && (
                  <CardContent className="pt-0 item-quantities">
                    <div className="space-y-3">
                      {shoppingList[category.key].map((item) => (
                        <div 
                          key={item.id}
                          className={`flex items-center space-x-3 p-3 rounded-lg border transition-all ${
                            item.checked 
                              ? 'bg-green-50 border-green-200' 
                              : 'bg-white border-gray-200'
                          }`}
                        >
                          <Checkbox
                            checked={item.checked}
                            onCheckedChange={() => toggleItem(category.key, item.id)}
                            className="flex-shrink-0"
                          />
                          <div className="flex-1 min-w-0">
                            <div className={`font-medium ${
                              item.checked ? 'line-through text-gray-500' : 'text-gray-900'
                            }`}>
                              {item.name}
                            </div>
                            <div className="text-sm text-gray-600">
                              {item.quantity}
                              {item.detail && (
                                <span className="text-gray-500 ml-1">{item.detail}</span>
                              )}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                )}
              </Card>
            )
          })}
        </div>

        {/* Résumé */}
        <Card className="budget-estimate">
          <CardContent className="p-4">
            <div className="grid grid-cols-3 gap-4 text-center">
              <div>
                <div className="text-2xl font-bold text-gray-900">{totalItems}</div>
                <div className="text-sm text-gray-600">Articles au total</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-green-600">{checkedItems}</div>
                <div className="text-sm text-gray-600">Articles cochés</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-blue-600">85-95€</div>
                <div className="text-sm text-gray-600">Budget estimé</div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

