from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel, Field

class RedditPost(BaseModel):
    """Model for Reddit post data from database."""
    id: int
    source: Optional[str] = None
    subreddit: Optional[str] = None
    title: Optional[str] = None
    url: Optional[str] = None
    author: Optional[str] = None
    score: Optional[int] = 0
    comments: Optional[int] = 0
    normalized_score: Optional[float] = None
    top_comments: Optional[List[Dict]] = None
    post_text: Optional[str] = None  # ✅ Added for DB match
    created_at: Optional[datetime] = None
    fetched_at: Optional[datetime] = None

    class Config:
        from_attributes = True
