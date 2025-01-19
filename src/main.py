import logging
import redis.asyncio as aioredis
import uvicorn as uvicorn

from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from api.v1 import film, genre, person
from core import config
from core.logger import LOGGING
from db import elastic, redis
from db.redis import RedisCache
from db.elastic import ElasticSearchService

app = FastAPI(
    title=config.PROJECT_NAME,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
)


@app.on_event('startup')
async def startup():
    # Подключаемся к базам при старте сервера
    # Подключиться можем при работающем event-loop
    # Поэтому логика подключения происходит в асинхронной функции
    redis_client = await aioredis.from_url(f"redis://{config.REDIS_HOST}:{config.REDIS_PORT}", max_connections=20)
    es_client = AsyncElasticsearch(hosts=[f"http://{config.ELASTIC_HOST}:{config.ELASTIC_PORT}"])

    redis.redis_cache = RedisCache(redis_client)
    elastic.es = ElasticSearchService(es_client)


@app.on_event('shutdown')
async def shutdown():
    # Отключаемся от баз при выключении сервера
    await redis.redis_cache.close()
    await elastic.es.close()


app.include_router(film.router, prefix='/v1/film', tags=['film'])
app.include_router(genre.router, prefix='/v1/genre', tags=['genre'])
app.include_router(person.router, prefix='/v1/person', tags=['person'])

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=8000,
        log_config=LOGGING,
        log_level=logging.DEBUG,
    )

