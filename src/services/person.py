from functools import lru_cache
from typing import Optional

from redis.asyncio import Redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends

from db.elastic import get_elastic
from db.redis import get_redis
from models.person import Person
from models.film import Film
from services.base import BaseService


FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5


class PersonService(BaseService):
    async def get_by_id(self, person_id: str) -> Optional[Person]:
        pers = await self._get_person_from_elastic(person_id)
        return pers

    async def get_films_by_person(self, person_id: str) -> list[Film]:
        films = await self._get_films_info(person_id)
        return films

    async def _get_films_info(self, person_id):
        pers_films = await self.elastic.search(index='movies', query=get_query(person_id))
        film_ids = [Film(**film['_source']) for film in pers_films['hits']['hits']]
        return film_ids

    async def _get_person_from_elastic(self, person_id):
        try:
            pers = await self.elastic.get(index='person', id=person_id)
            film_ids = await self._get_film_ids_by_person(person_id)
            return Person(**pers['_source'], film_ids=film_ids)
        except NotFoundError:
            return None

    async def _get_film_ids_by_person(self, person_id):
        pers_films = await self.elastic.search(index='movies', query=get_query(person_id))
        film_ids = [film['_source']['id'] for film in pers_films['hits']['hits']]
        return film_ids

    async def get_person_list(self, q, page_size, page_number) -> list[Person]:
        films = await self._get_persons_list_from_elastic(q, page_size, page_number)
        return films

    async def _get_persons_list_from_elastic(self, q, page_size, page_number):
        try:
            query = {
                "match": {
                    "full_name": {
                        "query": q,
                        "fuzziness": "AUTO"
                    }
                }
            }
            doc = await self.elastic.search(index='person', size=page_size, query=query,
                                            from_=(page_number - 1) * page_size)

            return [Person(**person['_source'], film_ids=await self._get_film_ids_by_person(person['_source']['id']))
                    for person in doc['hits']['hits']]
        except NotFoundError:
            return []


@lru_cache()
def get_person_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
    ) -> PersonService:
    return PersonService(redis, elastic)


def get_query(pers):
    return {
        "bool": {
          "should": [
            {
              "nested": {
                "path": "actors",
                "query": {
                  "term": {
                    "actors.id": {
                      "value": pers
                    }
                  }
                }
              }
            },
            {
              "nested": {
                "path": "directors",
                "query": {
                  "term": {
                    "directors.id": {
                      "value": pers
                    }
                  }
                }
              }
            },
            {
              "nested": {
                "path": "writers",
                "query": {
                  "term": {
                    "writers.id": {
                      "value": pers
                    }
                  }
                }
              }
            }
          ]
        }
      }