"""
Middleware pour protéger les routes avec authentification
"""
from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from models.auth import User


def auth_required(f):
    """Décorateur pour protéger les routes qui nécessitent une authentification"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            verify_jwt_in_request()
            
            # Vérifier que l'utilisateur existe et est actif
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            
            if not user or not user.is_active:
                return jsonify({'success': False, 'error': 'Authentification requise'}), 401
            
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({'success': False, 'error': 'Token invalide ou expiré'}), 401
    
    return decorated_function