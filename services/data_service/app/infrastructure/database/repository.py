from typing import List, Optional, Dict, Any
from sqlalchemy import select, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from app.domain.models.reddit_post import FilteredPost, RedditComment
from app.domain.models.story_summary import StorySummary, StorySummaryCreate
from app.domain.models.published_article import PublishedArticle, PublishedArticleCreate
from app.infrastructure.database.models import RedditPostDB, StorySummaryDB, PublishedArticleDB
from app.core.logging import logger
from datetime import datetime

class DataRepository:
    """Repository for all database operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session

    # Reddit Posts Operations
    async def save_reddit_posts(self, posts: List[FilteredPost]) -> None:
        """Save filtered Reddit posts to database."""
        try:
            db_posts = [self._to_reddit_db_model(post) for post in posts]
            self.session.add_all(db_posts)
            await self.session.commit()
            logger.info(f"Saved {len(posts)} Reddit posts to database")
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Failed to save Reddit posts: {str(e)}")
            raise

    async def get_reddit_posts(self, limit: int = 10, subreddit: Optional[str] = None) -> List[FilteredPost]:
        """Get recent Reddit posts."""
        try:
            query = select(RedditPostDB).order_by(desc(RedditPostDB.created_at))
            
            if subreddit:
                query = query.where(RedditPostDB.subreddit == subreddit)
            
            query = query.limit(limit)
            
            result = await self.session.execute(query)
            db_posts = result.scalars().all()
            
            return [self._to_reddit_domain_model(post) for post in db_posts]
        except SQLAlchemyError as e:
            logger.error(f"Failed to get Reddit posts: {str(e)}")
            raise

    # Story Summary Operations
    async def create_story_summary(self, summary: StorySummaryCreate) -> StorySummary:
        """Create a new story summary."""
        try:
            db_summary = StorySummaryDB(
                post_id=summary.post_id,
                title=summary.title,
                summary=summary.summary,
                generated_story=summary.generated_story,
                model_used=summary.model_used,
                generation_metadata=summary.generation_metadata
            )

            self.session.add(db_summary)
            await self.session.commit()
            await self.session.refresh(db_summary)

            return StorySummary.model_validate(db_summary)
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Failed to create story summary: {str(e)}")
            raise

    async def get_story_summary_by_id(self, summary_id: int) -> Optional[StorySummary]:
        """Get a story summary by ID."""
        try:
            query = select(StorySummaryDB).where(StorySummaryDB.id == summary_id)
            result = await self.session.execute(query)
            db_summary = result.scalar_one_or_none()
            return StorySummary.model_validate(db_summary) if db_summary else None
        except SQLAlchemyError as e:
            logger.error(f"Failed to get story summary: {str(e)}")
            raise

    async def get_story_summary_by_post_id(self, post_id: int) -> Optional[StorySummary]:
        """Get a story summary by post ID."""
        try:
            query = select(StorySummaryDB).where(StorySummaryDB.post_id == post_id)
            result = await self.session.execute(query)
            db_summary = result.scalar_one_or_none()
            return StorySummary.model_validate(db_summary) if db_summary else None
        except SQLAlchemyError as e:
            logger.error(f"Failed to get story summary by post ID: {str(e)}")
            raise

    # Published Article Operations
    async def create_published_article(self, article: PublishedArticleCreate) -> PublishedArticle:
        """Create a new published article."""
        try:
            db_article = PublishedArticleDB(
                story_summary_id=article.story_summary_id,
                title=article.title,
                content=article.content,
                seo_title=article.seo_title,
                seo_description=article.seo_description,
                featured_image_url=article.featured_image_url,
                tags=article.tags,
                status=article.status,
                generation_metadata=article.generation_metadata
            )
            
            self.session.add(db_article)
            await self.session.flush()
            await self.session.refresh(db_article)
            
            return PublishedArticle.model_validate(db_article)
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Failed to create published article: {str(e)}")
            raise

    async def update_published_article(self, article_id: int, updates: Dict[str, Any]) -> Optional[PublishedArticle]:
        """Update a published article."""
        try:
            query = select(PublishedArticleDB).where(PublishedArticleDB.id == article_id)
            result = await self.session.execute(query)
            db_article = result.scalar_one_or_none()
            
            if not db_article:
                return None
            
            for key, value in updates.items():
                if hasattr(db_article, key):
                    setattr(db_article, key, value)
            
            db_article.last_updated_at = datetime.utcnow()
            
            await self.session.commit()
            await self.session.refresh(db_article)
            
            return PublishedArticle.model_validate(db_article)
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Failed to update published article: {str(e)}")
            raise

    # Helper methods
    def _to_reddit_db_model(self, post: FilteredPost) -> RedditPostDB:
        """Convert domain model to database model."""
        top_comments_json = []
        if post.top_comments:
            for comment in post.top_comments:
                comment_dict = comment.dict()
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
            top_comments=top_comments_json,
            normalized_score=post.normalized_score,
            created_at=post.created_at,
            fetched_at=datetime.utcnow(),
            post_text=post.post_text
        )

    def _to_reddit_domain_model(self, db_post: RedditPostDB) -> FilteredPost:
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