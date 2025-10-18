from abc import ABC, abstractmethod
from typing import Dict, Optional, Any


class BaseLLMClient(ABC):
    """Base interface for LLM clients."""
    
    @abstractmethod
    async def generate_content(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        response_format: Optional[Dict] = None
    ) -> str:
        """
        Generate text content using the LLM.
        
        Args:
            prompt: The input prompt for content generation
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature (0.0 to 1.0)
            response_format: Optional format specification for the response
            
        Returns:
            Generated text content as a string
        """
        pass
    
    @abstractmethod
    async def generate_structured_content(
        self,
        prompt: str,
        structure: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate structured content (JSON) using the LLM.
        
        Args:
            prompt: The input prompt for content generation
            structure: Expected structure/schema for the response
            
        Returns:
            Generated content as a dictionary matching the structure
        """
        pass
    
    @abstractmethod
    async def generate_image(
        self,
        prompt: str,
        size: Optional[str] = None
    ) -> bytes:
        """
        Generate image content using the LLM.
        
        Args:
            prompt: The input prompt for image generation
            size: Optional size specification (e.g., "1024x1024")
            
        Returns:
            Generated image as bytes
        """
        pass
