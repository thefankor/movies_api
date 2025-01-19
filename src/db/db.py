from abc import ABC, abstractmethod
from typing import Any


class CacheWorker(ABC):
    def __init__(self, client: Any, **kwargs):
        self.client = client
        self.extra_args = kwargs

    @abstractmethod
    async def get(self, key: str, *args, **kwargs):
        pass

    @abstractmethod
    async def set(self, key: str, value, *args, **kwargs):
        pass

    async def close(self):
        self.client.close()


class SearchWorker(ABC):
    def __init__(self, client: Any, **kwargs):
        self.client = client
        self.extra_args = kwargs

    @abstractmethod
    async def get(self, *args, **kwargs):
        """index: str, id: str"""
        pass

    @abstractmethod
    async def search(self, *args, **kwargs):
        """index: str, query: dict, sort: list, size: int, from_: int"""
        pass

    async def close(self):
        self.client.close()
