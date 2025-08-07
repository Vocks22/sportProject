"""
Tests unitaires pour le ShoppingService avec les fonctionnalités US1.5
Teste l'agrégation, les statistiques et les fonctionnalités interactives
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, date
from decimal import Decimal

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'backend'))

from services.shopping_service import ShoppingService
from models.meal_plan import MealPlan, ShoppingList
from models.recipe import Recipe
from models.ingredient import Ingredient


class TestShoppingServiceUS15:
    """Tests pour les nouvelles fonctionnalités US1.5 du ShoppingService"""
    
    @pytest.fixture
    def sample_meal_plan(self):
        """Crée un plan de repas pour les tests"""
        meal_plan = Mock(spec=MealPlan)
        meal_plan.id = 1
        meal_plan.meals = {
            'monday': {
                'repas1': 1,
                'repas2': 2
            },
            'tuesday': {
                'repas1': 1,
                'collation1': 3
            }
        }
        return meal_plan
    
    @pytest.fixture
    def sample_recipes(self):
        """Crée des recettes fictives pour les tests"""
        recipes = {}
        
        # Recette 1: Poulet grillé
        recipes[1] = Mock(spec=Recipe)
        recipes[1].id = 1
        recipes[1].name = "Poulet grillé"
        recipes[1].ingredients = [
            {'ingredient_id': 1, 'quantity': 200, 'unit': 'g'},
            {'ingredient_id': 2, 'quantity': 50, 'unit': 'ml'}
        ]
        
        # Recette 2: Salade César
        recipes[2] = Mock(spec=Recipe)
        recipes[2].id = 2
        recipes[2].name = "Salade César"
        recipes[2].ingredients = [
            {'ingredient_id': 1, 'quantity': 150, 'unit': 'g'},
            {'ingredient_id': 3, 'quantity': 100, 'unit': 'g'}
        ]
        
        # Recette 3: Snack aux noix
        recipes[3] = Mock(spec=Recipe)
        recipes[3].id = 3
        recipes[3].name = "Snack aux noix"
        recipes[3].ingredients = [
            {'ingredient_id': 4, 'quantity': 30, 'unit': 'g'}
        ]
        
        return recipes
    
    @pytest.fixture
    def sample_ingredients(self):
        """Crée des ingrédients fictifs pour les tests"""
        ingredients = {}
        
        ingredients[1] = Mock(spec=Ingredient)
        ingredients[1].id = 1
        ingredients[1].name = "Blanc de poulet"
        ingredients[1].category = "protein"
        ingredients[1].unit_price = 15.50
        
        ingredients[2] = Mock(spec=Ingredient)
        ingredients[2].id = 2
        ingredients[2].name = "Huile d'olive"
        ingredients[2].category = "condiment"
        ingredients[2].unit_price = 12.00
        
        ingredients[3] = Mock(spec=Ingredient)
        ingredients[3].id = 3
        ingredients[3].name = "Laitue romaine"
        ingredients[3].category = "vegetable"
        ingredients[3].unit_price = 3.50
        
        ingredients[4] = Mock(spec=Ingredient)
        ingredients[4].id = 4
        ingredients[4].name = "Amandes"
        ingredients[4].category = "nuts"
        ingredients[4].unit_price = 8.00
        
        return ingredients
    
    def test_collect_ingredients_from_meal_plan(self, sample_meal_plan, sample_recipes):
        """Test la collecte d'ingrédients depuis un plan de repas"""
        with patch.object(Recipe, 'query') as mock_recipe_query:
            # Mock des requêtes Recipe
            mock_recipe_query.get.side_effect = lambda recipe_id: sample_recipes.get(recipe_id)
            
            # Test
            ingredients_list = ShoppingService._collect_ingredients_from_meal_plan(sample_meal_plan)
            
            # Vérifications
            assert len(ingredients_list) == 5  # Total des ingrédients dans toutes les recettes
            
            # Vérifier qu'on a les bons ingrédients
            ingredient_ids = [item['ingredient_id'] for item in ingredients_list]
            assert 1 in ingredient_ids  # Poulet (2 fois)
            assert 2 in ingredient_ids  # Huile d'olive
            assert 3 in ingredient_ids  # Laitue
            assert 4 in ingredient_ids  # Amandes
            
            # Vérifier les métadonnées
            first_ingredient = ingredients_list[0]
            assert 'recipe_name' in first_ingredient
            assert 'day' in first_ingredient
            assert 'meal_type' in first_ingredient
    
    def test_aggregate_ingredient_quantities(self, sample_ingredients):
        """Test l'agrégation des quantités d'ingrédients"""
        raw_ingredients = [
            {
                'recipe_id': 1, 'recipe_name': 'Poulet grillé', 'day': 'monday', 'meal_type': 'repas1',
                'ingredient_id': 1, 'quantity': 200.0, 'unit': 'g'
            },
            {
                'recipe_id': 2, 'recipe_name': 'Salade César', 'day': 'monday', 'meal_type': 'repas2',
                'ingredient_id': 1, 'quantity': 150.0, 'unit': 'g'
            },
            {
                'recipe_id': 1, 'recipe_name': 'Poulet grillé', 'day': 'tuesday', 'meal_type': 'repas1',
                'ingredient_id': 1, 'quantity': 200.0, 'unit': 'g'
            }
        ]
        
        with patch.object(Ingredient, 'query') as mock_ingredient_query:
            mock_ingredient_query.get.side_effect = lambda ingredient_id: sample_ingredients.get(ingredient_id)
            
            # Test
            aggregated_list = ShoppingService._aggregate_ingredient_quantities(raw_ingredients)
            
            # Vérifications
            assert len(aggregated_list) == 1  # Un seul ingrédient agrégé
            
            aggregated_item = aggregated_list[0]
            assert aggregated_item['ingredient_id'] == 1
            assert aggregated_item['name'] == "Blanc de poulet"
            assert aggregated_item['quantity'] == 550.0  # 200 + 150 + 200
            assert aggregated_item['unit'] == 'g'
            assert len(aggregated_item['sources']) == 3
    
    def test_unit_conversion_grams_to_kg(self):
        """Test la conversion automatique grammes vers kilogrammes"""
        quantity, unit, note = ShoppingService._apply_unit_conversion(1500, 'g', {})
        
        assert quantity == 1.5
        assert unit == 'kg'
        assert 'Converti de 1500g en 1.5kg' in note
    
    def test_unit_conversion_ml_to_liters(self):
        """Test la conversion automatique millilitres vers litres"""
        quantity, unit, note = ShoppingService._apply_unit_conversion(2500, 'ml', {})
        
        assert quantity == 2.5
        assert unit == 'L'
        assert 'Converti de 2500ml en 2.5L' in note
    
    def test_unit_conversion_units_to_dozen(self):
        """Test la conversion automatique unités vers douzaines"""
        quantity, unit, note = ShoppingService._apply_unit_conversion(24, 'unités', {})
        
        assert quantity == 2
        assert unit == 'douzaine'
        assert 'Converti de 24 unités en 2 douzaine(s)' in note
    
    def test_no_conversion_needed(self):
        """Test qu'aucune conversion n'est appliquée si pas nécessaire"""
        quantity, unit, note = ShoppingService._apply_unit_conversion(500, 'g', {})
        
        assert quantity == 500
        assert unit == 'g'
        assert note is None
    
    def test_group_by_store_categories(self):
        """Test le groupement par rayons de magasin"""
        ingredients = [
            {'id': '1', 'name': 'Poulet', 'category': 'protein'},
            {'id': '2', 'name': 'Amandes', 'category': 'nuts'},
            {'id': '3', 'name': 'Laitue', 'category': 'vegetable'},
            {'id': '4', 'name': 'Inconnu', 'category': 'unknown_category'}
        ]
        
        categorized = ShoppingService._group_by_store_categories(ingredients)
        
        # Vérifications
        assert 'protein' in categorized
        assert 'nuts' in categorized
        assert 'vegetable' in categorized
        assert 'other' in categorized  # Catégorie inconnue mappée vers 'other'
        
        assert len(categorized['protein']) == 1
        assert categorized['protein'][0]['name'] == 'Poulet'
    
    def test_calculate_estimated_budget(self):
        """Test le calcul du budget estimé"""
        ingredients = [
            {'name': 'Poulet', 'quantity': 1.0, 'unit_price': 15.50},
            {'name': 'Amandes', 'quantity': 0.5, 'unit_price': 8.00},
            {'name': 'Laitue', 'quantity': 1.0, 'unit_price': None}  # Pas de prix
        ]
        
        budget = ShoppingService._calculate_estimated_budget(ingredients)
        
        # Budget calculé: (1.0 * 15.50) + (0.5 * 8.00) = 19.50
        # Avec extrapolation pour l'article sans prix: 19.50 / (2/3) = 29.25
        assert budget is not None
        assert isinstance(budget, float)
        assert budget > 19.50  # Avec extrapolation
    
    def test_calculate_estimated_shopping_time(self):
        """Test le calcul du temps estimé de courses"""
        time_minutes = ShoppingService._calculate_estimated_shopping_time(20, 5)
        
        # Formule: (5 rayons * 2 min) + (20 articles * 0.5 min) + 5 min fixes
        expected_time = 10 + 10 + 5  # = 25 minutes
        assert time_minutes == expected_time
    
    def test_generate_optimized_shopping_list_complete(self, sample_meal_plan, sample_recipes, sample_ingredients):
        """Test complet de génération d'une liste de courses optimisée"""
        with patch.object(Recipe, 'query') as mock_recipe_query, \
             patch.object(Ingredient, 'query') as mock_ingredient_query:
            
            # Configuration des mocks
            mock_recipe_query.get.side_effect = lambda recipe_id: sample_recipes.get(recipe_id)
            mock_ingredient_query.get.side_effect = lambda ingredient_id: sample_ingredients.get(ingredient_id)
            
            # Test
            result = ShoppingService.generate_optimized_shopping_list(sample_meal_plan)
            
            # Vérifications de base
            assert 'items' in result
            assert 'category_grouping' in result
            assert 'estimated_budget' in result
            assert 'aggregation_rules' in result
            assert 'statistics' in result
            
            # Vérifier que les items ont les bonnes propriétés
            items = result['items']
            assert len(items) > 0
            
            first_item = items[0]
            assert 'id' in first_item
            assert 'name' in first_item
            assert 'quantity' in first_item
            assert 'unit' in first_item
            assert 'category' in first_item
            assert 'sources' in first_item
            
            # Vérifier les statistiques
            stats = result['statistics']
            assert 'total_items' in stats
            assert 'total_categories' in stats
            assert 'aggregation_savings' in stats
    
    def test_update_item_status(self):
        """Test la mise à jour du statut d'un article"""
        # Créer un mock de ShoppingList
        shopping_list = Mock(spec=ShoppingList)
        shopping_list.id = 1
        shopping_list.checked_items = {}
        shopping_list.version = 1
        shopping_list.items = [
            {'id': 'item_1', 'name': 'Test Item'}
        ]
        
        with patch('services.shopping_service.db') as mock_db, \
             patch.object(ShoppingService, '_record_shopping_list_change') as mock_record:
            
            # Test
            success = ShoppingService.update_item_status(
                shopping_list, 'item_1', True, 'user_123'
            )
            
            # Vérifications
            assert success is True
            assert shopping_list.checked_items['item_1'] is True
            assert shopping_list.version == 2
            mock_db.session.commit.assert_called_once()
            mock_record.assert_called_once()


