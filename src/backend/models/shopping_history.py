"""
Modèle pour l'historique des modifications des listes de courses (US1.5)
Permet de tracer toutes les actions effectuées sur les listes interactives
"""

from database import db
from datetime import datetime
import json

class ShoppingListHistory(db.Model):
    __tablename__ = 'shopping_list_history'
    
    id = db.Column(db.Integer, primary_key=True)
    shopping_list_id = db.Column(db.Integer, db.ForeignKey('shopping_lists.id'), nullable=False)
    
    # Type d'action effectuée
    action = db.Column(db.String(50), nullable=False)  # 'item_checked', 'item_unchecked', 'regenerated', etc.
    
    # Détails de la modification
    item_id = db.Column(db.String(100), nullable=True)  # ID de l'article modifié
    old_value = db.Column(db.Text, nullable=True)       # Ancienne valeur (JSON)
    new_value = db.Column(db.Text, nullable=True)       # Nouvelle valeur (JSON)
    
    # Métadonnées
    user_id = db.Column(db.String(50), nullable=True)   # Utilisateur qui a fait la modification
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    metadata_json = db.Column(db.Text, nullable=True)   # Métadonnées supplémentaires
    
    # Relation avec ShoppingList
    shopping_list = db.relationship('ShoppingList', backref=db.backref('history_entries', lazy=True))
    
    @property
    def old_value_dict(self):
        """Retourne old_value en tant que dictionnaire"""
        return json.loads(self.old_value) if self.old_value else {}
    
    @old_value_dict.setter
    def old_value_dict(self, value):
        self.old_value = json.dumps(value) if value else None
    
    @property
    def new_value_dict(self):
        """Retourne new_value en tant que dictionnaire"""
        return json.loads(self.new_value) if self.new_value else {}
    
    @new_value_dict.setter
    def new_value_dict(self, value):
        self.new_value = json.dumps(value) if value else None
    
    @property
    def metadata(self):
        """Retourne metadata_json en tant que dictionnaire"""
        return json.loads(self.metadata_json) if self.metadata_json else {}
    
    @metadata.setter
    def metadata(self, value):
        self.metadata_json = json.dumps(value) if value else None
    
    def to_dict(self):
        """Convertit l'entrée d'historique en dictionnaire"""
        return {
            'id': self.id,
            'shopping_list_id': self.shopping_list_id,
            'action': self.action,
            'item_id': self.item_id,
            'old_value': self.old_value_dict,
            'new_value': self.new_value_dict,
            'user_id': self.user_id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'metadata': self.metadata
        }
    
    @staticmethod
    def create_from_dict(data):
        """Crée une entrée d'historique depuis un dictionnaire"""
        history_entry = ShoppingListHistory(
            shopping_list_id=data['shopping_list_id'],
            action=data['action'],
            item_id=data.get('item_id'),
            user_id=data.get('user_id'),
            timestamp=data.get('timestamp', datetime.utcnow())
        )
        
        if 'old_value' in data:
            history_entry.old_value_dict = data['old_value']
        if 'new_value' in data:
            history_entry.new_value_dict = data['new_value']
        if 'metadata' in data:
            history_entry.metadata = data['metadata']
        
        return history_entry
    
    @staticmethod
    def record_action(shopping_list_id, action, item_id=None, old_value=None, new_value=None, user_id=None, metadata=None):
        """
        Enregistre une action dans l'historique
        
        Args:
            shopping_list_id: ID de la liste de courses
            action: Type d'action ('item_checked', 'item_unchecked', etc.)
            item_id: ID de l'article modifié (optionnel)
            old_value: Ancienne valeur
            new_value: Nouvelle valeur
            user_id: ID de l'utilisateur
            metadata: Métadonnées supplémentaires
        
        Returns:
            ShoppingListHistory: L'entrée d'historique créée
        """
        try:
            entry = ShoppingListHistory(
                shopping_list_id=shopping_list_id,
                action=action,
                item_id=item_id,
                user_id=user_id
            )
            
            if old_value is not None:
                entry.old_value_dict = old_value
            if new_value is not None:
                entry.new_value_dict = new_value
            if metadata is not None:
                entry.metadata = metadata
            
            db.session.add(entry)
            db.session.commit()
            
            return entry
            
        except Exception as e:
            db.session.rollback()
            print(f"Erreur lors de l'enregistrement de l'historique: {e}")
            return None


class StoreCategory(db.Model):
    """
    Modèle pour les rayons de magasin personnalisables (US1.5)
    Permet aux utilisateurs de personnaliser l'organisation de leurs courses
    """
    __tablename__ = 'store_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)           # Nom technique (protein, vegetable, etc.)
    display_name = db.Column(db.String(100), nullable=False)   # Nom affiché (🥩 PROTÉINES)
    icon = db.Column(db.String(20), nullable=True)             # Emoji ou icône
    sort_order = db.Column(db.Integer, default=0)              # Ordre d'affichage
    is_active = db.Column(db.Boolean, default=True)            # Actif/inactif
    
    # Personnalisation par utilisateur
    user_id = db.Column(db.String(50), nullable=True)          # null = catégorie globale
    
    # Métadonnées
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Contrainte d'unicité
    __table_args__ = (
        db.UniqueConstraint('name', 'user_id', name='unique_category_per_user'),
    )
    
    def to_dict(self):
        """Convertit la catégorie en dictionnaire"""
        return {
            'id': self.id,
            'name': self.name,
            'display_name': self.display_name,
            'icon': self.icon,
            'sort_order': self.sort_order,
            'is_active': self.is_active,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @staticmethod
    def get_user_categories(user_id=None):
        """
        Récupère les catégories pour un utilisateur (globales + personnalisées)
        
        Args:
            user_id: ID de l'utilisateur (None pour catégories globales seulement)
        
        Returns:
            List[StoreCategory]: Liste des catégories triées par sort_order
        """
        query = StoreCategory.query.filter(StoreCategory.is_active == True)
        
        if user_id:
            # Récupérer les catégories globales ET celles de l'utilisateur
            query = query.filter(
                (StoreCategory.user_id == user_id) | (StoreCategory.user_id == None)
            )
        else:
            # Récupérer seulement les catégories globales
            query = query.filter(StoreCategory.user_id == None)
        
        return query.order_by(StoreCategory.sort_order.asc()).all()
    
    @staticmethod
    def create_user_category(user_id, name, display_name, icon=None, sort_order=0):
        """
        Crée une catégorie personnalisée pour un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            name: Nom technique de la catégorie
            display_name: Nom affiché
            icon: Icône/emoji
            sort_order: Ordre d'affichage
        
        Returns:
            StoreCategory: La catégorie créée ou None si erreur
        """
        try:
            # Vérifier qu'une catégorie avec ce nom n'existe pas déjà pour cet utilisateur
            existing = StoreCategory.query.filter_by(
                user_id=user_id,
                name=name
            ).first()
            
            if existing:
                return None  # Catégorie déjà existante
            
            category = StoreCategory(
                user_id=user_id,
                name=name,
                display_name=display_name,
                icon=icon,
                sort_order=sort_order
            )
            
            db.session.add(category)
            db.session.commit()
            
            return category
            
        except Exception as e:
            db.session.rollback()
            print(f"Erreur lors de la création de la catégorie: {e}")
            return None