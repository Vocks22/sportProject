"""Add shopping list enhancements for US1.5

Revision ID: 003_shopping_list_enhancements
Revises: 002_add_chef_instructions
Create Date: 2025-08-07 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers
revision = '003_shopping_list_enhancements'
down_revision = '002_add_chef_instructions'
branch_labels = None
depends_on = None

def upgrade():
    # Ajouter les nouveaux champs à la table shopping_lists existante
    with op.batch_alter_table('shopping_lists', schema=None) as batch_op:
        batch_op.add_column(sa.Column('checked_items_json', sa.Text(), default='{}'))
        batch_op.add_column(sa.Column('aggregation_rules_json', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('category_grouping_json', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('estimated_budget', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('last_updated', sa.DateTime(), default=datetime.utcnow))
        batch_op.add_column(sa.Column('completion_date', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('version', sa.Integer(), default=1))

    # Créer la table pour l'historique des modifications de listes
    op.create_table('shopping_list_history',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('shopping_list_id', sa.Integer(), sa.ForeignKey('shopping_lists.id'), nullable=False),
        sa.Column('action', sa.String(50), nullable=False),  # 'item_checked', 'item_unchecked', 'regenerated'
        sa.Column('item_id', sa.String(100), nullable=True),  # ID de l'article modifié
        sa.Column('old_value', sa.Text(), nullable=True),     # Ancienne valeur (JSON)
        sa.Column('new_value', sa.Text(), nullable=True),     # Nouvelle valeur (JSON)
        sa.Column('user_id', sa.String(50), nullable=True),   # Utilisateur qui a fait la modification
        sa.Column('timestamp', sa.DateTime(), default=datetime.utcnow),
        sa.Column('metadata_json', sa.Text(), nullable=True)  # Métadonnées supplémentaires
    )

    # Créer la table pour les rayons de magasin personnalisables
    op.create_table('store_categories',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('display_name', sa.String(100), nullable=False),
        sa.Column('icon', sa.String(20), nullable=True),
        sa.Column('sort_order', sa.Integer(), default=0),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('user_id', sa.String(50), nullable=True),  # Pour personnalisation par utilisateur
        sa.Column('created_at', sa.DateTime(), default=datetime.utcnow),
        sa.UniqueConstraint('name', 'user_id', name='unique_category_per_user')
    )

    # Insérer les rayons par défaut
    default_categories = [
        ('protein', '🥩 PROTÉINES', '🥩', 1),
        ('nuts', '🥜 OLÉAGINEUX', '🥜', 2),
        ('vegetable', '🥬 LÉGUMES FRAIS', '🥬', 3),
        ('fruit', '🍓 FRUITS', '🍓', 4),
        ('dairy', '🥛 PRODUITS LAITIERS', '🥛', 5),
        ('grain', '🌾 CÉRÉALES', '🌾', 6),
        ('frozen', '🧊 SURGELÉS', '🧊', 7),
        ('condiment', '🫒 CONDIMENTS & ÉPICES', '🫒', 8),
        ('supplement', '💊 COMPLÉMENTS', '💊', 9),
        ('bakery', '🍞 BOULANGERIE', '🍞', 10),
        ('beverages', '🥤 BOISSONS', '🥤', 11),
        ('other', '📦 AUTRES', '📦', 99)
    ]
    
    categories_table = sa.table('store_categories',
        sa.column('name'),
        sa.column('display_name'),
        sa.column('icon'),
        sa.column('sort_order'),
        sa.column('is_active'),
        sa.column('user_id')
    )
    
    for name, display_name, icon, sort_order in default_categories:
        op.execute(categories_table.insert().values(
            name=name,
            display_name=display_name,
            icon=icon,
            sort_order=sort_order,
            is_active=True,
            user_id=None  # Catégories globales
        ))

def downgrade():
    # Supprimer les nouvelles tables
    op.drop_table('store_categories')
    op.drop_table('shopping_list_history')
    
    # Supprimer les nouvelles colonnes de shopping_lists
    with op.batch_alter_table('shopping_lists', schema=None) as batch_op:
        batch_op.drop_column('checked_items_json')
        batch_op.drop_column('aggregation_rules_json')
        batch_op.drop_column('category_grouping_json')
        batch_op.drop_column('estimated_budget')
        batch_op.drop_column('last_updated')
        batch_op.drop_column('completion_date')
        batch_op.drop_column('version')