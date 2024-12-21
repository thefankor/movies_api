from abc import ABC

from redis.asyncio import Redis
from elasticsearch import AsyncElasticsearch


class BaseService(ABC):
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic
