from typing import List, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.logging import logger
from app.domain.models.published_article import PublishedArticle, PublishingStats
from app.domain.models.story_summary import StorySummary
from app.infrastructure.wordpress.client import WordPressClient
from app.infrastructure.database.repository import PublisherRepository
from app.infrastructure.llm.factory import create_llm_client
from app.services.content_generator import ContentGeneratorService
from app.services.publisher_service import PublisherService

router = APIRouter()

async def get_publisher_service(db: AsyncSession = Depends(get_db)) -> PublisherService:
    """Dependency for getting publisher service instance."""
    wp_client = WordPressClient()
    repository = PublisherRepository(db)
    llm_client = create_llm_client()
    content_generator = ContentGeneratorService(llm_client, repository)
    return PublisherService(wp_client, repository, content_generator)

@router.post("/articles/", response_model=PublishedArticle)
async def create_article(
    story_summary_id: int,
    background_tasks: BackgroundTasks,
    service: PublisherService = Depends(get_publisher_service),
    auto_publish: bool = False
):
    """
    Create and optionally publish a new article from a story summary.
    
    - **story_summary_id**: ID of the story summary to create article from
    - **auto_publish**: If true, automatically publish to WordPress after creation
    """
    try:
        # First fetch the story summary
        summary = await service.repository.get_story_summary(story_summary_id)
        if not summary:
            raise HTTPException(
                status_code=404,
                detail=f"Story summary {story_summary_id} not found"
            )

        # Create article with actual data
        article = await service.content_generator.create_article(
            story_summary_id=story_summary_id,
            title=summary.title,
            summary=summary.summary,
            full_story=summary.generated_story
        )
        
        if auto_publish:
            background_tasks.add_task(
                service.publish_article,
                article_id=article.id,
                auto_publish=True
            )
            logger.info(f"Scheduled article {article.id} for publishing")
        
        return article
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating article: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/articles/{article_id}/publish", response_model=PublishedArticle)
async def publish_article(
    article_id: int,
    service: PublisherService = Depends(get_publisher_service),
    auto_publish: bool = False
):
    """
    Publish an existing article to WordPress.
    
    - **article_id**: ID of the article to publish
    - **auto_publish**: If true, publish immediately; if false, save as draft
    """
    try:
        return await service.publish_article(
            article_id=article_id,
            auto_publish=auto_publish
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error publishing article: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/articles/{article_id}", response_model=PublishedArticle)
async def get_article(
    article_id: int,
    service: PublisherService = Depends(get_publisher_service)
):
    """
    Get an article by ID.
    
    - **article_id**: ID of the article to retrieve
    """
    try:
        article = await service.repository.get_article_by_id(article_id)
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        return article
    except Exception as e:
        logger.error(f"Error getting article: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/articles/{article_id}", response_model=PublishedArticle)
async def update_article(
    article_id: int,
    updates: Dict,
    service: PublisherService = Depends(get_publisher_service)
):
    """
    Update an existing article.
    
    - **article_id**: ID of the article to update
    - **updates**: Dictionary of fields to update
    """
    try:
        updated = await service.update_published_article(
            article_id=article_id,
            updates=updates
        )
        if not updated:
            raise HTTPException(status_code=404, detail="Article not found")
        return updated
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating article: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/articles/", response_model=List[PublishedArticle])
async def list_articles(
    status: Optional[str] = None,
    limit: int = 10,
    service: PublisherService = Depends(get_publisher_service)
):
    """
    List articles with optional status filter.
    
    - **status**: Filter by status (e.g., 'unpublished', 'published', 'failed')
    - **limit**: Maximum number of articles to return
    """
    try:
        if status == "unpublished":
            return await service.repository.get_unpublished_articles(limit)
        return await service.repository.get_latest_articles(limit)
    except Exception as e:
        logger.error(f"Error listing articles: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats", response_model=PublishingStats)
async def get_stats(
    service: PublisherService = Depends(get_publisher_service)
):
    """Get publishing statistics."""
    try:
        return await service.get_publishing_stats()
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/process-batch")
async def process_batch(
    batch_size: int = 10,
    auto_publish: bool = False,
    service: PublisherService = Depends(get_publisher_service)
):
    """
    Process a batch of unpublished articles.
    
    - **batch_size**: Number of articles to process
    - **auto_publish**: If true, publish articles immediately
    """
    try:
        processed = await service.process_unpublished_articles(
            batch_size=batch_size,
            auto_publish=auto_publish
        )
        return {
            "processed_count": len(processed),
            "status": "success",
            "articles": processed
        }
    except Exception as e:
        logger.error(f"Error processing batch: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/retry-failed")
async def retry_failed(
    max_retries: int = 3,
    service: PublisherService = Depends(get_publisher_service)
):
    """
    Retry failed article publications.
    
    - **max_retries**: Maximum number of retry attempts per article
    """
    try:
        retried = await service.retry_failed_articles(max_retries=max_retries)
        return {
            "retried_count": len(retried),
            "status": "success",
            "articles": retried
        }
    except Exception as e:
        logger.error(f"Error retrying failed articles: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def check_health(
    service: PublisherService = Depends(get_publisher_service)
):
    """Check service health including WordPress connection."""
    try:
        wp_status = await service.check_wordpress_connection()
        return {
            "status": "healthy" if wp_status else "unhealthy",
            "wordpress_api": "connected" if wp_status else "disconnected"
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
