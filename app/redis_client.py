"""
کلاینت Redis برای کش و صف پیام‌ها
"""

from typing import Optional
import redis.asyncio as aioredis
from redis.asyncio import Redis

from config import settings

_redis_client: Optional[Redis] = None


async def get_redis() -> Redis:
    """دریافت کلاینت Redis"""
    global _redis_client

    if _redis_client is None:
        _redis_client = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            max_connections=20,
        )

    # بررسی اتصال
    await _redis_client.ping()
    return _redis_client


async def close_redis() -> None:
    """بستن اتصال Redis"""
    global _redis_client
    if _redis_client:
        await _redis_client.aclose()
        _redis_client = None


class RedisCache:
    """کلاس کمکی برای کار با Redis"""

    def __init__(self, redis: Redis, prefix: str = "bot"):
        self.redis = redis
        self.prefix = prefix

    def _key(self, key: str) -> str:
        return f"{self.prefix}:{key}"

    async def get(self, key: str) -> Optional[str]:
        return await self.redis.get(self._key(key))

    async def set(self, key: str, value: str, expire: int = 3600) -> None:
        await self.redis.setex(self._key(key), expire, value)

    async def delete(self, key: str) -> None:
        await self.redis.delete(self._key(key))

    async def exists(self, key: str) -> bool:
        return bool(await self.redis.exists(self._key(key)))

    async def increment(self, key: str, amount: int = 1) -> int:
        return await self.redis.incr(self._key(key), amount)

    async def expire(self, key: str, seconds: int) -> None:
        await self.redis.expire(self._key(key), seconds)

    async def get_int(self, key: str, default: int = 0) -> int:
        val = await self.get(key)
        return int(val) if val else default
