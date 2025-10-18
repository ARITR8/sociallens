from typing import Dict, Optional, Any
import json
import asyncio
import boto3
from botocore.config import Config
from app.core.config import settings
from app.core.logging import logger
from app.infrastructure.llm.base import BaseLLMClient


class BedrockClient(BaseLLMClient):
    """Client for interacting with AWS Bedrock (Claude)."""
    
    def __init__(self):
        self.model_id = settings.BEDROCK_MODEL_ID
        self.temperature = settings.BEDROCK_TEMPERATURE
        self.max_tokens = settings.BEDROCK_MAX_TOKENS
        
        # Configure AWS Bedrock client
        self.bedrock_client = boto3.client(
            service_name='bedrock-runtime',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION,
            config=Config(
                retries={'max_attempts': 3},
                connect_timeout=10,
                read_timeout=30
            )
        )
        
        logger.info("=== AWS Bedrock Client Initialized ===")
        logger.info(f"Using model: {self.model_id}")
        logger.info(f"AWS Region: {settings.AWS_REGION}")
        logger.info(f"AWS credentials configured: {'Yes' if settings.AWS_ACCESS_KEY_ID else 'No'}")

    async def generate_content(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        response_format: Optional[Dict] = None
    ) -> str:
        """Generate content using Claude via AWS Bedrock."""
        try:
            logger.info("\n=== Starting Bedrock API Request ===")
            
            # Validate AWS credentials
            if not settings.AWS_ACCESS_KEY_ID or not settings.AWS_SECRET_ACCESS_KEY:
                logger.error("❌ AWS credentials not set")
                raise ValueError("AWS credentials not set")
            logger.info("✓ AWS credentials validated")

            # Prepare request body
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": max_tokens or self.max_tokens,
                "temperature": temperature or self.temperature,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
            
            if response_format:
                request_body["response_format"] = response_format

            # Log request details
            logger.info("\n--- Request Details ---")
            logger.info(f"Model: {self.model_id}")
            logger.info(f"Temperature: {request_body['temperature']}")
            logger.info(f"Max tokens: {request_body['max_tokens']}")
            logger.info(f"Prompt (first 200 chars): {prompt[:200]}...")
            
            try:
                # Make API call
                logger.info("\n--- Making Bedrock API Call ---")
                response = await asyncio.to_thread(
                    self.bedrock_client.invoke_model,
                    modelId=self.model_id,
                    body=json.dumps(request_body)
                )
                
                # Parse response
                response_body = json.loads(response['body'].read())
                content = response_body['content'][0]['text']
                
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
        """Generate structured JSON content using Claude via AWS Bedrock."""
        try:
            logger.info("\n=== Generating Structured Content ===")
            logger.info(f"Expected structure: {structure}")
            
            # Add JSON instruction to prompt
            structured_prompt = f"""{prompt}

IMPORTANT: Return ONLY valid JSON matching this exact structure:
{json.dumps(structure, indent=2)}

Do not include any explanatory text before or after the JSON."""

            # Generate content
            content = await self.generate_content(
                prompt=structured_prompt,
                temperature=0.3  # Lower temperature for more consistent JSON
            )
            
            # Try to extract JSON if there's extra text
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
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
        Image generation is not supported in AWS Bedrock client.
        Use Stability AI or other image generation services instead.
        """
        logger.error("Image generation not supported in Bedrock client")
        raise NotImplementedError(
            "Image generation is not available with AWS Bedrock. "
            "Please use LLM_PROVIDER=gemini for image generation support."
        )
