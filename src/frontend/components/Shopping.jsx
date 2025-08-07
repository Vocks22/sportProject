import React, { useState, useEffect } from 'react'
import { 
  ShoppingCart, 
  Check, 
  Plus, 
  Printer, 
  Mail, 
  RefreshCw,
  Calendar,
  Wifi,
  WifiOff,
  Download,
  Clock,
  AlertCircle,
  BarChart3,
  History,
  FileText,
  Share2
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Checkbox } from '@/components/ui/checkbox'
import { Badge } from '@/components/ui/badge'
import { Progress as ProgressBar } from '@/components/ui/progress'
import useShoppingList, { useNetworkStatus } from '@/hooks/useShoppingList'
import { useNextWeekShopping } from '@/hooks/useISOWeek'

export function Shopping() {
  // État et hooks
  const {
    currentList,
    isLoading,
    error,
    offlineMode,
    pendingActionsCount,
    toggleItemStatus,
    bulkToggleItems,
    regenerateList,
    clearError,
    completionStats,
    itemsByCategory,
    // Nouvelles fonctionnalités US1.5
    getListStatistics,
    exportList,
    getListHistory
  } = useShoppingList()
  
  useNetworkStatus() // Active la détection réseau
  
  // Hook pour la gestion de "semaine prochaine"
  const {
    nextWeekInfo,
    nextWeekDays,
    displayText,
    isNextWeekFromToday,
    goBackToCurrentWeek
  } = useNextWeekShopping()
  
  // États pour les nouvelles fonctionnalités US1.5
  const [showExportModal, setShowExportModal] = useState(false)
  const [showStatsModal, setShowStatsModal] = useState(false)
  const [showHistoryModal, setShowHistoryModal] = useState(false)
  const [statistics, setStatistics] = useState(null)
  const [history, setHistory] = useState(null)
  const [isExporting, setIsExporting] = useState(false)
  
  // État pour la vue "semaine prochaine" (US1.6)
  const [showNextWeekView, setShowNextWeekView] = useState(false)
  
  // Fallback vers les données de test si pas de liste actuelle
  const [fallbackList, setFallbackList] = useState({
    id: 1,
    weekStart: showNextWeekView ? nextWeekInfo.mondayISO : "2025-08-06",
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

  // Utiliser la liste actuelle ou le fallback
  const activeList = currentList || fallbackList
  const activeItemsByCategory = currentList ? itemsByCategory : getItemsByCategoryFallback(fallbackList.items)
  const activeCompletionStats = currentList ? completionStats : getFallbackStats(fallbackList.items)
  
  // Fonctions helpers pour le fallback
  function getItemsByCategoryFallback(items) {
    const categorized = {}
    items.forEach(item => {
      const category = item.category || 'other'
      if (!categorized[category]) categorized[category] = []
      categorized[category].push(item)
    })
    return categorized
  }
  
  function getFallbackStats(items) {
    const total = items.length
    const completed = items.filter(item => item.checked).length
    return {
      total,
      completed,
      percentage: total > 0 ? Math.round((completed / total) * 100) : 0
    }
  }

  const handleToggleItem = async (itemId) => {
    if (currentList) {
      const currentStatus = currentList.items.find(item => 
        String(item.id) === String(itemId)
      )?.checked || false
      await toggleItemStatus(itemId, !currentStatus)
    } else {
      // Fallback pour mode démo
      setFallbackList(prev => ({
        ...prev,
        items: prev.items.map(item =>
          item.id === itemId ? { ...item, checked: !item.checked } : item
        )
      }))
    }
  }

  const handleToggleAll = async () => {
    const items = activeList.items || []
    const allChecked = items.every(item => item.checked)
    
    if (currentList) {
      const updates = items.map(item => ({
        itemId: String(item.id),
        checked: !allChecked
      }))
      await bulkToggleItems(updates)
    } else {
      // Fallback pour mode démo
      setFallbackList(prev => ({
        ...prev,
        items: prev.items.map(item => ({ ...item, checked: !allChecked }))
      }))
    }
  }

  const handleRegenerate = async () => {
    if (currentList) {
      await regenerateList(true)
    }
  }

  const handleExport = async (format) => {
    if (format === 'print') {
      window.print()
    } else if (format === 'email') {
      const subject = encodeURIComponent(`Liste de courses - Semaine du ${activeList.week_start}`)
      const body = encodeURIComponent(generateEmailBody())
      window.location.href = `mailto:?subject=${subject}&body=${body}`
    } else {
      // Nouvel export via API (US1.5)
      setIsExporting(true)
      try {
        const result = await exportList(format, {
          includeMetadata: true,
          includeCheckedItems: true
        })
        
        if (result?.success) {
          // Déclencher le téléchargement
          const blob = new Blob([JSON.stringify(result.export_data, null, 2)], {
            type: result.download_info?.mime_type || 'application/json'
          })
          const url = URL.createObjectURL(blob)
          const a = document.createElement('a')
          a.href = url
          a.download = result.download_info?.filename || `liste_courses_${Date.now()}.${format}`
          document.body.appendChild(a)
          a.click()
          URL.revokeObjectURL(url)
          document.body.removeChild(a)
        }
      } catch (error) {
        console.error('Erreur lors de l\'export:', error)
      } finally {
        setIsExporting(false)
      }
    }
  }
  
  const handleShowStatistics = async () => {
    if (!currentList) return
    
    const stats = await getListStatistics()
    if (stats) {
      setStatistics(stats)
      setShowStatsModal(true)
    }
  }
  
  const handleShowHistory = async () => {
    if (!currentList) return
    
    const historyData = await getListHistory(1, 50)
    if (historyData) {
      setHistory(historyData)
      setShowHistoryModal(true)
    }
  }

  const generateEmailBody = () => {
    let body = `Liste de courses - Semaine du ${activeList.week_start}\n\n`
    
    Object.entries(activeItemsByCategory).forEach(([categoryKey, items]) => {
      const category = categories.find(cat => cat.key === categoryKey)
      if (items.length > 0) {
        body += `${category?.label || categoryKey.toUpperCase()}\n`
        body += '========================\n'
        items.forEach(item => {
          const status = item.checked ? '✓' : '☐'
          body += `${status} ${item.name} - ${item.quantity} ${item.unit}\n`
          if (item.note) body += `   (${item.note})\n`
        })
        body += '\n'
      }
    })
    
    return body
  }

  const estimatedBudget = activeList.estimated_budget 
    ? `${activeList.estimated_budget}€`
    : "85-95€"

  return (
    <div className="space-y-6">
      {/* Header avec indicateurs de statut */}
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center space-x-3">
            <h1 className="text-3xl font-bold text-gray-900">Liste de Courses</h1>
            
            {/* Indicateurs de statut */}
            <div className="flex items-center space-x-2">
              {offlineMode && (
                <Badge variant="destructive" className="flex items-center space-x-1">
                  <WifiOff className="h-3 w-3" />
                  <span>Hors ligne</span>
                </Badge>
              )}
              
              {pendingActionsCount > 0 && (
                <Badge variant="secondary" className="flex items-center space-x-1">
                  <Clock className="h-3 w-3" />
                  <span>{pendingActionsCount} en attente</span>
                </Badge>
              )}
              
              {!offlineMode && (
                <Badge variant="outline" className="flex items-center space-x-1">
                  <Wifi className="h-3 w-3" />
                  <span>En ligne</span>
                </Badge>
              )}
            </div>
          </div>
          
          <p className="text-gray-600">
            {showNextWeekView 
              ? displayText
              : activeList.week_start 
              ? `Semaine du ${new Date(activeList.week_start).toLocaleDateString('fr-FR')}`
              : 'Semaine du 6-12 Août 2025'
            }
            {showNextWeekView && (
              <span className="ml-2 text-blue-600 font-medium">
                (Planification avancée)
              </span>
            )}
          </p>
        </div>
        
        <div className="flex items-center space-x-2">
          {/* Bouton pour basculer vers semaine prochaine (US1.6) */}
          <Button 
            variant={showNextWeekView ? "default" : "outline"} 
            size="sm"
            onClick={() => setShowNextWeekView(!showNextWeekView)}
            title={showNextWeekView ? "Retour à la semaine courante" : "Voir la semaine prochaine"}
          >
            <Calendar className="h-4 w-4 mr-2" />
            {showNextWeekView ? "Semaine courante" : "Semaine prochaine"}
          </Button>
          
          <Button 
            variant="outline" 
            size="sm"
            onClick={() => handleExport('email')}
          >
            <Mail className="h-4 w-4 mr-2" />
            Envoyer
          </Button>
          <Button 
            variant="outline" 
            size="sm"
            onClick={() => handleExport('print')}
          >
            <Printer className="h-4 w-4 mr-2" />
            Imprimer
          </Button>
          
          {/* Nouveaux boutons US1.5 */}
          {currentList && (
            <>
              <Button 
                variant="outline" 
                size="sm"
                onClick={handleShowStatistics}
                disabled={isLoading}
              >
                <BarChart3 className="h-4 w-4 mr-2" />
                Stats
              </Button>
              <Button 
                variant="outline" 
                size="sm"
                onClick={handleShowHistory}
                disabled={isLoading}
              >
                <History className="h-4 w-4 mr-2" />
                Historique
              </Button>
              <Button 
                variant="outline" 
                size="sm"
                onClick={() => handleExport('json')}
                disabled={isExporting}
              >
                <Download className={`h-4 w-4 mr-2 ${isExporting ? 'animate-spin' : ''}`} />
                Export
              </Button>
            </>
          )}
        </div>
      </div>

      {/* Message d'erreur */}
      {error && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <AlertCircle className="h-5 w-5 text-red-600" />
                <span className="text-red-800">{error}</span>
              </div>
              <Button 
                variant="ghost" 
                size="sm" 
                onClick={clearError}
                className="text-red-600"
              >
                Fermer
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Progress Card */}
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-lg font-semibold">Progression des courses</h3>
              <p className="text-sm text-gray-600">
                {showNextWeekView 
                  ? `Liste pour ${nextWeekInfo.displayRange} • Budget estimé: ${estimatedBudget}`
                  : activeList.generated_date 
                  ? `Générée le ${new Date(activeList.generated_date).toLocaleDateString('fr-FR')} • Budget estimé: ${estimatedBudget}`
                  : `Générée le 3 août 2025 • Budget estimé: ${estimatedBudget}`
                }
              </p>
            </div>
            <Badge variant="outline" className="text-lg px-3 py-1">
              {activeCompletionStats.completed}/{activeCompletionStats.total}
            </Badge>
          </div>
          
          <ProgressBar value={activeCompletionStats.percentage} className="h-3 mb-4" />
          
          <div className="flex items-center justify-between">
            <div className="flex space-x-4">
              <Button
                variant="outline"
                size="sm"
                onClick={handleToggleAll}
                disabled={isLoading || showNextWeekView}
                title={showNextWeekView ? "Non disponible en mode planification" : ""}
              >
                <Check className="h-4 w-4 mr-2" />
                {activeCompletionStats.completed === activeCompletionStats.total ? 'Tout décocher' : 'Tout cocher'}
              </Button>
              <Button 
                variant="outline" 
                size="sm"
                onClick={handleRegenerate}
                disabled={isLoading || !currentList || showNextWeekView}
                title={showNextWeekView ? "Non disponible en mode planification" : ""}
              >
                <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
                Régénérer
              </Button>
              
              {showNextWeekView && (
                <Button 
                  variant="default" 
                  size="sm"
                  onClick={() => {
                    // Générer la liste pour la semaine prochaine
                    console.log('Génération liste pour semaine prochaine:', nextWeekInfo.mondayISO)
                  }}
                >
                  <Plus className="h-4 w-4 mr-2" />
                  Générer liste
                </Button>
              )}
            </div>
            <div className="text-sm text-gray-600">
              {showNextWeekView 
                ? `Planification pour ${nextWeekInfo.displayRange.split(' ').slice(-2).join(' ')}`
                : `${activeCompletionStats.percentage}% terminé`
              }
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Shopping List */}
      <div className="space-y-4">
        {categories.map((category) => {
          const categoryItems = activeItemsByCategory[category.key] || []
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
                    className={`flex items-center space-x-3 p-3 rounded-lg border transition-all duration-200 ${
                      item.checked 
                        ? 'bg-green-50 border-green-200 opacity-75' 
                        : 'bg-white border-gray-200 hover:bg-gray-50 hover:border-gray-300'
                    }`}
                  >
                    <Checkbox
                      checked={item.checked}
                      onChange={() => handleToggleItem(item.id)}
                      className="h-5 w-5"
                      disabled={isLoading || showNextWeekView}
                      title={showNextWeekView ? "Mode planification - cocher non disponible" : ""}
                    />
                    <div className="flex-1">
                      <div className={`font-medium transition-all duration-200 ${
                        item.checked 
                          ? 'line-through text-gray-500' 
                          : 'text-gray-900'
                      }`}>
                        {item.name}
                      </div>
                      <div className="text-sm text-gray-600">
                        {item.quantity} {item.unit}
                        {item.note && (
                          <span className="ml-2 text-gray-500">({item.note})</span>
                        )}
                        {item.conversion_applied && (
                          <span className="ml-2 text-blue-600 text-xs">
                            • {item.conversion_applied}
                          </span>
                        )}
                      </div>
                    </div>
                    
                    {/* Indicateurs d'état */}
                    <div className="flex items-center space-x-1">
                      {showNextWeekView && (
                        <Calendar className="h-4 w-4 text-blue-500" title="Article planifié pour la semaine prochaine" />
                      )}
                      {!showNextWeekView && offlineMode && item.checked && (
                        <Clock className="h-4 w-4 text-orange-500" title="Modification en attente de synchronisation" />
                      )}
                      {!showNextWeekView && item.checked && (
                        <Check className="h-5 w-5 text-green-600" />
                      )}
                    </div>
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
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 text-center">
            <div>
              <div className="text-2xl font-bold text-gray-900">{activeCompletionStats.total}</div>
              <div className="text-sm text-gray-600">Articles au total</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-green-600">{activeCompletionStats.completed}</div>
              <div className="text-sm text-gray-600">Articles cochés</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-blue-600">{estimatedBudget}</div>
              <div className="text-sm text-gray-600">Budget estimé</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-orange-600">
                {Object.keys(activeItemsByCategory).length}
              </div>
              <div className="text-sm text-gray-600">Rayons magasin</div>
            </div>
          </div>
          
          {/* Informations additionnelles pour l'état de synchronisation */}
          {(offlineMode || pendingActionsCount > 0) && (
            <div className="mt-4 pt-4 border-t border-gray-200">
              <div className="flex items-center justify-center space-x-4 text-sm">
                {offlineMode && (
                  <div className="flex items-center space-x-1 text-orange-600">
                    <WifiOff className="h-4 w-4" />
                    <span>Mode hors ligne actif</span>
                  </div>
                )}
                {pendingActionsCount > 0 && (
                  <div className="flex items-center space-x-1 text-blue-600">
                    <Clock className="h-4 w-4" />
                    <span>{pendingActionsCount} modification(s) en attente de synchronisation</span>
                  </div>
                )}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Modale de statistiques (US1.5) */}
      {showStatsModal && statistics && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-4xl w-full max-h-[90vh] overflow-y-auto m-4">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-2xl font-bold">Statistiques de la liste</h2>
              <Button
                variant="ghost"
                onClick={() => setShowStatsModal(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                ×
              </Button>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
              <Card>
                <CardContent className="p-4 text-center">
                  <div className="text-2xl font-bold text-blue-600">
                    {statistics.overview?.total_items || 0}
                  </div>
                  <div className="text-sm text-gray-600">Articles total</div>
                </CardContent>
              </Card>
              
              <Card>
                <CardContent className="p-4 text-center">
                  <div className="text-2xl font-bold text-green-600">
                    {statistics.overview?.completed_items || 0}
                  </div>
                  <div className="text-sm text-gray-600">Articles cochés</div>
                </CardContent>
              </Card>
              
              <Card>
                <CardContent className="p-4 text-center">
                  <div className="text-2xl font-bold text-orange-600">
                    {statistics.overview?.estimated_shopping_time_minutes || 0}min
                  </div>
                  <div className="text-sm text-gray-600">Temps estimé</div>
                </CardContent>
              </Card>
              
              <Card>
                <CardContent className="p-4 text-center">
                  <div className="text-2xl font-bold text-purple-600">
                    {statistics.overview?.estimated_budget || 0}€
                  </div>
                  <div className="text-sm text-gray-600">Budget estimé</div>
                </CardContent>
              </Card>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Répartition par catégorie</CardTitle>
                </CardHeader>
                <CardContent>
                  {statistics.by_category && Object.entries(statistics.by_category).map(([category, data]) => (
                    <div key={category} className="flex justify-between items-center py-2 border-b">
                      <span className="capitalize">{category}</span>
                      <div className="text-right">
                        <div>{data.completed}/{data.total}</div>
                        <div className="text-sm text-gray-500">
                          {data.completion_percentage || 0}%
                        </div>
                      </div>
                    </div>
                  ))}
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Métriques d'efficacité</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span>Tendance de completion:</span>
                      <Badge variant={
                        statistics.efficiency_metrics?.completion_rate_trend === 'improving' ? 'default' :
                        statistics.efficiency_metrics?.completion_rate_trend === 'declining' ? 'destructive' : 'secondary'
                      }>
                        {statistics.efficiency_metrics?.completion_rate_trend || 'unknown'}
                      </Badge>
                    </div>
                    <div className="flex justify-between">
                      <span>Articles économisés:</span>
                      <span>{statistics.efficiency_metrics?.aggregation_reduction || 0}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Coût par article:</span>
                      <span>{statistics.efficiency_metrics?.cost_per_item || 0}€</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      )}

      {/* Modale d'historique (US1.5) */}
      {showHistoryModal && history && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-4xl w-full max-h-[90vh] overflow-y-auto m-4">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-2xl font-bold">Historique des modifications</h2>
              <Button
                variant="ghost"
                onClick={() => setShowHistoryModal(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                ×
              </Button>
            </div>
            
            <div className="space-y-3">
              {history.history && history.history.length > 0 ? (
                history.history.map((entry) => (
                  <Card key={entry.id} className="p-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <Badge variant={
                          entry.action === 'item_checked' ? 'default' :
                          entry.action === 'item_unchecked' ? 'secondary' :
                          entry.action === 'regenerated' ? 'outline' : 'destructive'
                        }>
                          {entry.action}
                        </Badge>
                        <span className="text-sm">
                          {entry.item_id && `Article: ${entry.item_id}`}
                        </span>
                      </div>
                      <span className="text-sm text-gray-500">
                        {new Date(entry.timestamp).toLocaleString('fr-FR')}
                      </span>
                    </div>
                    {entry.metadata && Object.keys(entry.metadata).length > 0 && (
                      <div className="mt-2 text-sm text-gray-600">
                        Détails: {JSON.stringify(entry.metadata, null, 2)}
                      </div>
                    )}
                  </Card>
                ))
              ) : (
                <div className="text-center text-gray-500 py-8">
                  Aucun historique disponible
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default Shopping

