from pydantic_settings import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    # Service name
    SERVICE_NAME: str = "publisher_service"
    
    # Database settings
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "newsettler"
    POSTGRES_USER: str = "newsettler_user"
    POSTGRES_PASSWORD: str = "newsettler_pass"
    POSTGRES_SCHEMA: str = "publisher"
    
    # The DATABASE_URL should be computed before validation
    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )
    
    # API settings
    API_V1_STR: str = "/api/v1"
    CORS_ORIGINS: List[str] = ["*"]

    # LLM Provider Configuration
    LLM_PROVIDER: str = "bedrock"  # Options: "bedrock", "gemini"
    
    # WordPress settings - Make optional for migrations
    WP_API_URL: str = "https://industechie.com/wp-json/wp/v2"
    WP_USERNAME: Optional[str] = None  # Changed to Optional
    WP_APP_PASSWORD: Optional[str] = None  # Changed to Optional
    WP_CATEGORY_ID: int = 1
    WP_DEFAULT_STATUS: str = "draft"
    
    # AWS Bedrock settings - Make optional for migrations
    AWS_ACCESS_KEY_ID: Optional[str] = None  # Changed to Optional
    AWS_SECRET_ACCESS_KEY: Optional[str] = None  # Changed to Optional
    AWS_REGION: str = "us-east-1"
    BEDROCK_MODEL_ID: str = "anthropic.claude-3-sonnet-20240229-v1:0"
    BEDROCK_TEMPERATURE: float = 0.7
    BEDROCK_MAX_TOKENS: int = 4096

    # Google Gemini settings
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL_ID: str = "gemini-pro"  # For text generation
    GEMINI_VISION_MODEL_ID: str = "gemini-pro-vision"  # For vision tasks
    GEMINI_TEMPERATURE: float = 0.7
    GEMINI_MAX_TOKENS: int = 4096
    
    # Publisher settings
    ARTICLE_MIN_LENGTH: int = 800
    ARTICLE_MAX_LENGTH: int = 2000
    ARTICLE_STYLE: str = "india_today"
    SEO_DESCRIPTION_LENGTH: int = 160
    MAX_RETRIES: int = 3
    RETRY_DELAY: int = 60
    
    # Monitoring
    ENABLE_METRICS: bool = True
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"

settings = Settings()
