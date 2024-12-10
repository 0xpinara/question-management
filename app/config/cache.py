from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis
from typing import Optional

class CacheConfig:
    redis_url: str = "redis://redis:6379"
    prefix: str = "fastapi-cache"
    
    @classmethod
    async def init_cache(cls):
        try:
            redis = aioredis.from_url(
                cls.redis_url,
                encoding="utf8",
                decode_responses=True
            )
            FastAPICache.init(
                RedisBackend(redis),
                prefix=cls.prefix
            )
        except Exception as e:
            print(f"Failed to initialize cache: {str(e)}")
            # You might want to handle this error differently
            pass

    @classmethod
    async def clear_cache(cls):
        try:
            if FastAPICache.get_backend():
                await FastAPICache.clear()
        except Exception as e:
            print(f"Failed to clear cache: {str(e)}")