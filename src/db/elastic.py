from elasticsearch import AsyncElasticsearch, NotFoundError

from db.db import SearchWorker


class ElasticSearchService(SearchWorker):
    def __init__(self, client: AsyncElasticsearch):
        super().__init__(client)
        self.es = self.client

    async def get(self, index: str, id: str, **kwargs):
        try:
            return await self.es.get(index=index, id=id, **kwargs)
        except NotFoundError:
            return None

    async def search(self, index: str, **kwargs):
        return await self.es.search(index=index, **kwargs)


es: ElasticSearchService = None


async def get_elastic() -> ElasticSearchService:
    return es
