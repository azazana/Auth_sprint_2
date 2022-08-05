from http import HTTPStatus
import pytest

pytestmark = pytest.mark.asyncio

TEST_ROLE_ADMIN = 'admin'
TEST_ADMIN_NAME = 'admin'
TEST_ADMIN_EMAIL = 'admin@admin.ru'
TEST_ROLE_USER = 'user'
TEST_ADMIN_PASSWORD = 'admin'


async def get_access_token(make_post_request):
    response = await make_post_request(
        f'/auth/v1/login?email={TEST_ADMIN_EMAIL}&password={TEST_ADMIN_PASSWORD}'
    )
    return response.body["access_token"]


async def test_create_role(make_put_request, make_post_request):
    response = await make_post_request(
        f'/auth/v1/signup?email={TEST_ADMIN_EMAIL}&password={TEST_ADMIN_PASSWORD}&name={TEST_ADMIN_NAME}'
    )

    assert response.status == HTTPStatus.OK

    _TEST_ACCESS_TOKEN = await get_access_token(make_post_request)
    response = await make_post_request(
        f'/auth/v1/roles?name={TEST_ROLE_USER}',
        headers={"Authorization": f"Bearer {_TEST_ACCESS_TOKEN}"}
    )
    assert response.status == HTTPStatus.OK
    assert (response.body["msg"] == f"The role {TEST_ROLE_USER} has created" or
            response.body["msg"] == f"The role has already existed")


async def test_get_role(make_post_request, make_get_request):
    _TEST_ACCESS_TOKEN = await get_access_token(make_post_request)
    response = await make_get_request(
        f'/auth/v1/roles_name?name={TEST_ROLE_USER}',
        headers={"Authorization": f"Bearer {_TEST_ACCESS_TOKEN}"}
    )
    assert response.status == HTTPStatus.OK
    assert response.body["msg"] == "Role " + TEST_ROLE_USER


async def test_get_roles(make_post_request, make_get_request):
    _TEST_ACCESS_TOKEN = await get_access_token(make_post_request)
    response = await make_get_request(
        f'/auth/v1/roles',
        headers={"Authorization": f"Bearer {_TEST_ACCESS_TOKEN}"}
    )

    assert response.status == HTTPStatus.OK
    PASS = False
    for el in response.body:
        for _, value in el.items():
            if value == TEST_ROLE_USER:
                PASS = True
    assert PASS


async def test_get_user_role(make_post_request, make_get_request):
    _TEST_ACCESS_TOKEN = await get_access_token(make_post_request)
    response = await make_get_request(
        f'/auth/v1/user_roles?name_user={TEST_ADMIN_NAME}',
        headers={"Authorization": f"Bearer {_TEST_ACCESS_TOKEN}"}
    )

    assert response.status == HTTPStatus.OK
    PASS = False
    for el in response.body["eqrls"]:
        for _, value in el.items():
            if value == TEST_ROLE_ADMIN:
                PASS = True
    assert PASS


async def test_put_user_role(make_post_request, make_put_request):
    _TEST_ACCESS_TOKEN = await get_access_token(make_post_request)
    response = await make_put_request(
        f'/auth/v1/user_roles?name_user={TEST_ADMIN_NAME}&name_role={TEST_ROLE_USER}',
        headers={"Authorization": f"Bearer {_TEST_ACCESS_TOKEN}"}
    )

    assert response.status == HTTPStatus.OK
    assert response.body["msg"] == "The role has edited to user"


async def test_delete_user_role(make_post_request, make_put_request):
    _TEST_ACCESS_TOKEN = await get_access_token(make_post_request)
    response = await make_put_request(
        f'/auth/v1/user_roles_delete?name_user={TEST_ADMIN_NAME}&name_role={TEST_ROLE_USER}',
        headers={"Authorization": f"Bearer {_TEST_ACCESS_TOKEN}"}
    )

    assert response.status == HTTPStatus.OK
    assert response.body["msg"] == "The role has deleted to user"


