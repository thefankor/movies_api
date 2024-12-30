from functools import lru_cache
from typing import Optional

from redis.asyncio import Redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends

from db.elastic import get_elastic
from db.redis import get_redis
from models.genre import Genre
from services.base import BaseService



FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5


class GenreService(BaseService):
    async def get_genre_list(self) -> list[Genre]:
        genre_cache = self.generate_cache_key("genres")
        genres = await self._get_list_from_cache(genre_cache, Genre)
        if not genres:
            genres = await self._get_genres_list_from_elastic()
            await self._put_list_to_cache(genre_cache, genres)
        return genres

    async def get_by_id(self, genre_id: str) -> Optional[Genre]:
        genre_cache = self.generate_cache_key("genre", genre_id=genre_id)
        genre = await self._get_from_cache(genre_cache, Genre)
        if not genre:
            genre = await self._get_genre_from_elastic(genre_id)
            if not genre:
                return None
            await self._put_to_cache(genre_cache, genre)
        return genre

    async def _get_genres_list_from_elastic(self):
        try:
            doc = await self.elastic.search(index='genres', size=100)
            return [Genre(**genre['_source']) for genre in doc['hits']['hits']]
        except NotFoundError:
            return []  # Если фильм не найден

    async def _get_genre_from_elastic(self, genre_id):
        try:
            doc = await self.elastic.get(index='genres', id=genre_id)
            return Genre(**doc['_source'])
        except NotFoundError:
            return None


@lru_cache()
def get_genre_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
    ) -> GenreService:
    return GenreService(redis, elastic)