from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logging import request_id, logger
import uuid

class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Get or generate request ID
        rid = request.headers.get('X-Request-ID') or str(uuid.uuid4())
        
        # Set request ID in context
        request_id.set(rid)
        
        # Log request details
        logger.info(
            "Incoming request",
            extra={
                'method': request.method,
                'path': request.url.path,
                'query_params': str(request.query_params),
                'client_host': request.client.host if request.client else None,
                'request_id': rid
            }
        )

        try:
            # Process request
            response = await call_next(request)
            
            # Add request ID to response headers
            response.headers['X-Request-ID'] = rid
            
            # Log response status
            logger.info(
                "Request completed",
                extra={
                    'status_code': response.status_code,
                    'request_id': rid
                }
            )
            
            return response
            
        except Exception as e:
            # Log any unhandled exceptions
            logger.error(
                "Request failed",
                extra={
                    'error': str(e),
                    'error_type': type(e).__name__,
                    'request_id': rid
                }
            )
            raise