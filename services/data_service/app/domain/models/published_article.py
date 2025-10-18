from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class PublishedArticleCreate(BaseModel):
    story_summary_id: int
    title: str
    content: str
    seo_title: str
    seo_description: str
    featured_image_url: Optional[str] = None
    tags: List[str] = []
    status: str = "draft"
    generation_metadata: Optional[Dict[str, Any]] = None

class PublishedArticle(BaseModel):
    id: int
    story_summary_id: int
    title: str
    content: str
    seo_title: str
    seo_description: str
    featured_image_url: Optional[str] = None
    tags: List[str] = []
    status: str
    wordpress_post_id: Optional[int] = None
    wordpress_url: Optional[str] = None
    publish_attempts: int = 0
    generation_metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    published_at: Optional[datetime] = None
    last_updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True