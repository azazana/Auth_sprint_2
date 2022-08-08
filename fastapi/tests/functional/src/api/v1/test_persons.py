import sys
import pytest
from http import HTTPStatus

from ....testdata.person_test_data import (
    test_person_data_dict_for_index,
    test_person_data_dict,
    test_person_detail_data_dict,
)
from ....testdata.films_test_data import test_shortfilm_data_dict

if sys.path[0].startswith("/home/"):
    sys.path.append("....")
    from src.models.enums import URLIndexName, NotFoundText
else:
    from models.enums import URLIndexName, NotFoundText

URL_INDEX = URLIndexName.person.value
NOT_FOUND_TEXT = NotFoundText.person.value

pytestmark = pytest.mark.asyncio


async def test_persons_fake_search(es_client, make_get_request):
    response = await make_get_request(f"/{URL_INDEX}/search/", {"query": "FakePerson"})

    assert response.status == HTTPStatus.NOT_FOUND
    assert len(response.body) == 1
    assert response.body["detail"] == NOT_FOUND_TEXT


async def test_persons_search(es_client, make_get_request):
    response = await make_get_request(f"/{URL_INDEX}/search/", {"query": "Baby"})

    assert response.status == HTTPStatus.OK
    assert len(response.body) == 1

    response.body[0]["film_ids"] = set(response.body[0]["film_ids"])
    test_person_data_dict[0]["film_ids"] = set(test_person_data_dict[0]["film_ids"])
    assert response.body[0] == test_person_data_dict[0]


async def test_persons_with_data(es_client, make_get_request):
    response = await make_get_request(f"/{URL_INDEX}/search/")

    assert response.status == HTTPStatus.OK
    assert len(response.body) == len(test_person_data_dict)

    for i in range(len(test_person_data_dict)):
        response.body[i]["film_ids"] = set(response.body[i]["film_ids"])
        test_person_data_dict[i]["film_ids"] = set(test_person_data_dict[i]["film_ids"])
    assert response.body == test_person_data_dict


async def test_persons_error_url(es_client, make_get_request):
    response = await make_get_request(f"/{URL_INDEX}/")

    assert response.status == HTTPStatus.NOT_FOUND
    assert len(response.body) == 1
    assert response.body["detail"] == "Not Found"


async def test_persons_fake_uuid(es_client, make_get_request):
    response = await make_get_request(f"/{URL_INDEX}/its_fake_uuid_person/")

    assert response.status == HTTPStatus.NOT_FOUND
    assert len(response.body) == 1
    assert response.body["detail"] == NOT_FOUND_TEXT


async def test_persons_films_role_for_uuid(es_client, make_get_request):
    response = await make_get_request(
        f'/{URL_INDEX}/{test_person_detail_data_dict[0]["id"]}/'
    )

    assert response.status == HTTPStatus.OK
    assert len(response.body) == len(test_person_detail_data_dict)
    assert response.body == test_person_detail_data_dict


async def test_persons_films_for_uuid(es_client, make_get_request):
    response = await make_get_request(
        f'/{URL_INDEX}/{test_person_data_dict_for_index[2]["id"]}/films/'
    )

    assert response.status == HTTPStatus.OK
    assert len(response.body) == 1
    assert response.body[0] == test_shortfilm_data_dict[2]


async def test_persons_films_for_uuid_2(es_client, make_get_request):
    response = await make_get_request(
        f'/{URL_INDEX}/{test_person_data_dict_for_index[0]["id"]}/films/'
    )

    assert response.status == HTTPStatus.OK
    assert len(response.body) == 2
    assert response.body == test_shortfilm_data_dict[0:2]
