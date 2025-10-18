"""initial migration

Revision ID: 1a1c76b54e9c
Revises: 
Create Date: 2025-10-05 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func

# revision identifiers, used by Alembic.
revision = '1a1c76b54e9c'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'reddit_posts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('source', sa.String(50), nullable=False),
        sa.Column('subreddit', sa.String(100), nullable=False),
        sa.Column('title', sa.Text(), nullable=False),
        sa.Column('url', sa.String(500), nullable=False),
        sa.Column('author', sa.String(100), nullable=False),
        sa.Column('score', sa.Integer(), nullable=False),
        sa.Column('comments', sa.Integer(), nullable=False),
        sa.Column('normalized_score', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('fetched_at', sa.DateTime(), server_default=func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Add indexes
    op.create_index('idx_reddit_posts_score_date', 'reddit_posts', ['normalized_score', 'created_at'])
    op.create_index('idx_reddit_posts_subreddit_date', 'reddit_posts', ['subreddit', 'created_at'])
    op.create_index('idx_reddit_posts_url', 'reddit_posts', ['url'], unique=True)
    op.create_index('idx_reddit_posts_source', 'reddit_posts', ['source'])
    op.create_index('idx_reddit_posts_author', 'reddit_posts', ['author'])

def downgrade():
    # Drop indexes first
    op.drop_index('idx_reddit_posts_author')
    op.drop_index('idx_reddit_posts_source')
    op.drop_index('idx_reddit_posts_url')
    op.drop_index('idx_reddit_posts_subreddit_date')
    op.drop_index('idx_reddit_posts_score_date')
    
    # Then drop the table
    op.drop_table('reddit_posts')