class TestShoppingListStatistics:
    """Tests pour les statistiques des listes de courses"""
    
    @pytest.fixture
    def sample_shopping_list(self):
        """Crée une liste de courses pour les tests"""
        shopping_list = Mock(spec=ShoppingList)
        shopping_list.id = 1
        shopping_list.items = [
            {'id': '1', 'name': 'Poulet', 'category': 'protein', 'quantity': 1, 'unit_price': 15.0},
            {'id': '2', 'name': 'Amandes', 'category': 'nuts', 'quantity': 0.5, 'unit_price': 8.0},
            {'id': '3', 'name': 'Laitue', 'category': 'vegetable', 'quantity': 1, 'unit_price': 3.0}
        ]
        shopping_list.checked_items = {'1': True, '2': False, '3': False}
        shopping_list.estimated_budget = 26.0
        shopping_list.is_completed = False
        shopping_list.last_updated = datetime.utcnow()
        shopping_list.version = 1
        shopping_list.aggregation_rules = {}
        
        # Mock meal_plan relationship
        shopping_list.meal_plan = Mock()
        shopping_list.meal_plan_id = 1
        shopping_list.week_start = date.today()
        shopping_list.meal_plan.meals = {'monday': {'repas1': 1}}
        shopping_list.meal_plan.daily_calories = 2000
        shopping_list.meal_plan.daily_protein = 150
        
        return shopping_list
    
    def test_get_shopping_list_statistics(self, sample_shopping_list):
        """Test le calcul des statistiques d'une liste de courses"""
        with patch.object(ShoppingService, '_calculate_completion_trend', return_value='improving'):
            
            statistics = ShoppingService.get_shopping_list_statistics(sample_shopping_list)
            
            # Vérifications overview
            overview = statistics['overview']
            assert overview['total_items'] == 3
            assert overview['completed_items'] == 1
            assert overview['completion_percentage'] == 33.3
            assert overview['estimated_budget'] == 26.0
            assert overview['is_completed'] is False
            assert 'estimated_shopping_time_minutes' in overview
            
            # Vérifications par catégorie
            by_category = statistics['by_category']
            assert 'protein' in by_category
            assert 'nuts' in by_category
            assert 'vegetable' in by_category
            
            protein_stats = by_category['protein']
            assert protein_stats['total'] == 1
            assert protein_stats['completed'] == 1
            assert protein_stats['completion_percentage'] == 100.0
            
            # Vérifications métriques d'efficacité
            efficiency = statistics['efficiency_metrics']
            assert 'completion_rate_trend' in efficiency
            assert efficiency['completion_rate_trend'] == 'improving'
    
    def test_export_shopping_list_data_json(self, sample_shopping_list):
        """Test l'export d'une liste de courses en JSON"""
        result = ShoppingService.export_shopping_list_data(
            sample_shopping_list, 
            export_format='json',
            include_metadata=True,
            include_checked_items=True
        )
        
        assert result['success'] is True
        
        export_data = result['export_data']
        assert 'shopping_list' in export_data
        assert 'metadata' in export_data
        assert 'meal_plan' in export_data
        
        # Vérifier les données de base
        shopping_data = export_data['shopping_list']
        assert shopping_data['id'] == 1
        assert len(shopping_data['items']) == 3
        assert 'checked_items' in shopping_data
        
        # Vérifier les métadonnées
        metadata = export_data['metadata']
        assert metadata['export_format'] == 'json'
        assert metadata['total_items'] == 3
        assert metadata['completed_items'] == 1
        
        # Vérifier les informations de téléchargement
        download_info = result['download_info']
        assert 'filename' in download_info
        assert download_info['mime_type'] == 'application/json'
    
    def test_format_list_as_text(self, sample_shopping_list):
        """Test le formatage de la liste en texte"""
        text_output = ShoppingService._format_list_as_text(sample_shopping_list)
        
        assert 'LISTE DE COURSES' in text_output
        assert 'Poulet' in text_output
        assert 'Amandes' in text_output
        assert 'Laitue' in text_output
        assert '✓ Poulet' in text_output  # Poulet est coché
        assert '☐ Amandes' in text_output  # Amandes pas cochées
        assert 'DietTracker' in text_output


if __name__ == '__main__':
    # Lancer les tests
    pytest.main([__file__, '-v'])