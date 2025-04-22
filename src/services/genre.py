from functools import lru_cache

from elasticsearch import NotFoundError
from fastapi import Depends

from db.elastic import get_elastic
from db.redis import get_cache
from models.genre import Genre
from services.base import BaseService

from db.db import CacheWorker, SearchWorker

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5


class GenreService(BaseService):
    model = Genre
    cache_one_prefix = "genre"

    async def get_genre_list(self) -> list[Genre]:
        genre_cache = self.generate_cache_key("genres")
        genres = await self._get_list_from_cache(genre_cache, Genre)
        if not genres:
            genres = await self._get_genres_list_from_elastic()
            await self._put_list_to_cache(genre_cache, genres)
        return genres

    async def _get_genres_list_from_elastic(self):
        try:
            doc = await self.search.search(index='genres', size=100)
            return [Genre(**genre['_source']) for genre in doc['hits']['hits']]
        except NotFoundError:
            return []  # Если фильм не найден


@lru_cache()
def get_genre_service(
        cache: CacheWorker = Depends(get_cache),
        # redis: Redis = Depends(get_redis),
        search: SearchWorker = Depends(get_elastic),
    ) -> GenreService:
    return GenreService(cache, search)