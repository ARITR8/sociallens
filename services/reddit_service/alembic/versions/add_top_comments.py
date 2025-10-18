"""add top comments column

Revision ID: add_top_comments
Revises: 1a1c76b54e9c
Create Date: 2025-10-06 17:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic
revision = 'add_top_comments'
down_revision = '1a1c76b54e9c'  # This should match your previous migration ID
branch_labels = None
depends_on = None

def upgrade():
    # Add top_comments column
    op.add_column(
        'reddit_posts',
        sa.Column(
            'top_comments',
            JSONB,
            nullable=True,
            comment="Array of top comments in JSON format"
        )
    )

def downgrade():
    # Remove top_comments column
    op.drop_column('reddit_posts', 'top_comments')