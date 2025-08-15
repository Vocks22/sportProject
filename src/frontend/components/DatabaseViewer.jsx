import React, { useState, useEffect } from 'react'
import { Database, RefreshCw, Eye, EyeOff } from 'lucide-react'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000'

export function DatabaseViewer() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [showJson, setShowJson] = useState(false)
  
  const fetchDatabaseInfo = async () => {
    setLoading(true)
    setError(null)
    try {
      const apiUrl = API_URL.includes('/api') ? API_URL : `${API_URL}/api`
      const response = await fetch(`${apiUrl}/admin/database-info`)
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const result = await response.json()
      setData(result.database_info)
    } catch (err) {
      console.error('Erreur:', err)
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }
  
  useEffect(() => {
    fetchDatabaseInfo()
  }, [])
  
  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="bg-white rounded-xl shadow-lg p-6">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <Database className="h-6 w-6 text-blue-600" />
            Visualiseur de Base de Données
          </h1>
          <div className="flex gap-2">
            <button
              onClick={() => setShowJson(!showJson)}
              className="px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg flex items-center gap-2"
            >
              {showJson ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              {showJson ? 'Vue Formatée' : 'Vue JSON'}
            </button>
            <button
              onClick={fetchDatabaseInfo}
              disabled={loading}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2 disabled:opacity-50"
            >
              <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
              Rafraîchir
            </button>
          </div>
        </div>
        
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-4">
            Erreur: {error}
          </div>
        )}
        
        {loading && (
          <div className="text-center py-12">
            <RefreshCw className="h-8 w-8 animate-spin mx-auto text-blue-600" />
            <p className="mt-2 text-gray-600">Chargement des données...</p>
          </div>
        )}
        
        {data && !loading && (
          <div>
            {showJson ? (
              <div className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-auto max-h-[600px]">
                <pre className="text-xs font-mono">
                  {JSON.stringify(data, null, 2)}
                </pre>
              </div>
            ) : (
              <div className="space-y-6">
                {/* Programme alimentaire */}
                <div className="border rounded-lg p-4">
                  <h2 className="text-lg font-semibold mb-3 text-gray-900">
                    Programme Alimentaire ({data.diet_program?.count || 0} repas)
                  </h2>
                  <div className="overflow-x-auto">
                    <table className="min-w-full text-sm">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-3 py-2 text-left">ID</th>
                          <th className="px-3 py-2 text-left">Type</th>
                          <th className="px-3 py-2 text-left">Nom</th>
                          <th className="px-3 py-2 text-left">Horaire</th>
                          <th className="px-3 py-2 text-left">Ordre</th>
                          <th className="px-3 py-2 text-left">Aliments</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y">
                        {data.diet_program?.meals?.map((meal) => (
                          <tr key={meal.id} className="hover:bg-gray-50">
                            <td className="px-3 py-2 font-mono">{meal.id}</td>
                            <td className="px-3 py-2 font-mono text-blue-600">{meal.meal_type}</td>
                            <td className="px-3 py-2">{meal.meal_name}</td>
                            <td className="px-3 py-2">{meal.time_slot}</td>
                            <td className="px-3 py-2">{meal.order_index}</td>
                            <td className="px-3 py-2 text-xs">
                              {meal.foods?.length || 0} aliments
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
                
                {/* Trackings récents */}
                <div className="border rounded-lg p-4">
                  <h2 className="text-lg font-semibold mb-3 text-gray-900">
                    Trackings Récents ({data.recent_trackings?.count || 0} entrées)
                  </h2>
                  <div className="overflow-x-auto">
                    <table className="min-w-full text-sm">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-3 py-2 text-left">Date</th>
                          <th className="px-3 py-2 text-left">Meal ID</th>
                          <th className="px-3 py-2 text-left">Type</th>
                          <th className="px-3 py-2 text-left">Nom</th>
                          <th className="px-3 py-2 text-left">Complété</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y">
                        {data.recent_trackings?.trackings?.map((tracking) => (
                          <tr key={tracking.id} className="hover:bg-gray-50">
                            <td className="px-3 py-2">{tracking.date}</td>
                            <td className="px-3 py-2 font-mono">{tracking.meal_id}</td>
                            <td className="px-3 py-2 font-mono text-blue-600">{tracking.meal_type}</td>
                            <td className="px-3 py-2">{tracking.meal_name}</td>
                            <td className="px-3 py-2">
                              <span className={`px-2 py-1 rounded text-xs ${
                                tracking.completed 
                                  ? 'bg-green-100 text-green-800' 
                                  : 'bg-gray-100 text-gray-600'
                              }`}>
                                {tracking.completed ? '✓' : '○'}
                              </span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
                
                {/* Statistiques */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="border rounded-lg p-4">
                    <h3 className="text-sm font-semibold text-gray-600 mb-2">Stats Streak</h3>
                    {data.stats ? (
                      <div className="text-sm space-y-1">
                        <p>Streak actuel: <span className="font-bold">{data.stats.current_streak}</span></p>
                        <p>Record: <span className="font-bold">{data.stats.longest_streak}</span></p>
                        <p>Jours suivis: <span className="font-bold">{data.stats.total_days_tracked}</span></p>
                      </div>
                    ) : (
                      <p className="text-gray-500">Aucune donnée</p>
                    )}
                  </div>
                  
                  <div className="border rounded-lg p-4">
                    <h3 className="text-sm font-semibold text-gray-600 mb-2">Recettes & Ingrédients</h3>
                    <div className="text-sm space-y-1">
                      <p>Recettes: <span className="font-bold">{data.recipes_count}</span></p>
                      <p>Ingrédients: <span className="font-bold">{data.ingredients_count}</span></p>
                    </div>
                  </div>
                  
                  <div className="border rounded-lg p-4">
                    <h3 className="text-sm font-semibold text-gray-600 mb-2">Serveur</h3>
                    <p className="text-xs font-mono">{data.server_time}</p>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}