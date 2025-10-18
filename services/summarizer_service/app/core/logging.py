import logging
import sys
import os
import json
from datetime import datetime
import contextvars
import uuid
from typing import Any, Dict

# Request tracking
request_id = contextvars.ContextVar('request_id', default=None)

def get_request_id():
    return request_id.get() or str(uuid.uuid4())

# Different format for Lambda vs local
IS_LAMBDA = os.environ.get('AWS_LAMBDA_FUNCTION_NAME') is not None

if IS_LAMBDA:
    # Simple format for Lambda/CloudWatch
    LOG_FORMAT = '%(levelname)s %(asctime)s %(name)s: %(message)s'
else:
    # Colored format for local development
    LOG_FORMAT = "\033[1;36m%(asctime)s\033[0m [\033[1;33m%(name)s\033[0m] \033[1;35m%(levelname)s\033[0m: %(message)s"

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

class LambdaAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        rid = get_request_id()
        extra = {
            'request_id': rid,
            'lambda_function': os.environ.get('AWS_LAMBDA_FUNCTION_NAME', 'local'),
            'lambda_version': os.environ.get('AWS_LAMBDA_FUNCTION_VERSION', 'local')
        }
        if 'extra' in kwargs:
            kwargs['extra'].update(extra)
        else:
            kwargs['extra'] = extra
        return msg, kwargs

def setup_logging(level: str = "INFO") -> Dict[str, Any]:
    """Configure logging for the application."""
    
    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)
    
    # Use stderr for Lambda
    handler = logging.StreamHandler(sys.stderr if IS_LAMBDA else sys.stdout)
    handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Remove any existing handlers
    for h in root_logger.handlers:
        root_logger.removeHandler(h)
    root_logger.addHandler(handler)
    
    # Configure specific loggers with higher level for Lambda
    loggers = {
        "summarizer_service": "DEBUG" if not IS_LAMBDA else "INFO",
        "huggingface_client": level,
        "uvicorn": "INFO",
        "sqlalchemy": "INFO" if IS_LAMBDA else "WARNING",  # More SQL logs in Lambda
    }
    
    for logger_name, log_level in loggers.items():
        logger = logging.getLogger(logger_name)
        logger.setLevel(log_level)
        if not logger.handlers:
            logger.addHandler(handler)
        logger.propagate = False

    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": LOG_FORMAT,
                "datefmt": DATE_FORMAT,
            },
        },
        "handlers": {
            "default": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "stream": "ext://sys.stderr" if IS_LAMBDA else "ext://sys.stdout",
            },
        },
        "loggers": {
            name: {"level": level, "handlers": ["default"]} 
            for name, level in loggers.items()
        }
    }

# Create logger instance
logger = logging.getLogger("summarizer_service")

# Add JSON structured logging for Lambda
if IS_LAMBDA:
    original_error = logger.error
    original_info = logger.info
    original_warning = logger.warning
    original_debug = logger.debug

    def structured_log(level: str, msg: str, *args, **kwargs):
        log_dict = {
            "level": level,
            "message": msg % args if args else msg,
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": get_request_id(),
            "lambda_function": os.environ.get('AWS_LAMBDA_FUNCTION_NAME'),
            "lambda_version": os.environ.get('AWS_LAMBDA_FUNCTION_VERSION'),
            **kwargs.get('extra', {})
        }
        print(json.dumps(log_dict), file=sys.stderr)

    def structured_error(msg, *args, **kwargs):
        structured_log("ERROR", msg, *args, **kwargs)
        original_error(msg, *args, **kwargs)

    def structured_info(msg, *args, **kwargs):
        structured_log("INFO", msg, *args, **kwargs)
        original_info(msg, *args, **kwargs)

    def structured_warning(msg, *args, **kwargs):
        structured_log("WARNING", msg, *args, **kwargs)
        original_warning(msg, *args, **kwargs)

    def structured_debug(msg, *args, **kwargs):
        structured_log("DEBUG", msg, *args, **kwargs)
        original_debug(msg, *args, **kwargs)

    logger.error = structured_error
    logger.info = structured_info
    logger.warning = structured_warning
    logger.debug = structured_debug

# Wrap logger with Lambda adapter
logger = LambdaAdapter(logger, {})