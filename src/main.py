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


async def init_redis(host: str, port: int) -> RedisCache:
    client = await aioredis.from_url(f"redis://{host}:{port}", max_connections=20)
    return RedisCache(client)

async def init_elastic(host: str, port: int) -> ElasticSearchService:
    client = AsyncElasticsearch(hosts=[f"http://{host}:{port}"])
    return ElasticSearchService(client)

@app.on_event('startup')
async def startup():
    redis.redis_cache = await init_redis(config.REDIS_HOST, config.REDIS_PORT)
    elastic.es = await init_elastic(config.ELASTIC_HOST, config.ELASTIC_PORT)


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

