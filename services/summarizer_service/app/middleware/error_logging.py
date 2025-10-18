from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logging import logger
import traceback
import sys

class ErrorLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
            
        except Exception as e:
            # Get full traceback
            exc_info = sys.exc_info()
            tb_lines = traceback.format_exception(*exc_info)
            
            # Log detailed error information
            logger.error(
                "Unhandled exception",
                extra={
                    'path': request.url.path,
                    'method': request.method,
                    'error': str(e),
                    'error_type': type(e).__name__,
                    'traceback': ''.join(tb_lines),
                    'query_params': str(request.query_params),
                    'client_host': request.client.host if request.client else None,
                }
            )

            # For Lambda, include AWS request context if available
            if hasattr(request.state, 'aws_context'):
                logger.error(
                    "Lambda context for error",
                    extra={
                        'function_name': request.state.aws_context.function_name,
                        'function_version': request.state.aws_context.function_version,
                        'remaining_time_ms': request.state.aws_context.get_remaining_time_in_millis(),
                        'aws_request_id': request.state.aws_context.aws_request_id,
                    }
                )

            # Return error response
            return JSONResponse(
                status_code=500,
                content={
                    "detail": "Internal server error",
                    "error_type": type(e).__name__,
                    "message": str(e) if str(e) else "An unexpected error occurred"
                }
            )