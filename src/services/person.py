from functools import lru_cache

from elasticsearch import NotFoundError
from fastapi import Depends

from db.elastic import get_elastic
from db.redis import get_cache
from models.person import Person
from models.film import Film
from services.base import BaseService
from services.elastic_builder import ElasticQueryBuilder as EQBuilder

from db.db import CacheWorker, SearchWorker

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5


class PersonService(BaseService):
    model = Person
    cache_one_prefix = "person"

    async def get_films_by_person(self, person_id: str) -> list[Film]:
        person_cache = self.generate_cache_key("person_films", person_id=person_id)
        print(person_cache)
        films = await self._get_list_from_cache(person_cache, Film)
        if not films:
            print('no cache')
            films = await self._get_films_info(person_id)
            await self._put_list_to_cache(person_cache, films)
        return films

    async def _get_films_info(self, person_id):
        pers_films = await self.search.search(index='movies', query=get_query(person_id))
        film_ids = [Film(**film['_source']) for film in pers_films['hits']['hits']]
        return film_ids

    async def _get_one_from_elastic(self, person_id):
        try:
            pers = await self.search.get(index='person', id=person_id)
            film_ids = await self._get_film_ids_by_person(person_id)
            return Person(**pers['_source'], film_ids=film_ids)
        except (NotFoundError, TypeError):
            return None

    async def _get_film_ids_by_person(self, person_id):
        pers_films = await self.search.search(index='movies', query=get_query(person_id))
        film_ids = [film['_source']['id'] for film in pers_films['hits']['hits']]
        return film_ids

    async def get_person_list(self, q, page_size, page_number) -> list[Person]:
        person_cache = self.generate_cache_key("persons", q=q, page_size=page_size, page_number=page_number)
        persons = await self._get_list_from_cache(person_cache, Person)
        if not persons:
            persons = await self._get_persons_list_from_elastic(q, page_size, page_number)
            await self._put_list_to_cache(person_cache, persons)
        return persons

    async def _get_persons_list_from_elastic(self, q, page_size, page_number):
        try:
            query = EQBuilder.match(field="full_name", query=q)
            doc = await self.search.search(index='person', size=page_size, query=query,
                                            from_=(page_number - 1) * page_size)

            return [Person(**person['_source'], film_ids=await self._get_film_ids_by_person(person['_source']['id']))
                    for person in doc['hits']['hits']]
        except NotFoundError:
            return []


@lru_cache()
def get_person_service(
        cache: CacheWorker = Depends(get_cache),
        search: SearchWorker = Depends(get_elastic),
    ) -> PersonService:
    return PersonService(cache, search)


def get_query(pers):
    person_queries = [
        EQBuilder.nested(
            path="actors",
            query=EQBuilder.term(field="actors.id", value=pers)
        ),
        EQBuilder.nested(
            path="directors",
            query=EQBuilder.term(field="directors.id", value=pers)
        ),
        EQBuilder.nested(
            path="writers",
            query=EQBuilder.term(field="writers.id", value=pers)
        ),
    ]
    return EQBuilder.bool_query(should=person_queries)
