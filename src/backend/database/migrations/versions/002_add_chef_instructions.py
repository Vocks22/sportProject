"""Add chef instructions to recipes

Revision ID: 002
Revises: 001
Create Date: 2025-08-06

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add chef instructions fields to recipes table
    op.add_column('recipes', sa.Column('chef_instructions_json', sa.Text(), nullable=True))
    op.add_column('recipes', sa.Column('cooking_steps_json', sa.Text(), nullable=True))
    op.add_column('recipes', sa.Column('chef_tips_json', sa.Text(), nullable=True))
    op.add_column('recipes', sa.Column('visual_cues_json', sa.Text(), nullable=True))
    op.add_column('recipes', sa.Column('timing_details_json', sa.Text(), nullable=True))
    op.add_column('recipes', sa.Column('media_references_json', sa.Text(), nullable=True))
    op.add_column('recipes', sa.Column('difficulty_level', sa.String(length=20), nullable=True, default='beginner'))
    op.add_column('recipes', sa.Column('has_chef_mode', sa.Boolean(), nullable=True, default=False))


def downgrade() -> None:
    # Remove chef instructions fields from recipes table
    op.drop_column('recipes', 'has_chef_mode')
    op.drop_column('recipes', 'difficulty_level')
    op.drop_column('recipes', 'media_references_json')
    op.drop_column('recipes', 'timing_details_json')
    op.drop_column('recipes', 'visual_cues_json')
    op.drop_column('recipes', 'chef_tips_json')
    op.drop_column('recipes', 'cooking_steps_json')
    op.drop_column('recipes', 'chef_instructions_json')