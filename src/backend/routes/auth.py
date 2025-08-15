"""
Routes d'authentification
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from database import db
from models.user import User
from datetime import datetime, timedelta
import os

auth_bp = Blueprint('auth', __name__)

# Durée de vie du token (24 heures)
ACCESS_TOKEN_EXPIRES = timedelta(hours=24)


@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    """Endpoint de connexion"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'success': False, 'error': 'Username et password requis'}), 400
        
        # Chercher l'utilisateur
        user = User.query.filter_by(username=username).first()
        
        if not user or not user.check_password(password):
            return jsonify({'success': False, 'error': 'Identifiants invalides'}), 401
        
        if not user.is_active:
            return jsonify({'success': False, 'error': 'Compte désactivé'}), 403
        
        # Mettre à jour last_login
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Créer le token JWT
        access_token = create_access_token(
            identity=str(user.id),
            expires_delta=ACCESS_TOKEN_EXPIRES,
            additional_claims={'username': user.username}
        )
        
        return jsonify({
            'success': True,
            'access_token': access_token,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@auth_bp.route('/api/auth/verify', methods=['GET'])
@jwt_required()
def verify_token():
    """Vérifie si le token est valide"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.is_active:
            return jsonify({'success': False, 'error': 'Utilisateur non trouvé ou inactif'}), 404
        
        return jsonify({
            'success': True,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@auth_bp.route('/api/auth/logout', methods=['POST'])
@jwt_required()
def logout():
    """Endpoint de déconnexion (côté client, on supprime le token)"""
    return jsonify({'success': True, 'message': 'Déconnecté avec succès'}), 200


@auth_bp.route('/api/auth/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change le mot de passe de l'utilisateur connecté"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'success': False, 'error': 'Utilisateur non trouvé'}), 404
        
        data = request.get_json()
        old_password = data.get('old_password')
        new_password = data.get('new_password')
        
        if not old_password or not new_password:
            return jsonify({'success': False, 'error': 'Ancien et nouveau mot de passe requis'}), 400
        
        if not user.check_password(old_password):
            return jsonify({'success': False, 'error': 'Mot de passe actuel incorrect'}), 401
        
        if len(new_password) < 8:
            return jsonify({'success': False, 'error': 'Le nouveau mot de passe doit faire au moins 8 caractères'}), 400
        
        user.set_password(new_password)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Mot de passe modifié avec succès'}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500