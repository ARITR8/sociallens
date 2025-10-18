# app/api/v1/endpoints/fetcher.py
from fastapi import APIRouter, Depends, Query, HTTPException, status
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.domain.models.filtered_post import FilteredPost
from app.services.post_processor_services import PostProcessorService
from app.infrastructure.reddit.client import RedditClient
from app.infrastructure.reddit.repository import RedditRepository
from app.infrastructure.database.repository import PostRepository
from app.domain.filters.post_filter import PostFilter
from app.domain.filters.config import FilterConfig
from app.services.fetcher_service import FetcherService
from app.core.exceptions import RedditFetchError, DatabaseError, FilterError
import logging
import traceback

logger = logging.getLogger(__name__)

router = APIRouter(tags=["reddit"])

async def get_post_processor(db: AsyncSession = Depends(get_db)) -> PostProcessorService:
    """
    Dependency for PostProcessorService.
    Creates and configures all necessary dependencies for post processing.
    """
    try:
        reddit_client = RedditClient()
        reddit_repository = RedditRepository(reddit_client)
        fetcher_service = FetcherService(reddit_repository)
        post_repository = PostRepository(db)
        filter_config = FilterConfig()
        post_filter = PostFilter(filter_config)
        
        return PostProcessorService(
            fetcher_service=fetcher_service,
            post_filter=post_filter,
            post_repository=post_repository
        )
    except Exception as e:
        logger.error(f"Failed to create PostProcessorService: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initialize service: {str(e)}"
        )

@router.get(
    "/posts/{subreddit}",
    response_model=List[FilteredPost],
    summary="Fetch and filter posts",
    description="Fetches posts from specified subreddit, applies filtering, and stores in database"
)
async def fetch_and_process_posts(
    subreddit: str,
    limit: int = Query(5, ge=1, le=100, description="Number of posts to fetch"),
    mode: str = Query("top", regex="^(hot|new|top)$", description="Sorting mode"),
    post_processor: PostProcessorService = Depends(get_post_processor)
) -> List[FilteredPost]:
    """Fetch, filter and store posts from specified subreddit."""
    try:
        return await post_processor.fetch_and_process_posts(
            subreddit=subreddit,
            limit=limit,
            mode=mode
        )
    except RedditFetchError as e:
        logger.error(f"Reddit fetch error: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to fetch from Reddit: {str(e)}"
        )
    except FilterError as e:
        logger.error(f"Filter error: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Post filtering failed: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )