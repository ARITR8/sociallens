from typing import Optional, List, Dict
from datetime import datetime

from app.domain.models.story_summary import StorySummary, StorySummaryCreate
from app.domain.models.reddit_post import RedditPost
from app.domain.summarizer.config import SummarizerConfig
from app.infrastructure.huggingface.client import HuggingFaceClient
from app.infrastructure.lambda_client import DataServiceLambdaClient
from app.core.logging import logger

class SummarizerService:
    """Service for generating summaries and stories from Reddit content using Lambda-to-Lambda pattern."""
    
    def __init__(
        self,
        huggingface_client: HuggingFaceClient,
        lambda_client: DataServiceLambdaClient
    ):
        self.client = huggingface_client
        self.lambda_client = lambda_client
        self.config = SummarizerConfig()

    def _prepare_comments_text(self, comments: List[Dict]) -> str:
        """Format comments for the prompt."""
        if not comments:
            return "No comments available."
        
        # Take only the first comment to keep input focused
        top_comment = comments[0]
        return f"Top comment: {top_comment.get('body', '')}"

    async def generate_summary_by_id(self, post_id: int) -> StorySummary:
        """Generate a summary by fetching post data via Data Service Lambda."""
        try:
            # Check if summary already exists via Data Service Lambda
            existing_summary = await self.lambda_client.get_story_summary_by_post_id(post_id)
            if existing_summary:
                logger.info(f"Summary already exists for post {post_id}")
                return existing_summary

            # TODO: Fetch post data via Data Service Lambda
            # For now, create a mock post for testing
            logger.info(f"Fetching post data for post {post_id} via Data Service Lambda")
            
            # Mock post data - in real implementation, this would come from Data Service Lambda
            post = RedditPost(
                id=post_id,
                title=f"Mock Post {post_id}",
                url="https://example.com",
                author="test_user",
                score=100,
                comments=5,
                subreddit="test",
                created_at=datetime.utcnow(),
                post_text="This is a mock post for testing Lambda-to-Lambda pattern",
                top_comments=[{"body": "Mock comment for testing", "author": "test_user", "score": 10}]
            )

            # Format comments
            comments_text = self._prepare_comments_text(post.top_comments or [])
            
            # Generate story first
            story_prompt = (
                f"Title: {post.title}\n\n"
                f"The developer of Apollo, a popular Reddit app, has released their backend code "
                f"on GitHub ({post.url}) to counter Reddit's claims. A top community member stated: "
                f"{comments_text}\n\n"
                "Write a short news article about this situation, focusing on what happened "
                "and the community's reaction."
            )

            logger.info("Generating story...")
            generated_story = await self.client.generate_text(
                prompt=story_prompt,
                parameters={
                    "max_length": 300,
                    "min_length": 100,
                    "temperature": 0.8,
                    "top_p": 0.95,
                    "num_beams": 4,
                    "no_repeat_ngram_size": 2
                }
            )
            logger.info(f"Generated story: {generated_story}")
            
            # Generate brief summary
            summary_prompt = (
                f"Write a brief, clear summary of this situation:\n\n"
                f"The Apollo app developer published their code to prove their app's efficiency, "
                f"countering Reddit's claims. The community reacted strongly, with users expressing "
                f"disappointment in Reddit's accusations about API abuse and poor programming."
            )

            logger.info("Generating summary...")
            summary_text = await self.client.generate_text(
                prompt=summary_prompt,
                parameters={
                    "max_length": 150,
                    "min_length": 30,
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "num_beams": 4,
                    "no_repeat_ngram_size": 2
                }
            )
            logger.info(f"Generated summary: {summary_text}")

            # Create and store the summary via Data Service Lambda
            summary_data = StorySummaryCreate(
                post_id=post_id,
                title=f"Summary: {post.title}",
                summary=summary_text,  # Store the generated summary
                generated_story=generated_story,  # Store the generated story
                model_used=self.config.DEFAULT_MODEL,
                generation_metadata={
                    "original_title": post.title,
                    "subreddit": post.subreddit,
                    "comment_count": len(post.top_comments or []),
                    "post_score": post.score,
                    "generation_timestamp": datetime.utcnow().isoformat()
                }
            )
            
            # Log before saving to database
            logger.info("About to save summary to database with content:")
            logger.info(f"Summary text: {summary_text}")
            logger.info(f"Generated story: {generated_story}")
            
            # Save to database via Data Service Lambda
            saved_summary = await self.lambda_client.create_story_summary(summary_data)
            logger.info(f"Created new summary for post {post_id}")
            return saved_summary
            
        except Exception as e:
            logger.error(f"Error generating summary for post {post_id}: {str(e)}")
            raise

    async def generate_summary(
        self,
        post_id: int,
        title: str,
        content: str,
        comments: List[Dict],
        model_id: Optional[str] = None
    ) -> StorySummary:
        """
        Generate a summary and story for a Reddit post using Lambda-to-Lambda pattern.
        
        Args:
            post_id: ID of the Reddit post
            title: Post title
            content: Post content/body
            comments: List of top comments
            model_id: Optional specific model to use
            
        Returns:
            Generated summary
        """
        try:
            # Check if summary already exists via Data Service Lambda
            existing_summary = await self.lambda_client.get_story_summary_by_post_id(post_id)
            if existing_summary:
                logger.info(f"Summary already exists for post {post_id}")
                return existing_summary

            # Format comments
            comments_text = self._prepare_comments_text(comments)
            
            # Generate story first
            story_prompt = self.config.get_story_prompt(
                title=title,
                content=content,
                comments=comments_text
            )
            
            generated_story = await self.client.generate_text(
                prompt=story_prompt,
                model_id=model_id,
                parameters=self.config.get_model_params(model_id or self.config.DEFAULT_MODEL)
            )
            
            # Generate brief summary
            summary_prompt = self.config.get_summary_prompt(
                title=title,
                content=content,
                comments=comments_text
            )
            
            summary_text = await self.client.generate_text(
                prompt=summary_prompt,
                model_id=model_id,
                parameters={
                    **self.config.get_model_params(model_id or self.config.DEFAULT_MODEL),
                    "max_length": 300  # Shorter for summary
                }
            )
            
            # Create summary object
            summary_data = StorySummaryCreate(
                post_id=post_id,
                title=f"Summary: {title}",
                summary=summary_text,
                generated_story=generated_story,
                model_used=model_id or self.config.DEFAULT_MODEL,
                generation_metadata={
                    "original_title": title,
                    "comment_count": len(comments),
                    "generation_timestamp": datetime.utcnow().isoformat(),
                    "generation_params": self.config.get_model_params(
                        model_id or self.config.DEFAULT_MODEL
                    )
                }
            )
            
            # Save to database via Data Service Lambda
            saved_summary = await self.lambda_client.create_story_summary(summary_data)
            logger.info(f"Created new summary for post {post_id}")
            return saved_summary
            
        except Exception as e:
            logger.error(f"Error generating summary for post {post_id}: {str(e)}")
            raise

    async def get_summary(self, post_id: int) -> Optional[StorySummary]:
        """Get an existing summary by post ID via Data Service Lambda."""
        return await self.lambda_client.get_story_summary_by_post_id(post_id)

    async def get_latest_summaries(self, limit: int = 10) -> List[StorySummary]:
        """Get the most recent summaries via Data Service Lambda."""
        # TODO: Implement via Data Service Lambda
        # For now, return empty list
        logger.info(f"Getting latest {limit} summaries via Data Service Lambda")
        return []

    async def delete_summary(self, summary_id: int) -> bool:
        """Delete a summary by its ID via Data Service Lambda."""
        # TODO: Implement via Data Service Lambda
        # For now, return False
        logger.info(f"Deleting summary {summary_id} via Data Service Lambda")
        return False