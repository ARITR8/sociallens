from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from app.core.database import Base

class StorySummaryDB(Base):
    """Database model for story summaries."""
    __tablename__ = "story_summaries"
    # Remove the __table_args__ line with schema specification

    # Primary key
    id = Column(
        Integer, 
        primary_key=True, 
        index=True,
        comment="Unique identifier for the summary"
    )
    
    # Foreign key to Reddit post
    post_id = Column(
        Integer,
        nullable=False,
        index=True,
        comment="Reference to the original Reddit post ID"
    )
    
    # Summary content
    title = Column(
        Text,
        nullable=False,
        comment="Generated title for the summary"
    )
    
    summary = Column(
        Text,
        nullable=False,
        comment="Brief summary of the content"
    )
    
    generated_story = Column(
        Text,
        nullable=False,
        comment="Full generated story content"
    )
    
    # Generation metadata
    model_used = Column(
        String(100),
        nullable=False,
        comment="The LLM model used for generation"
    )
    
    generation_metadata = Column(
        JSONB,
        nullable=True,
        comment="Additional metadata about the generation"
    )
    
    # Timestamps
    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        comment="When the summary was generated"
    )

    def __repr__(self):
        return f"<StorySummary(id={self.id}, post_id={self.post_id}, title={self.title[:30]}...)>"
