# app/domain/filters/config.py
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field

class FilterConfig(BaseSettings):
    """Configuration for post filtering."""
    KEYWORDS: List[str] = Field(
        default=[
            "python",
            "programming",
            "software",
            "development",
            "tech",
            "code",
            "coding",
            "developer",
            "web",
            "api",
            "database",
            "cloud",
            "git",
            "github",
            "opensource",
            "engineering",
            "computer",
            "science",
            "app",
            "application",
            "system",
            "data",
            "security",
            "design",
            "architecture",
            "framework",
            "library",
            "tool",
            "platform",
            "language",
            "server",
            "client",
            "frontend",
            "backend",
            "fullstack",
            "devops",
            "ai",
            "machine",
            "learning",
            "algorithm",
            "performance",
            "optimization",
            "testing",
            "debug",
            "release",
            "update",
            "feature",
            "fix",
            "issue",
            "bug"
        ],
        description="Keywords to match in post titles"
    )

    MIN_NORMALIZED_SCORE: float = Field(
        default=0.0,
        ge=0,
        description="Minimum normalized score required for posts"
    )

    NSFW_TAGS: List[str] = Field(
        default=["nsfw", "nsfl", "18+"],
        description="Tags that indicate NSFW content"
    )

    MAX_TITLE_LENGTH: int = Field(
        default=500,
        gt=0,
        description="Maximum allowed title length"
    )

    MIN_COMMENTS: int = Field(
        default=0,
        ge=0,
        description="Minimum number of comments required"
    )

    MIN_POST_SCORE: float = Field(
        default=1.0,
        ge=0,
        description="Minimum post score required"
    )

    class Config:
        """Pydantic model configuration."""
        case_sensitive = False
        env_prefix = "FILTER_"  # Environment variables will be prefixed with FILTER_
        
        # Example configuration via environment variables:
        # FILTER_KEYWORDS=["tech","ai","cloud"]
        # FILTER_MIN_NORMALIZED_SCORE=15.0
        # FILTER_MIN_COMMENTS=5