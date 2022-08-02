import sys
import pytest
from http import HTTPStatus

from ....testdata.genre_test_data import test_genres_data_dict
if sys.path[0].startswith("/home/"):
    sys.path.append("....")
    from src.models.enums import URLIndexName, NotFoundText
else:
    from models.enums import URLIndexName, NotFoundText

URL_INDEX = URLIndexName.genre.value
NOT_FOUND_TEXT = NotFoundText.genre.value

pytestmark = pytest.mark.asyncio


async def test_genres_with_data(es_client, make_get_request):
    response = await make_get_request(f'/{URL_INDEX}/')

    assert response.status == HTTPStatus.OK
    assert len(response.body) == len(test_genres_data_dict)
    assert response.body == test_genres_data_dict


async def test_genres_by_id_with_data(es_client, make_get_request):
    response = await make_get_request(
        f'/{URL_INDEX}/{test_genres_data_dict[0]["id"]}')

    assert response.status == HTTPStatus.OK
    assert len(response.body) == 2
    assert response.body == test_genres_data_dict[0]


async def test_genres_by_fake_id_with_data(es_client, make_get_request):
    response = await make_get_request(f'/{URL_INDEX}/fake_uuid_genre/')

    assert response.status == HTTPStatus.NOT_FOUND
    assert len(response.body) == 1
    assert response.body['detail'] == NOT_FOUND_TEXT

