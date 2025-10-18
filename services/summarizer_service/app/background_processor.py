import json
import traceback
import asyncio
from app.core.logging import logger

def lambda_handler(event, context):
    """Lambda handler for background processing."""
    try:
        # Parse the SQS event
        for record in event.get('Records', []):
            body = json.loads(record['body'])
            job_id = body['job_id']
            post_id = body['post_id']
            
            # Process the summary asynchronously
            asyncio.run(process_summary(job_id, post_id))
            
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Processing completed'})
        }
        
    except Exception as e:
        logger.error(f"Error in lambda_handler: {str(e)}")
        print(traceback.format_exc())
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

async def process_summary(job_id: str, post_id: int):
    """Process the summary generation."""
    try:
        logger.info(f"Starting summary generation for job {job_id}, post {post_id}")
        
        # Call HuggingFace API
        summary_text = await call_huggingface_api(job_id, post_id)
        
        logger.info(f"Summary generated for job {job_id}: {summary_text[:100]}...")
        
        # Store in database via Data Service Lambda
        await store_summary_in_database(job_id, post_id, summary_text)
        
        logger.info(f"Job {job_id} status: completed and stored in database")
        
    except Exception as e:
        logger.error(f"Error in process_summary: {str(e)}")
        import traceback
        print(traceback.format_exc())
        raise

async def call_huggingface_api(job_id: str, post_id: int):
    """Call HuggingFace API to generate summary."""
    try:
        import requests
        import os
        
        # Get HuggingFace API token
        api_token = os.getenv('HUGGINGFACE_API_TOKEN')
        if not api_token:
            raise Exception("HUGGINGFACE_API_TOKEN not found")
        
        # For now, return a simple summary
        # TODO: Implement actual HuggingFace API call
        summary_text = f"This is a generated summary for post {post_id} in job {job_id}. The actual HuggingFace API integration can be implemented here."
        
        logger.info(f"Successfully generated summary for job {job_id}")
        return summary_text
        
    except Exception as e:
        logger.error(f"Error calling HuggingFace API: {str(e)}")
        raise

async def store_summary_in_database(job_id: str, post_id: int, summary_text: str):
    """Store the generated summary in the database via Data Service Lambda."""
    try:
        logger.info(f"Storing summary in database for job {job_id}")
        
        # Import with error handling
        try:
            from app.infrastructure.lambda_client import DataServiceLambdaClient
            from app.domain.models.story_summary import StorySummaryCreate
            logger.info("Successfully imported Lambda client and models")
        except ImportError as e:
            logger.error(f"Import error: {str(e)}")
            raise Exception(f"Failed to import required modules: {str(e)}")
        
        lambda_client = DataServiceLambdaClient()
        logger.info("Created Lambda client")
        
        # Create summary object
        summary = StorySummaryCreate(
            post_id=post_id,
            title=f"Summary for Post {post_id}",
            summary=summary_text[:500],  # Truncate if too long
            generated_story=summary_text,
            model_used="facebook/bart-large-cnn",
            generation_metadata={"job_id": job_id}
        )
        logger.info("Created summary object")
        
        # Store via Data Service Lambda
        logger.info("Calling Data Service Lambda...")
        result = await lambda_client.create_story_summary(summary)
        logger.info(f"Summary stored successfully with ID: {result.id}")
        
    except Exception as e:
        logger.error(f"Error storing summary in database: {str(e)}")
        import traceback
        print("Full traceback:")
        print(traceback.format_exc())
        raise