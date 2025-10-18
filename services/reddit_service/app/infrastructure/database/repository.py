# app/infrastructure/database/repository.py
from datetime import datetime
from typing import List, Optional
from sqlalchemy import select, and_, desc
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.models.filtered_post import FilteredPost
from app.infrastructure.database.models import RedditPostDB
from app.core.exceptions import DatabaseError
# At the top of repository.py, add:
from app.domain.models.reddit_comment import RedditComment
import logging


logger = logging.getLogger(__name__)

class PostRepository:
    """Repository for database operations on posts."""
    
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_posts(self, posts: List[FilteredPost]) -> None:
        """
        Save filtered posts to database via Data Service Lambda.
        
        Args:
            posts: List of filtered posts to save
            
        Raises:
            DatabaseError: If saving fails
        """
        try:
            # Use Lambda client instead of direct database access
            from app.infrastructure.lambda_client import DataServiceLambdaClient
            lambda_client = DataServiceLambdaClient()
            
            result = await lambda_client.save_reddit_posts(posts)
            
            if result.get('success'):
                logger.info(f"Saved {len(posts)} posts to database via Data Service Lambda")
            else:
                logger.error(f"Failed to save posts via Data Service Lambda: {result.get('error')}")
                raise DatabaseError(f"Failed to save posts via Data Service Lambda: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"Failed to save posts: {str(e)}")
            raise DatabaseError(f"Failed to save posts: {str(e)}")

    async def get_recent_posts(
        self,
        limit: int = 10,
        subreddit: Optional[str] = None
    ) -> List[FilteredPost]:
        """Get recent Reddit posts via Data Service Lambda."""
        try:
            # Use Lambda client instead of direct database access
            from app.infrastructure.lambda_client import DataServiceLambdaClient
            lambda_client = DataServiceLambdaClient()
            
            posts = await lambda_client.get_reddit_posts(limit=limit, subreddit=subreddit)
            logger.info(f"Retrieved {len(posts)} posts via Data Service Lambda")
            return posts
            
        except Exception as e:
            logger.error(f"Failed to get recent posts: {str(e)}")
            raise DatabaseError(f"Failed to get recent posts: {str(e)}")

    async def search_posts(
        self,
        subreddit: Optional[str] = None,
        min_score: Optional[float] = None,
        limit: int = 10
    ) -> List[FilteredPost]:
        """Search posts with filters via Data Service Lambda."""
        try:
            # For now, use get_recent_posts as a fallback
            # TODO: Implement proper search functionality in Data Service Lambda
            return await self.get_recent_posts(limit=limit, subreddit=subreddit)
            
        except Exception as e:
            logger.error(f"Failed to search posts: {str(e)}")
            raise DatabaseError(f"Failed to search posts: {str(e)}")

    def _to_db_model(self, post: FilteredPost) -> RedditPostDB:
        """Convert domain model to database model."""
        # Convert comments to JSON-serializable format
        top_comments_json = []
        if post.top_comments:
            for comment in post.top_comments:
                comment_dict = comment.dict()
                # Convert datetime to ISO format string
                comment_dict['created_at'] = comment_dict['created_at'].isoformat()
                top_comments_json.append(comment_dict)

        return RedditPostDB(
            source=post.source,
            subreddit=post.subreddit,
            title=post.title,
            url=str(post.url),
            author=post.author,
            score=post.score,
            comments=post.comments,
            top_comments=top_comments_json,  # Use the JSON-serializable list
            normalized_score=post.normalized_score,
            created_at=post.created_at,
            fetched_at=datetime.utcnow(),
            post_text=post.post_text  # Add this line
        )

    def _to_domain_model(self, db_post: RedditPostDB) -> FilteredPost:
        """Convert database model to domain model."""
        top_comments = []
        if db_post.top_comments:
            for comment_data in db_post.top_comments:
                comment_data['created_at'] = datetime.fromisoformat(comment_data['created_at'])
                top_comments.append(RedditComment(**comment_data))

        return FilteredPost(
            source=db_post.source,
            subreddit=db_post.subreddit,
            title=db_post.title,
            url=db_post.url,
            author=db_post.author,
            score=db_post.score,
            comments=db_post.comments,
            top_comments=top_comments,
            normalized_score=db_post.normalized_score,
            created_at=db_post.created_at,
            post_text=db_post.post_text
        )