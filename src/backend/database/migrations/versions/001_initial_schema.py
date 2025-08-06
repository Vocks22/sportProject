"""Initial schema creation

Revision ID: 001
Revises: 
Create Date: 2025-08-06

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=80), nullable=False),
        sa.Column('email', sa.String(length=120), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=True),
        sa.Column('current_weight', sa.Float(), nullable=True),
        sa.Column('target_weight', sa.Float(), nullable=True),
        sa.Column('height', sa.Float(), nullable=True),
        sa.Column('age', sa.Integer(), nullable=True),
        sa.Column('gender', sa.String(length=10), nullable=True),
        sa.Column('activity_level', sa.String(length=20), nullable=True),
        sa.Column('daily_calories_target', sa.Float(), nullable=True, default=1500),
        sa.Column('daily_protein_target', sa.Float(), nullable=True, default=150),
        sa.Column('daily_carbs_target', sa.Float(), nullable=True, default=85),
        sa.Column('daily_fat_target', sa.Float(), nullable=True, default=75),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(), nullable=True, default=datetime.utcnow),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('username')
    )
    
    # Create ingredients table
    op.create_table('ingredients',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('calories_per_100g', sa.Float(), nullable=False),
        sa.Column('protein_per_100g', sa.Float(), nullable=False),
        sa.Column('carbs_per_100g', sa.Float(), nullable=False),
        sa.Column('fat_per_100g', sa.Float(), nullable=False),
        sa.Column('unit', sa.String(length=10), nullable=False, default='g'),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=datetime.utcnow),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create recipes table
    op.create_table('recipes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('meal_type', sa.String(length=20), nullable=False),
        sa.Column('ingredients_json', sa.Text(), nullable=False),
        sa.Column('instructions_json', sa.Text(), nullable=False),
        sa.Column('prep_time', sa.Integer(), nullable=True, default=0),
        sa.Column('cook_time', sa.Integer(), nullable=True, default=0),
        sa.Column('servings', sa.Integer(), nullable=True, default=1),
        sa.Column('total_calories', sa.Float(), nullable=True, default=0),
        sa.Column('total_protein', sa.Float(), nullable=True, default=0),
        sa.Column('total_carbs', sa.Float(), nullable=True, default=0),
        sa.Column('total_fat', sa.Float(), nullable=True, default=0),
        sa.Column('utensils_json', sa.Text(), nullable=True),
        sa.Column('tags_json', sa.Text(), nullable=True),
        sa.Column('rating', sa.Float(), nullable=True, default=0),
        sa.Column('is_favorite', sa.Boolean(), nullable=True, default=False),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(), nullable=True, default=datetime.utcnow),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create meal_plans table
    op.create_table('meal_plans',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(length=50), nullable=True),
        sa.Column('week_start', sa.Date(), nullable=False),
        sa.Column('meals_json', sa.Text(), nullable=False),
        sa.Column('daily_calories', sa.Float(), nullable=True, default=0),
        sa.Column('daily_protein', sa.Float(), nullable=True, default=0),
        sa.Column('daily_carbs', sa.Float(), nullable=True, default=0),
        sa.Column('daily_fat', sa.Float(), nullable=True, default=0),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(), nullable=True, default=datetime.utcnow),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create shopping_lists table
    op.create_table('shopping_lists',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('meal_plan_id', sa.Integer(), nullable=False),
        sa.Column('week_start', sa.Date(), nullable=False),
        sa.Column('items_json', sa.Text(), nullable=False),
        sa.Column('generated_date', sa.DateTime(), nullable=True, default=datetime.utcnow),
        sa.Column('is_completed', sa.Boolean(), nullable=True, default=False),
        sa.ForeignKeyConstraint(['meal_plan_id'], ['meal_plans.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for better performance
    op.create_index('idx_users_email', 'users', ['email'])
    op.create_index('idx_recipes_category', 'recipes', ['category'])
    op.create_index('idx_recipes_meal_type', 'recipes', ['meal_type'])
    op.create_index('idx_meal_plans_user_id', 'meal_plans', ['user_id'])
    op.create_index('idx_meal_plans_week_start', 'meal_plans', ['week_start'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_meal_plans_week_start', 'meal_plans')
    op.drop_index('idx_meal_plans_user_id', 'meal_plans')
    op.drop_index('idx_recipes_meal_type', 'recipes')
    op.drop_index('idx_recipes_category', 'recipes')
    op.drop_index('idx_users_email', 'users')
    
    # Drop tables
    op.drop_table('shopping_lists')
    op.drop_table('meal_plans')
    op.drop_table('recipes')
    op.drop_table('ingredients')
    op.drop_table('users')