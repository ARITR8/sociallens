# app/core/exceptions.py
class BaseServiceException(Exception):
    """Base exception for service errors."""
    pass

class RedditFetchError(BaseServiceException):
    """Raised when fetching from Reddit fails."""
    pass

class DatabaseError(BaseServiceException):
    """Raised when database operations fail."""
    pass

class FilterError(BaseServiceException):
    """Raised when post filtering fails."""
    pass