from flask import Blueprint, jsonify, request
from database import db
from models.user import User

user_bp = Blueprint('user', __name__)

@user_bp.route('/users', methods=['GET'])
def get_users():
    try:
        users = User.query.all()
        return jsonify([user.to_dict() for user in users])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    try:
        user = User.query.get_or_404(user_id)
        return jsonify(user.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    user = User(
        username=data['username'],
        email=data['email'],
        current_weight=data.get('current_weight'),
        target_weight=data.get('target_weight'),
        height=data.get('height'),
        age=data.get('age'),
        gender=data.get('gender'),
        activity_level=data.get('activity_level', 'moderate'),
        daily_calories_target=data.get('daily_calories_target', 2000),
        daily_protein_target=data.get('daily_protein_target', 100),
        daily_carbs_target=data.get('daily_carbs_target', 250),
        daily_fat_target=data.get('daily_fat_target', 65)
    )
    db.session.add(user)
    db.session.commit()
    return jsonify(user.to_dict()), 201

@user_bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    for key, value in data.items():
        if hasattr(user, key):
            setattr(user, key, value)
    
    db.session.commit()
    return jsonify(user.to_dict())