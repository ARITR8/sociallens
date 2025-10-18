from typing import Dict, Optional
import httpx
from app.core.config import settings
from app.core.logging import logger

class HuggingFaceClient:
    """Client for interacting with HuggingFace's API."""
    
    def __init__(self):
        """Initialize the client with configuration and timeouts."""
        self.api_token = settings.hf_token
        self.base_url = "https://api-inference.huggingface.co/models"
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "User-Agent": "Lambda/HTTPX"  # Add explicit user agent
        }
        self.default_model = settings.HUGGINGFACE_DEFAULT_MODEL
        
        logger.info("=== HuggingFace Client Initialized ===")
        logger.info(f"Using model: {self.default_model}")
        logger.info(f"API token present: {'Yes' if self.api_token else 'No'}")

    async def generate_text(
        self,
        prompt: str,
        model_id: Optional[str] = None,
        parameters: Optional[Dict] = None
    ) -> str:
        """Generate text using a specified HuggingFace model."""
        try:
            logger.info("\n=== Starting HuggingFace API Request ===")
            
            # Prepare request
            model = model_id or self.default_model
            url = f"{self.base_url}/{model}"
            logger.info(f"✓ Using model: {model}")
            logger.info(f"✓ API URL: {url}")
            
            # Log request details
            logger.info("\n--- Request Details ---")
            logger.info(f"Prompt (first 200 chars): {prompt[:200]}...")
            logger.info(f"Parameters: {parameters}")

            # Configure client with explicit transport settings
            transport = httpx.AsyncHTTPTransport(
                retries=3,
                verify=True,
                http1=True,
                http2=False
            )

            # Make API call
            logger.info("\n--- Making API Call ---")
            async with httpx.AsyncClient(
                transport=transport,
                timeout=60.0,
                follow_redirects=True
            ) as client:
                try:
                    logger.info("Sending request to HuggingFace API...")
                    response = await client.post(
                        url,
                        headers=self.headers,
                        json={
                            "inputs": prompt,
                            **(parameters or {})
                        }
                    )
                    
                    # Log response details
                    logger.info("\n--- API Response ---")
                    logger.info(f"Status Code: {response.status_code}")
                    
                    if response.status_code == 200:
                        logger.info("✓ API call successful")
                    else:
                        logger.error(f"❌ API call failed with status {response.status_code}")
                        logger.error(f"Error response: {response.text}")
                        raise Exception(f"HuggingFace API Error: {response.text}")

                    # Parse response
                    result = response.json()
                    
                    if isinstance(result, list) and len(result) > 0:
                        if isinstance(result[0], dict):
                            text = result[0].get("generated_text", "") or result[0].get("summary_text", "")
                            if text:
                                logger.info(f"Extracted text from response: {text[:200]}...")
                                return text
                        return result[0]
                    
                    return str(result)

                except httpx.TimeoutException:
                    logger.error("❌ API request timed out")
                    raise
                except httpx.HTTPError as e:
                    logger.error(f"❌ HTTP error occurred: {str(e)}")
                    raise
                except Exception as e:
                    logger.error(f"❌ Unexpected error during API call: {str(e)}")
                    raise

        except Exception as e:
            logger.error("\n=== Error in generate_text ===")
            logger.error(f"Error type: {type(e).__name__}")
            logger.error(f"Error message: {str(e)}")
            logger.exception("Full traceback:")
            raise

    async def check_model_status(self, model_id: Optional[str] = None) -> bool:
        """Check if the model is ready to accept requests."""
        try:
            logger.info("\n=== Checking Model Status ===")
            model = model_id or self.default_model
            url = f"{self.base_url}/{model}"
            
            transport = httpx.AsyncHTTPTransport(
                retries=1,
                verify=True,
                http1=True,
                http2=False
            )
            
            async with httpx.AsyncClient(
                transport=transport,
                timeout=5.0,
                follow_redirects=True
            ) as client:
                response = await client.get(
                    url,
                    headers=self.headers
                )
                is_ready = response.status_code == 200
                logger.info(f"Model status check: {'Ready' if is_ready else 'Not Ready'}")
                return is_ready
        except Exception as e:
            logger.error(f"❌ Model status check failed: {str(e)}")
            return False