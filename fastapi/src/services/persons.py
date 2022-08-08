from functools import lru_cache

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from db.elastic import get_elastic
from db.redis import get_redis
from models.enums import ESIndexName
from models.input_base import Pagination
from models.input_models import Person
from services.base import BaseService, cache, RedisCacheStorage
from core.config import settings

ES_INDEX_NAME = ESIndexName.person.value


class PersonService(BaseService):
    @cache(
        storage=RedisCacheStorage(
            redis=Redis(host=settings.REDIS_HOST), expire=settings.CACHE_EXPIRE
        )
    )
    async def search_persons(self, pagination: Pagination, query: str = None, **kwargs):
        body = self._get_query_config(pagination=pagination)

        if query is not None:
            body["query"] = self._get_query_person_search_multimatch(query=query)
        response = await self.elastic.search(index=ES_INDEX_NAME, body=body)
        for data in response["hits"]["hits"]:
            yield Person(**data["_source"])


@lru_cache()
def get_person_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(redis, elastic)
