from app.core.config import settings
from app.core.logging import logger
from app.infrastructure.llm.base import BaseLLMClient
from app.infrastructure.llm.bedrock_client import BedrockClient
from app.infrastructure.llm.gemini_client import GeminiClient


def create_llm_client() -> BaseLLMClient:
    """
    Factory function to create the appropriate LLM client based on configuration.
    
    Returns:
        BaseLLMClient: An instance of the configured LLM client
        
    Raises:
        ValueError: If the configured LLM provider is not supported
    """
    provider = settings.LLM_PROVIDER.lower()
    
    logger.info(f"\n=== Creating LLM Client ===")
    logger.info(f"Configured provider: {provider}")
    
    if provider == "gemini":
        logger.info("Initializing Google Gemini client...")
        return GeminiClient()
    elif provider == "bedrock":
        logger.info("Initializing AWS Bedrock client...")
        return BedrockClient()
    else:
        error_msg = (
            f"Unsupported LLM provider: {settings.LLM_PROVIDER}. "
            f"Supported providers are: 'bedrock', 'gemini'"
        )
        logger.error(f"❌ {error_msg}")
        raise ValueError(error_msg)
