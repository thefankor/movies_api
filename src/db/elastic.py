import uuid
from typing import Optional

from elasticsearch import AsyncElasticsearch, Elasticsearch

from pydantic import BaseModel, Field

es: AsyncElasticsearch = None

class Person(BaseModel):
    id: uuid.UUID
    name: str


class Genre(BaseModel):
    id: uuid.UUID
    name: str


class Film(BaseModel):
    id: str
    title: str
    description: Optional[str]
    rating: float = Field(default=0.0)
    genres: list[Genre]
    directors: list[Person]
    writers: list[Person]
    actors: list[Person]

# Функция понадобится при внедрении зависимостей
async def get_elastic() -> AsyncElasticsearch:
    return es

if __name__ == '__main__':
    es = Elasticsearch("http://localhost:9200")

    # Параметры для поиска по ID
    index = "movies"
    doc_id = "12afc5d5-af95-489b-801e-70cefa1b3ce5"

    # Запрос для получения документа
    response = es.search(index=index, size=10, from_=1, sort=[{"rating": {"order": "desc"}}],)
    # doc = es.search(index=index)
    # films = [Film(**film['_source']) for film in doc['hits']['hits']]
    # films = [Film(**film['_source']) for film in doc['hits']['hits']]

    # Вывод результата
    print(response)