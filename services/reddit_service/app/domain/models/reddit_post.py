# app/domain/models/reddit_post.py
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from app.domain.models.reddit_comment import RedditComment

class RedditPost(BaseModel):
    """Model for Reddit posts."""
    source: str = "reddit"
    subreddit: str
    title: str
    url: str
    author: str
    score: int
    comments: int  # Total number of comments
    top_comments: Optional[List[RedditComment]] = []  # Store top comments
    normalized_score: float
    created_at: datetime
    fetched_at: Optional[datetime] = None
    post_text: str = ""

    class Config:
        """Pydantic model configuration."""
        from_attributes = True

    @classmethod
    def from_reddit_post(cls, post_data: dict) -> "RedditPost":
        """Create RedditPost from raw Reddit post data."""
        return cls(
            source="reddit",
            subreddit=post_data["subreddit"],
            title=post_data["title"],
            url=post_data["url"],
            author=post_data["author"],
            score=post_data["score"],
            comments=post_data["num_comments"],
            top_comments=post_data.get("top_comments", []),
            normalized_score=post_data.get("normalized_score", post_data["score"]),
            created_at=datetime.fromtimestamp(post_data["created_utc"]),
            post_text=post_data.get("post_text", ""),
            fetched_at=datetime.utcnow()
        )