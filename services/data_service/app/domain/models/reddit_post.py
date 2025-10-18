from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class RedditComment(BaseModel):
    author: str
    body: str
    score: int
    created_at: datetime

class FilteredPost(BaseModel):
    source: str
    subreddit: str
    title: str
    url: str
    author: str
    score: int
    comments: int
    top_comments: Optional[List[RedditComment]] = None
    normalized_score: float
    created_at: datetime
    post_text: Optional[str] = None

class RedditPostCreate(BaseModel):
    posts: List[FilteredPost]