from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    
    # Service name
    SERVICE_NAME: str = "summarizer_service"
    
    # Database settings - remove property, use direct field
    DATABASE_URL: str
    
    # API settings
    API_V1_STR: str = "/api/v1"
    CORS_ORIGINS: List[str] = ["*"]
    
    # HuggingFace settings
    HUGGINGFACE_API_TOKEN: str | None = None
    HUGGINGFACE_DEFAULT_MODEL: str = "facebook/bart-large-cnn"

    @property
    def hf_token(self):
        if not self.HUGGINGFACE_API_TOKEN:
            raise ValueError("Missing HUGGINGFACE_API_TOKEN in Lambda environment")
        return self.HUGGINGFACE_API_TOKEN

    

    
    # Summarizer settings
    SUMMARY_MIN_LENGTH: int = 256
    SUMMARY_MAX_LENGTH: int = 1024
    SUMMARY_TEMPERATURE: float = 0.7

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
