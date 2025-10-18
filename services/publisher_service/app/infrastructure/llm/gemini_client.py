from typing import Dict, Optional, Any
import json
import asyncio
import google.generativeai as genai
from app.core.config import settings
from app.core.logging import logger
from app.infrastructure.llm.base import BaseLLMClient


class GeminiClient(BaseLLMClient):
    """Client for interacting with Google Gemini."""
    
    def __init__(self):
        self.model_id = settings.GEMINI_MODEL_ID
        self.vision_model_id = settings.GEMINI_VISION_MODEL_ID
        self.temperature = settings.GEMINI_TEMPERATURE
        self.max_tokens = settings.GEMINI_MAX_TOKENS
        
        # Validate API key
        if not settings.GEMINI_API_KEY:
            logger.error("❌ Gemini API key not set")
            raise ValueError("GEMINI_API_KEY not configured")
        
        # Configure Gemini
        genai.configure(api_key=settings.GEMINI_API_KEY)
        
        # Initialize models
        self.model = genai.GenerativeModel(self.model_id)
        self.vision_model = genai.GenerativeModel(self.vision_model_id)
        
        logger.info("=== Google Gemini Client Initialized ===")
        logger.info(f"Using text model: {self.model_id}")
        logger.info(f"Using vision model: {self.vision_model_id}")
        logger.info(f"Gemini API key configured: {'Yes' if settings.GEMINI_API_KEY else 'No'}")

    async def generate_content(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        response_format: Optional[Dict] = None
    ) -> str:
        """Generate content using Google Gemini."""
        try:
            logger.info("\n=== Starting Gemini API Request ===")
            
            # Validate API key
            if not settings.GEMINI_API_KEY:
                logger.error("❌ Gemini API key not set")
                raise ValueError("Gemini API key not set")
            logger.info("✓ Gemini API key validated")

            # Log request details
            logger.info("\n--- Request Details ---")
            logger.info(f"Model: {self.model_id}")
            logger.info(f"Temperature: {temperature or self.temperature}")
            logger.info(f"Max tokens: {max_tokens or self.max_tokens}")
            logger.info(f"Prompt (first 200 chars): {prompt[:200]}...")
            
            # Prepare generation config
            generation_config = genai.GenerationConfig(
                max_output_tokens=max_tokens or self.max_tokens,
                temperature=temperature or self.temperature,
            )
            
            try:
                # Make API call
                logger.info("\n--- Making Gemini API Call ---")
                response = await asyncio.to_thread(
                    self.model.generate_content,
                    prompt,
                    generation_config=generation_config
                )
                
                # Extract text from response
                content = response.text
                
                # Log response details
                logger.info("\n--- API Response ---")
                logger.info(f"Response length: {len(content)}")
                logger.info(f"Generated content (first 200 chars): {content[:200]}...")
                
                return content

            except Exception as e:
                logger.error(f"❌ API call failed: {str(e)}")
                raise

        except Exception as e:
            logger.error("\n=== Error in generate_content ===")
            logger.error(f"Error type: {type(e).__name__}")
            logger.error(f"Error message: {str(e)}")
            logger.exception("Full traceback:")
            raise

    async def generate_structured_content(
        self,
        prompt: str,
        structure: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate structured JSON content using Google Gemini."""
        try:
            logger.info("\n=== Generating Structured Content ===")
            logger.info(f"Expected structure: {structure}")
            
            # Add JSON instruction to prompt
            structured_prompt = f"""{prompt}

IMPORTANT: Return ONLY valid JSON matching this exact structure:
{json.dumps(structure, indent=2)}

Do not include any explanatory text before or after the JSON."""

            # Generate content with lower temperature for consistency
            content = await self.generate_content(
                prompt=structured_prompt,
                temperature=0.3  # Lower temperature for more consistent JSON
            )
            
            # Try to extract JSON if there's extra text
            content = content.strip()
            
            # Remove markdown code blocks if present
            if content.startswith("```json"):
                content = content[7:]
            elif content.startswith("```"):
                content = content[3:]
            
            if content.endswith("```"):
                content = content[:-3]
            
            content = content.strip()
            
            # Parse JSON
            try:
                result = json.loads(content)
                logger.info("✓ Successfully parsed structured content")
                return result
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {e}")
                logger.error(f"Response content: {content}")
                raise ValueError(f"Invalid JSON response from LLM: {str(e)}")
                
        except Exception as e:
            logger.error(f"Error in generate_structured_content: {str(e)}")
            raise

    async def generate_image(
        self,
        prompt: str,
        size: Optional[str] = None
    ) -> bytes:
        """
        Generate image content using Google Gemini.
        
        Note: As of now, Gemini API doesn't directly support image generation like DALL-E.
        This is a placeholder for future implementation or integration with Imagen.
        For now, it raises NotImplementedError.
        """
        try:
            logger.info("\n=== Image Generation Request ===")
            logger.info(f"Prompt: {prompt[:200]}...")
            logger.info(f"Size: {size or 'default'}")
            
            # Note: Gemini Pro Vision is for image understanding, not generation
            # For image generation, you would need to integrate with Google's Imagen API
            # or use a different service
            
            logger.error("❌ Image generation not yet implemented for Gemini")
            raise NotImplementedError(
                "Image generation is not yet implemented for Gemini. "
                "Please integrate with Google Imagen API or use an alternative image generation service."
            )
                
        except Exception as e:
            logger.error(f"Error in generate_image: {str(e)}")
            raise
