from datetime import datetime
from typing import Optional, Dict, List, Any
from pydantic import BaseModel, Field, HttpUrl

class WPMedia(BaseModel):
    """WordPress media object model."""
    id: int = Field(..., description="WordPress media ID")
    url: HttpUrl = Field(..., description="URL of the media file")
    alt_text: Optional[str] = Field(None, description="Alternative text for the image")
    mime_type: str = Field(..., description="Media MIME type")

class WPTaxonomy(BaseModel):
    """WordPress taxonomy (categories/tags) model."""
    id: int = Field(..., description="Taxonomy term ID")
    name: str = Field(..., description="Term name")
    slug: str = Field(..., description="Term slug")
    taxonomy: str = Field(..., description="Taxonomy type (category/post_tag)")

class WPPostCreate(BaseModel):
    """Model for creating a WordPress post."""
    title: str = Field(..., description="Post title")
    content: str = Field(..., description="Post content in HTML format")
    status: str = Field(default="Draft", description="Post status (Draft/publish/private)")
    featured_media: Optional[int] = Field(None, description="Featured image ID")
    categories: List[int] = Field(default_factory=list, description="Category IDs")
    tags: List[str] = Field(default_factory=list, description="Tag names")
    meta: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Post meta fields")
    slug: Optional[str] = Field(None, description="Post URL slug")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "AI Breakthrough: New Systems Show Self-Awareness",
                "content": "<article><h1>Revolutionary Tech Breakthrough...</h1></article>",
                "status": "publish",
                "featured_media": 123,
                "categories": [1],
                "tags": ["AI", "Technology", "Innovation"],
                "meta": {
                    "_yoast_wpseo_metadesc": "Groundbreaking research reveals...",
                    "_yoast_wpseo_title": "AI Breakthrough: %%sitename%%",
                    "_newsettler_source_id": 456
                },
                "slug": "ai-breakthrough-systems-self-aware"
            }
        }

class WPPostResponse(BaseModel):
    """Model for WordPress API post response."""
    id: int = Field(..., description="WordPress post ID")
    title: Dict[str, str] = Field(..., description="Post title object")
    content: Dict[str, Any] = Field(..., description="Post content object")  # Changed to Any to handle mixed types
    link: HttpUrl = Field(..., description="Published post URL")
    status: str = Field(..., description="Post status")
    featured_media: int = Field(..., description="Featured image ID")
    categories: List[int] = Field(..., description="Category IDs")
    tags: List[int] = Field(..., description="Tag IDs")
    meta: Dict[str, Any] = Field(..., description="Post meta fields")
    date: datetime = Field(..., description="Post creation date")
    modified: datetime = Field(..., description="Post last modified date")

    class Config:
        extra = "allow"  # Allow extra fields from WordPress API
        json_schema_extra = {
            "example": {
                "id": 789,
                "title": {"rendered": "AI Breakthrough: New Systems Show Self-Awareness"},
                "content": {"rendered": "<article>...</article>"},
                "link": "https://industechie.com/2025/10/ai-breakthrough",
                "status": "publish",
                "featured_media": 123,
                "categories": [1],
                "tags": [45, 46, 47],
                "meta": {
                    "_yoast_wpseo_metadesc": "Groundbreaking research reveals...",
                    "_newsettler_source_id": 456
                },
                "date": "2025-10-07T10:00:00",
                "modified": "2025-10-07T10:15:00"
            }
        }

class WPError(BaseModel):
    """WordPress API error response model."""
    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    data: Optional[Dict[str, Any]] = Field(None, description="Additional error data")

    class Config:
        json_schema_extra = {
            "example": {
                "code": "rest_post_invalid_id",
                "message": "Invalid post ID.",
                "data": {"status": 404}
            }
        }
