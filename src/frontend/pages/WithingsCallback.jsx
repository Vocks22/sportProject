import React, { useEffect } from 'react'
import { useSearchParams, useNavigate } from 'react-router-dom'
import { CheckCircle, XCircle, Loader } from 'lucide-react'

export function WithingsCallback() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const code = searchParams.get('code')
  const state = searchParams.get('state')
  const error = searchParams.get('error')

  useEffect(() => {
    if (code && state) {
      // Si on est dans une popup, envoyer le code à la fenêtre parent
      if (window.opener) {
        window.opener.postMessage({
          type: 'WITHINGS_CALLBACK',
          code: code,
          state: state
        }, '*')
        
        // Afficher un message de succès
        setTimeout(() => {
          window.close()
        }, 2000)
      } else {
        // Si on n'est pas dans une popup, rediriger vers le profil
        navigate('/profile')
      }
    } else if (error) {
      // Gérer l'erreur
      console.error('Erreur OAuth:', error)
      setTimeout(() => {
        if (window.opener) {
          window.close()
        } else {
          navigate('/profile')
        }
      }, 3000)
    }
  }, [code, state, error, navigate])

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-xl p-8 max-w-md w-full text-center">
        {error ? (
          <>
            <div className="w-16 h-16 mx-auto mb-4 bg-red-100 rounded-full flex items-center justify-center">
              <XCircle className="w-8 h-8 text-red-500" />
            </div>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">
              Erreur de connexion
            </h1>
            <p className="text-gray-600">
              La connexion à Withings a échoué. Veuillez réessayer.
            </p>
          </>
        ) : code ? (
          <>
            <div className="w-16 h-16 mx-auto mb-4 bg-green-100 rounded-full flex items-center justify-center">
              <CheckCircle className="w-8 h-8 text-green-500" />
            </div>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">
              Connexion réussie !
            </h1>
            <p className="text-gray-600">
              Votre compte Withings est maintenant connecté.
              Cette fenêtre va se fermer automatiquement.
            </p>
          </>
        ) : (
          <>
            <div className="w-16 h-16 mx-auto mb-4 bg-blue-100 rounded-full flex items-center justify-center">
              <Loader className="w-8 h-8 text-blue-500 animate-spin" />
            </div>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">
              Connexion en cours...
            </h1>
            <p className="text-gray-600">
              Finalisation de la connexion avec Withings.
            </p>
          </>
        )}
      </div>
    </div>
  )
}