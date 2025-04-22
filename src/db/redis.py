from typing import Any

import redis.asyncio as redis

from db.db import CacheWorker


class RedisCache(CacheWorker):
    def __init__(self, client: redis.Redis):
        super().__init__(client)
        self.redis = self.client

    async def get(self, key: str, *args, **kwargs):
        print("get redis")
        return await self.redis.get(key)

    async def set(self, key: str, value: Any, ex: int = None, *args, **kwargs):
        print("set redis")
        await self.redis.set(key, value, ex=ex)


redis_cache: RedisCache = None


async def get_cache() -> RedisCache:
    return redis_cache