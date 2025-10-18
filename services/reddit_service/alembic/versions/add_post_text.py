"""add post text column

Revision ID: add_post_text
Revises: add_top_comments
Create Date: 2025-10-11 12:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic
revision = 'add_post_text'
down_revision = 'add_top_comments'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column(
        'reddit_posts',
        sa.Column(
            'post_text',
            sa.Text,
            nullable=True,
            comment="Actual text content of the post (selftext for self posts)"
        )
    )

def downgrade():
    op.drop_column('reddit_posts', 'post_text')
