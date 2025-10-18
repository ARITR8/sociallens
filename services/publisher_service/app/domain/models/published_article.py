from datetime import datetime
from typing import Optional, Dict, List
from pydantic import BaseModel, Field, HttpUrl

class PublishedArticleBase(BaseModel):
    """Base model for published articles."""
    story_summary_id: int = Field(..., description="ID of the source story summary")
    title: str = Field(..., description="Article title")
    content: str = Field(..., description="Article content in HTML format")
    seo_title: str = Field(..., description="SEO optimized title")
    seo_description: str = Field(..., description="SEO meta description")
    featured_image_url: Optional[HttpUrl] = Field(None, description="URL of the featured image")
    tags: List[str] = Field(default_factory=list, description="Article tags")
    status: str = Field(
        default="draft",
        description="Article status (draft/published/failed)"
    )
    generation_metadata: Optional[Dict] = Field(
        default=None,
        description="Additional metadata about the generation process"
    )

class PublishedArticleCreate(PublishedArticleBase):
    """Model for creating a new published article."""
    pass

class PublishedArticleUpdate(PublishedArticleBase):
    """Model for updating an existing published article."""
    pass

class PublishedArticle(PublishedArticleBase):
    """Complete published article model with database fields."""
    id: int
    wordpress_post_id: Optional[int] = Field(None, description="WordPress post ID after publishing")
    wordpress_url: Optional[HttpUrl] = Field(None, description="URL of the published WordPress post")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    published_at: Optional[datetime] = Field(None, description="When the article was published")
    last_updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    publish_attempts: int = Field(default=0, description="Number of publishing attempts")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "story_summary_id": 123,
                "title": "Revolutionary Tech Breakthrough: AI Systems Now Self-Aware",
                "seo_title": "AI Breakthrough: New Systems Show Self-Awareness | NewsSettler",
                "seo_description": "Groundbreaking research reveals AI systems demonstrating genuine self-awareness, marking a historic milestone in artificial intelligence development.",
                "content": "<article><h1>Revolutionary Tech Breakthrough...</h1><p>In a groundbreaking development...</p></article>",
                "featured_image_url": "https://industechie.com/wp-content/uploads/2025/10/ai-breakthrough.jpg",
                "tags": ["AI", "Technology", "Research", "Innovation"],
                "status": "published",
                "wordpress_post_id": 456,
                "wordpress_url": "https://industechie.com/2025/10/ai-breakthrough-systems-self-aware",
                "generation_metadata": {
                    "llm_model": "gpt-4-turbo-preview",
                    "generation_params": {"temperature": 0.7},
                    "processing_time": 2.5
                },
                "created_at": "2025-10-07T10:00:00",
                "published_at": "2025-10-07T10:15:00",
                "last_updated_at": "2025-10-07T10:15:00",
                "publish_attempts": 1
            }
        }

class PublishingStats(BaseModel):
    """Statistics about publishing operations."""
    total_articles: int
    published_count: int
    draft_count: int
    failed_count: int
    average_processing_time: float
    success_rate: float

    class Config:
        json_schema_extra = {
            "example": {
                "total_articles": 100,
                "published_count": 85,
                "draft_count": 10,
                "failed_count": 5,
                "average_processing_time": 2.5,
                "success_rate": 0.85
            }
        }
