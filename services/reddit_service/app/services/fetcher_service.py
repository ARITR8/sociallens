# app/services/fetcher_service.py
import logging
from typing import List, Optional
from datetime import datetime
from app.domain.models.reddit_post import RedditPost
from app.infrastructure.reddit.repository import RedditRepository
from app.core.exceptions import RedditFetchError

logger = logging.getLogger(__name__)

class FetcherService:
    """Service for fetching Reddit posts."""

    def __init__(self, repository: RedditRepository):
        """
        Initialize FetcherService.
        
        Args:
            repository: Reddit repository instance
        """
        self.repository = repository

    async def fetch_posts(
        self,
        subreddit: str,
        limit: int = 5,
        mode: str = "top",
        before: Optional[datetime] = None
    ) -> List[RedditPost]:
        """
        Fetch posts from specified subreddit.
        
        Args:
            subreddit: Subreddit name to fetch from
            limit: Maximum number of posts to fetch (default: 5)
            mode: Sorting mode (hot/new/top) (default: top)
            before: Optional timestamp to fetch posts before
            
        Returns:
            List of RedditPost models
            
        Raises:
            RedditFetchError: If fetching or validation fails
            ValueError: If invalid parameters provided
        """
        try:
            # Validate inputs
            self._validate_inputs(subreddit, limit, mode)

            # Check if subreddit exists
            exists = await self.repository.check_subreddit_exists(subreddit)
            if not exists:
                raise RedditFetchError(f"Subreddit r/{subreddit} does not exist")

            # Fetch posts
            logger.info(f"Fetching {limit} {mode} posts from r/{subreddit}")
            return await self.repository.fetch_posts(
                subreddit=subreddit,
                limit=limit,
                mode=mode,
                before=before
            )

        except RedditFetchError:
            raise
        except Exception as e:
            logger.error(f"Failed to fetch posts from r/{subreddit}: {str(e)}")
            raise RedditFetchError(f"Failed to fetch posts: {str(e)}")

    def _validate_inputs(self, subreddit: str, limit: int, mode: str) -> None:
        """
        Validate input parameters.
        
        Args:
            subreddit: Subreddit name
            limit: Number of posts to fetch
            mode: Sorting mode
            
        Raises:
            ValueError: If any parameter is invalid
        """
        # Validate subreddit
        if not subreddit or not isinstance(subreddit, str):
            raise ValueError("Invalid subreddit name")
        
        # Validate limit
        if not isinstance(limit, int) or limit < 1 or limit > 100:
            raise ValueError("Limit must be between 1 and 100")
        
        # Validate mode
        valid_modes = ["hot", "new", "top"]
        if mode not in valid_modes:
            raise ValueError(f"Mode must be one of: {', '.join(valid_modes)}")

    async def get_subreddit_info(self, subreddit: str) -> dict:
        """
        Get information about a subreddit.
        
        Args:
            subreddit: Subreddit name
            
        Returns:
            Dictionary containing subreddit information
            
        Raises:
            RedditFetchError: If fetching fails
        """
        try:
            if not subreddit or not isinstance(subreddit, str):
                raise ValueError("Invalid subreddit name")

            return await self.repository.fetch_subreddit_info(subreddit)
        except Exception as e:
            logger.error(f"Failed to get info for r/{subreddit}: {str(e)}")
            raise RedditFetchError(f"Failed to get subreddit info: {str(e)}")

    async def check_subreddit_status(self, subreddit: str) -> dict:
        """
        Check status and basic information of a subreddit.
        
        Args:
            subreddit: Subreddit name
            
        Returns:
            Dictionary containing status information
        """
        try:
            info = await self.get_subreddit_info(subreddit)
            return {
                "exists": True,
                "public": info["public"],
                "over18": info["over18"],
                "subscribers": info["subscribers"]
            }
        except RedditFetchError:
            return {
                "exists": False,
                "error": "Subreddit not found or inaccessible"
            }
        except Exception as e:
            return {
                "exists": False,
                "error": str(e)
            }