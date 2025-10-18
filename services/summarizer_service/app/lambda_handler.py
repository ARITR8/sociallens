import json
import traceback
from typing import Any, Dict, Callable
from app.core.logging import logger, get_request_id
import time
import os

def lambda_handler_wrapper(handler: Callable) -> Callable:
    """
    Wrapper for Lambda handlers to add logging, error handling, and metrics.
    """
    def wrapper(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
        start_time = time.time()
        
        try:
            # Log invocation details
            logger.info(
                "Lambda invocation started",
                extra={
                    'event_type': event.get('requestContext', {}).get('eventType'),
                    'http_method': event.get('requestContext', {}).get('http', {}).get('method'),
                    'path': event.get('requestContext', {}).get('http', {}).get('path'),
                    'request_id': get_request_id(),
                    'function_name': os.environ.get('AWS_LAMBDA_FUNCTION_NAME'),
                    'function_version': os.environ.get('AWS_LAMBDA_FUNCTION_VERSION'),
                    'remaining_time_ms': context.get_remaining_time_in_millis()
                }
            )
            
            # Execute handler
            response = handler(event, context)
            
            # Calculate execution time
            execution_time = (time.time() - start_time) * 1000  # in milliseconds
            
            # Log successful completion
            logger.info(
                "Lambda execution completed",
                extra={
                    'execution_time_ms': execution_time,
                    'status_code': response.get('statusCode'),
                    'remaining_time_ms': context.get_remaining_time_in_millis(),
                    'request_id': get_request_id()
                }
            )
            
            return response
            
        except Exception as e:
            # Calculate execution time even for failures
            execution_time = (time.time() - start_time) * 1000
            
            # Get full traceback
            exc_info = traceback.format_exc()
            
            # Log error details
            logger.error(
                "Lambda execution failed",
                extra={
                    'error': str(e),
                    'error_type': type(e).__name__,
                    'traceback': exc_info,
                    'execution_time_ms': execution_time,
                    'remaining_time_ms': context.get_remaining_time_in_millis(),
                    'request_id': get_request_id(),
                    'event': {
                        'path': event.get('requestContext', {}).get('http', {}).get('path'),
                        'method': event.get('requestContext', {}).get('http', {}).get('method'),
                        'query': event.get('queryStringParameters'),
                    }
                }
            )
            
            # Return error response
            return {
                'statusCode': 500,
                'body': json.dumps({
                    'error': 'Internal server error',
                    'error_type': type(e).__name__,
                    'message': str(e)
                }),
                'headers': {
                    'Content-Type': 'application/json',
                    'X-Request-ID': get_request_id()
                }
            }
            
    return wrapper