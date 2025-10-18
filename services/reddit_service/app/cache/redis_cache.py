# app/cache/redis_cache.py
from typing import Optional, Any
import aioredis
import json
from app.core.config import Settings

class RedisCache:
    def __init__(self, settings: Settings):
        self.redis = aioredis.from_url(settings.REDIS_URL)
        self.ttl = settings.CACHE_TTL

    async def get(self, key: str) -> Optional[Any]:
        value = await self.redis.get(key)
        return json.loads(value) if value else None

    async def set(self, key: str, value: Any) -> None:
        await self.redis.setex(
            key,
            self.ttl,
            json.dumps(value)
        )