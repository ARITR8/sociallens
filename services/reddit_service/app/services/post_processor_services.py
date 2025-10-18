# app/services/post_processor_service.py
import logging
from typing import List, Optional
from datetime import datetime
from app.domain.models.reddit_post import RedditPost
from app.domain.models.filtered_post import FilteredPost
from app.domain.filters.post_filter import PostFilter
from app.infrastructure.database.repository import PostRepository
from app.services.fetcher_service import FetcherService
from app.core.exceptions import RedditFetchError, FilterError, DatabaseError

logger = logging.getLogger(__name__)

class PostProcessorService:
    """Service for processing and storing Reddit posts."""

    def __init__(
        self,
        fetcher_service: FetcherService,
        post_filter: PostFilter,
        post_repository: PostRepository
    ):
        self.fetcher_service = fetcher_service
        self.post_filter = post_filter
        self.post_repository = post_repository

    async def fetch_and_process_posts(
        self,
        subreddit: str,
        limit: int = 5,
        mode: str = "top"
    ) -> List[FilteredPost]:
        """
        Fetch, filter, and store relevant posts.
        
        Args:
            subreddit: Subreddit to fetch from
            limit: Number of posts to fetch
            mode: Sorting mode (hot/new/top)
            
        Returns:
            List of filtered and processed posts
            
        Raises:
            RedditFetchError: If fetching posts fails
            FilterError: If filtering posts fails
            DatabaseError: If storing posts fails
        """
        try:
            # Fetch posts
            logger.info(f"Fetching posts from r/{subreddit}")
            raw_posts = await self.fetcher_service.fetch_posts(
                subreddit=subreddit,
                limit=limit,
                mode=mode
            )
            logger.info(f"Fetched {len(raw_posts)} posts from r/{subreddit}")

            # Convert and filter posts
            filtered_posts = []
            for raw_post in raw_posts:
                try:
                    filtered_post = FilteredPost.from_reddit_post(raw_post)
                    if self.post_filter.is_valid_post(filtered_post):
                        filtered_posts.append(filtered_post)
                except Exception as e:
                    logger.warning(f"Failed to process post: {str(e)}")
                    continue

            logger.info(
                f"Filtered {len(raw_posts)} posts to {len(filtered_posts)} relevant posts"
            )

            # Store filtered posts
            if filtered_posts:
                logger.info(f"Storing {len(filtered_posts)} filtered posts")
                await self.post_repository.save_posts(filtered_posts)
            else:
                logger.info("No posts passed filtering criteria")

            return filtered_posts

        except RedditFetchError as e:
            logger.error(f"Failed to fetch posts: {str(e)}")
            raise
        except FilterError as e:
            logger.error(f"Failed to filter posts: {str(e)}")
            raise
        except DatabaseError as e:
            logger.error(f"Failed to store posts: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in post processing: {str(e)}")
            raise

    async def get_processed_posts(
        self,
        subreddit: Optional[str] = None,
        min_score: Optional[float] = None,
        limit: int = 10
    ) -> List[FilteredPost]:
        """
        Retrieve processed posts from database.
        
        Args:
            subreddit: Optional subreddit filter
            min_score: Optional minimum normalized score
            limit: Maximum number of posts to return
            
        Returns:
            List of filtered posts
            
        Raises:
            DatabaseError: If retrieval fails
        """
        try:
            return await self.post_repository.search_posts(
                subreddit=subreddit,
                min_score=min_score,
                limit=limit
            )
        except DatabaseError as e:
            logger.error(f"Failed to retrieve posts: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error retrieving posts: {str(e)}")
            raise DatabaseError(str(e))

    async def process_batch(
        self,
        subreddits: List[str],
        posts_per_subreddit: int = 5,
        mode: str = "top"
    ) -> dict:
        """
        Process posts from multiple subreddits.
        
        Args:
            subreddits: List of subreddits to process
            posts_per_subreddit: Number of posts to fetch per subreddit
            mode: Sorting mode (hot/new/top)
            
        Returns:
            Dictionary with results per subreddit
        """
        results = {}
        for subreddit in subreddits:
            try:
                filtered_posts = await self.fetch_and_process_posts(
                    subreddit=subreddit,
                    limit=posts_per_subreddit,
                    mode=mode
                )
                results[subreddit] = {
                    "success": True,
                    "processed_count": len(filtered_posts)
                }
            except Exception as e:
                logger.error(f"Failed to process r/{subreddit}: {str(e)}")
                results[subreddit] = {
                    "success": False,
                    "error": str(e)
                }

        return results