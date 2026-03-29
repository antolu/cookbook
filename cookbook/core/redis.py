from __future__ import annotations

import redis.asyncio as aioredis

from cookbook.config import settings

redis_client: aioredis.Redis | None = None


async def init_redis() -> None:
    """Initialize Redis connection."""
    global redis_client
    redis_client = aioredis.from_url(settings.redis_url, decode_responses=True)


async def close_redis() -> None:
    """Close Redis connection."""
    if redis_client:
        await redis_client.close()


async def get_redis() -> aioredis.Redis:
    """Get Redis client."""
    if not redis_client:
        await init_redis()
    return redis_client