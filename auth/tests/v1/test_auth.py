import datetime
import random
import pytest
from http import HTTPStatus

pytestmark = pytest.mark.asyncio
TEST_EMAIL = f'test{random.randint(100, 200)}@test.ru'
TEST_PASSWORD = '123123'
TEST_NAME = 'qwe'


async def test_signup(make_post_request):
    response = await make_post_request(
        f'/auth/v1/signup?email={TEST_EMAIL}&password={TEST_PASSWORD}&name={TEST_NAME}'
    )

    assert response.status == HTTPStatus.OK
    # assert response.body == {'msg': 'signup success'}
    assert response.body.get('msg') == 'signup success'


async def test_signup_email_exists(make_post_request):
    response = await make_post_request(
        f'/auth/v1/signup?email={TEST_EMAIL}&password={TEST_PASSWORD}&name={TEST_NAME}'
    )

    assert response.status == HTTPStatus.OK
    # assert response.body == {'msg': 'email already exists'}
    assert response.body.get('msg') == 'email already exists'

async def test_login(make_post_request):
    response = await make_post_request(
        f'/auth/v1/login?email={TEST_EMAIL}&password={TEST_PASSWORD}'
    )
    assert response.status == HTTPStatus.OK
    assert len(response.body["access_token"].split(".")) == 3
    assert len(response.body["refresh_token"].split(".")) == 3


async def test_login_history(make_get_request, make_post_request):
    response = await make_post_request(
        f'/auth/v1/login?email={TEST_EMAIL}&password={TEST_PASSWORD}'
    )
    _TEST_ACCESS_TOKEN = response.body["access_token"]
    response = await make_get_request(
        '/auth/v1/profile/login_history',
        headers={"Authorization": f"Bearer {_TEST_ACCESS_TOKEN}"}
    )
    assert response.status == HTTPStatus.OK
    assert len(response.body["history"]) == 2 # 2 теста выше заходят в этот акк (1 логин и 2 этот)
    assert isinstance(
        datetime.datetime.strptime(response.body["history"][0], "%a, %d %b %Y %X %Z"),
        datetime.datetime)


async def test_refresh_tokens(make_post_request):
    response = await make_post_request(
        f'/auth/v1/login?email={TEST_EMAIL}&password={TEST_PASSWORD}'
    )
    _TEST_REFRESH_TOKEN = response.body["refresh_token"]
    response = await make_post_request(
        f'/auth/v1/refresh',
        headers={"Authorization": f"Bearer {_TEST_REFRESH_TOKEN}"}
    )
    assert response.status == HTTPStatus.OK
    assert len(response.body["access_token"].split(".")) == 3
    assert len(response.body["refresh_token"].split(".")) == 3


async def test_edit_userdata_error(make_put_request, make_post_request):
    response = await make_post_request(
        f'/auth/v1/login?email={TEST_EMAIL}&password={TEST_PASSWORD}'
    )
    _TEST_ACCESS_TOKEN = response.body["access_token"]
    response = await make_put_request(
        f'/auth/v1/profile?password={TEST_PASSWORD}',
        headers={"Authorization": f"Bearer {_TEST_ACCESS_TOKEN}"}
    )
    assert response.status == HTTPStatus.OK
    assert response.body["msg"] == "password must be different from the current"


async def test_edit_userdata(make_put_request, make_post_request):
    response = await make_post_request(
        f'/auth/v1/login?email={TEST_EMAIL}&password={TEST_PASSWORD}'
    )
    _TEST_ACCESS_TOKEN = response.body["access_token"]
    response = await make_put_request(
        f'/auth/v1/profile?email=new{random.randint(0, 100)}@email.ru',
        headers={"Authorization": f"Bearer {_TEST_ACCESS_TOKEN}"}
    )
    assert response.status == HTTPStatus.OK
    assert response.body["msg"] == "user data edit success"
