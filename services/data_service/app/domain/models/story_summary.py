from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class StorySummaryCreate(BaseModel):
    post_id: int
    title: str
    summary: str
    generated_story: str
    model_used: str
    generation_metadata: Optional[Dict[str, Any]] = None

class StorySummary(BaseModel):
    id: int
    post_id: int
    title: str
    summary: str
    generated_story: str
    model_used: str
    generation_metadata: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True