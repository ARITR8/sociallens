from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import select, func, and_, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from app.domain.models.published_article import (
    PublishedArticle,
    PublishedArticleCreate,
    PublishingStats
)
from app.domain.models.story_summary import StorySummary
from app.infrastructure.database.models import PublishedArticleDB, PublishingErrorDB
from app.core.logging import logger

class PublisherRepository:
    """Repository for handling published article database operations."""

    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def get_story_summary(self, summary_id: int) -> Optional[StorySummary]:
        """Get story summary by ID."""
        try:
            logger.info(f"Fetching story summary with ID: {summary_id}")
            query = text("""
                SELECT 
                    id, 
                    post_id,
                    title, 
                    summary, 
                    generated_story,
                    model_used,
                    generation_metadata,
                    created_at
                FROM story_summaries 
                WHERE id = :id
            """)
            result = await self.db.execute(query, {"id": summary_id})
            row = result.fetchone()
            
            if row:
                logger.info(f"Found story summary: {row.title[:50]}...")
                return StorySummary(
                    id=row.id,
                    post_id=row.post_id,
                    title=row.title,
                    summary=row.summary,
                    generated_story=row.generated_story,
                    model_used=row.model_used,
                    generation_metadata=row.generation_metadata,
                    created_at=row.created_at
                )
            
            logger.warning(f"Story summary {summary_id} not found")
            return None
            
        except Exception as e:
            logger.error(f"Error fetching story summary {summary_id}: {str(e)}")
            raise

    async def create_article(self, article: PublishedArticleCreate) -> PublishedArticle:
        """Create a new published article."""
        try:
            logger.info(f"Creating new article for summary ID: {article.story_summary_id}")
            
            # First verify story summary exists
            summary = await self.get_story_summary(article.story_summary_id)
            if not summary:
                raise ValueError(f"Story summary {article.story_summary_id} not found")
            
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
            
            self.db.add(db_article)
            await self.db.flush()
            await self.db.refresh(db_article)
            
            logger.info(f"Successfully created article with ID: {db_article.id}")
            return PublishedArticle.model_validate(db_article)
        
        except Exception as e:
            logger.error(f"Error creating article: {str(e)}")
            raise

    async def update_article(self, article_id: int, updates: Dict[str, Any]) -> Optional[PublishedArticle]:
        """Update an existing article."""
        try:
            query = select(PublishedArticleDB).where(PublishedArticleDB.id == article_id)
            result = await self.db.execute(query)
            db_article = result.scalar_one_or_none()
            
            if db_article:
                for key, value in updates.items():
                    setattr(db_article, key, value)
                db_article.last_updated_at = datetime.utcnow()
                
                await self.db.flush()
                await self.db.refresh(db_article)
                logger.info(f"Successfully updated article {article_id}")
                return PublishedArticle.model_validate(db_article)
            
            logger.warning(f"Article {article_id} not found for update")
            return None
            
        except Exception as e:
            logger.error(f"Error updating article {article_id}: {str(e)}")
            raise

    async def get_article_by_id(self, article_id: int) -> Optional[PublishedArticle]:
        """Get an article by its ID."""
        try:
            query = select(PublishedArticleDB).where(PublishedArticleDB.id == article_id)
            result = await self.db.execute(query)
            db_article = result.scalar_one_or_none()
            
            if db_article:
                return PublishedArticle.model_validate(db_article)
            return None
            
        except Exception as e:
            logger.error(f"Error getting article by ID {article_id}: {str(e)}")
            raise

    async def get_by_summary_id(self, summary_id: int) -> Optional[PublishedArticle]:
        """Get an article by its story summary ID."""
        try:
            query = select(PublishedArticleDB).where(PublishedArticleDB.story_summary_id == summary_id)
            result = await self.db.execute(query)
            db_article = result.scalar_one_or_none()
            
            if db_article:
                return PublishedArticle.model_validate(db_article)
            return None
            
        except Exception as e:
            logger.error(f"Error getting article by summary ID {summary_id}: {str(e)}")
            raise

    async def get_unpublished_articles(self, limit: int = 10) -> List[PublishedArticle]:
        """Get articles that haven't been published yet."""
        try:
            query = (
                select(PublishedArticleDB)
                .where(
                    and_(
                        PublishedArticleDB.status == "draft",
                        PublishedArticleDB.publish_attempts < 3
                    )
                )
                .order_by(PublishedArticleDB.created_at.asc())
                .limit(limit)
            )
            result = await self.db.execute(query)
            db_articles = result.scalars().all()
            
            return [PublishedArticle.model_validate(a) for a in db_articles]
            
        except Exception as e:
            logger.error(f"Error getting unpublished articles: {str(e)}")
            raise

    async def log_publishing_error(
        self,
        article_id: int,
        error_type: str,
        error_message: str,
        error_details: Optional[Dict] = None
    ) -> None:
        """Log a publishing error."""
        try:
            error = PublishingErrorDB(
                article_id=article_id,
                error_type=error_type,
                error_message=error_message,
                error_details=error_details
            )
            self.db.add(error)
            
            # Update article status and attempts
            await self.update_article(
                article_id,
                {
                    "status": "failed",
                    "publish_attempts": PublishedArticleDB.publish_attempts + 1
                }
            )
            
            logger.info(f"Logged publishing error for article {article_id}: {error_message}")
            
        except Exception as e:
            logger.error(f"Error logging publishing error: {str(e)}")
            raise

    async def get_publishing_stats(self) -> PublishingStats:
        """Get publishing statistics."""
        try:
            # Get counts by status
            status_counts = (
                select(
                    PublishedArticleDB.status,
                    func.count(PublishedArticleDB.id).label("count")
                )
                .group_by(PublishedArticleDB.status)
            )
            result = await self.db.execute(status_counts)
            counts = dict(result.fetchall())
            
            # Calculate average processing time
            avg_time = (
                select(
                    func.avg(
                        func.extract(
                            'epoch',
                            PublishedArticleDB.published_at - PublishedArticleDB.created_at
                        )
                    )
                )
                .where(PublishedArticleDB.published_at.isnot(None))
            )
            result = await self.db.execute(avg_time)
            avg_processing_time = result.scalar() or 0
            
            total = sum(counts.values())
            published = counts.get('published', 0)
            
            return PublishingStats(
                total_articles=total,
                published_count=published,
                draft_count=counts.get('draft', 0),
                failed_count=counts.get('failed', 0),
                average_processing_time=float(avg_processing_time),
                success_rate=published / total if total > 0 else 0
            )
            
        except Exception as e:
            logger.error(f"Error getting publishing stats: {str(e)}")
            raise
