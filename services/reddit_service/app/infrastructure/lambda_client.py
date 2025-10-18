import boto3
import json
import logging
from typing import List, Dict, Any, Optional
from app.domain.models.filtered_post import FilteredPost

logger = logging.getLogger(__name__)

class DataServiceLambdaClient:
    """Client for invoking the Data Service Lambda."""
    
    def __init__(self):
        self.lambda_client = boto3.client('lambda', region_name='us-east-1')
        self.data_service_function_name = 'data-service-lambda'
    
    async def save_reddit_posts(self, posts: List[FilteredPost]) -> Dict[str, Any]:
        """Save Reddit posts via Data Service Lambda."""
        try:
            # Convert posts to the format expected by Data Service Lambda
            posts_data = []
            for post in posts:
                post_dict = {
                    "source": post.source,
                    "subreddit": post.subreddit,
                    "title": post.title,
                    "url": str(post.url),
                    "author": post.author,
                    "score": post.score,
                    "comments": post.comments,
                    "normalized_score": post.normalized_score,
                    "created_at": post.created_at.isoformat(),
                    "post_text": post.post_text
                }
                
                # Handle top_comments if they exist
                if post.top_comments:
                    comments_data = []
                    for comment in post.top_comments:
                        comment_dict = {
                            "author": comment.author,
                            "body": comment.body,
                            "score": comment.score,
                            "created_at": comment.created_at.isoformat()
                        }
                        comments_data.append(comment_dict)
                    post_dict["top_comments"] = comments_data
                
                posts_data.append(post_dict)
            
            # Create the payload for Data Service Lambda
            payload = {
                "resource": "/api/v1/reddit/posts",
                "path": "/api/v1/reddit/posts",
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
                    "resourcePath": "/api/v1/reddit/posts",
                    "httpMethod": "POST",
                    "extendedRequestId": "test",
                    "requestTime": "01/Jan/2024:00:00:00 +0000",
                    "path": "/api/v1/reddit/posts",
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
                        "userAgent": "reddit-fetcher-lambda",
                        "user": None
                    },
                    "domainName": "test.execute-api.us-east-1.amazonaws.com",
                    "apiId": "test"
                },
                "body": json.dumps({"posts": posts_data}),
                "isBase64Encoded": False
            }
            
            # Invoke the Data Service Lambda
            response = self.lambda_client.invoke(
                FunctionName=self.data_service_function_name,
                InvocationType='RequestResponse',
                Payload=json.dumps(payload)
            )
            
            # Parse the response
            response_payload = json.loads(response['Payload'].read())
            
            if response_payload.get('statusCode') == 200:
                logger.info(f"Successfully saved {len(posts)} posts via Data Service Lambda")
                return {"success": True, "message": response_payload.get('body', '')}
            else:
                logger.error(f"Data Service Lambda returned error: {response_payload}")
                return {"success": False, "error": response_payload.get('body', 'Unknown error')}
                
        except Exception as e:
            logger.error(f"Failed to save posts via Data Service Lambda: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def get_reddit_posts(self, limit: int = 10, subreddit: Optional[str] = None) -> List[FilteredPost]:
        """Get Reddit posts via Data Service Lambda."""
        try:
            # Create query parameters
            query_params = f"?limit={limit}"
            if subreddit:
                query_params += f"&subreddit={subreddit}"
            
            # Create the payload for Data Service Lambda
            payload = {
                "resource": "/api/v1/reddit/posts",
                "path": f"/api/v1/reddit/posts{query_params}",
                "httpMethod": "GET",
                "headers": {
                    "Accept": "application/json",
                    "Content-Type": "application/json"
                },
                "multiValueHeaders": {},
                "queryStringParameters": {"limit": str(limit), "subreddit": subreddit} if subreddit else {"limit": str(limit)},
                "multiValueQueryStringParameters": None,
                "pathParameters": None,
                "stageVariables": None,
                "requestContext": {
                    "resourceId": "test",
                    "resourcePath": "/api/v1/reddit/posts",
                    "httpMethod": "GET",
                    "extendedRequestId": "test",
                    "requestTime": "01/Jan/2024:00:00:00 +0000",
                    "path": f"/api/v1/reddit/posts{query_params}",
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
                        "userAgent": "reddit-fetcher-lambda",
                        "user": None
                    },
                    "domainName": "test.execute-api.us-east-1.amazonaws.com",
                    "apiId": "test"
                },
                "body": None,
                "isBase64Encoded": False
            }
            
            # Invoke the Data Service Lambda
            response = self.lambda_client.invoke(
                FunctionName=self.data_service_function_name,
                InvocationType='RequestResponse',
                Payload=json.dumps(payload)
            )
            
            # Parse the response
            response_payload = json.loads(response['Payload'].read())
            
            if response_payload.get('statusCode') == 200:
                posts_data = json.loads(response_payload.get('body', '[]'))
                # Convert back to FilteredPost objects
                posts = []
                for post_data in posts_data:
                    # Convert datetime strings back to datetime objects
                    from datetime import datetime
                    post_data['created_at'] = datetime.fromisoformat(post_data['created_at'])
                    
                    # Handle top_comments if they exist
                    if post_data.get('top_comments'):
                        from app.domain.models.reddit_comment import RedditComment
                        comments = []
                        for comment_data in post_data['top_comments']:
                            comment_data['created_at'] = datetime.fromisoformat(comment_data['created_at'])
                            comments.append(RedditComment(**comment_data))
                        post_data['top_comments'] = comments
                    
                    posts.append(FilteredPost(**post_data))
                
                logger.info(f"Successfully retrieved {len(posts)} posts via Data Service Lambda")
                return posts
            else:
                logger.error(f"Data Service Lambda returned error: {response_payload}")
                return []
                
        except Exception as e:
            logger.error(f"Failed to get posts via Data Service Lambda: {str(e)}")
            return []