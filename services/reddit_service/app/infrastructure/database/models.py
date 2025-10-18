# app/infrastructure/database/models.py
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import JSONB

Base = declarative_base()

class RedditPostDB(Base):
    """Database model for Reddit posts."""
    __tablename__ = "reddit_posts"

    # Primary key
    id = Column(Integer, primary_key=True)
    
    # Post metadata
    source = Column(
        String(50), 
        nullable=False, 
        index=True,
        comment="Source platform of the post"
    )
    subreddit = Column(
        String(100), 
        nullable=False, 
        index=True,
        comment="Subreddit name"
    )
    
    # Post content
    title = Column(
        Text, 
        nullable=False,
        comment="Post title"
    )
    url = Column(
        String(500), 
        nullable=False, 
        unique=True,
        comment="Post URL"
    )
    author = Column(
        String(100), 
        nullable=False, 
        index=True,
        comment="Post author username"
    )
    
    # Metrics
    score = Column(
        Integer, 
        nullable=False,
        comment="Post score/upvotes"
    )
    comments = Column(
        Integer, 
        nullable=False,
        comment="Total number of comments"
    )
    top_comments = Column(
        JSONB,
        nullable=True,
        comment="Array of top comments in JSON format"
    )
    normalized_score = Column(
        Float, 
        nullable=False, 
        index=True,
        comment="Calculated normalized score"
    )
    
    # Timestamps
    created_at = Column(
        DateTime, 
        nullable=False,
        comment="Post creation timestamp"
    )
    fetched_at = Column(
        DateTime, 
        nullable=False, 
        server_default="NOW()",
        comment="When the post was fetched"
    )

    # Add this field in RedditPostDB class
    post_text = Column(
        Text,
        nullable=True,
        comment="Actual text content of the post (selftext for self posts)"
    )

    # Indexes for common queries
    __table_args__ = (
        Index('idx_reddit_posts_score_date', 'normalized_score', 'created_at'),
        Index('idx_reddit_posts_subreddit_date', 'subreddit', 'created_at'),
        {'comment': 'Stores filtered Reddit posts with their metrics and metadata'}
    )

    def __repr__(self):
        """String representation of the post."""
        return f"<RedditPost(id={self.id}, subreddit={self.subreddit}, title={self.title[:30]}...)>"