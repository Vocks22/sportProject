import pytest
import json
from flask import Flask
from flask_testing import TestCase
import sys
import os

# Ajouter le chemin src/backend au path pour les imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src/backend'))

from database import db
from models.recipe import Recipe
from models.ingredient import Ingredient
from routes.recipes import recipes_bp

class TestRecipesAPI(TestCase):
    
    def create_app(self):
        """Créer l'application Flask pour les tests"""
        app = Flask(__name__)
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        db.init_app(app)
        app.register_blueprint(recipes_bp, url_prefix='/api')
        
        return app
    
    def setUp(self):
        """Configuration avant chaque test"""
        db.create_all()
        
        # Créer des ingrédients de test
        self.ingredient1 = Ingredient(
            name="Farine",
            category="grain",
            calories_per_100g=364,
            protein_per_100g=10.3,
            carbs_per_100g=76.3,
            fat_per_100g=0.9,
            unit="g"
        )
        self.ingredient2 = Ingredient(
            name="Oeuf",
            category="protein",
            calories_per_100g=155,
            protein_per_100g=13.0,
            carbs_per_100g=1.1,
            fat_per_100g=11.0,
            unit="g"
        )
        
        db.session.add_all([self.ingredient1, self.ingredient2])
        db.session.commit()
        
        # Données de test pour les recettes
        self.sample_recipe_data = {
            "name": "Crêpes simples",
            "category": "breakfast",
            "meal_type": "repas1",
            "ingredients": [
                {
                    "ingredient_id": 1,
                    "name": "Farine",
                    "quantity": 250,
                    "unit": "g"
                },
                {
                    "ingredient_id": 2,
                    "name": "Oeuf",
                    "quantity": 200,
                    "unit": "g"
                }
            ],
            "instructions": [
                {
                    "step": 1,
                    "description": "Mélanger la farine avec les oeufs"
                },
                {
                    "step": 2,
                    "description": "Cuire les crêpes dans une poêle"
                }
            ],
            "prep_time": 15,
            "cook_time": 10,
            "servings": 4,
            "utensils": ["poêle", "fouet"],
            "tags": ["facile", "rapide"]
        }
    
    def tearDown(self):
        """Nettoyage après chaque test"""
        db.session.remove()
        db.drop_all()
    
    def test_create_recipe_success(self):
        """Test de création d'une recette valide"""
        response = self.client.post(
            '/api/recipes',
            data=json.dumps(self.sample_recipe_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        
        self.assertEqual(data['name'], "Crêpes simples")
        self.assertEqual(data['category'], "breakfast")
        self.assertEqual(data['meal_type'], "repas1")
        self.assertEqual(len(data['ingredients']), 2)
        self.assertEqual(len(data['instructions']), 2)
        self.assertIn('nutrition_total', data)
        self.assertGreater(data['nutrition_total']['calories'], 0)
    
    def test_create_recipe_missing_required_field(self):
        """Test de création d'une recette avec champ obligatoire manquant"""
        invalid_data = self.sample_recipe_data.copy()
        del invalid_data['name']
        
        response = self.client.post(
            '/api/recipes',
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('Données invalides', data['error'])
    
    def test_create_recipe_invalid_category(self):
        """Test de création d'une recette avec catégorie invalide"""
        invalid_data = self.sample_recipe_data.copy()
        invalid_data['category'] = 'invalid_category'
        
        response = self.client.post(
            '/api/recipes',
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_create_recipe_invalid_content_type(self):
        """Test de création d'une recette sans Content-Type JSON"""
        response = self.client.post(
            '/api/recipes',
            data='invalid data',
            content_type='text/plain'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('Content-Type doit être application/json', data['error'])
    
    def test_get_recipes_empty(self):
        """Test de récupération des recettes quand aucune n'existe"""
        response = self.client.get('/api/recipes')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertEqual(len(data['recipes']), 0)
        self.assertIn('pagination', data)
        self.assertEqual(data['pagination']['total'], 0)
    
    def test_get_recipes_with_pagination(self):
        """Test de récupération des recettes avec pagination"""
        # Créer d'abord une recette
        self.client.post(
            '/api/recipes',
            data=json.dumps(self.sample_recipe_data),
            content_type='application/json'
        )
        
        response = self.client.get('/api/recipes?page=1&per_page=10')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertEqual(len(data['recipes']), 1)
        self.assertIn('pagination', data)
        self.assertEqual(data['pagination']['page'], 1)
        self.assertEqual(data['pagination']['per_page'], 10)
        self.assertEqual(data['pagination']['total'], 1)
    
    def test_get_recipes_with_filters(self):
        """Test de récupération des recettes avec filtres"""
        # Créer d'abord une recette
        self.client.post(
            '/api/recipes',
            data=json.dumps(self.sample_recipe_data),
            content_type='application/json'
        )
        
        # Test filtre par catégorie
        response = self.client.get('/api/recipes?category=breakfast')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data['recipes']), 1)
        
        # Test filtre par catégorie inexistante
        response = self.client.get('/api/recipes?category=dinner')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data['recipes']), 0)
    
    def test_get_recipe_by_id_success(self):
        """Test de récupération d'une recette par ID"""
        # Créer d'abord une recette
        create_response = self.client.post(
            '/api/recipes',
            data=json.dumps(self.sample_recipe_data),
            content_type='application/json'
        )
        
        recipe_id = json.loads(create_response.data)['id']
        
        response = self.client.get(f'/api/recipes/{recipe_id}')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['id'], recipe_id)
        self.assertEqual(data['name'], "Crêpes simples")
    
    def test_get_recipe_by_id_not_found(self):
        """Test de récupération d'une recette inexistante"""
        response = self.client.get('/api/recipes/999')
        
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('Recette non trouvée', data['error'])
    
    def test_get_recipe_by_id_invalid_id(self):
        """Test de récupération d'une recette avec ID invalide"""
        response = self.client.get('/api/recipes/-1')
        
        # Flask traite les IDs négatifs comme des 404
        self.assertEqual(response.status_code, 404)
        # Flask retourne une page HTML 404, pas JSON pour les IDs invalides
        # On vérifie juste le code de statut dans ce cas
    
    def test_update_recipe_success(self):
        """Test de mise à jour d'une recette"""
        # Créer d'abord une recette
        create_response = self.client.post(
            '/api/recipes',
            data=json.dumps(self.sample_recipe_data),
            content_type='application/json'
        )
        
        recipe_id = json.loads(create_response.data)['id']
        
        update_data = {
            "name": "Crêpes modifiées",
            "rating": 4.5
        }
        
        response = self.client.put(
            f'/api/recipes/{recipe_id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['name'], "Crêpes modifiées")
        self.assertEqual(data['rating'], 4.5)
    
    def test_update_recipe_not_found(self):
        """Test de mise à jour d'une recette inexistante"""
        update_data = {"name": "Test"}
        
        response = self.client.put(
            '/api/recipes/999',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('Recette non trouvée', data['error'])
    
    def test_update_recipe_invalid_data(self):
        """Test de mise à jour avec données invalides"""
        # Créer d'abord une recette
        create_response = self.client.post(
            '/api/recipes',
            data=json.dumps(self.sample_recipe_data),
            content_type='application/json'
        )
        
        recipe_id = json.loads(create_response.data)['id']
        
        invalid_update_data = {
            "category": "invalid_category"
        }
        
        response = self.client.put(
            f'/api/recipes/{recipe_id}',
            data=json.dumps(invalid_update_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_delete_recipe_success(self):
        """Test de suppression d'une recette"""
        # Créer d'abord une recette
        create_response = self.client.post(
            '/api/recipes',
            data=json.dumps(self.sample_recipe_data),
            content_type='application/json'
        )
        
        recipe_id = json.loads(create_response.data)['id']
        
        response = self.client.delete(f'/api/recipes/{recipe_id}')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('Recette supprimée avec succès', data['message'])
        
        # Vérifier que la recette n'existe plus
        get_response = self.client.get(f'/api/recipes/{recipe_id}')
        self.assertEqual(get_response.status_code, 404)
    
    def test_delete_recipe_not_found(self):
        """Test de suppression d'une recette inexistante"""
        response = self.client.delete('/api/recipes/999')
        
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('Recette non trouvée', data['error'])
    
    def test_toggle_favorite_success(self):
        """Test de basculement du statut favori"""
        # Créer d'abord une recette
        create_response = self.client.post(
            '/api/recipes',
            data=json.dumps(self.sample_recipe_data),
            content_type='application/json'
        )
        
        recipe_id = json.loads(create_response.data)['id']
        
        # Basculer vers favori
        response = self.client.post(f'/api/recipes/{recipe_id}/favorite')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['is_favorite'])
        self.assertEqual(data['recipe_id'], recipe_id)
        
        # Basculer de nouveau (enlever des favoris)
        response = self.client.post(f'/api/recipes/{recipe_id}/favorite')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertFalse(data['is_favorite'])
    
    def test_toggle_favorite_not_found(self):
        """Test de basculement du statut favori pour une recette inexistante"""
        response = self.client.post('/api/recipes/999/favorite')
        
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('Recette non trouvée', data['error'])
    
    def test_query_parameters_validation(self):
        """Test de validation des paramètres de requête"""
        # Test avec paramètres invalides
        response = self.client.get('/api/recipes?page=0')  # page doit être >= 1
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('Paramètres de requête invalides', data['error'])
        
        # Test avec per_page trop grand
        response = self.client.get('/api/recipes?per_page=200')  # per_page max 100
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('Paramètres de requête invalides', data['error'])


if __name__ == '__main__':
    pytest.main([__file__])