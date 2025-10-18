# app/domain/models/reddit_comment.py
from datetime import datetime
from pydantic import BaseModel

class RedditComment(BaseModel):
    """Model for Reddit comments."""
    id: str
    author: str
    body: str
    score: int
    created_at: datetime
    is_submitter: bool = False  # True if comment author is post author

    class Config:
        """Pydantic model configuration."""
        from_attributes = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }