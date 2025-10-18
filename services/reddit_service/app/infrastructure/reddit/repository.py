# app/infrastructure/reddit/repository.py
from datetime import datetime
from typing import List, Optional
import logging
from app.domain.models.reddit_post import RedditPost
from app.domain.models.reddit_comment import RedditComment
from app.infrastructure.reddit.client import RedditClient
from app.core.exceptions import RedditFetchError

logger = logging.getLogger(__name__)

class RedditRepository:
    """Repository for fetching posts from Reddit."""

    def __init__(self, client: RedditClient):
        self.client = client

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
            limit: Maximum number of posts to fetch
            mode: Sorting mode (hot/new/top)
            before: Optional timestamp to fetch posts before
        """
        try:
            logger.info(f"Fetching {limit} {mode} posts from r/{subreddit}")
            
            # Validate mode
            if mode not in ["hot", "new", "top"]:
                raise ValueError(f"Invalid mode: {mode}")

            # Fetch raw posts from Reddit with comments
            raw_posts = await self.client.get_posts(
                subreddit=subreddit,
                limit=limit,
                mode=mode,
                before=before,
                fetch_comments=True,
                comment_limit=10
            )

            # Convert to domain models
            posts = []
            for raw_post in raw_posts:
                try:
                    # Convert comments to RedditComment objects
                    top_comments = []
                    for comment_data in raw_post.get("top_comments", []):
                        try:
                            comment = RedditComment(
                                id=comment_data["id"],
                                author=comment_data["author"],
                                body=comment_data["body"],
                                score=comment_data["score"],
                                created_at=comment_data["created_at"],
                                is_submitter=comment_data["is_submitter"]
                            )
                            top_comments.append(comment)
                        except Exception as e:
                            logger.warning(f"Failed to parse comment: {str(e)}")
                            continue

                    # Create RedditPost with comments
                    post = RedditPost(
                        source="reddit",
                        subreddit=raw_post["subreddit"],
                        title=raw_post["title"],
                        url=raw_post["url"],
                        author=raw_post["author"],
                        score=raw_post["score"],
                        comments=raw_post["num_comments"],
                        top_comments=top_comments,
                        normalized_score=raw_post["score"],
                        created_at=datetime.fromtimestamp(raw_post["created_utc"]),
                        post_text=raw_post.get("post_text", "")
                    )
                    posts.append(post)
                except Exception as e:
                    logger.warning(f"Failed to parse post: {str(e)}")
                    continue

            logger.info(f"Successfully fetched {len(posts)} posts from r/{subreddit}")
            return posts

        except Exception as e:
            logger.error(f"Failed to fetch posts from r/{subreddit}: {str(e)}")
            raise RedditFetchError(f"Failed to fetch posts: {str(e)}")

    async def fetch_subreddit_info(self, subreddit: str) -> dict:
        """Fetch information about a subreddit."""
        try:
            logger.info(f"Fetching info for r/{subreddit}")
            return await self.client.get_subreddit_info(subreddit)
        except Exception as e:
            logger.error(f"Failed to fetch subreddit info for r/{subreddit}: {str(e)}")
            raise RedditFetchError(f"Failed to fetch subreddit info: {str(e)}")

    async def check_subreddit_exists(self, subreddit: str) -> bool:
        """Check if a subreddit exists."""
        try:
            await self.fetch_subreddit_info(subreddit)
            return True
        except RedditFetchError:
            return False