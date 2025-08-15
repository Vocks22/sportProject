"""
Routes pour l'intégration Withings OAuth2 et synchronisation des données
"""
from flask import Blueprint, request, jsonify, redirect, session
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import db
from models.withings import WithingsAuth, WithingsMeasurement
from models.user import User
from datetime import datetime, timedelta
import requests
import hashlib
import hmac
import os
import json
from urllib.parse import urlencode

withings_bp = Blueprint('withings', __name__)

# Configuration Withings (à mettre dans .env en production)
WITHINGS_CLIENT_ID = os.environ.get('WITHINGS_CLIENT_ID', '')
WITHINGS_CLIENT_SECRET = os.environ.get('WITHINGS_CLIENT_SECRET', '')
WITHINGS_REDIRECT_URI = os.environ.get('WITHINGS_REDIRECT_URI', 'https://diettracker.netlify.app/withings/callback')

# URLs Withings API
WITHINGS_AUTH_URL = 'https://account.withings.com/oauth2_user/authorize2'
WITHINGS_TOKEN_URL = 'https://wbsapi.withings.net/v2/oauth2'
WITHINGS_MEASURE_URL = 'https://wbsapi.withings.net/measure'


@withings_bp.route('/api/withings/auth', methods=['GET'])
@jwt_required()
def initiate_auth():
    """Initie le flux OAuth2 avec Withings"""
    try:
        user_id = get_jwt_identity()
        
        # Paramètres OAuth2
        params = {
            'response_type': 'code',
            'client_id': WITHINGS_CLIENT_ID,
            'redirect_uri': WITHINGS_REDIRECT_URI,
            'scope': 'user.info,user.metrics,user.activity',
            'state': str(user_id)  # On passe l'user_id dans le state
        }
        
        auth_url = f"{WITHINGS_AUTH_URL}?{urlencode(params)}"
        
        return jsonify({
            'success': True,
            'auth_url': auth_url,
            'message': 'Redirigez l\'utilisateur vers cette URL'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@withings_bp.route('/api/withings/callback', methods=['POST'])
@jwt_required()
def handle_callback():
    """Gère le callback OAuth2 de Withings"""
    try:
        data = request.json
        code = data.get('code')
        state = data.get('state')  # Contient l'user_id
        
        if not code:
            return jsonify({'success': False, 'error': 'Code d\'autorisation manquant'}), 400
        
        user_id = get_jwt_identity()
        
        # Échanger le code contre un token
        token_data = {
            'action': 'requesttoken',
            'grant_type': 'authorization_code',
            'client_id': WITHINGS_CLIENT_ID,
            'client_secret': WITHINGS_CLIENT_SECRET,
            'code': code,
            'redirect_uri': WITHINGS_REDIRECT_URI
        }
        
        response = requests.post(WITHINGS_TOKEN_URL, data=token_data)
        result = response.json()
        
        if result.get('status') != 0:
            return jsonify({
                'success': False, 
                'error': f"Erreur Withings: {result.get('error', 'Unknown error')}"
            }), 400
        
        body = result.get('body', {})
        
        # Sauvegarder ou mettre à jour les tokens
        auth = WithingsAuth.query.filter_by(user_id=user_id).first()
        
        if auth:
            # Mettre à jour
            auth.access_token = body.get('access_token')
            auth.refresh_token = body.get('refresh_token')
            auth.token_expiry = datetime.utcnow() + timedelta(seconds=body.get('expires_in', 3600))
            auth.withings_user_id = str(body.get('userid'))
            auth.scope = body.get('scope', '')
            auth.updated_at = datetime.utcnow()
        else:
            # Créer nouveau
            auth = WithingsAuth(
                user_id=user_id,
                withings_user_id=str(body.get('userid')),
                access_token=body.get('access_token'),
                refresh_token=body.get('refresh_token'),
                token_expiry=datetime.utcnow() + timedelta(seconds=body.get('expires_in', 3600)),
                scope=body.get('scope', '')
            )
            db.session.add(auth)
        
        db.session.commit()
        
        # Synchroniser immédiatement les dernières mesures
        sync_latest_measurements(user_id)
        
        return jsonify({
            'success': True,
            'message': 'Compte Withings connecté avec succès',
            'withings_user_id': auth.withings_user_id
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@withings_bp.route('/api/withings/sync', methods=['POST'])
@jwt_required()
def sync_measurements():
    """Synchronise manuellement les mesures Withings"""
    try:
        user_id = get_jwt_identity()
        
        # Vérifier si l'utilisateur a connecté Withings
        auth = WithingsAuth.query.filter_by(user_id=user_id).first()
        if not auth:
            return jsonify({
                'success': False, 
                'error': 'Compte Withings non connecté'
            }), 400
        
        # Rafraîchir le token si nécessaire
        if auth.is_token_expired():
            if not refresh_token(auth):
                return jsonify({
                    'success': False,
                    'error': 'Token expiré, reconnexion nécessaire'
                }), 401
        
        # Synchroniser les mesures
        measurements = sync_latest_measurements(user_id)
        
        return jsonify({
            'success': True,
            'message': f'{len(measurements)} mesures synchronisées',
            'measurements': [m.to_dict() for m in measurements]
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@withings_bp.route('/api/withings/disconnect', methods=['POST'])
@jwt_required()
def disconnect():
    """Déconnecte le compte Withings"""
    try:
        user_id = get_jwt_identity()
        
        # Supprimer l'authentification
        WithingsAuth.query.filter_by(user_id=user_id).delete()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Compte Withings déconnecté'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@withings_bp.route('/api/withings/status', methods=['GET'])
@jwt_required()
def get_status():
    """Vérifie le statut de connexion Withings"""
    try:
        user_id = get_jwt_identity()
        auth = WithingsAuth.query.filter_by(user_id=user_id).first()
        
        if not auth:
            return jsonify({
                'success': True,
                'connected': False
            })
        
        return jsonify({
            'success': True,
            'connected': True,
            'withings_user_id': auth.withings_user_id,
            'token_valid': not auth.is_token_expired(),
            'last_sync': auth.updated_at.isoformat() if auth.updated_at else None
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@withings_bp.route('/api/withings/webhook', methods=['POST'])
def handle_webhook():
    """Gère les notifications webhook de Withings"""
    try:
        # Vérifier la signature (si configurée)
        # TODO: Implémenter la vérification de signature
        
        data = request.json
        user_id = data.get('userid')
        
        if not user_id:
            return jsonify({'success': False}), 400
        
        # Trouver l'utilisateur correspondant
        auth = WithingsAuth.query.filter_by(withings_user_id=str(user_id)).first()
        if auth:
            # Synchroniser les nouvelles mesures
            sync_latest_measurements(auth.user_id)
        
        return jsonify({'success': True})
        
    except Exception as e:
        print(f"Webhook error: {e}")
        return jsonify({'success': False}), 500


def refresh_token(auth):
    """Rafraîchit le token d'accès"""
    try:
        data = {
            'action': 'requesttoken',
            'grant_type': 'refresh_token',
            'client_id': WITHINGS_CLIENT_ID,
            'client_secret': WITHINGS_CLIENT_SECRET,
            'refresh_token': auth.refresh_token
        }
        
        response = requests.post(WITHINGS_TOKEN_URL, data=data)
        result = response.json()
        
        if result.get('status') == 0:
            body = result.get('body', {})
            auth.access_token = body.get('access_token')
            auth.refresh_token = body.get('refresh_token')
            auth.token_expiry = datetime.utcnow() + timedelta(seconds=body.get('expires_in', 3600))
            auth.updated_at = datetime.utcnow()
            db.session.commit()
            return True
            
    except Exception as e:
        print(f"Token refresh error: {e}")
    
    return False


def sync_latest_measurements(user_id):
    """Synchronise les dernières mesures depuis Withings"""
    measurements = []
    
    try:
        auth = WithingsAuth.query.filter_by(user_id=user_id).first()
        if not auth:
            return measurements
        
        # Paramètres pour récupérer les mesures
        params = {
            'action': 'getmeas',
            'access_token': auth.access_token,
            'meastype': '1,5,6,8,76,77,88',  # Poids, graisse, muscle, hydratation, etc.
            'category': 1,  # Mesures réelles (pas objectifs)
            'lastupdate': 0  # Récupérer toutes les mesures
        }
        
        response = requests.post(WITHINGS_MEASURE_URL, data=params)
        result = response.json()
        
        if result.get('status') != 0:
            print(f"Erreur récupération mesures: {result}")
            return measurements
        
        body = result.get('body', {})
        measuregrps = body.get('measuregrps', [])
        
        for grp in measuregrps[:5]:  # Limiter aux 5 dernières mesures
            # Vérifier si la mesure existe déjà
            measure_id = str(grp.get('grpid'))
            existing = WithingsMeasurement.query.filter_by(
                withings_measure_id=measure_id
            ).first()
            
            if existing:
                continue
            
            # Créer nouvelle mesure
            measurement = WithingsMeasurement(
                user_id=user_id,
                withings_measure_id=measure_id,
                measured_at=datetime.fromtimestamp(grp.get('date')),
                device_id=str(grp.get('deviceid'))
            )
            
            # Parser les différentes mesures
            for measure in grp.get('measures', []):
                value = measure.get('value') * (10 ** measure.get('unit'))
                measure_type = measure.get('type')
                
                if measure_type == 1:  # Poids
                    measurement.weight = value
                elif measure_type == 5:  # Masse grasse
                    measurement.fat_mass = value
                elif measure_type == 6:  # Ratio masse grasse
                    measurement.fat_ratio = value
                elif measure_type == 76:  # Masse musculaire
                    measurement.muscle_mass = value
                elif measure_type == 77:  # Hydratation
                    measurement.hydration = value
                elif measure_type == 88:  # Masse osseuse
                    measurement.bone_mass = value
                elif measure_type == 11:  # Fréquence cardiaque
                    measurement.heart_rate = int(value)
            
            db.session.add(measurement)
            measurements.append(measurement)
        
        # Mettre à jour le poids actuel de l'utilisateur si on a une nouvelle mesure
        if measurements:
            latest = measurements[0]
            if latest.weight:
                user = User.query.get(user_id)
                if user:
                    user.current_weight = latest.weight
        
        db.session.commit()
        
    except Exception as e:
        print(f"Sync error: {e}")
        db.session.rollback()
    
    return measurements