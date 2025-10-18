"""create story summaries table

Revision ID: 001
Revises: 
Create Date: 2025-10-06 10:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

# revision identifiers
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'story_summaries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('post_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.Text(), nullable=False),
        sa.Column('summary', sa.Text(), nullable=False),
        sa.Column('generated_story', sa.Text(), nullable=False),
        sa.Column('model_used', sa.String(100), nullable=False),
        sa.Column('generation_metadata', JSONB, nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Add indexes
    op.create_index('idx_story_summaries_post_id', 'story_summaries', ['post_id'])
    op.create_index('idx_story_summaries_created_at', 'story_summaries', ['created_at'])

def downgrade():
    # Drop indexes
    op.drop_index('idx_story_summaries_created_at')
    op.drop_index('idx_story_summaries_post_id')
    
    # Drop table
    op.drop_table('story_summaries')
