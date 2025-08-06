import { useState } from 'react'
import { 
  ShoppingCart, 
  Check, 
  Plus, 
  Printer, 
  Mail, 
  RefreshCw,
  Calendar
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Checkbox } from '@/components/ui/checkbox'
import { Badge } from '@/components/ui/badge'
import { Progress as ProgressBar } from '@/components/ui/progress'

export function Shopping() {
  const [shoppingList, setShoppingList] = useState({
    id: 1,
    weekStart: "2025-08-06",
    generatedDate: "2025-08-03",
    isCompleted: false,
    items: [
      // Protéines
      { id: 1, name: "Blanc de poulet", quantity: 1080, unit: "g", category: "protein", checked: false, note: "6 portions de 180g" },
      { id: 2, name: "Escalope de dinde", quantity: 540, unit: "g", category: "protein", checked: false, note: "3 portions de 180g" },
      { id: 3, name: "Filet de cabillaud", quantity: 800, unit: "g", category: "protein", checked: false, note: "4 portions de 200g" },
      { id: 4, name: "Filet de sole", quantity: 600, unit: "g", category: "protein", checked: false, note: "3 portions de 200g" },
      { id: 5, name: "Œufs frais", quantity: 42, unit: "unités", category: "protein", checked: false, note: "6 par jour" },
      
      // Oléagineux
      { id: 6, name: "Noix de cajou", quantity: 280, unit: "g", category: "nuts", checked: false, note: "7 portions de 40g" },
      { id: 7, name: "Amandes", quantity: 280, unit: "g", category: "nuts", checked: false, note: "7 portions de 40g" },
      
      // Légumes
      { id: 8, name: "Brocolis", quantity: 525, unit: "g", category: "vegetable", checked: false, note: "3.5 portions de 150g" },
      { id: 9, name: "Épinards frais", quantity: 525, unit: "g", category: "vegetable", checked: false, note: "3.5 portions de 150g" },
      { id: 10, name: "Salade verte (mélange)", quantity: 700, unit: "g", category: "vegetable", checked: false, note: "" },
      { id: 11, name: "Ail", quantity: 1, unit: "tête", category: "vegetable", checked: false, note: "" },
      
      // Fruits
      { id: 12, name: "Ananas frais", quantity: 350, unit: "g", category: "fruit", checked: false, note: "7 portions de 50g" },
      { id: 13, name: "Fruits rouges mélangés", quantity: 350, unit: "g", category: "fruit", checked: false, note: "" },
      { id: 14, name: "Pamplemousse", quantity: 7, unit: "unités", category: "fruit", checked: false, note: "" },
      
      // Produits laitiers
      { id: 15, name: "Lait d'amande", quantity: 1.4, unit: "L", category: "dairy", checked: false, note: "200ml par jour" },
      
      // Céréales
      { id: 16, name: "Flocons d'avoine", quantity: 420, unit: "g", category: "grain", checked: false, note: "7 portions de 60g" },
      
      // Condiments
      { id: 17, name: "Huile d'olive extra vierge", quantity: 70, unit: "ml", category: "condiment", checked: false, note: "" },
      { id: 18, name: "Sel de mer", quantity: 1, unit: "paquet", category: "condiment", checked: false, note: "" },
      { id: 19, name: "Herbes de Provence", quantity: 1, unit: "pot", category: "condiment", checked: false, note: "" },
      { id: 20, name: "Paprika", quantity: 1, unit: "pot", category: "condiment", checked: false, note: "" },
      { id: 21, name: "Chocolat noir 70%", quantity: 1, unit: "tablette", category: "condiment", checked: false, note: "" },
      
      // Compléments
      { id: 22, name: "Multi-vitamines", quantity: 1, unit: "boîte", category: "supplement", checked: false, note: "" },
      { id: 23, name: "CLA 3000mg", quantity: 1, unit: "boîte", category: "supplement", checked: false, note: "" }
    ]
  })

  const categories = [
    { key: 'protein', label: '🥩 PROTÉINES', icon: '🥩' },
    { key: 'nuts', label: '🥜 OLÉAGINEUX', icon: '🥜' },
    { key: 'vegetable', label: '🥬 LÉGUMES', icon: '🥬' },
    { key: 'fruit', label: '🍓 FRUITS', icon: '🍓' },
    { key: 'dairy', label: '🥛 PRODUITS LAITIERS', icon: '🥛' },
    { key: 'grain', label: '🌾 CÉRÉALES', icon: '🌾' },
    { key: 'condiment', label: '🫒 CONDIMENTS & ÉPICES', icon: '🫒' },
    { key: 'supplement', label: '💊 COMPLÉMENTS', icon: '💊' }
  ]

  const toggleItem = (itemId) => {
    setShoppingList(prev => ({
      ...prev,
      items: prev.items.map(item =>
        item.id === itemId ? { ...item, checked: !item.checked } : item
      )
    }))
  }

  const toggleAll = () => {
    const allChecked = shoppingList.items.every(item => item.checked)
    setShoppingList(prev => ({
      ...prev,
      items: prev.items.map(item => ({ ...item, checked: !allChecked }))
    }))
  }

  const checkedCount = shoppingList.items.filter(item => item.checked).length
  const totalCount = shoppingList.items.length
  const progressPercentage = (checkedCount / totalCount) * 100

  const getItemsByCategory = (categoryKey) => {
    return shoppingList.items.filter(item => item.category === categoryKey)
  }

  const estimatedBudget = "85-95€"

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Liste de Courses</h1>
          <p className="text-gray-600">Semaine du 6-12 Août 2025</p>
        </div>
        <div className="flex items-center space-x-2">
          <Button variant="outline" size="sm">
            <Mail className="h-4 w-4 mr-2" />
            Envoyer
          </Button>
          <Button variant="outline" size="sm">
            <Printer className="h-4 w-4 mr-2" />
            Imprimer
          </Button>
        </div>
      </div>

      {/* Progress Card */}
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-lg font-semibold">Progression des courses</h3>
              <p className="text-sm text-gray-600">
                Générée le 3 août 2025 • Budget estimé: {estimatedBudget}
              </p>
            </div>
            <Badge variant="outline" className="text-lg px-3 py-1">
              {checkedCount}/{totalCount}
            </Badge>
          </div>
          
          <ProgressBar value={progressPercentage} className="h-3 mb-4" />
          
          <div className="flex items-center justify-between">
            <div className="flex space-x-4">
              <Button
                variant="outline"
                size="sm"
                onClick={toggleAll}
              >
                <Check className="h-4 w-4 mr-2" />
                {checkedCount === totalCount ? 'Tout décocher' : 'Tout cocher'}
              </Button>
              <Button variant="outline" size="sm">
                <RefreshCw className="h-4 w-4 mr-2" />
                Régénérer
              </Button>
            </div>
            <div className="text-sm text-gray-600">
              {Math.round(progressPercentage)}% terminé
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Shopping List */}
      <div className="space-y-4">
        {categories.map((category) => {
          const categoryItems = getItemsByCategory(category.key)
          if (categoryItems.length === 0) return null

          const categoryChecked = categoryItems.filter(item => item.checked).length
          const categoryTotal = categoryItems.length

          return (
            <Card key={category.key}>
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-lg flex items-center space-x-2">
                    <span>{category.icon}</span>
                    <span>{category.label}</span>
                  </CardTitle>
                  <Badge variant="outline">
                    {categoryChecked}/{categoryTotal}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent className="space-y-3">
                {categoryItems.map((item) => (
                  <div
                    key={item.id}
                    className={`flex items-center space-x-3 p-3 rounded-lg border transition-colors ${
                      item.checked 
                        ? 'bg-green-50 border-green-200' 
                        : 'bg-white border-gray-200 hover:bg-gray-50'
                    }`}
                  >
                    <Checkbox
                      checked={item.checked}
                      onCheckedChange={() => toggleItem(item.id)}
                      className="h-5 w-5"
                    />
                    <div className="flex-1">
                      <div className={`font-medium ${
                        item.checked ? 'line-through text-gray-500' : 'text-gray-900'
                      }`}>
                        {item.name}
                      </div>
                      <div className="text-sm text-gray-600">
                        {item.quantity} {item.unit}
                        {item.note && (
                          <span className="ml-2 text-gray-500">({item.note})</span>
                        )}
                      </div>
                    </div>
                    {item.checked && (
                      <Check className="h-5 w-5 text-green-600" />
                    )}
                  </div>
                ))}
              </CardContent>
            </Card>
          )
        })}
      </div>

      {/* Summary */}
      <Card>
        <CardContent className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-center">
            <div>
              <div className="text-2xl font-bold text-gray-900">{totalCount}</div>
              <div className="text-sm text-gray-600">Articles au total</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-green-600">{checkedCount}</div>
              <div className="text-sm text-gray-600">Articles cochés</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-blue-600">{estimatedBudget}</div>
              <div className="text-sm text-gray-600">Budget estimé</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

