from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any

from app.core.database import get_db
from app.domain.models.reddit_post import RedditPostCreate, FilteredPost
from app.domain.models.story_summary import StorySummaryCreate, StorySummary
from app.domain.models.published_article import PublishedArticleCreate, PublishedArticle
from app.infrastructure.database.repository import DataRepository
from app.core.logging import logger

router = APIRouter()

def get_repository(db: AsyncSession = Depends(get_db)) -> DataRepository:
    """Get data repository instance."""
    return DataRepository(db)

# Reddit Posts Endpoints
@router.post("/reddit/posts", response_model=Dict[str, str])
async def save_reddit_posts(
    post_data: RedditPostCreate,
    repository: DataRepository = Depends(get_repository)
):
    """Save Reddit posts to database."""
    try:
        await repository.save_reddit_posts(post_data.posts)
        return {"message": f"Successfully saved {len(post_data.posts)} posts"}
    except Exception as e:
        logger.error(f"Error saving Reddit posts: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to save posts: {str(e)}")

@router.get("/reddit/posts", response_model=List[FilteredPost])
async def get_reddit_posts(
    limit: int = 10,
    subreddit: Optional[str] = None,
    repository: DataRepository = Depends(get_repository)
):
    """Get Reddit posts from database."""
    try:
        posts = await repository.get_reddit_posts(limit=limit, subreddit=subreddit)
        return posts
    except Exception as e:
        logger.error(f"Error getting Reddit posts: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get posts: {str(e)}")

# Story Summary Endpoints
@router.post("/story-summaries", response_model=StorySummary)
async def create_story_summary(
    summary: StorySummaryCreate,
    repository: DataRepository = Depends(get_repository)
):
    """Create a new story summary."""
    try:
        result = await repository.create_story_summary(summary)
        return result
    except Exception as e:
        logger.error(f"Error creating story summary: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create summary: {str(e)}")

@router.get("/story-summaries/{summary_id}", response_model=StorySummary)
async def get_story_summary_by_id(
    summary_id: int,
    repository: DataRepository = Depends(get_repository)
):
    """Get a story summary by ID."""
    try:
        summary = await repository.get_story_summary_by_id(summary_id)
        if not summary:
            raise HTTPException(status_code=404, detail="Story summary not found")
        return summary
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting story summary: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get summary: {str(e)}")

@router.get("/story-summaries/by-post/{post_id}", response_model=StorySummary)
async def get_story_summary_by_post_id(
    post_id: int,
    repository: DataRepository = Depends(get_repository)
):
    """Get a story summary by post ID."""
    try:
        summary = await repository.get_story_summary_by_post_id(post_id)
        if not summary:
            raise HTTPException(status_code=404, detail="Story summary not found")
        return summary
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting story summary by post ID: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get summary: {str(e)}")

# Published Article Endpoints
@router.post("/published-articles", response_model=PublishedArticle)
async def create_published_article(
    article: PublishedArticleCreate,
    repository: DataRepository = Depends(get_repository)
):
    """Create a new published article."""
    try:
        result = await repository.create_published_article(article)
        return result
    except Exception as e:
        logger.error(f"Error creating published article: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create article: {str(e)}")

@router.put("/published-articles/{article_id}", response_model=PublishedArticle)
async def update_published_article(
    article_id: int,
    updates: Dict[str, Any],
    repository: DataRepository = Depends(get_repository)
):
    """Update a published article."""
    try:
        result = await repository.update_published_article(article_id, updates)
        if not result:
            raise HTTPException(status_code=404, detail="Published article not found")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating published article: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update article: {str(e)}")