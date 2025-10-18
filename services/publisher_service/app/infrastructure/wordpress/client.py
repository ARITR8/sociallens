from typing import Dict, List, Optional, Any, BinaryIO
import httpx
import aiofiles
import os
from datetime import datetime
from app.core.config import settings
from app.core.logging import logger
from app.domain.models.wp_post import WPPostCreate, WPPostResponse, WPMedia, WPError

class WordPressClient:
    """Client for interacting with WordPress REST API."""
    
    def __init__(self):
        self.api_url = settings.WP_API_URL
        self.username = settings.WP_USERNAME
        self.password = settings.WP_APP_PASSWORD
        self.auth = (self.username, self.password)
        logger.info("=== WordPress Client Initialized ===")
        logger.info(f"API URL: {self.api_url}")
        logger.info(f"Username: {self.username}")
        logger.info("Authentication configured: Yes" if self.password else "Authentication configured: No")

    async def create_post(self, post: WPPostCreate) -> WPPostResponse:
        """Create a new WordPress post."""
        try:
            logger.info("\n=== Creating WordPress Post ===")
            logger.info(f"Title: {post.title}")
            
            url = f"{self.api_url}/posts"
            
            # Prepare post data
            post_data = {
                "title": post.title,
                "content": post.content,
                "status": post.status,
                "featured_media": post.featured_media,
                "categories": post.categories,
                "tags": await self._ensure_tags_exist(post.tags),
                "meta": post.meta
            }
            
            if post.slug:
                post_data["slug"] = post.slug

            async with httpx.AsyncClient() as client:
                logger.info("Sending request to WordPress API...")
                response = await client.post(
                    url,
                    json=post_data,
                    auth=self.auth,
                    timeout=30.0
                )
                
                if response.status_code == 201:
                    logger.info("✓ Post created successfully")
                    return WPPostResponse.model_validate(response.json())
                else:
                    error = WPError.model_validate(response.json())
                    logger.error(f"❌ Failed to create post: {error.message}")
                    raise Exception(f"WordPress API Error: {error.message}")

        except Exception as e:
            logger.error(f"Error creating WordPress post: {str(e)}")
            raise

    async def upload_media(
        self,
        file_path: str,
        title: Optional[str] = None,
        alt_text: Optional[str] = None
    ) -> WPMedia:
        """Upload media to WordPress."""
        try:
            logger.info(f"\n=== Uploading Media: {file_path} ===")
            
            url = f"{self.api_url}/media"
            
            async with aiofiles.open(file_path, 'rb') as f:
                file_content = await f.read()
            
            # Get file information
            file_name = os.path.basename(file_path)
            file_ext = os.path.splitext(file_name)[1].lower()
            
            # Determine content type
            content_types = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.gif': 'image/gif',
                '.webp': 'image/webp'
            }
            content_type = content_types.get(file_ext, 'application/octet-stream')
            
            # Prepare headers
            headers = {
                'Content-Type': content_type,
                'Content-Disposition': f'attachment; filename="{file_name}"'
            }

            async with httpx.AsyncClient() as client:
                logger.info("Uploading file to WordPress...")
                response = await client.post(
                    url,
                    content=file_content,
                    headers=headers,
                    auth=self.auth,
                    timeout=60.0
                )
                
                if response.status_code == 201:
                    logger.info("✓ Media uploaded successfully")
                    media = WPMedia.model_validate(response.json())
                    
                    # Update media metadata if provided
                    if title or alt_text:
                        await self.update_media_metadata(
                            media.id,
                            title=title,
                            alt_text=alt_text
                        )
                    
                    return media
                else:
                    error = WPError.model_validate(response.json())
                    logger.error(f"❌ Failed to upload media: {error.message}")
                    raise Exception(f"WordPress API Error: {error.message}")

        except Exception as e:
            logger.error(f"Error uploading media: {str(e)}")
            raise

    async def update_media_metadata(
        self,
        media_id: int,
        title: Optional[str] = None,
        alt_text: Optional[str] = None
    ) -> WPMedia:
        """Update media metadata."""
        try:
            logger.info(f"\n=== Updating Media Metadata: ID {media_id} ===")
            
            url = f"{self.api_url}/media/{media_id}"
            data = {}
            
            if title:
                data["title"] = title
            if alt_text:
                data["alt_text"] = alt_text

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    json=data,
                    auth=self.auth,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    logger.info("✓ Media metadata updated successfully")
                    return WPMedia.model_validate(response.json())
                else:
                    error = WPError.model_validate(response.json())
                    logger.error(f"❌ Failed to update media metadata: {error.message}")
                    raise Exception(f"WordPress API Error: {error.message}")

        except Exception as e:
            logger.error(f"Error updating media metadata: {str(e)}")
            raise

    async def _ensure_tags_exist(self, tags: List[str]) -> List[int]:
        """Ensure tags exist and return their IDs."""
        try:
            tag_ids = []
            for tag_name in tags:
                # Check if tag exists
                existing_tag = await self._get_tag_by_name(tag_name)
                if existing_tag:
                    tag_ids.append(existing_tag["id"])
                else:
                    # Create new tag
                    new_tag = await self._create_tag(tag_name)
                    tag_ids.append(new_tag["id"])
            return tag_ids
        except Exception as e:
            logger.error(f"Error ensuring tags exist: {str(e)}")
            raise

    async def _get_tag_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a tag by its name."""
        try:
            url = f"{self.api_url}/tags"
            params = {"search": name}
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    params=params,
                    auth=self.auth,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    tags = response.json()
                    return next(
                        (tag for tag in tags if tag["name"].lower() == name.lower()),
                        None
                    )
                return None

        except Exception as e:
            logger.error(f"Error getting tag: {str(e)}")
            raise

    async def _create_tag(self, name: str) -> Dict[str, Any]:
        """Create a new tag."""
        try:
            url = f"{self.api_url}/tags"
            data = {"name": name}
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    json=data,
                    auth=self.auth,
                    timeout=30.0
                )
                
                if response.status_code == 201:
                    return response.json()
                else:
                    error = WPError.model_validate(response.json())
                    raise Exception(f"WordPress API Error: {error.message}")

        except Exception as e:
            logger.error(f"Error creating tag: {str(e)}")
            raise

    async def check_api_status(self) -> bool:
        """Check if the WordPress API is accessible."""
        try:
            logger.info("\n=== Checking WordPress API Status ===")
            
            url = f"{self.api_url}"
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    auth=self.auth,
                    timeout=10.0
                )
                
                is_ready = response.status_code == 200
                logger.info(f"WordPress API status check: {'Ready' if is_ready else 'Not Ready'}")
                return is_ready

        except Exception as e:
            logger.error(f"❌ WordPress API status check failed: {str(e)}")
            return False
