from typing import Optional
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from app.domain.models.reddit_post import RedditPost
from app.core.logging import logger
import json
import os

class RedditPostRepository:
    """Repository for fetching Reddit posts from the database."""
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def get_by_id(self, post_id: int) -> Optional[RedditPost]:
        """Fetch a Reddit post by its ID."""
        try:
            # Verify database connection first
            try:
                await self.db.execute(text("SELECT 1"))
                logger.debug("Database connection verified")
            except SQLAlchemyError as e:
                logger.error(
                    "Database connection failed",
                    extra={
                        'error': str(e),
                        'error_type': type(e).__name__,
                        'post_id': post_id
                    }
                )
                raise

            # First verify the table exists
            verify_query = text("""
                SELECT EXISTS (
                    SELECT 1 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'reddit_posts'
                )
            """)
            result = await self.db.execute(verify_query)
            exists = result.scalar()
            logger.info(
                "Table existence check",
                extra={
                    'table_exists': exists,
                    'table_name': 'reddit_posts',
                    'schema': 'public'
                }
            )

            if not exists:
                logger.error(
                    "reddit_posts table not found in public schema",
                    extra={'post_id': post_id}
                )
                return None

            query = text("""
                SELECT 
                    id,
                    source,
                    subreddit,
                    title,
                    url,
                    author,
                    score,
                    comments,
                    normalized_score,
                    top_comments,
                    post_text,
                    created_at,
                    fetched_at
                FROM public.reddit_posts
                WHERE id = :post_id
            """)
            
            logger.info(
                "Fetching Reddit post",
                extra={'post_id': post_id}
            )
            
            result = await self.db.execute(query, {"post_id": post_id})
            post_data = result.mappings().first()
            
            if post_data:
                # Convert post_data to dict and handle JSON fields
                post_dict = dict(post_data)
                logger.debug(
                    "Raw post data retrieved",
                    extra={
                        'post_id': post_id,
                        'has_top_comments': 'top_comments' in post_dict,
                        'has_post_text': 'post_text' in post_dict
                    }
                )
                
                # Handle top_comments JSON parsing
                if isinstance(post_dict.get('top_comments'), str):
                    try:
                        post_dict['top_comments'] = json.loads(post_dict['top_comments'])
                        logger.debug(
                            "Successfully parsed top_comments JSON",
                            extra={
                                'post_id': post_id,
                                'comments_count': len(post_dict['top_comments'])
                            }
                        )
                    except json.JSONDecodeError as e:
                        logger.error(
                            "Failed to parse top_comments JSON",
                            extra={
                                'error': str(e),
                                'post_id': post_id,
                                'raw_value': post_dict['top_comments'][:100]  # Log first 100 chars
                            }
                        )
                        post_dict['top_comments'] = None
                
                try:
                    return RedditPost.model_validate(post_dict)
                except Exception as e:
                    logger.error(
                        "Model validation failed",
                        extra={
                            'error': str(e),
                            'error_type': type(e).__name__,
                            'post_id': post_id,
                            'post_data': {k: str(v)[:100] for k, v in post_dict.items()}  # Truncate long values
                        }
                    )
                    raise
            
            logger.warning(
                "Reddit post not found",
                extra={'post_id': post_id}
            )
            return None
            
        except SQLAlchemyError as e:
            logger.error(
                "Database error",
                extra={
                    'error': str(e),
                    'error_type': type(e).__name__,
                    'post_id': post_id
                }
            )
            raise
        except Exception as e:
            logger.error(
                "Unexpected error",
                extra={
                    'error': str(e),
                    'error_type': type(e).__name__,
                    'post_id': post_id
                }
            )
            raise