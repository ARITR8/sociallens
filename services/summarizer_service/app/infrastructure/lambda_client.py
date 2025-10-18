import boto3
import json
import logging
import asyncio
from typing import Dict, Any, List, Optional
from app.domain.models.story_summary import StorySummaryCreate, StorySummary

logger = logging.getLogger(__name__)

class DataServiceLambdaClient:
    """Client for invoking Data Service Lambda functions."""
    
    def __init__(self):
        self.lambda_client = boto3.client('lambda', region_name='us-east-1')
        self.data_service_function_name = 'data-service-lambda'
        self.timeout_seconds = 30
    
    async def create_story_summary(self, summary: StorySummaryCreate) -> StorySummary:
        """Create a story summary via Data Service Lambda."""
        try:
            # Convert summary to dict
            summary_data = {
                "post_id": summary.post_id,
                "title": summary.title,
                "summary": summary.summary,
                "generated_story": summary.generated_story,
                "model_used": summary.model_used,
                "generation_metadata": summary.generation_metadata
            }
            
            # Create the payload for Data Service Lambda
            payload = {
                "resource": "/api/v1/story-summaries",
                "path": "/api/v1/story-summaries",
                "httpMethod": "POST",
                "headers": {
                    "Accept": "application/json",
                    "Content-Type": "application/json"
                },
                "multiValueHeaders": {},
                "queryStringParameters": None,
                "multiValueQueryStringParameters": None,
                "pathParameters": None,
                "stageVariables": None,
                "requestContext": {
                    "resourceId": "test",
                    "resourcePath": "/api/v1/story-summaries",
                    "httpMethod": "POST",
                    "extendedRequestId": "test",
                    "requestTime": "01/Jan/2024:00:00:00 +0000",
                    "path": "/api/v1/story-summaries",
                    "accountId": "565393069809",
                    "protocol": "HTTP/1.1",
                    "stage": "test",
                    "domainPrefix": "test",
                    "requestTimeEpoch": 1704067200000,
                    "requestId": "test",
                    "identity": {
                        "cognitoIdentityPoolId": None,
                        "accountId": None,
                        "cognitoIdentityId": None,
                        "caller": None,
                        "sourceIp": "127.0.0.1",
                        "principalOrgId": None,
                        "accessKey": None,
                        "cognitoAuthenticationType": None,
                        "cognitoAuthenticationProvider": None,
                        "userArn": None,
                        "userAgent": "summarizer-lambda",
                        "user": None
                    },
                    "domainName": "test.execute-api.us-east-1.amazonaws.com",
                    "apiId": "test"
                },
                "body": json.dumps(summary_data),
                "isBase64Encoded": False
            }
            
            # Invoke the Data Service Lambda with timeout
            loop = asyncio.get_event_loop()
            response = await asyncio.wait_for(
                loop.run_in_executor(
                    None,
                    lambda: self.lambda_client.invoke(
                        FunctionName=self.data_service_function_name,
                        InvocationType='RequestResponse',
                        Payload=json.dumps(payload)
                    )
                ),
                timeout=self.timeout_seconds
            )
            
            # Parse the response
            response_payload = json.loads(response['Payload'].read())
            
            if response_payload.get('statusCode') == 200:
                body = json.loads(response_payload.get('body', '{}'))
                logger.info(f"Successfully created story summary via Data Service Lambda")
                return StorySummary(**body)
            else:
                logger.error(f"Data Service Lambda returned error: {response_payload}")
                raise Exception(f"Failed to create story summary: {response_payload.get('body', 'Unknown error')}")
                
        except asyncio.TimeoutError:
            logger.error(f"Timeout calling Data Service Lambda after {self.timeout_seconds} seconds")
            raise Exception(f"Timeout calling Data Service Lambda")
        except Exception as e:
            logger.error(f"Failed to create story summary via Data Service Lambda: {str(e)}")
            raise
    
    async def get_story_summary_by_id(self, summary_id: int) -> Optional[StorySummary]:
        """Get story summary by ID via Data Service Lambda."""
        try:
            # Create the payload for Data Service Lambda
            payload = {
                "resource": "/api/v1/story-summaries/{summary_id}",
                "path": f"/api/v1/story-summaries/{summary_id}",
                "httpMethod": "GET",
                "headers": {
                    "Accept": "application/json",
                    "Content-Type": "application/json"
                },
                "multiValueHeaders": {},
                "queryStringParameters": None,
                "multiValueQueryStringParameters": None,
                "pathParameters": {"summary_id": str(summary_id)},
                "stageVariables": None,
                "requestContext": {
                    "resourceId": "test",
                    "resourcePath": "/api/v1/story-summaries/{summary_id}",
                    "httpMethod": "GET",
                    "extendedRequestId": "test",
                    "requestTime": "01/Jan/2024:00:00:00 +0000",
                    "path": f"/api/v1/story-summaries/{summary_id}",
                    "accountId": "565393069809",
                    "protocol": "HTTP/1.1",
                    "stage": "test",
                    "domainPrefix": "test",
                    "requestTimeEpoch": 1704067200000,
                    "requestId": "test",
                    "identity": {
                        "cognitoIdentityPoolId": None,
                        "accountId": None,
                        "cognitoIdentityId": None,
                        "caller": None,
                        "sourceIp": "127.0.0.1",
                        "principalOrgId": None,
                        "accessKey": None,
                        "cognitoAuthenticationType": None,
                        "cognitoAuthenticationProvider": None,
                        "userArn": None,
                        "userAgent": "summarizer-lambda",
                        "user": None
                    },
                    "domainName": "test.execute-api.us-east-1.amazonaws.com",
                    "apiId": "test"
                },
                "body": None,
                "isBase64Encoded": False
            }
            
            # Invoke the Data Service Lambda with timeout
            loop = asyncio.get_event_loop()
            response = await asyncio.wait_for(
                loop.run_in_executor(
                    None,
                    lambda: self.lambda_client.invoke(
                        FunctionName=self.data_service_function_name,
                        InvocationType='RequestResponse',
                        Payload=json.dumps(payload)
                    )
                ),
                timeout=self.timeout_seconds
            )
            
            # Parse the response
            response_payload = json.loads(response['Payload'].read())
            
            if response_payload.get('statusCode') == 200:
                body = json.loads(response_payload.get('body', '{}'))
                logger.info(f"Successfully retrieved story summary {summary_id} via Data Service Lambda")
                return StorySummary(**body)
            elif response_payload.get('statusCode') == 404:
                logger.info(f"No story summary found with ID {summary_id}")
                return None
            else:
                logger.error(f"Data Service Lambda returned error: {response_payload}")
                return None
                
        except asyncio.TimeoutError:
            logger.error(f"Timeout calling Data Service Lambda after {self.timeout_seconds} seconds")
            return None
        except Exception as e:
            logger.error(f"Failed to get story summary by ID via Data Service Lambda: {str(e)}")
            return None
    
    async def get_story_summary_by_post_id(self, post_id: int) -> Optional[StorySummary]:
        """Get story summary by post ID via Data Service Lambda."""
        try:
            # Create the payload for Data Service Lambda
            payload = {
                "resource": "/api/v1/story-summaries/by-post/{post_id}",
                "path": f"/api/v1/story-summaries/by-post/{post_id}",
                "httpMethod": "GET",
                "headers": {
                    "Accept": "application/json",
                    "Content-Type": "application/json"
                },
                "multiValueHeaders": {},
                "queryStringParameters": None,
                "multiValueQueryStringParameters": None,
                "pathParameters": {"post_id": str(post_id)},
                "stageVariables": None,
                "requestContext": {
                    "resourceId": "test",
                    "resourcePath": "/api/v1/story-summaries/by-post/{post_id}",
                    "httpMethod": "GET",
                    "extendedRequestId": "test",
                    "requestTime": "01/Jan/2024:00:00:00 +0000",
                    "path": f"/api/v1/story-summaries/by-post/{post_id}",
                    "accountId": "565393069809",
                    "protocol": "HTTP/1.1",
                    "stage": "test",
                    "domainPrefix": "test",
                    "requestTimeEpoch": 1704067200000,
                    "requestId": "test",
                    "identity": {
                        "cognitoIdentityPoolId": None,
                        "accountId": None,
                        "cognitoIdentityId": None,
                        "caller": None,
                        "sourceIp": "127.0.0.1",
                        "principalOrgId": None,
                        "accessKey": None,
                        "cognitoAuthenticationType": None,
                        "cognitoAuthenticationProvider": None,
                        "userArn": None,
                        "userAgent": "summarizer-lambda",
                        "user": None
                    },
                    "domainName": "test.execute-api.us-east-1.amazonaws.com",
                    "apiId": "test"
                },
                "body": None,
                "isBase64Encoded": False
            }
            
            # Invoke the Data Service Lambda with timeout
            loop = asyncio.get_event_loop()
            response = await asyncio.wait_for(
                loop.run_in_executor(
                    None,
                    lambda: self.lambda_client.invoke(
                        FunctionName=self.data_service_function_name,
                        InvocationType='RequestResponse',
                        Payload=json.dumps(payload)
                    )
                ),
                timeout=self.timeout_seconds
            )
            
            # Parse the response
            response_payload = json.loads(response['Payload'].read())
            
            if response_payload.get('statusCode') == 200:
                body = json.loads(response_payload.get('body', '{}'))
                logger.info(f"Successfully retrieved story summary for post {post_id} via Data Service Lambda")
                return StorySummary(**body)
            elif response_payload.get('statusCode') == 404:
                logger.info(f"No story summary found for post {post_id}")
                return None
            else:
                logger.error(f"Data Service Lambda returned error: {response_payload}")
                return None
                
        except asyncio.TimeoutError:
            logger.error(f"Timeout calling Data Service Lambda after {self.timeout_seconds} seconds")
            return None
        except Exception as e:
            logger.error(f"Failed to get story summary by post ID via Data Service Lambda: {str(e)}")
            return None

    async def health_check(self) -> Dict[str, Any]:
        """Check if Data Service Lambda is healthy."""
        try:
            # Create a simple health check payload
            payload = {
                "resource": "/health",
                "path": "/health",
                "httpMethod": "GET",
                "headers": {
                    "Accept": "application/json",
                    "Content-Type": "application/json"
                },
                "multiValueHeaders": {},
                "queryStringParameters": None,
                "multiValueQueryStringParameters": None,
                "pathParameters": None,
                "stageVariables": None,
                "requestContext": {
                    "resourceId": "test",
                    "resourcePath": "/health",
                    "httpMethod": "GET",
                    "extendedRequestId": "test",
                    "requestTime": "01/Jan/2024:00:00:00 +0000",
                    "path": "/health",
                    "accountId": "565393069809",
                    "protocol": "HTTP/1.1",
                    "stage": "test",
                    "domainPrefix": "test",
                    "requestTimeEpoch": 1704067200000,
                    "requestId": "test",
                    "identity": {
                        "cognitoIdentityPoolId": None,
                        "accountId": None,
                        "cognitoIdentityId": None,
                        "caller": None,
                        "sourceIp": "127.0.0.1",
                        "principalOrgId": None,
                        "accessKey": None,
                        "cognitoAuthenticationType": None,
                        "cognitoAuthenticationProvider": None,
                        "userArn": None,
                        "userAgent": "summarizer-lambda",
                        "user": None
                    },
                    "domainName": "test.execute-api.us-east-1.amazonaws.com",
                    "apiId": "test"
                },
                "body": None,
                "isBase64Encoded": False
            }
            
            # Invoke the Data Service Lambda with timeout
            loop = asyncio.get_event_loop()
            response = await asyncio.wait_for(
                loop.run_in_executor(
                    None,
                    lambda: self.lambda_client.invoke(
                        FunctionName=self.data_service_function_name,
                        InvocationType='RequestResponse',
                        Payload=json.dumps(payload)
                    )
                ),
                timeout=self.timeout_seconds
            )
            
            # Parse the response
            response_payload = json.loads(response['Payload'].read())
            
            if response_payload.get('statusCode') == 200:
                logger.info("Data Service Lambda health check successful")
                return {"success": True, "message": "Data Service Lambda is healthy"}
            else:
                logger.error(f"Data Service Lambda health check failed: {response_payload}")
                return {"success": False, "error": response_payload.get('body', 'Unknown error')}
            
        except asyncio.TimeoutError:
            logger.error(f"Timeout calling Data Service Lambda after {self.timeout_seconds} seconds")
            return {"success": False, "error": "Timeout calling Data Service Lambda"}
        except Exception as e:
            logger.error(f"Failed to check Data Service Lambda health: {str(e)}")
            return {"success": False, "error": str(e)}