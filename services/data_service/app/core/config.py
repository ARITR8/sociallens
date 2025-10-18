from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Data Service configuration."""
    
    # Service Configuration
    SERVICE_NAME: str = "data-service"
    DATABASE_URL: str
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()