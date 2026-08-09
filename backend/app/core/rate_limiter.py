from typing import Optional
from fastapi import Request, HTTPException, status
from redis.asyncio import Redis
from app.core.config import settings

_redis_client: Optional[Redis] = None


async def get_redis_client() -> Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = Redis.from_url(settings.REDIS_URI, decode_responses=True)
    return _redis_client


class RateLimiter:
    def __init__(self, limit: int = 5, window_seconds : int = 60) -> None:
        self.limit = limit
        self.window_seconds = window_seconds

    async def __call__(self, request: Request) -> None:
        client_ip = request.client.host if request.client else "127.0.0.1"
        key = f"ratelimit:lauth:{client_ip}:{request.url.path}"
        redis = await get_redis_client()
        try:
            current = await redis.incr(key)
            if current == 1:
                await redis.expire(key, self.window_seconds)
            if current > self.limit:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Too many requests. Please try again later.",
                )
        except HTTPException:
            raise
        except Exception:
            # If Redis is unavailable, allow request in development/tests
            pass
