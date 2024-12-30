import hashlib
import json

from abc import ABC
from typing import Optional

from redis.asyncio import Redis
from elasticsearch import AsyncElasticsearch

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5


class BaseService(ABC):
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def _get_from_cache(self, key: str, model) -> Optional[object]:
        data = await self.redis.get(key)
        if not data:
            return None
        return model.parse_raw(data)

    async def _put_to_cache(self, key: str, obj: object):
        await self.redis.set(key, obj.json(), ex=FILM_CACHE_EXPIRE_IN_SECONDS)

    async def _get_list_from_cache(self, key: str, model) -> Optional[list]:
        data = await self.redis.get(key)
        if not data:
            return None
        return [model.parse_raw(item) for item in json.loads(data)]

    async def _put_list_to_cache(self, key: str, obj_list: list):
        data = json.dumps([obj.json() for obj in obj_list])
        await self.redis.set(key, data, ex=FILM_CACHE_EXPIRE_IN_SECONDS)

    @staticmethod
    def generate_cache_key(prefix: str, *args, **kwargs) -> str:
        """
        Генерирует хэш для уникального набора параметров.

        :param prefix: Префикс для типа данных (например, 'film', 'genre', 'character').
        :param args: Позиционные аргументы.
        :param kwargs: Именованные аргументы.
        :return: Уникальный хэш-ключ для кэша.
        """
        key_data = json.dumps({'args': args, 'kwargs': kwargs}, sort_keys=True)
        hash_key = hashlib.md5(key_data.encode()).hexdigest()
        return f"{prefix}:{hash_key}"
