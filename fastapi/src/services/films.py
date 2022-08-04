from functools import lru_cache

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from db.elastic import get_elastic
from db.redis import get_redis
from models.enums import ESIndexName
from models.input_base import Pagination
from models.input_models import Film
from services.base import BaseService, cache, RedisCacheStorage
from core.config import settings

ES_INDEX_NAME = ESIndexName.film.value


class FilmService(BaseService):
    @cache(
        storage=RedisCacheStorage(
            redis=Redis(host=settings.REDIS_HOST),
            expire=settings.CACHE_EXPIRE
        )
    )
    async def get_films(
            self,
            pagination: Pagination = None,
            search: str = None,
            sort: str = None,
            role: str = None,
            person_id: str = None,
            genre_id: str = None,
            **kwargs
    ):
        """
        Фукция общая с 3мя вариантами работы,
        1-поиском полнотекстовым по фильмам,
        2-поиском фильмов с определенным жанром,
        3-поиском фильмов с участием определённой персоны в определённой её роли (актёр, режисёр, директор)
        :param pagination: page_size: количество фильмов на странице, page_number: номер текущей страницы
        :param search: 1 вариант работы
        :param sort: возможность сортировки по рейтингу
        :param genre_id: 2 вариант работы
        :param role: 3 вариант работы
        :param person_id: 3 вариант работы
        :return: Генератор по Фильмам
        """
        if pagination:
            body = self._get_query_config(
                pagination=pagination,
                sort=sort
            )
        else:
            body = dict()

        # TODO: поддержку фильтра жанров во время поиска
        if genre_id is not None:
            body["query"] = self._get_query_films_list(path="genres", query_id=genre_id)
        if search is not None:
            body["query"] = self._get_query_films_search(search=search)
        if role and person_id:
            body["query"] = self._get_query_films_list(query_id=person_id, path=role)

        response = await self.elastic.search(index=ES_INDEX_NAME, body=body)
        for data in response["hits"]["hits"]:
            yield Film(**data["_source"])

    async def get_role_film_ids_list(
            self,
            person_id: str,
            role: str,
            **kwargs
    ) -> list[str]:
        return [
            film.id
            async for film in self.get_films(
                person_id=person_id,
                role=role,
                **kwargs
            )
        ]


@lru_cache()
def get_film_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(redis, elastic)
