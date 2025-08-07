import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

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
    
    return app

# Create app instance
app = create_app()

# Import all models to ensure they are registered
from models.ingredient import Ingredient
from models.recipe import Recipe
from models.meal_plan import MealPlan, ShoppingList
from models.shopping_history import ShoppingListHistory, StoreCategory

# Create tables if running directly
if __name__ == '__main__':
    with app.app_context():
        db.create_all()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


if __name__ == '__main__':
    config = get_config()
    app.run(
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG if hasattr(config, 'DEBUG') else False
    )
