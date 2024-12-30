from functools import lru_cache
from typing import Optional


# from aioredis import Redis
from redis.asyncio import Redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends

from db.elastic import get_elastic
from db.redis import get_redis
from models.film import Film
from services.base import BaseService
# from base import BaseService


FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5


class FilmService(BaseService):
    async def get_by_id(self, film_id: str) -> Optional[Film]:
        film_cache = self.generate_cache_key("film", id=film_id)
        film = await self._get_from_cache(film_cache, Film)
        if not film:
            film = await self._get_film_from_elastic(film_id)
            if not film:
                return None
            await self._put_to_cache(film_cache, film)
        return film

    async def _get_film_from_elastic(self, film_id: str) -> Optional[Film]:
        try:
            doc = await self.elastic.get(index='movies', id=film_id)
            return Film(**doc['_source'])
        except NotFoundError:
            return None  # Если фильм не найден

    async def get_film_list(self, q, sort, page_size, page_number, genre) -> list[Film]:
        films_cache = self.generate_cache_key("films", q=q, sort=sort,
                                              page_size=page_size, page_number=page_number, genre=genre)
        films = await self._get_list_from_cache(films_cache, Film)
        if not films:
            films = await self._get_films_list_from_elastic(q, sort, page_size, page_number, genre)
            await self._put_list_to_cache(films_cache, films)
        return films

    async def _get_films_list_from_elastic(self, q, sort, page_size, page_number, genre):
        try:
            query = None
            if q:
                query = {
                    "match": {
                        "title": {
                            "query": q,
                            "fuzziness": "AUTO"
                        }
                    }
                }
            if genre:
                query = {
                    "nested": {
                        "path": "genres",
                        "query": {
                            "bool": {
                                "must": [
                                    {"term": {"genres.id": genre}}
                                ]
                            }
                        }
                    }
                }
            sort_clause = []
            if sort:
                if sort.startswith("-"):  # Сортировка по убыванию
                    field = sort[1:]  # Убираем знак минус
                    sort_clause.append({field: {"order": "desc"}})
                else:  # Сортировка по возрастанию
                    sort_clause.append({sort: {"order": "asc"}})

            doc = await self.elastic.search(index='movies', size=page_size, query=query,
                                            from_=(page_number-1)*page_size, sort=sort_clause)

            return [Film(**film['_source']) for film in doc['hits']['hits']]
        except NotFoundError:
            return []  # Если фильм не найден


# get_film_service — это провайдер FilmService.
# С помощью Depends он сообщает, что ему необходимы Redis и Elasticsearch
# Для их получения вы ранее создали функции-провайдеры в модуле db
# Используем lru_cache-декоратор, чтобы создать объект сервиса в едином экземпляре(синглтона)
@lru_cache()
def get_film_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
    ) -> FilmService:
    return FilmService(redis, elastic)