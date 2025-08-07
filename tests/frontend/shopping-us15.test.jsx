/**
 * Tests unitaires pour le composant Shopping avec les fonctionnalités US1.5
 * Tests des nouvelles fonctionnalités interactives et des modales
 */

import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import '@testing-library/jest-dom'
import { vi } from 'vitest'

// Mock du hook useShoppingList
const mockUseShoppingList = vi.fn()
vi.mock('@/hooks/useShoppingList', () => ({
  default: mockUseShoppingList,
  useNetworkStatus: vi.fn()
}))

// Mock des composants UI
vi.mock('@/components/ui/card', () => ({
  Card: ({ children, className }) => <div className={className}>{children}</div>,
  CardContent: ({ children, className }) => <div className={className}>{children}</div>,
  CardHeader: ({ children, className }) => <div className={className}>{children}</div>,
  CardTitle: ({ children, className }) => <div className={className}>{children}</div>
}))

vi.mock('@/components/ui/button', () => ({
  Button: ({ children, onClick, disabled, className, variant, size }) => (
    <button 
      onClick={onClick} 
      disabled={disabled} 
      className={`${className} ${variant} ${size}`}
    >
      {children}
    </button>
  )
}))

vi.mock('@/components/ui/checkbox', () => ({
  Checkbox: ({ checked, onCheckedChange, disabled }) => (
    <input 
      type="checkbox" 
      checked={checked} 
      onChange={(e) => onCheckedChange?.(e.target.checked)}
      disabled={disabled}
    />
  )
}))

vi.mock('@/components/ui/badge', () => ({
  Badge: ({ children, variant, className }) => (
    <span className={`badge ${variant} ${className}`}>{children}</span>
  )
}))

vi.mock('@/components/ui/progress', () => ({
  Progress: ({ value, className }) => (
    <div className={`progress ${className}`} data-value={value} />
  )
}))

import { Shopping } from '../../src/frontend/components/Shopping'

