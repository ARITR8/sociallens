# app/domain/filters/post_filter.py
import logging
from typing import List
from app.domain.models.filtered_post import FilteredPost
from app.domain.filters.config import FilterConfig
from app.core.exceptions import FilterError

logger = logging.getLogger(__name__)

class PostFilter:
    """Post filtering strategy."""
    def __init__(self, config: FilterConfig):
        self.config = config

    def filter_posts(self, posts: List[FilteredPost]) -> List[FilteredPost]:
        """
        Filter multiple posts.
        
        Args:
            posts: List of posts to filter
            
        Returns:
            List of posts that pass all filtering criteria
            
        Raises:
            FilterError: If filtering process fails
        """
        try:
            filtered_posts = [
                post for post in posts 
                if self.is_valid_post(post)
            ]
            logger.info(f"Filtered {len(posts)} posts to {len(filtered_posts)} posts")
            return filtered_posts
        except Exception as e:
            raise FilterError(f"Failed to filter posts: {str(e)}")

    def is_valid_post(self, post: FilteredPost) -> bool:
        """
        Check if post meets all quality criteria.
        
        Args:
            post: Post to validate
            
        Returns:
            bool: Whether post meets all criteria
        """
        try:
            # Check title length
            if len(post.title) > self.config.MAX_TITLE_LENGTH:
                logger.debug(f"Post {post.url} rejected: Title too long")
                return False

            # Check for NSFW content
            if self._is_nsfw(post):
                logger.debug(f"Post {post.url} rejected: NSFW content")
                return False
                
            # Check score threshold
            if not self._meets_score_threshold(post):
                logger.debug(f"Post {post.url} rejected: Below score threshold")
                return False
                
            # Check comment threshold
            if post.comments < self.config.MIN_COMMENTS:
                logger.debug(f"Post {post.url} rejected: Too few comments")
                return False
                
            # Check keywords
            if not self._has_relevant_keywords(post):
                logger.debug(f"Post {post.url} rejected: No relevant keywords")
                return False
                
            logger.debug(f"Post {post.url} accepted")
            return True
            
        except Exception as e:
            logger.error(f"Error validating post {post.url}: {str(e)}")
            return False

    def _is_nsfw(self, post: FilteredPost) -> bool:
        """Check if post contains NSFW indicators."""
        title_lower = post.title.lower()
        return any(tag.lower() in title_lower for tag in self.config.NSFW_TAGS)

    def _meets_score_threshold(self, post: FilteredPost) -> bool:
        """Check if post meets minimum score threshold."""
        return post.normalized_score >= self.config.MIN_NORMALIZED_SCORE

    def _has_relevant_keywords(self, post: FilteredPost) -> bool:
        """Check if post contains any relevant keywords."""
        title_lower = post.title.lower()
        return any(keyword.lower() in title_lower for keyword in self.config.KEYWORDS)