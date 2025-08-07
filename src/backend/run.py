#!/usr/bin/env python3
"""
Script de démarrage du serveur Flask
Corrige les problèmes d'importation circulaire
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from flask import Flask, send_from_directory
from flask_cors import CORS
from database import db
from database.config import get_config

def create_app(config_name=None):
    """Application factory pattern"""
    app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
    
    # Load configuration
    config = get_config(config_name)
    app.config.from_object(config)
    
    # Initialize extensions
    db.init_app(app)
    CORS(app, origins=app.config['CORS_ORIGINS'])
    
    with app.app_context():
        # Import models after app context is established
        from models.ingredient import Ingredient
        from models.recipe import Recipe
        from models.meal_plan import MealPlan, ShoppingList
        from models.user import User, WeightHistory
        
        # Only import if table doesn't exist to avoid circular import
        try:
            from models.shopping_history import ShoppingListHistory, StoreCategory
        except Exception as e:
            print(f"Warning: Could not import shopping_history models: {e}")
        
        # Create tables
        db.create_all()
        
        # Register blueprints
        from routes.user import user_bp
        from routes.recipes import recipes_bp
        from routes.ingredients import ingredients_bp
        from routes.meal_plans import meal_plans_bp
        
        api_prefix = app.config.get('API_PREFIX', '/api')
        app.register_blueprint(user_bp, url_prefix=api_prefix)
        app.register_blueprint(recipes_bp, url_prefix=api_prefix)
        app.register_blueprint(ingredients_bp, url_prefix=api_prefix)
        app.register_blueprint(meal_plans_bp, url_prefix=api_prefix)
        
        # Health check endpoint
        @app.route('/health')
        def health_check():
            return {'status': 'healthy', 'service': 'diet-tracker-backend'}, 200
        
        # Serve static files in production
        @app.route('/static/<path:filename>')
        def serve_static(filename):
            return send_from_directory(app.static_folder, filename)
    
    return app

if __name__ == '__main__':
    app = create_app()
    
    # Get configuration
    config = get_config()
    
    print(f"""
    ╔══════════════════════════════════════════════════════════╗
    ║         🥗 DietTracker Backend Server Starting 🥗          ║
    ╠══════════════════════════════════════════════════════════╣
    ║  Server running at: http://{config.HOST}:{config.PORT}              ║
    ║  API Prefix: {config.API_PREFIX}                              ║
    ║  CORS Origins: {', '.join(config.CORS_ORIGINS[:2])}          ║
    ║  Environment: {os.environ.get('FLASK_ENV', 'development')}                   ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    app.run(
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG
    )