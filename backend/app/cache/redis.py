"""Redis cache helpers with graceful failure handling."""

import logging

from redis.asyncio import Redis
from redis.exceptions import RedisError

from app.config import get_settings


logger = logging.getLogger(__name__)
settings = get_settings()
redis_client = Redis.from_url(settings.redis_url, decode_responses=True)


def cache_key(short_code: str) -> str:
    """Build the namespaced Redis key for a short code."""

    return f"url:{short_code}"


async def get_cached_url(short_code: str) -> str | None:
    """Return a cached original URL, or None when Redis is unavailable/missing."""

    try:
        return await redis_client.get(cache_key(short_code))
    except RedisError:
        logger.warning("Redis read failed for short code %s", short_code)
        return None


async def cache_url(short_code: str, original_url: str) -> None:
    """Cache an original URL for the configured TTL when Redis is available."""

    try:
        await redis_client.set(
            cache_key(short_code),
            original_url,
            ex=settings.redis_ttl_seconds,
        )
    except RedisError:
        logger.warning("Redis write failed for short code %s", short_code)


async def close_redis() -> None:
    """Close the Redis connection pool during application shutdown."""

    await redis_client.aclose()