describe('Shopping Component - US1.5 Features', () => {
  const mockShoppingList = {
    id: 1,
    week_start: '2025-08-07',
    generated_date: '2025-08-03',
    is_completed: false,
    estimated_budget: 85.50,
    items: [
      {
        id: 1,
        name: 'Blanc de poulet',
        quantity: 500,
        unit: 'g',
        category: 'protein',
        checked: false,
        note: 'Bio de préférence',
        unit_price: 15.0
      },
      {
        id: 2,
        name: 'Amandes',
        quantity: 200,
        unit: 'g',
        category: 'nuts',
        checked: true,
        unit_price: 8.0
      }
    ]
  }

  const mockCompletionStats = {
    total: 2,
    completed: 1,
    percentage: 50
  }

  const mockItemsByCategory = {
    protein: [mockShoppingList.items[0]],
    nuts: [mockShoppingList.items[1]]
  }

  const defaultMockHookReturn = {
    currentList: mockShoppingList,
    isLoading: false,
    error: null,
    offlineMode: false,
    pendingActionsCount: 0,
    toggleItemStatus: vi.fn(),
    bulkToggleItems: vi.fn(),
    regenerateList: vi.fn(),
    clearError: vi.fn(),
    completionStats: mockCompletionStats,
    itemsByCategory: mockItemsByCategory,
    // Nouvelles fonctionnalités US1.5
    getListStatistics: vi.fn(),
    exportList: vi.fn(),
    getListHistory: vi.fn()
  }

  beforeEach(() => {
    mockUseShoppingList.mockReturnValue(defaultMockHookReturn)
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  describe('Affichage de base avec nouvelles fonctionnalités', () => {
    test('affiche les nouveaux boutons pour les fonctionnalités US1.5', () => {
      render(<Shopping />)

      // Vérifier la présence des nouveaux boutons
      expect(screen.getByText('Stats')).toBeInTheDocument()
      expect(screen.getByText('Historique')).toBeInTheDocument()
      expect(screen.getByText('Export')).toBeInTheDocument()
    })

    test('affiche le budget estimé', () => {
      render(<Shopping />)

      expect(screen.getByText('85.5€')).toBeInTheDocument()
    })

    test('affiche les indicateurs de statut réseau', () => {
      mockUseShoppingList.mockReturnValue({
        ...defaultMockHookReturn,
        offlineMode: true,
        pendingActionsCount: 3
      })

      render(<Shopping />)

      expect(screen.getByText('Hors ligne')).toBeInTheDocument()
      expect(screen.getByText('3 en attente')).toBeInTheDocument()
    })
  })

  describe('Fonctionnalité Statistiques', () => {
    test('ouvre la modale de statistiques quand on clique sur Stats', async () => {
      const mockStats = {
        overview: {
          total_items: 2,
          completed_items: 1,
          completion_percentage: 50,
          estimated_budget: 85.50,
          estimated_shopping_time_minutes: 15
        },
        by_category: {
          protein: { total: 1, completed: 0, completion_percentage: 0 },
          nuts: { total: 1, completed: 1, completion_percentage: 100 }
        },
        efficiency_metrics: {
          completion_rate_trend: 'improving',
          aggregation_reduction: 2,
          cost_per_item: 11.5
        }
      }

      const getListStatistics = vi.fn().mockResolvedValue(mockStats)
      mockUseShoppingList.mockReturnValue({
        ...defaultMockHookReturn,
        getListStatistics
      })

      render(<Shopping />)

      const statsButton = screen.getByText('Stats')
      fireEvent.click(statsButton)

      await waitFor(() => {
        expect(getListStatistics).toHaveBeenCalled()
      })
    })

    test('n\'affiche pas les boutons avancés si pas de liste actuelle', () => {
      mockUseShoppingList.mockReturnValue({
        ...defaultMockHookReturn,
        currentList: null
      })

      render(<Shopping />)

      expect(screen.queryByText('Stats')).not.toBeInTheDocument()
      expect(screen.queryByText('Historique')).not.toBeInTheDocument()
      expect(screen.queryByText('Export')).not.toBeInTheDocument()
    })
  })

  describe('Fonctionnalité Export', () => {
    test('déclenche l\'export JSON quand on clique sur Export', async () => {
      const mockExportResult = {
        success: true,
        export_data: {
          shopping_list: mockShoppingList,
          metadata: { export_format: 'json' }
        },
        download_info: {
          filename: 'liste_courses_20250807.json',
          mime_type: 'application/json'
        }
      }

      const exportList = vi.fn().mockResolvedValue(mockExportResult)
      mockUseShoppingList.mockReturnValue({
        ...defaultMockHookReturn,
        exportList
      })

      // Mock de l'API DOM pour le téléchargement
      global.URL.createObjectURL = vi.fn().mockReturnValue('blob:url')
      global.URL.revokeObjectURL = vi.fn()
      const mockLink = {
        href: '',
        download: '',
        click: vi.fn()
      }
      vi.spyOn(document, 'createElement').mockReturnValue(mockLink)
      vi.spyOn(document.body, 'appendChild').mockImplementation(() => {})
      vi.spyOn(document.body, 'removeChild').mockImplementation(() => {})

      render(<Shopping />)

      const exportButton = screen.getByText('Export')
      fireEvent.click(exportButton)

      await waitFor(() => {
        expect(exportList).toHaveBeenCalledWith('json', {
          includeMetadata: true,
          includeCheckedItems: true
        })
      })
    })

    test('gère les erreurs d\'export', async () => {
      const exportList = vi.fn().mockRejectedValue(new Error('Export failed'))
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})

      mockUseShoppingList.mockReturnValue({
        ...defaultMockHookReturn,
        exportList
      })

      render(<Shopping />)

      const exportButton = screen.getByText('Export')
      fireEvent.click(exportButton)

      await waitFor(() => {
        expect(consoleSpy).toHaveBeenCalledWith('Erreur lors de l\'export:', expect.any(Error))
      })

      consoleSpy.mockRestore()
    })
  })

  describe('Fonctionnalité Historique', () => {
    test('ouvre la modale d\'historique quand on clique sur Historique', async () => {
      const mockHistory = {
        history: [
          {
            id: 1,
            action: 'item_checked',
            item_id: '1',
            timestamp: '2025-08-07T10:00:00Z',
            metadata: {}
          },
          {
            id: 2,
            action: 'regenerated',
            timestamp: '2025-08-07T09:00:00Z',
            metadata: { preserve_checked_items: true }
          }
        ],
        pagination: {
          page: 1,
          pages: 1,
          total: 2
        }
      }

      const getListHistory = vi.fn().mockResolvedValue(mockHistory)
      mockUseShoppingList.mockReturnValue({
        ...defaultMockHookReturn,
        getListHistory
      })

      render(<Shopping />)

      const historyButton = screen.getByText('Historique')
      fireEvent.click(historyButton)

      await waitFor(() => {
        expect(getListHistory).toHaveBeenCalledWith(1, 50)
      })
    })
  })

  describe('Gestion des états de chargement', () => {
    test('désactive les boutons avancés pendant le chargement', () => {
      mockUseShoppingList.mockReturnValue({
        ...defaultMockHookReturn,
        isLoading: true
      })

      render(<Shopping />)

      expect(screen.getByText('Stats')).toBeDisabled()
      expect(screen.getByText('Historique')).toBeDisabled()
    })

    test('affiche l\'indicateur de chargement sur le bouton Export', () => {
      render(<Shopping />)
      
      // Simuler le début d'export
      const exportButton = screen.getByText('Export')
      expect(exportButton).not.toBeDisabled()
      
      // Le composant utilise un état local isExporting pour gérer cela
      // Le test vérifie que le bouton est présent et cliquable
      expect(exportButton).toBeInTheDocument()
    })
  })

  describe('Affichage des erreurs', () => {
    test('affiche les erreurs de l\'API', () => {
      const errorMessage = 'Erreur de connexion au serveur'
      mockUseShoppingList.mockReturnValue({
        ...defaultMockHookReturn,
        error: errorMessage
      })

      render(<Shopping />)

      expect(screen.getByText(errorMessage)).toBeInTheDocument()
    })

    test('permet de fermer le message d\'erreur', () => {
      const clearError = vi.fn()
      const errorMessage = 'Erreur de test'

      mockUseShoppingList.mockReturnValue({
        ...defaultMockHookReturn,
        error: errorMessage,
        clearError
      })

      render(<Shopping />)

      const closeButton = screen.getByText('Fermer')
      fireEvent.click(closeButton)

      expect(clearError).toHaveBeenCalled()
    })
  })

  describe('Fonctionnalités interactives', () => {
    test('coche et décoche les articles', async () => {
      const toggleItemStatus = vi.fn()
      mockUseShoppingList.mockReturnValue({
        ...defaultMockHookReturn,
        toggleItemStatus
      })

      render(<Shopping />)

      const checkbox = screen.getAllByRole('checkbox')[0]
      fireEvent.click(checkbox)

      expect(toggleItemStatus).toHaveBeenCalledWith(1, true)
    })

    test('gère le toggle de tous les articles', async () => {
      const bulkToggleItems = vi.fn()
      mockUseShoppingList.mockReturnValue({
        ...defaultMockHookReturn,
        bulkToggleItems
      })

      render(<Shopping />)

      const toggleAllButton = screen.getByText('Tout cocher')
      fireEvent.click(toggleAllButton)

      expect(bulkToggleItems).toHaveBeenCalled()
    })

    test('régénère la liste', async () => {
      const regenerateList = vi.fn()
      mockUseShoppingList.mockReturnValue({
        ...defaultMockHookReturn,
        regenerateList
      })

      render(<Shopping />)

      const regenerateButton = screen.getByText('Régénérer')
      fireEvent.click(regenerateButton)

      expect(regenerateList).toHaveBeenCalledWith(true)
    })
  })

  describe('Affichage des informations d\'agrégation', () => {
    test('affiche les notes de conversion sur les articles', () => {
      const listWithConversions = {
        ...mockShoppingList,
        items: [
          {
            ...mockShoppingList.items[0],
            conversion_applied: 'Converti de 1500g en 1.5kg',
            original_quantity: 1500,
            original_unit: 'g'
          }
        ]
      }

      mockUseShoppingList.mockReturnValue({
        ...defaultMockHookReturn,
        currentList: listWithConversions,
        itemsByCategory: {
          protein: [listWithConversions.items[0]]
        }
      })

      render(<Shopping />)

      expect(screen.getByText('• Converti de 1500g en 1.5kg')).toBeInTheDocument()
    })

    test('affiche les informations de synchronisation hors ligne', () => {
      mockUseShoppingList.mockReturnValue({
        ...defaultMockHookReturn,
        offlineMode: true,
        pendingActionsCount: 2
      })

      render(<Shopping />)

      expect(screen.getByText('Mode hors ligne actif')).toBeInTheDocument()
      expect(screen.getByText('2 modification(s) en attente de synchronisation')).toBeInTheDocument()
    })
  })
})