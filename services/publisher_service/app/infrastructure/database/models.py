from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from app.core.database import Base

class PublishedArticleDB(Base):
    """Database model for published articles."""
    __tablename__ = "published_articles"
    __table_args__ = (
        # Explicitly set schema
        {'schema': 'public'}
    )

    # Primary key
    id = Column(
        Integer,
        primary_key=True,
        index=True,
        comment="Unique identifier for the published article"
    )

    # Foreign key to story summary (in public schema)
    story_summary_id = Column(
        Integer,
        nullable=False,
        index=True,
        comment="Reference to the original story summary"
    )

    # Article content
    title = Column(
        Text,
        nullable=False,
        comment="Article title"
    )

    content = Column(
        Text,
        nullable=False,
        comment="Article content in HTML format"
    )

    seo_title = Column(
        Text,
        nullable=False,
        comment="SEO optimized title"
    )

    seo_description = Column(
        Text,
        nullable=False,
        comment="SEO meta description"
    )

    featured_image_url = Column(
        Text,
        nullable=True,
        comment="URL of the featured image"
    )

    tags = Column(
        ARRAY(String),
        nullable=False,
        default=[],
        comment="Article tags"
    )

    # WordPress specific fields
    wordpress_post_id = Column(
        Integer,
        nullable=True,
        unique=True,
        comment="WordPress post ID after publishing"
    )

    wordpress_url = Column(
        Text,
        nullable=True,
        unique=True,
        comment="URL of the published WordPress post"
    )

    status = Column(
        String(20),
        nullable=False,
        default="draft",
        comment="Article status (draft/published/failed)"
    )

    publish_attempts = Column(
        Integer,
        nullable=False,
        default=0,
        comment="Number of publishing attempts"
    )

    # Metadata
    generation_metadata = Column(
        JSONB,
        nullable=True,
        comment="Additional metadata about the generation process"
    )

    # Timestamps
    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        comment="When the article was created"
    )

    published_at = Column(
        DateTime,
        nullable=True,
        comment="When the article was published"
    )

    last_updated_at = Column(
        DateTime,
        nullable=True,
        onupdate=datetime.utcnow,
        comment="Last update timestamp"
    )

    def __repr__(self):
        return f"<PublishedArticle(id={self.id}, title={self.title[:30]}..., status={self.status})>"

class PublishingErrorDB(Base):
    """Database model for publishing errors."""
    __tablename__ = "publishing_errors"
    __table_args__ = (
        # Explicitly set schema
        {'schema': 'public'}
    )

    # Primary key
    id = Column(
        Integer,
        primary_key=True,
        index=True,
        comment="Unique identifier for the error"
    )

    # Foreign key to published article
    article_id = Column(
        Integer,
        ForeignKey(
            'public.published_articles.id',  # Add schema prefix
            ondelete='CASCADE',
            name='fk_publishing_errors_article'
        ),
        nullable=False,
        index=True,
        comment="Reference to the published article"
    )

    error_type = Column(
        String(50),
        nullable=False,
        comment="Type of error (wp_api, generation, etc.)"
    )

    error_message = Column(
        Text,
        nullable=False,
        comment="Error message"
    )

    error_details = Column(
        JSONB,
        nullable=True,
        comment="Additional error details"
    )

    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        comment="When the error occurred"
    )

    def __repr__(self):
        return f"<PublishingError(id={self.id}, article_id={self.article_id}, type={self.error_type})>"
