from __future__ import annotations

import redis.asyncio as aioredis

from cookbook.config import settings

redis_client: aioredis.Redis | None = None


def init_redis() -> None:
    """Initialize Redis connection."""
    global redis_client  # noqa: PLW0603
    # Use redis.url from Settings
    redis_client = aioredis.from_url(settings.redis.url, decode_responses=True)


async def close_redis() -> None:
    """Close Redis connection."""
    if redis_client:
        await redis_client.close()


async def get_redis() -> aioredis.Redis:  # noqa: RUF029
    """Get Redis client."""
    global redis_client  # noqa: PLW0602
    if redis_client is None:
        init_redis()
    assert redis_client is not None
    return redis_client
