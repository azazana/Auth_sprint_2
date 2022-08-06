from abc import ABC, abstractmethod
from typing import Optional, Any

from aioredis import Redis
from elasticsearch import AsyncElasticsearch, NotFoundError

from models.input_base import Pagination
from models.input_models import ListForChash
from core.config import settings


class AsyncCacheStorage(ABC):
    @abstractmethod
    async def get(self, key: str, **kwargs):
        pass

    @abstractmethod
    async def set(self, key: str, value: Any, **kwargs):
        pass


class RedisCacheStorage(AsyncCacheStorage):

    def __init__(self, redis: Redis, expire: int):
        self.redis = redis
        self.ex = expire

    async def get(self, key: str, **kwargs):
        return await self.redis.get(name=key)

    async def set(self, key: str, value: Any, **kwargs):
        await self.redis.set(name=key, value=value, ex=self.ex)


def cache(storage: AsyncCacheStorage):
    def async_cache(func):
        """Кэш запросов к ElasticSearch"""

        async def wrapper(self, index, url, model, **kwargs):

            str_key = index + url + str(kwargs.values())
            data = await storage.get(str_key)
            if not data:
                py_list: ListForChash = ListForChash()
                py_list.data = [
                    data
                    async for data in func(
                        self,
                        model=model,
                        index=index,
                        url=url,
                        **kwargs
                    )
                ]
                await storage.set(str_key, py_list.json())
                for item in py_list.data:
                    yield item
            else:
                if data == b'{"data": [null]}':
                    yield None
                for item in ListForChash.parse_raw(data).data:
                    yield item

        return wrapper
    return async_cache


class BaseService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    @staticmethod
    def _get_query_films_search(search: str) -> dict:
        return {

            "multi_match": {
                "query": search,
                "fields": [
                    "title",
                    "description",
                    "directors_names",
                    "writers_names",
                    "actors_names",
                ],
                "fuzziness": "auto",
            }
        }

    @staticmethod
    def _get_query_films_search2(search, premium: int) -> dict:
        return {
            "bool": {
                  "must": {
                    "multi_match": {
                        "query": search,
                        "fields": [
                            "title",
                            "description",
                            "directors_names",
                            "writers_names",
                            "actors_names",
                        ],
                        "fuzziness": "auto",
                    },
                  },
                  "filter": {
                    "term": {
                      "premium": premium
                    }
                  }
                }
        }

    @staticmethod
    def _get_query_films_list(query_id: str, path: str) -> dict:
        return {
            "nested": {
                "path": path,
                "query": {"bool": {"must": [{"match": {f"{path}.id": query_id}}]}},
            }
        }

    @staticmethod
    def _get_query_person_search_multimatch(query: str) -> dict:
        return {
            "multi_match": {
                "query": query,
                "fields": ["full_name"],
                "fuzziness": "auto",
            }
        }

    # deprecated
    @staticmethod
    def _get_query_person_search_match(query: str) -> dict:
        return {"match": {"full_name": query}}

    @staticmethod
    def _get_query_config(
            pagination: Pagination = Pagination(),
            sort: str = None,
    ) -> dict:
        body = dict()

        if pagination.page_size is not None:
            body["size"] = pagination.page_size
        if pagination.page_number is not None:
            body["from"] = (pagination.page_number - 1) * pagination.page_size

        if sort is not None:
            if sort.startswith("-"):
                sort = "desc"
            else:
                sort = "asc"
            body["sort"] = {"imdb_rating": sort}

        return body

    @cache(
        storage=RedisCacheStorage(
            redis=Redis(host=settings.REDIS_HOST),
            expire=settings.CACHE_EXPIRE
        )
    )
    async def get_model_by_id_from_elastic(
            self,
            index: str,
            model_id: str,
            model,
            url: Optional[str] = None
    ):
        try:
            doc = await self.elastic.get(index, model_id)
            yield model(**doc["_source"])
        except NotFoundError:
            yield None
