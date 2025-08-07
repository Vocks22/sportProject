"""
Tests d'intégration pour les nouvelles API US1.5 - Liste de Courses Interactive
Teste les endpoints REST et leur intégration avec le service
"""

import pytest
import json
from unittest.mock import Mock, patch
from datetime import datetime, date

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'backend'))

from main import create_app
from models.meal_plan import ShoppingList
from services.shopping_service import ShoppingService


class TestShoppingListAPIUS15:
    """Tests pour les nouveaux endpoints API US1.5"""
    
    @pytest.fixture
    def app(self):
        """Créer l'application Flask pour les tests"""
        app = create_app('testing')
        app.config['TESTING'] = True
        return app
    
    @pytest.fixture
    def client(self, app):
        """Client de test Flask"""
        return app.test_client()
    
    @pytest.fixture
    def sample_shopping_list(self):
        """Liste de courses pour les tests"""
        shopping_list = Mock(spec=ShoppingList)
        shopping_list.id = 1
        shopping_list.meal_plan_id = 1
        shopping_list.week_start = date.today()
        shopping_list.items = [
            {
                'id': '1',
                'name': 'Blanc de poulet',
                'quantity': 500,
                'unit': 'g',
                'category': 'protein',
                'checked': False,
                'unit_price': 15.0,
                'note': 'Bio de préférence'
            },
            {
                'id': '2',
                'name': 'Amandes',
                'quantity': 200,
                'unit': 'g',
                'category': 'nuts',
                'checked': False,
                'unit_price': 8.0
            }
        ]
        shopping_list.checked_items = {}
        shopping_list.estimated_budget = 23.0
        shopping_list.is_completed = False
        shopping_list.version = 1
        shopping_list.aggregation_rules = {}
        shopping_list.category_grouping = {}
        return shopping_list
    
    def test_toggle_shopping_item_success(self, client, sample_shopping_list):
        """Test cocher/décocher un article - succès"""
        with patch.object(ShoppingList, 'query') as mock_query, \
             patch.object(ShoppingService, 'update_item_status', return_value=True):
            
            mock_query.get.return_value = sample_shopping_list
            
            # Données de requête
            data = {
                'checked': True,
                'user_id': 'user_123'
            }
            
            # Test
            response = client.patch(
                '/api/shopping-lists/1/items/1/toggle',
                data=json.dumps(data),
                content_type='application/json'
            )
            
            # Vérifications
            assert response.status_code == 200
            result = json.loads(response.data)
            assert result['success'] is True
            assert 'shopping_list' in result
    
    def test_toggle_shopping_item_not_found(self, client):
        """Test cocher/décocher un article - liste non trouvée"""
        with patch.object(ShoppingList, 'query') as mock_query:
            mock_query.get.return_value = None
            
            data = {'checked': True}
            
            response = client.patch(
                '/api/shopping-lists/999/items/1/toggle',
                data=json.dumps(data),
                content_type='application/json'
            )
            
            assert response.status_code == 404
            result = json.loads(response.data)
            assert 'error' in result
    
    def test_toggle_shopping_item_invalid_id(self, client):
        """Test cocher/décocher un article - ID invalide"""
        data = {'checked': True}
        
        response = client.patch(
            '/api/shopping-lists/0/items/1/toggle',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        result = json.loads(response.data)
        assert 'error' in result
    
    def test_bulk_toggle_items_success(self, client, sample_shopping_list):
        """Test mise à jour groupée d'articles - succès"""
        with patch.object(ShoppingList, 'query') as mock_query, \
             patch.object(ShoppingService, 'update_item_status', return_value=True):
            
            mock_query.get.return_value = sample_shopping_list
            
            # Données de requête
            data = {
                'items': [
                    {'item_id': '1', 'checked': True},
                    {'item_id': '2', 'checked': False}
                ],
                'user_id': 'user_123'
            }
            
            # Test
            response = client.patch(
                '/api/shopping-lists/1/bulk-toggle',
                data=json.dumps(data),
                content_type='application/json'
            )
            
            # Vérifications
            assert response.status_code == 200
            result = json.loads(response.data)
            assert result['success'] is True
            assert result['updated_items'] == 2
            assert result['total_items'] == 2
    
    def test_bulk_toggle_items_empty_list(self, client, sample_shopping_list):
        """Test mise à jour groupée - liste vide"""
        with patch.object(ShoppingList, 'query') as mock_query:
            mock_query.get.return_value = sample_shopping_list
            
            data = {'items': []}
            
            response = client.patch(
                '/api/shopping-lists/1/bulk-toggle',
                data=json.dumps(data),
                content_type='application/json'
            )
            
            assert response.status_code == 400
            result = json.loads(response.data)
            assert 'error' in result
    
    def test_regenerate_shopping_list_success(self, client, sample_shopping_list):
        """Test régénération de liste - succès"""
        mock_result = {
            'success': True,
            'shopping_list': sample_shopping_list,
            'statistics': {'total_items': 2}
        }
        
        with patch.object(ShoppingList, 'query') as mock_query, \
             patch.object(ShoppingService, 'regenerate_shopping_list', return_value=mock_result):
            
            mock_query.get.return_value = sample_shopping_list
            
            data = {'preserve_checked_items': True}
            
            response = client.post(
                '/api/shopping-lists/1/regenerate',
                data=json.dumps(data),
                content_type='application/json'
            )
            
            assert response.status_code == 200
            result = json.loads(response.data)
            assert result['success'] is True
    
    def test_get_shopping_list_statistics_success(self, client, sample_shopping_list):
        """Test récupération des statistiques - succès"""
        mock_statistics = {
            'overview': {
                'total_items': 2,
                'completed_items': 0,
                'completion_percentage': 0,
                'estimated_budget': 23.0,
                'is_completed': False,
                'estimated_shopping_time_minutes': 15
            },
            'by_category': {
                'protein': {'total': 1, 'completed': 0, 'completion_percentage': 0},
                'nuts': {'total': 1, 'completed': 0, 'completion_percentage': 0}
            },
            'efficiency_metrics': {
                'completion_rate_trend': 'unknown',
                'aggregation_reduction': 0,
                'cost_per_item': 11.5
            }
        }
        
        with patch.object(ShoppingList, 'query') as mock_query, \
             patch.object(ShoppingService, 'get_shopping_list_statistics', return_value=mock_statistics):
            
            mock_query.get.return_value = sample_shopping_list
            
            response = client.get('/api/shopping-lists/1/statistics')
            
            assert response.status_code == 200
            result = json.loads(response.data)
            assert 'overview' in result
            assert 'by_category' in result
            assert 'efficiency_metrics' in result
            assert result['overview']['total_items'] == 2
    
    def test_prepare_shopping_list_export_success(self, client, sample_shopping_list):
        """Test préparation d'export - succès"""
        mock_export_result = {
            'success': True,
            'export_data': {
                'shopping_list': {
                    'id': 1,
                    'items': sample_shopping_list.items
                },
                'metadata': {
                    'export_format': 'json',
                    'total_items': 2
                }
            },
            'download_info': {
                'filename': 'liste_courses_20250807.json',
                'mime_type': 'application/json',
                'size_estimate': 1024
            }
        }
        
        with patch.object(ShoppingList, 'query') as mock_query, \
             patch.object(ShoppingService, 'export_shopping_list_data', return_value=mock_export_result):
            
            mock_query.get.return_value = sample_shopping_list
            
            data = {
                'format': 'json',
                'include_metadata': True,
                'include_checked_items': True
            }
            
            response = client.post(
                '/api/shopping-lists/1/export-data',
                data=json.dumps(data),
                content_type='application/json'
            )
            
            assert response.status_code == 200
            result = json.loads(response.data)
            assert result['success'] is True
            assert 'export_data' in result
            assert 'download_info' in result
    
    def test_prepare_shopping_list_export_invalid_format(self, client, sample_shopping_list):
        """Test préparation d'export - format invalide"""
        with patch.object(ShoppingList, 'query') as mock_query:
            mock_query.get.return_value = sample_shopping_list
            
            data = {
                'format': 'invalid_format',
                'include_metadata': True
            }
            
            response = client.post(
                '/api/shopping-lists/1/export-data',
                data=json.dumps(data),
                content_type='application/json'
            )
            
            assert response.status_code == 400
            result = json.loads(response.data)
            assert 'error' in result
            assert 'details' in result
    
    def test_get_shopping_list_history_success(self, client, sample_shopping_list):
        """Test récupération de l'historique - succès"""
        from models.shopping_history import ShoppingListHistory
        
        mock_history_entries = [
            Mock(spec=ShoppingListHistory),
            Mock(spec=ShoppingListHistory)
        ]
        
        # Configurer les mocks d'historique
        for i, entry in enumerate(mock_history_entries):
            entry.id = i + 1
            entry.shopping_list_id = 1
            entry.action = 'item_checked'
            entry.item_id = f'item_{i + 1}'
            entry.timestamp = datetime.utcnow()
            entry.user_id = 'user_123'
            entry.to_dict.return_value = {
                'id': entry.id,
                'action': entry.action,
                'item_id': entry.item_id,
                'timestamp': entry.timestamp.isoformat()
            }
        
        # Mock de pagination
        mock_paginated = Mock()
        mock_paginated.items = mock_history_entries
        mock_paginated.page = 1
        mock_paginated.pages = 1
        mock_paginated.per_page = 20
        mock_paginated.total = 2
        mock_paginated.has_next = False
        mock_paginated.has_prev = False
        
        with patch.object(ShoppingList, 'query') as mock_shopping_query, \
             patch('routes.meal_plans.ShoppingListHistory') as mock_history_class:
            
            mock_shopping_query.get.return_value = sample_shopping_list
            mock_history_class.query.filter_by.return_value.order_by.return_value.paginate.return_value = mock_paginated
            
            response = client.get('/api/shopping-lists/1/history?page=1&per_page=20')
            
            assert response.status_code == 200
            result = json.loads(response.data)
            assert 'history' in result
            assert 'pagination' in result
            assert len(result['history']) == 2
            assert result['pagination']['total'] == 2
    
    def test_get_store_categories_success(self, client):
        """Test récupération des catégories de rayons - succès"""
        from models.shopping_history import StoreCategory
        
        mock_categories = [
            Mock(spec=StoreCategory),
            Mock(spec=StoreCategory)
        ]
        
        # Configurer les mocks
        for i, category in enumerate(mock_categories):
            category.id = i + 1
            category.name = f'category_{i + 1}'
            category.display_name = f'Category {i + 1}'
            category.icon = '🛒'
            category.to_dict.return_value = {
                'id': category.id,
                'name': category.name,
                'display_name': category.display_name,
                'icon': category.icon
            }
        
        with patch('routes.meal_plans.StoreCategory') as mock_category_class:
            mock_category_class.get_user_categories.return_value = mock_categories
            
            response = client.get('/api/shopping-lists/categories')
            
            assert response.status_code == 200
            result = json.loads(response.data)
            assert 'categories' in result
            assert 'total' in result
            assert len(result['categories']) == 2
            assert result['total'] == 2
    
    def test_get_store_categories_with_user_id(self, client):
        """Test récupération des catégories de rayons avec user_id"""
        from models.shopping_history import StoreCategory
        
        with patch('routes.meal_plans.StoreCategory') as mock_category_class:
            mock_category_class.get_user_categories.return_value = []
            
            response = client.get('/api/shopping-lists/categories?user_id=user_123')
            
            assert response.status_code == 200
            mock_category_class.get_user_categories.assert_called_once_with('user_123')


class TestShoppingListValidation:
    """Tests de validation pour les nouveaux endpoints"""
    
    @pytest.fixture
    def app(self):
        """Créer l'application Flask pour les tests"""
        app = create_app('testing')
        app.config['TESTING'] = True
        return app
    
    @pytest.fixture
    def client(self, app):
        """Client de test Flask"""
        return app.test_client()
    
    def test_toggle_item_missing_checked_field(self, client):
        """Test validation - champ 'checked' manquant"""
        with patch.object(ShoppingList, 'query') as mock_query:
            mock_query.get.return_value = Mock()
            
            data = {'user_id': 'user_123'}  # Pas de champ 'checked'
            
            response = client.patch(
                '/api/shopping-lists/1/items/1/toggle',
                data=json.dumps(data),
                content_type='application/json'
            )
            
            assert response.status_code == 500  # Le schéma devrait valider
    
    def test_bulk_toggle_invalid_structure(self, client):
        """Test validation - structure invalide pour bulk toggle"""
        with patch.object(ShoppingList, 'query') as mock_query:
            mock_query.get.return_value = Mock()
            
            data = {
                'items': [
                    {'invalid_field': 'value'}  # Structure incorrecte
                ]
            }
            
            response = client.patch(
                '/api/shopping-lists/1/bulk-toggle',
                data=json.dumps(data),
                content_type='application/json'
            )
            
            # Devrait échouer à cause de la structure invalide
            assert response.status_code in [400, 500]
    
    def test_export_invalid_format_validation(self, client):
        """Test validation - format d'export invalide"""
        with patch.object(ShoppingList, 'query') as mock_query:
            mock_query.get.return_value = Mock()
            
            data = {
                'format': 'unsupported_format',  # Format non supporté
                'include_metadata': True
            }
            
            response = client.post(
                '/api/shopping-lists/1/export-data',
                data=json.dumps(data),
                content_type='application/json'
            )
            
            assert response.status_code == 400
            result = json.loads(response.data)
            assert 'error' in result


if __name__ == '__main__':
    # Lancer les tests
    pytest.main([__file__, '-v'])