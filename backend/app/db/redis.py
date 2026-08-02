from typing import Optional

from redis.asyncio import Redis

from app.core.config import settings

_redis_client: Optional[Redis] = None

async def get_redis() -> Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            decode_responses=True
        )
    return _redis_client
