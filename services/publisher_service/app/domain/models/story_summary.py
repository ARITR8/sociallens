from datetime import datetime
from typing import Optional, Dict
from pydantic import BaseModel, Field

class StorySummary(BaseModel):
    """Model for story summaries from the summarizer service."""
    
    id: int = Field(..., description="Unique identifier for the story summary")
    post_id: int = Field(..., description="Original post ID")
    title: str = Field(..., description="Original story title")
    summary: str = Field(..., description="Generated summary of the story")
    generated_story: str = Field(..., description="Full generated story content")
    model_used: str = Field(..., description="Model used for generation")
    generation_metadata: Optional[Dict] = Field(None, description="Additional metadata about generation")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "title": "Major Tech Breakthrough in AI Research",
                "summary": "Researchers have achieved a significant breakthrough in AI...",
                "content": "In a groundbreaking development, researchers at...",
                "source_url": "https://example.com/tech-news/ai-breakthrough",
                "created_at": "2025-10-10T10:00:00"
            }
        }
