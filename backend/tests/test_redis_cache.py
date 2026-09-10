import pytest
from redis.exceptions import RedisError

from app.cache import redis as redis_cache


def test_cache_key_uses_url_namespace() -> None:
    assert redis_cache.cache_key("9IX") == "url:9IX"


class FakeRedis:
    def __init__(self) -> None:
        self.values: dict[str, str] = {}
        self.expirations: dict[str, int] = {}

    async def get(self, key: str) -> str | None:
        return self.values.get(key)

    async def set(self, key: str, value: str, ex: int) -> None:
        self.values[key] = value
        self.expirations[key] = ex


@pytest.mark.asyncio
async def test_cache_helpers_store_and_read_with_ttl(monkeypatch) -> None:
    fake_redis = FakeRedis()
    monkeypatch.setattr(redis_cache, "redis_client", fake_redis)

    await redis_cache.cache_url("9IX", 1, "https://example.com")

    cached = await redis_cache.get_cached_url("9IX")
    assert cached is not None
    assert cached.url_id == 1
    assert cached.original_url == "https://example.com"
    assert fake_redis.expirations["url:9IX"] == 3600


class FailingRedis:
    async def get(self, key: str) -> str:
        raise RedisError("redis unavailable")

    async def set(self, key: str, value: str, ex: int) -> None:
        raise RedisError("redis unavailable")

    async def delete(self, key: str) -> None:
        raise RedisError("redis unavailable")


@pytest.mark.asyncio
async def test_cache_failures_are_non_fatal(monkeypatch) -> None:
    monkeypatch.setattr(redis_cache, "redis_client", FailingRedis())

    assert await redis_cache.get_cached_url("9IX") is None
    await redis_cache.cache_url("9IX", 1, "https://example.com")
    await redis_cache.delete_cached_url("9IX")