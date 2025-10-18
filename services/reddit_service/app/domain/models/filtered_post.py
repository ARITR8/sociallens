# app/domain/models/filtered_post.py
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, HttpUrl, Field, validator
from app.domain.models.reddit_post import RedditPost
from app.domain.models.reddit_comment import RedditComment

class FilteredPost(BaseModel):
    """Enhanced post model with filtering capabilities."""
    source: str = Field(default="reddit", description="Source platform of the post")
    subreddit: str = Field(..., description="Subreddit name")
    title: str = Field(..., description="Post title")
    url: HttpUrl = Field(..., description="Post URL")
    author: str = Field(..., description="Post author username")
    score: int = Field(..., ge=0, description="Post score/upvotes")
    comments: int = Field(..., ge=0, description="Number of comments")
    top_comments: List[RedditComment] = Field(default=[], description="List of top comments")
    created_at: datetime = Field(..., description="Post creation timestamp")
    normalized_score: float = Field(..., ge=0, description="Calculated normalized score")
    fetched_at: Optional[datetime] = Field(default=None, description="When the post was fetched")
    post_text: str = Field(default="", description="Actual text content of the post")

    @validator('normalized_score', pre=True)
    def calculate_normalized_score(cls, v, values):
        """Calculate normalized score if not provided."""
        if v is None and 'score' in values and 'comments' in values:
            return values['score'] + (values['comments'] * 0.5)
        return v

    @classmethod
    def from_reddit_post(cls, post: RedditPost) -> "FilteredPost":
        """Create FilteredPost from RedditPost."""
        return cls(
            source=post.source,
            subreddit=post.subreddit,
            title=post.title,
            url=post.url,
            author=post.author,
            score=post.score,
            comments=post.comments,
            top_comments=post.top_comments,
            created_at=post.created_at,
            normalized_score=post.score + (post.comments * 0.5),
            fetched_at=datetime.utcnow(),
            post_text=post.post_text
        )

    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "source": "reddit",
                "subreddit": "programming",
                "title": "Announcing FastAPI v1.0.0",
                "url": "https://reddit.com/r/programming/123",
                "author": "user123",
                "score": 100,
                "comments": 50,
                "top_comments": [],
                "created_at": "2023-10-06T12:00:00Z",
                "normalized_score": 125.0,
                "fetched_at": "2023-10-06T12:01:00Z",
                "post_text": "This is the actual content of the post..."
            }
        }