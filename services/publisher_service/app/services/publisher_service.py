from typing import Optional, List, Dict, Any
from datetime import datetime
import tempfile
import os

from app.domain.models.published_article import PublishedArticle, PublishingStats
from app.domain.models.wp_post import WPPostCreate, WPPostResponse, WPMedia
from app.infrastructure.wordpress.client import WordPressClient
from app.infrastructure.database.repository import PublisherRepository
from app.services.content_generator import ContentGeneratorService
from app.core.config import settings
from app.core.logging import logger

class PublisherService:
    """Service for publishing articles to WordPress."""
    
    def __init__(
        self,
        wordpress_client: WordPressClient,
        publisher_repository: PublisherRepository,
        content_generator: ContentGeneratorService
    ):
        self.wp_client = wordpress_client
        self.repository = publisher_repository
        self.content_generator = content_generator

    async def publish_article(
        self,
        article_id: int,
        auto_publish: bool = False
    ) -> PublishedArticle:
        """Publish an article to WordPress."""
        try:
            logger.info(f"\n=== Publishing Article {article_id} ===")
            
            # Get article from database
            article = await self.repository.get_article_by_id(article_id)
            if not article:
                raise ValueError(f"Article {article_id} not found")
            
            # Check if already published
            if article.status == "published":
                logger.info(f"Article {article_id} is already published")
                return article
            
            # Check content quality
            # Comment out this block
            """
            # Check content quality
            is_quality_ok, issues = await self.content_generator.check_content_quality(
                content=article.content,
                title=article.title
            )
            
            if not is_quality_ok:
                logger.warning(f"Content quality issues found: {issues}")
                await self.repository.log_publishing_error(
                    article_id=article_id,
                    error_type="quality_check",
                    error_message="Content quality issues found",
                    error_details={"issues": issues}
                )
                return article
            """

            # Prepare WordPress post
            wp_post = await self.content_generator.prepare_wordpress_post(
                article=article,
                category_id=settings.WP_CATEGORY_ID
            )
            
            # Set status based on auto_publish setting
            wp_post.status = "publish" if auto_publish else "draft"
            
            try:
                # Create post in WordPress
                response = await self.wp_client.create_post(wp_post)
                
                # Update article with WordPress data
                updates = {
                    "wordpress_post_id": response.id,
                    "wordpress_url": str(response.link),
                    "status": "published" if auto_publish else "draft",
                     "published_at": None 
                    #"published_at": datetime.utcnow() if auto_publish else None
                }
                
                updated_article = await self.repository.update_article(
                    article_id=article_id,
                    updates=updates
                )
                
                logger.info(
                    f"Successfully {'published' if auto_publish else 'drafted'} "
                    f"article {article_id} to WordPress"
                )
                return updated_article
                
            except Exception as e:
                await self.repository.log_publishing_error(
                    article_id=article_id,
                    error_type="wordpress_api",
                    error_message=str(e)
                )
                raise
            
        except Exception as e:
            logger.error(f"Error publishing article {article_id}: {str(e)}")
            raise

    async def update_published_article(
        self,
        article_id: int,
        updates: Dict[str, Any]
    ) -> PublishedArticle:
        """Update an already published article."""
        try:
            logger.info(f"\n=== Updating Published Article {article_id} ===")
            
            # Get article
            article = await self.repository.get_article_by_id(article_id)
            if not article:
                raise ValueError(f"Article {article_id} not found")
            
            if not article.wordpress_post_id:
                raise ValueError(f"Article {article_id} has not been published to WordPress")
            
            # Update WordPress post
            wp_post = WPPostCreate(
                title=updates.get("title", article.title),
                content=updates.get("content", article.content),
                status=article.status,
                featured_media=article.featured_media_url,
                categories=[settings.WP_CATEGORY_ID],
                tags=updates.get("tags", article.tags),
                meta={
                    "_yoast_wpseo_metadesc": updates.get("seo_description", article.seo_description),
                    "_yoast_wpseo_title": updates.get("seo_title", article.seo_title),
                    "_newsettler_source_id": article.story_summary_id,
                    "_newsettler_metadata": article.generation_metadata
                }
            )
            
            # Update in WordPress
            await self.wp_client.update_post(article.wordpress_post_id, wp_post)
            
            # Update local database
            updated_article = await self.repository.update_article(
                article_id=article_id,
                updates={
                    **updates,
                    "last_updated_at": datetime.utcnow()
                }
            )
            
            logger.info(f"Successfully updated article {article_id} in WordPress")
            return updated_article
            
        except Exception as e:
            logger.error(f"Error updating article {article_id}: {str(e)}")
            raise

    async def process_unpublished_articles(
        self,
        batch_size: int = 10,
        auto_publish: bool = False
    ) -> List[PublishedArticle]:
        """Process a batch of unpublished articles."""
        try:
            logger.info(f"\n=== Processing Unpublished Articles (batch_size={batch_size}) ===")
            
            # Get unpublished articles
            articles = await self.repository.get_unpublished_articles(limit=batch_size)
            
            processed_articles = []
            for article in articles:
                try:
                    processed = await self.publish_article(
                        article_id=article.id,
                        auto_publish=auto_publish
                    )
                    processed_articles.append(processed)
                except Exception as e:
                    logger.error(f"Error processing article {article.id}: {str(e)}")
                    continue
            
            return processed_articles
            
        except Exception as e:
            logger.error(f"Error processing unpublished articles: {str(e)}")
            raise

    async def get_publishing_stats(self) -> PublishingStats:
        """Get publishing statistics."""
        return await self.repository.get_publishing_stats()

    async def retry_failed_articles(
        self,
        max_retries: int = 3
    ) -> List[PublishedArticle]:
        """Retry publishing failed articles."""
        try:
            logger.info("\n=== Retrying Failed Articles ===")
            
            # Get failed articles that haven't exceeded max retries
            failed_articles = await self.repository.get_failed_articles(max_retries)
            
            retried_articles = []
            for article in failed_articles:
                try:
                    retried = await self.publish_article(
                        article_id=article.id,
                        auto_publish=False  # Always draft for retries
                    )
                    retried_articles.append(retried)
                except Exception as e:
                    logger.error(f"Error retrying article {article.id}: {str(e)}")
                    continue
            
            return retried_articles
            
        except Exception as e:
            logger.error(f"Error retrying failed articles: {str(e)}")
            raise

    async def check_wordpress_connection(self) -> bool:
        """Check WordPress API connection."""
        try:
            return await self.wp_client.check_api_status()
        except Exception as e:
            logger.error(f"WordPress connection check failed: {str(e)}")
            return False
