import sys
from http import HTTPStatus
from uuid import uuid4

import pytest
from aioredis import Redis

from ....settings import settings
from ....testdata.films_test_data import (
    test_film_data_dict_for_index,
    test_shortfilm_data_dict
)
from ....utils.transform_data_to_load_in_es import transform_data_to_load
from ....utils.models_pydantic import FilmForValidation, Film
if sys.path[0].startswith("/home/"):
    sys.path.append("....")
    from src.models.enums import URLIndexName, NotFoundText, ESIndexName
else:
    from models.enums import URLIndexName, NotFoundText, ESIndexName

URL_INDEX = URLIndexName.film.value
ES_INDEX = ESIndexName.film.value
NOT_FOUND_TEXT = NotFoundText.film.value

test_data_for_load = transform_data_to_load(
    data=test_film_data_dict_for_index,
    model=FilmForValidation,
    index=ES_INDEX
)

pytestmark = pytest.mark.asyncio


async def test_films_with_data(es_client, make_get_request):
    response = await make_get_request(f'/{URL_INDEX}/')

    assert response.status == HTTPStatus.OK
    assert len(response.body) == len(test_shortfilm_data_dict)
    assert response.body == test_shortfilm_data_dict


async def test_films_with_id(es_client, make_get_request):
    for data in test_data_for_load:
        response = await make_get_request(f'/{URL_INDEX}/{data["id"]}')

        assert response.status == HTTPStatus.OK
        assert response.body == Film(**data).dict()


async def test_films_with_id_fake(es_client, make_get_request):
    uuid: str = str(uuid4())
    response = await make_get_request(URL_INDEX + uuid)

    assert response.status == HTTPStatus.NOT_FOUND


async def test_persons_fake_search(es_client, make_get_request):
    response = await make_get_request(f'/{URL_INDEX}/search/', {'query': 'FakeFilm'})

    assert response.status == HTTPStatus.NOT_FOUND
    assert len(response.body) == 1
    assert response.body['detail'] == NOT_FOUND_TEXT


async def test_persons_search(es_client, make_get_request):
    response = await make_get_request(f'/{URL_INDEX}/search/', {'query': 'First'})

    assert response.status == HTTPStatus.OK
    assert len(response.body) == 1
    assert response.body[0] == test_shortfilm_data_dict[0]


async def test_films_with_cache(es_client, make_get_request):
    await make_get_request(f'/{URL_INDEX}/')
    await es_client.delete_index(ES_INDEX)
    response = await make_get_request(f'/{URL_INDEX}/')

    assert response.status == HTTPStatus.OK
    assert len(response.body) == len(test_shortfilm_data_dict)
    assert response.body == test_shortfilm_data_dict

    await es_client.create_index_movies()
    await es_client.load_data(test_data_for_load)


async def test_films_with_no_cache(es_client, make_get_request):
    await make_get_request(f'/{URL_INDEX}/')
    await es_client.delete_index(ES_INDEX)
    r_for_clear = Redis(host=settings.redis_host)
    await r_for_clear.flushall()

    with pytest.raises(Exception):
        await make_get_request(f'/{URL_INDEX}/')

    await es_client.create_index_movies()
    await es_client.load_data(test_data_for_load)
