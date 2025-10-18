from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from app.domain.models.story_summary import StorySummary
from app.infrastructure.huggingface.client import HuggingFaceClient
from app.infrastructure.lambda_client import DataServiceLambdaClient

import traceback
import boto3
import uuid
import json
from datetime import datetime

router = APIRouter()

# Add SQS client
sqs = boto3.client('sqs')
queue_url = "https://sqs.us-east-1.amazonaws.com/565393069809/summarizer-jobs"

@router.post("/generate/from-post/{post_id}")
async def generate_summary_from_post(post_id: int):
    """Generate summary asynchronously using SQS."""
    print(f"✅ ASYNC API CALLED: /generate/from-post/{post_id}")
    
    # Create job ID
    job_id = str(uuid.uuid4())
    
    try:
        # Send message to SQS
        sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps({
                "job_id": job_id,
                "post_id": post_id,
                "timestamp": datetime.utcnow().isoformat()
            })
        )
        
        print(f"✅ Job {job_id} queued for post {post_id}")
        
        # Return immediately
        return {
            "job_id": job_id,
            "status": "pending",
            "message": "Summary generation started",
            "post_id": post_id
        }
        
    except Exception as e:
        print(f"❌ ERROR queuing job for post {post_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start summary generation: {str(e)}")

@router.get("/job/{job_id}")
async def get_job_status(job_id: str):
    """Get job status."""
    print(f"✅ STATUS API CALLED: /job/{job_id}")
    
    try:
        # TODO: Query database for job status via Data Service Lambda
        # For now, return a placeholder response
        return {
            "job_id": job_id,
            "status": "pending",
            "message": "Job status tracking not implemented yet"
        }
    except Exception as e:
        print(f"❌ ERROR getting job status for {job_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get job status: {str(e)}")

# Simplified sync endpoint for testing (without direct database access)
@router.post("/generate/from-post-sync/{post_id}")
async def generate_summary_from_post_sync(post_id: int):
    """Generate summary synchronously (for testing) - uses Lambda-to-Lambda pattern."""
    print(f"✅ SYNC API CALLED: /generate/from-post-sync/{post_id}")
    try:
        # Use Lambda-to-Lambda pattern instead of direct database access
        lambda_client = DataServiceLambdaClient()
        
        # For now, return a simple response indicating the pattern is working
        # In a real implementation, this would:
        # 1. Get post data via Data Service Lambda
        # 2. Generate summary via HuggingFace
        # 3. Store summary via Data Service Lambda
        
        return {
            "post_id": post_id,
            "status": "lambda_to_lambda_pattern_active",
            "message": "Sync endpoint updated to use Lambda-to-Lambda pattern",
            "note": "Full implementation requires Data Service Lambda endpoints for post retrieval"
        }
    except Exception as e:
        print(f"❌ ERROR while generating summary for post {post_id}: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to generate summary: {str(e)}")

@router.get("/summary/{post_id}")
async def get_summary(post_id: int):
    """Get summary by post ID using Lambda-to-Lambda pattern."""
    print(f"✅ API CALLED: /summary/{post_id}")
    try:
        # Use Lambda-to-Lambda pattern to get summary
        lambda_client = DataServiceLambdaClient()
        summary = await lambda_client.get_story_summary_by_post_id(post_id)
        
        if not summary:
            print(f"⚠️ Summary not found for post {post_id}")
            raise HTTPException(status_code=404, detail="Summary not found")
        return summary
    except Exception as e:
        print(f"❌ ERROR getting summary for post {post_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get summary: {str(e)}")

@router.get("/latest")
async def get_latest_summaries(limit: int = 10):
    """Get latest summaries using Lambda-to-Lambda pattern."""
    print(f"✅ API CALLED: /latest")
    try:
        # TODO: Implement via Data Service Lambda
        # For now, return placeholder
        return {
            "message": "Latest summaries endpoint updated for Lambda-to-Lambda pattern",
            "limit": limit,
            "note": "Implementation requires Data Service Lambda endpoint for latest summaries"
        }
    except Exception as e:
        print(f"❌ ERROR getting latest summaries: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get latest summaries: {str(e)}")

@router.delete("/summary/{summary_id}")
async def delete_summary(summary_id: int):
    """Delete summary using Lambda-to-Lambda pattern."""
    print(f"🗑️ API CALLED: DELETE /summary/{summary_id}")
    try:
        # TODO: Implement via Data Service Lambda
        # For now, return placeholder
        return {
            "message": f"Delete endpoint updated for Lambda-to-Lambda pattern",
            "summary_id": summary_id,
            "note": "Implementation requires Data Service Lambda endpoint for deletion"
        }
    except Exception as e:
        print(f"❌ ERROR deleting summary {summary_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete summary: {str(e)}")