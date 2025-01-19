from functools import lru_cache

from elasticsearch import NotFoundError
from fastapi import Depends

from db.elastic import get_elastic
from db.redis import get_cache
from models.film import Film
from services.base import BaseService

from db.db import CacheWorker, SearchWorker

from services.elastic_builder import ElasticQueryBuilder as EQBuilder


FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5


class FilmService(BaseService):
    model = Film
    cache_one_prefix = 'film'

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
                query = EQBuilder.match('title', q)
            if genre:
                query = EQBuilder.nested(path="genres",
                                         query=EQBuilder.bool_query(
                                             must=EQBuilder.term(field="genres.id", value=genre)
                                            )
                                         )

            sort_clause = []
            if sort:
                if sort.startswith("-"):  # Сортировка по убыванию
                    field = sort[1:]  # Убираем знак минус
                    sort_clause.append({field: {"order": "desc"}})
                else:  # Сортировка по возрастанию
                    sort_clause.append({sort: {"order": "asc"}})

            doc = await self.search.search(index='movies', size=page_size, query=query,
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
        cache: CacheWorker = Depends(get_cache),
        search: SearchWorker = Depends(get_elastic),
    ) -> FilmService:
    return FilmService(cache, search)