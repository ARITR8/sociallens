from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.story_summary import StorySummary, StorySummaryCreate
from app.infrastructure.database.models import StorySummaryDB
import logging

logger = logging.getLogger(__name__)

class SummaryRepository:
    """Repository for handling story summary database operations via Lambda-to-Lambda pattern."""

    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def create(self, summary: StorySummaryCreate) -> StorySummary:
        """Create a new story summary via Data Service Lambda."""
        try:
            logger.info("[SummaryRepository] Creating new summary via Data Service Lambda")

            # Use Lambda client instead of direct database access
            from app.infrastructure.lambda_client import DataServiceLambdaClient
            lambda_client = DataServiceLambdaClient()
            
            result = await lambda_client.create_story_summary(summary)
            logger.info("[SummaryRepository] Successfully created summary via Data Service Lambda")
            return result

        except Exception as e:
            logger.error(f"[SummaryRepository] Error creating summary: {str(e)}")
            raise

    async def get_by_id(self, summary_id: int) -> Optional[StorySummary]:
        """Get a summary by its ID via Data Service Lambda."""
        try:
            # Use Lambda client instead of direct database access
            from app.infrastructure.lambda_client import DataServiceLambdaClient
            lambda_client = DataServiceLambdaClient()
            
            result = await lambda_client.get_story_summary_by_id(summary_id)
            logger.info(f"[SummaryRepository] Retrieved summary {summary_id} via Data Service Lambda")
            return result

        except Exception as e:
            logger.error(f"[SummaryRepository] Error getting summary by ID: {str(e)}")
            return None

    async def get_by_post_id(self, post_id: int) -> Optional[StorySummary]:
        """Get a summary by its post ID via Data Service Lambda."""
        try:
            # Use Lambda client instead of direct database access
            from app.infrastructure.lambda_client import DataServiceLambdaClient
            lambda_client = DataServiceLambdaClient()
            
            result = await lambda_client.get_story_summary_by_post_id(post_id)
            logger.info(f"[SummaryRepository] Retrieved summary for post {post_id} via Data Service Lambda")
            return result

        except Exception as e:
            logger.error(f"[SummaryRepository] Error getting summary by post ID: {str(e)}")
            return None

    async def get_latest(self, limit: int = 10) -> List[StorySummary]:
        """Get the most recent summaries via Data Service Lambda."""
        try:
            # For now, we'll implement a simple approach
            # TODO: Add get_latest endpoint to Data Service Lambda
            logger.info(f"[SummaryRepository] Getting latest {limit} summaries via Data Service Lambda")
            
            # For now, return empty list since we don't have this endpoint in Data Service Lambda yet
            # This can be implemented later if needed
            return []

        except Exception as e:
            logger.error(f"[SummaryRepository] Error getting latest summaries: {str(e)}")
            return []

    async def delete(self, summary_id: int) -> bool:
        """Delete a summary by its ID via Data Service Lambda."""
        try:
            # For now, we'll implement a simple approach
            # TODO: Add delete endpoint to Data Service Lambda
            logger.info(f"[SummaryRepository] Deleting summary {summary_id} via Data Service Lambda")
            
            # For now, return False since we don't have this endpoint in Data Service Lambda yet
            # This can be implemented later if needed
            return False

        except Exception as e:
            logger.error(f"[SummaryRepository] Error deleting summary: {str(e)}")
            return False