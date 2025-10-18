# app/core/config.py
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field, validator

class Settings(BaseSettings):
    """Application settings and configuration."""
    
    # Service Configuration
    SERVICE_NAME: str = "reddit-fetcher"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = False
    
    # Reddit API Configuration
    REDDIT_CLIENT_ID: str
    REDDIT_CLIENT_SECRET: str
    REDDIT_USER_AGENT: str = Field(
        default="python:newsettler:v1.0.0 (by /u/your_username)",
        description="User agent for Reddit API"
    )
    
    # Optional: Pre-obtained access token (bypasses OAuth flow)
    REDDIT_ACCESS_TOKEN: str = Field(
        default="",
        description="Pre-obtained Reddit access token (optional)"
    )
    
    # Database Configuration
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/newsettler"
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = Field(
        default=["*"],
        description="List of allowed CORS origins"
    )
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]
    
    # Cache Configuration
    REDIS_URL: str = "redis://redis:6379/0"
    CACHE_TTL: int = 300  # 5 minutes
    
    # Metrics Configuration
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090
    
    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    # Rate Limiting
    RATE_LIMIT_PER_SECOND: int = 10
    
    # Filter Configuration
    MIN_POST_SCORE: float = 10.0
    MAX_POSTS_PER_REQUEST: int = 100
    DEFAULT_POSTS_LIMIT: int = 5

    @validator("CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str]:
        """
        Parse CORS origins from string or list.
        
        Handles both comma-separated string and list inputs:
        - CORS_ORIGINS=["http://localhost:3000", "https://example.com"]
        - CORS_ORIGINS=http://localhost:3000,https://example.com
        """
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        raise ValueError("CORS_ORIGINS should be a list or comma-separated string")

    class Config:
        """Pydantic model configuration."""
        env_file = ".env"
        case_sensitive = True
        
        # Example configuration in .env:
        # SERVICE_NAME=reddit-fetcher
        # REDDIT_CLIENT_ID=your_client_id
        # REDDIT_CLIENT_SECRET=your_client_secret
        # REDDIT_ACCESS_TOKEN=your_access_token
        # DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/newsettler
        # CORS_ORIGINS=http://localhost:3000,https://example.com
        # LOG_LEVEL=INFO