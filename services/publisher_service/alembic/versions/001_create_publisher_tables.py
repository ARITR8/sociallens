"""create publisher tables

Revision ID: 001
Revises: 
Create Date: 2025-10-10 10:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.sql import func

# revision identifiers
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'published_articles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('story_summary_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.Text(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('seo_title', sa.Text(), nullable=False),
        sa.Column('seo_description', sa.Text(), nullable=False),
        sa.Column('featured_image_url', sa.Text(), nullable=True),
        sa.Column('tags', ARRAY(sa.String()), nullable=False),
        sa.Column('wordpress_post_id', sa.Integer(), nullable=True),
        sa.Column('wordpress_url', sa.Text(), nullable=True),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('publish_attempts', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('generation_metadata', JSONB, nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=func.now(), nullable=False),
        sa.Column('published_at', sa.DateTime(), nullable=True),
        sa.Column('last_updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('wordpress_post_id'),
        sa.UniqueConstraint('wordpress_url')
    )
    
    # Add indexes
    op.create_index('idx_published_articles_story_summary_id', 'published_articles', ['story_summary_id'])
    op.create_index('idx_published_articles_status', 'published_articles', ['status'])
    op.create_index('idx_published_articles_created_at', 'published_articles', ['created_at'])
    op.create_index('idx_published_articles_published_at', 'published_articles', ['published_at'])

    op.create_table(
        'publishing_errors',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('article_id', sa.Integer(), nullable=False),
        sa.Column('error_type', sa.String(50), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=False),
        sa.Column('error_details', JSONB, nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['article_id'], ['published_articles.id'], name='fk_publishing_errors_article')
    )
    
    op.create_index('idx_publishing_errors_article_id', 'publishing_errors', ['article_id'])

def downgrade():
    # Drop indexes
    op.drop_index('idx_publishing_errors_article_id')
    op.drop_index('idx_published_articles_published_at')
    op.drop_index('idx_published_articles_created_at')
    op.drop_index('idx_published_articles_status')
    op.drop_index('idx_published_articles_story_summary_id')
    
    # Drop tables
    op.drop_table('publishing_errors')
    op.drop_table('published_articles')
