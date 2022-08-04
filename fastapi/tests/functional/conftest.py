import asyncio
import sys
from typing import Optional
from dataclasses import dataclass
from multidict import CIMultiDictProxy

import aiohttp
import pytest

from .settings import settings
from .utils.MyElasticsearch import MyElasticsearch
from .utils.models_pydantic import (
    GenreForValidation,
    FilmForValidation,
    PersonForValidation
)
from .utils.transform_data_to_load_in_es import transform_data_to_load
from .testdata.genre_test_data import test_genres_data_dict
from .testdata.person_test_data import test_person_data_dict_for_index
from .testdata.films_test_data import test_film_data_dict_for_index
if sys.path[0].startswith("/home/"):
    sys.path.append("....")
    from src.models.enums import ESIndexName
else:
    from models.enums import ESIndexName

SERVICE_URL = settings.fastapi_url


@dataclass
class HTTPResponse:
    body: dict
    headers: CIMultiDictProxy[str]
    status: int


@pytest.fixture(scope='session')
async def es_client():
    client = MyElasticsearch(hosts=settings.es_host+':'+settings.es_port)
    await client.create_index_movies()
    await client.create_index_genres()
    await client.create_index_persons()
    film_data_to_load = transform_data_to_load(
        data=test_film_data_dict_for_index,
        model=FilmForValidation,
        index=ESIndexName.film.value
    )
    genre_data_to_load = transform_data_to_load(
        data=test_genres_data_dict,
        model=GenreForValidation,
        index=ESIndexName.genre.value
    )
    person_data_to_load = transform_data_to_load(
        data=test_person_data_dict_for_index,
        model=PersonForValidation,
        index=ESIndexName.person.value
    )
    all_data_to_load = film_data_to_load + genre_data_to_load + person_data_to_load
    await client.load_data(all_data_to_load)

    yield client
    [await client.delete_index(item.value) for item in ESIndexName]
    await client.close()


@pytest.fixture(scope='session')
async def session():
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest.fixture
def make_get_request(session):
    async def inner(method: str, params: Optional[dict] = None) -> HTTPResponse:
        params = params or {}
        url = 'http://' + SERVICE_URL + '/api/v1' + method  # в боевых системах старайтесь так не делать!
        async with session.get(url, params=params) as response:
            return HTTPResponse(
                body=await response.json(),
                headers=response.headers,
                status=response.status,
            )

    return inner


@pytest.fixture(scope="session", autouse=True)
def event_loop():
    loop = asyncio.get_event_loop_policy().get_event_loop()
    yield loop
    loop.close()
