import logging
import sys
from typing import Any, Dict

# Configure logging format with colors and better formatting
LOG_FORMAT = "\033[1;36m%(asctime)s\033[0m [\033[1;33m%(name)s\033[0m] \033[1;35m%(levelname)s\033[0m: %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

def setup_logging(level: str = "INFO") -> Dict[str, Any]:
    """Configure logging for the application."""
    
    # Create formatters
    formatter = logging.Formatter(
        LOG_FORMAT,
        datefmt=DATE_FORMAT
    )
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(console_handler)
    
    # Configure specific loggers
    loggers = {
        "publisher_service": level,
        "llm_client": level,
        "wordpress_client": level,
        "content_generator": level,
        "uvicorn": "INFO",
        "sqlalchemy": "WARNING",
    }
    
    for logger_name, log_level in loggers.items():
        logger = logging.getLogger(logger_name)
        logger.setLevel(log_level)
        if not logger.handlers:
            logger.addHandler(console_handler)
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
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "stream": sys.stdout,
            },
        },
        "loggers": {
            name: {"level": level, "handlers": ["console"]} 
            for name, level in loggers.items()
        }
    }

# Create logger instance
logger = logging.getLogger("publisher_service")

# Add specific logging methods for publisher service
def log_article_generation(article_id: int, status: str, details: str = None):
    """Log article generation events."""
    msg = f"Article {article_id} generation {status}"
    if details:
        msg += f": {details}"
    logger.info(msg)

def log_wordpress_operation(operation: str, post_id: int = None, status: str = None, error: str = None):
    """Log WordPress API operations."""
    msg = f"WordPress {operation}"
    if post_id:
        msg += f" for post {post_id}"
    if status:
        msg += f" - {status}"
    if error:
        logger.error(f"{msg}: {error}")
    else:
        logger.info(msg)
