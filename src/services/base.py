import hashlib
import json

from abc import ABC
from typing import Optional, TypeVar

from elasticsearch import NotFoundError

from db.db import CacheWorker, SearchWorker

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5

T = TypeVar('T')

class BaseService(ABC):
    model = None
    cache_one_prefix = None

    def __init__(self, cache: CacheWorker, search: SearchWorker):
        self.cache = cache
        self.search = search

    async def get_by_id(self, obj_id: str) -> Optional[T]:
        obj_cache = self.generate_cache_key(self.cache_one_prefix, id=obj_id)
        obj = await self._get_from_cache(obj_cache, self.model)
        if not obj:
            obj = await self._get_one_from_elastic(obj_id)
            if not obj:
                return None
            await self._put_to_cache(obj_cache, obj)
        return obj

    async def _get_one_from_elastic(self, obj_id: str) -> Optional[T]:
        try:
            doc = await self.search.get(index=self.model.__title__, id=obj_id)
            return self.model(**doc['_source'])
        except (NotFoundError, TypeError):
            return None  # Если фильм не найден

    async def _get_from_cache(self, key: str, model) -> Optional[object]:
        data = await self.cache.get(key)
        if not data:
            return None
        return model.parse_raw(data)

    async def _put_to_cache(self, key: str, obj: object):
        await self.cache.set(key, obj.json(), ex=FILM_CACHE_EXPIRE_IN_SECONDS)

    async def _get_list_from_cache(self, key: str, model) -> Optional[list]:
        data = await self.cache.get(key)
        if not data:
            return None
        return [model.parse_raw(item) for item in json.loads(data)]

    async def _put_list_to_cache(self, key: str, obj_list: list):
        data = json.dumps([obj.json() for obj in obj_list])
        await self.cache.set(key, data, ex=FILM_CACHE_EXPIRE_IN_SECONDS)

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
