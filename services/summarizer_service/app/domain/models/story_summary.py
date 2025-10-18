from datetime import datetime
from typing import Optional, Dict
from pydantic import BaseModel, Field

class StorySummaryBase(BaseModel):
    """Base model for story summaries."""
    post_id: int = Field(..., description="ID of the original Reddit post")
    title: str = Field(..., description="Generated title for the summary")
    summary: str = Field(..., description="Brief summary of the content")
    generated_story: str = Field(..., description="Full generated story content")
    model_used: str = Field(..., description="The LLM model used for generation")
    generation_metadata: Optional[Dict] = Field(default=None, description="Additional metadata about the generation")

class StorySummaryCreate(StorySummaryBase):
    """Model for creating a new summary."""
    pass

class StorySummaryUpdate(StorySummaryBase):
    """Model for updating an existing summary."""
    pass

class StorySummary(StorySummaryBase):
    """Complete story summary model with database fields."""
    id: int
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "post_id": 123,
                "title": "Amazing Discovery in Science",
                "summary": "Brief overview of the discovery...",
                "generated_story": "Full detailed story...",
                "model_used": "facebook/bart-large-cnn",
                "generation_metadata": {
                    "original_title": "Reddit post title",
                    "subreddit": "science",
                    "generation_params": {"temperature": 0.7}
                },
                "created_at": "2025-10-06T10:00:00"
            }
        }
