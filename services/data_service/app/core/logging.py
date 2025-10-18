import logging
import sys
import json
from typing import Any, Dict

def setup_logging(level: str = "INFO"):
    """Setup structured logging for Lambda."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(name)

logger = get_logger(__name__)

def log_structured(level: str, message: str, extra: Dict[str, Any] = None):
    """Log structured data."""
    log_data = {
        "level": level,
        "message": message,
        "service": "data-service"
    }
    if extra:
        log_data.update(extra)
    
    print(json.dumps(log_data))