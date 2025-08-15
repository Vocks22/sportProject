import React, { useState, useEffect } from 'react'
import { Activity, RefreshCw, Unlink, Check, AlertCircle, Weight } from 'lucide-react'
import { apiGet, apiPost } from '../utils/api'

export function WithingsConnection() {
  const [status, setStatus] = useState(null)
  const [loading, setLoading] = useState(true)
  const [syncing, setSyncing] = useState(false)
  const [measurements, setMeasurements] = useState([])
  const [error, setError] = useState(null)

  useEffect(() => {
    checkConnectionStatus()
  }, [])

  const checkConnectionStatus = async () => {
    try {
      const response = await apiGet('/api/withings/status')
      if (response) {
        const data = await response.json()
        if (data.success) {
          setStatus(data)
        }
      }
    } catch (err) {
      console.error('Erreur vérification statut:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleConnect = async () => {
    try {
      setLoading(true)
      setError(null)
      
      const response = await apiGet('/api/withings/auth')
      if (response) {
        const data = await response.json()
        if (data.success && data.auth_url) {
          // Ouvrir l'URL d'autorisation dans une nouvelle fenêtre
          const authWindow = window.open(data.auth_url, 'withings-auth', 'width=600,height=700')
          
          // Écouter le message de callback
          window.addEventListener('message', async (event) => {
            if (event.data.type === 'WITHINGS_CALLBACK') {
              authWindow.close()
              
              // Envoyer le code au backend
              const callbackResponse = await apiPost('/api/withings/callback', {
                code: event.data.code,
                state: event.data.state
              })
              
              if (callbackResponse) {
                const result = await callbackResponse.json()
                if (result.success) {
                  await checkConnectionStatus()
                  setError(null)
                } else {
                  setError(result.error)
                }
              }
            }
          })
        }
      }
    } catch (err) {
      setError('Erreur lors de la connexion')
      console.error('Erreur connexion:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleDisconnect = async () => {
    if (!confirm('Voulez-vous vraiment déconnecter votre compte Withings ?')) {
      return
    }
    
    try {
      setLoading(true)
      const response = await apiPost('/api/withings/disconnect')
      if (response) {
        const data = await response.json()
        if (data.success) {
          setStatus({ connected: false })
          setMeasurements([])
        }
      }
    } catch (err) {
      setError('Erreur lors de la déconnexion')
    } finally {
      setLoading(false)
    }
  }

  const handleSync = async () => {
    try {
      setSyncing(true)
      setError(null)
      
      const response = await apiPost('/api/withings/sync')
      if (response) {
        const data = await response.json()
        if (data.success) {
          setMeasurements(data.measurements || [])
          await checkConnectionStatus()
        } else {
          setError(data.error)
        }
      }
    } catch (err) {
      setError('Erreur lors de la synchronisation')
    } finally {
      setSyncing(false)
    }
  }

  if (loading && !status) {
    return (
      <div className="bg-white rounded-xl shadow-md p-6">
        <div className="flex items-center justify-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-xl shadow-md p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-gradient-to-r from-blue-500 to-purple-500 rounded-lg">
            <Activity className="w-6 h-6 text-white" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-gray-900">Balance Withings</h2>
            <p className="text-sm text-gray-600">
              Synchronisation automatique de vos mesures
            </p>
          </div>
        </div>
      </div>

      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center gap-2">
          <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0" />
          <span className="text-sm text-red-700">{error}</span>
        </div>
      )}

      {!status?.connected ? (
        <div className="text-center py-8">
          <div className="w-20 h-20 mx-auto mb-4 bg-gray-100 rounded-full flex items-center justify-center">
            <Weight className="w-10 h-10 text-gray-400" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            Connectez votre balance Withings
          </h3>
          <p className="text-gray-600 mb-6 max-w-md mx-auto">
            Synchronisez automatiquement votre poids et votre composition corporelle
            depuis votre balance connectée
          </p>
          <button
            onClick={handleConnect}
            disabled={loading}
            className="px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-500 text-white font-medium rounded-lg hover:from-blue-600 hover:to-purple-600 transition-all disabled:opacity-50"
          >
            {loading ? (
              <span className="flex items-center gap-2">
                <RefreshCw className="w-4 h-4 animate-spin" />
                Connexion...
              </span>
            ) : (
              'Connecter Withings'
            )}
          </button>
        </div>
      ) : (
        <div>
          {/* Statut de connexion */}
          <div className="flex items-center justify-between p-4 bg-green-50 border border-green-200 rounded-lg mb-4">
            <div className="flex items-center gap-3">
              <Check className="w-5 h-5 text-green-600" />
              <div>
                <p className="font-medium text-green-900">Compte connecté</p>
                <p className="text-sm text-green-700">
                  ID: {status.withings_user_id}
                  {status.last_sync && (
                    <span className="ml-2">
                      • Dernière sync: {new Date(status.last_sync).toLocaleDateString()}
                    </span>
                  )}
                </p>
              </div>
            </div>
            <button
              onClick={handleDisconnect}
              className="text-red-600 hover:text-red-700 transition-colors"
              title="Déconnecter"
            >
              <Unlink className="w-5 h-5" />
            </button>
          </div>

          {/* Bouton de synchronisation */}
          <button
            onClick={handleSync}
            disabled={syncing}
            className="w-full py-3 bg-blue-500 text-white font-medium rounded-lg hover:bg-blue-600 transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
          >
            <RefreshCw className={`w-5 h-5 ${syncing ? 'animate-spin' : ''}`} />
            {syncing ? 'Synchronisation...' : 'Synchroniser maintenant'}
          </button>

          {/* Dernières mesures */}
          {measurements.length > 0 && (
            <div className="mt-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-3">
                Dernières mesures
              </h3>
              <div className="space-y-2">
                {measurements.slice(0, 3).map((m, index) => (
                  <div key={m.id || index} className="p-3 bg-gray-50 rounded-lg">
                    <div className="flex justify-between items-center">
                      <div>
                        <p className="font-medium text-gray-900">
                          {m.weight ? `${m.weight} kg` : 'N/A'}
                        </p>
                        <p className="text-sm text-gray-600">
                          {new Date(m.measured_at).toLocaleString()}
                        </p>
                      </div>
                      {m.fat_ratio && (
                        <div className="text-right">
                          <p className="text-sm text-gray-600">Masse grasse</p>
                          <p className="font-medium">{m.fat_ratio}%</p>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}