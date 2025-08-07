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
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'environment': app.config.get('FLASK_ENV', 'unknown')}, 200
    
    # API root endpoint
    @app.route(f'{api_prefix}/')
    def api_root():
        return {
            'name': 'DietTracker API',
            'version': '1.0.0',
            'status': 'running',
            'endpoints': {
                'users': f'{api_prefix}/users',
                'recipes': f'{api_prefix}/recipes',
                'ingredients': f'{api_prefix}/ingredients',
                'meal_plans': f'{api_prefix}/meal-plans'
            }
        }, 200
    
    return app

# Create app instance
app = create_app()

# Import all models to ensure they are registered
from models.ingredient import Ingredient
from models.recipe import Recipe
from models.meal_plan import MealPlan, ShoppingList
from models.measurements import UserMeasurement
from models.user import User
# from models.shopping_history import ShoppingListHistory, StoreCategory  # Commenté car problème

# Initialize database with app context
with app.app_context():
    try:
        db.create_all()
        print("✅ Tables de base de données créées/vérifiées")
        
        # Créer un utilisateur test s'il n'existe pas
        if not User.query.filter_by(id=1).first():
            test_user = User(
                id=1,
                username="testuser",
                email="test@diettracker.com",
                age=30,
                gender="male",
                height=175,
                current_weight=75.0,
                target_weight=70.0,
                activity_level="moderate",
                dietary_restrictions=[],
                fitness_goal="weight_loss"
            )
            db.session.add(test_user)
            db.session.commit()
            print(f"✅ Utilisateur test créé avec ID: 1")
    except Exception as e:
        print(f"⚠️ Erreur lors de l'initialisation de la base de données: {e}")

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
