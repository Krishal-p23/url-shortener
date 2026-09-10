"""Redis cache helpers with graceful failure handling."""

import logging
import json
from dataclasses import dataclass

from redis.asyncio import Redis
from redis.exceptions import RedisError

from app.config import get_settings


logger = logging.getLogger(__name__)
settings = get_settings()
redis_client = Redis.from_url(
    settings.redis_url,
    decode_responses=True,
    socket_connect_timeout=settings.redis_timeout_seconds,
    socket_timeout=settings.redis_timeout_seconds,
)


@dataclass(frozen=True)
class CachedURL:
    """URL data needed to redirect and record analytics from the cache."""

    url_id: int
    original_url: str


def cache_key(short_code: str) -> str:
    """Build the namespaced Redis key for a short code."""

    return f"url:{short_code}"


async def get_cached_url(short_code: str) -> CachedURL | None:
    """Return cached URL data, or None when Redis is unavailable/missing."""

    try:
        value = await redis_client.get(cache_key(short_code))
        if value is None:
            return None
        payload = json.loads(value)
        return CachedURL(
            url_id=int(payload["url_id"]),
            original_url=payload["original_url"],
        )
    except (RedisError, ValueError, KeyError, TypeError, json.JSONDecodeError):
        logger.warning("Redis read failed for short code %s", short_code)
        return None


async def cache_url(short_code: str, url_id: int, original_url: str) -> None:
    """Cache URL identity and destination for the configured TTL."""

    try:
        await redis_client.set(
            cache_key(short_code),
            json.dumps({"url_id": url_id, "original_url": original_url}),
            ex=settings.redis_ttl_seconds,
        )
    except RedisError:
        logger.warning("Redis write failed for short code %s", short_code)


async def delete_cached_url(short_code: str) -> None:
    """Remove a URL from Redis when it is deactivated."""

    try:
        await redis_client.delete(cache_key(short_code))
    except RedisError:
        logger.warning("Redis delete failed for short code %s", short_code)


async def close_redis() -> None:
    """Close the Redis connection pool during application shutdown."""

    await redis_client.aclose()