from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Index
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from app.core.database import Base

class RedditPostDB(Base):
    """Database model for Reddit posts."""
    __tablename__ = "reddit_posts"

    id = Column(Integer, primary_key=True)
    source = Column(String(50), nullable=False, index=True)
    subreddit = Column(String(100), nullable=False, index=True)
    title = Column(Text, nullable=False)
    url = Column(String(500), nullable=False, unique=True)
    author = Column(String(100), nullable=False, index=True)
    score = Column(Integer, nullable=False)
    comments = Column(Integer, nullable=False)
    top_comments = Column(JSONB, nullable=True)
    normalized_score = Column(Float, nullable=False, index=True)
    created_at = Column(DateTime, nullable=False)
    fetched_at = Column(DateTime, nullable=False, server_default="NOW()")
    post_text = Column(Text, nullable=True)

    __table_args__ = (
        Index('idx_reddit_posts_score_date', 'normalized_score', 'created_at'),
        Index('idx_reddit_posts_subreddit_date', 'subreddit', 'created_at'),
    )

class StorySummaryDB(Base):
    """Database model for story summaries."""
    __tablename__ = "story_summaries"

    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, nullable=False, index=True)
    title = Column(Text, nullable=False)
    summary = Column(Text, nullable=False)
    generated_story = Column(Text, nullable=False)
    model_used = Column(String(100), nullable=False)
    generation_metadata = Column(JSONB, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default="NOW()")

class PublishedArticleDB(Base):
    """Database model for published articles."""
    __tablename__ = "published_articles"

    id = Column(Integer, primary_key=True)
    story_summary_id = Column(Integer, nullable=False, index=True)
    title = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    seo_title = Column(Text, nullable=False)
    seo_description = Column(Text, nullable=False)
    featured_image_url = Column(Text, nullable=True)
    tags = Column(ARRAY(String), nullable=False, default=[])
    status = Column(String(20), nullable=False)
    wordpress_post_id = Column(Integer, nullable=True, unique=True)
    wordpress_url = Column(Text, nullable=True, unique=True)
    publish_attempts = Column(Integer, nullable=False, server_default='0')
    generation_metadata = Column(JSONB, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default="NOW()")
    published_at = Column(DateTime, nullable=True)
    last_updated_at = Column(DateTime, nullable=True)