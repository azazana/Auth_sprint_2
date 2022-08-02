import asyncio
from typing import Optional
from dataclasses import dataclass
from multidict import CIMultiDictProxy

import aiohttp
import pytest

from .settings import settings


SERVICE_URL = settings.auth_url


@dataclass
class HTTPResponse:
    body: dict
    headers: CIMultiDictProxy[str]
    status: int


@pytest.fixture(scope='session')
async def session():
    session = aiohttp.ClientSession()
    yield session
    await session.close()



@pytest.fixture
def make_post_request(session):
    async def inner(
            method: str,
            params: Optional[dict] = None,
            headers: Optional[dict] = None
    ) -> HTTPResponse:
        params = params or {}
        headers = headers or {}
        url = 'http://' + SERVICE_URL + method
        async with session.post(url, params=params, headers=headers) as response:
            return HTTPResponse(
                body=await response.json(),
                headers=response.headers,
                status=response.status,
            )
    return inner


@pytest.fixture
def make_get_request(session):
    async def inner(
            method: str,
            params: Optional[dict] = None,
            headers: Optional[dict] = None
    ) -> HTTPResponse:
        params = params or {}
        headers = headers or {}
        url = 'http://' + SERVICE_URL + method
        async with session.get(url, params=params, headers=headers) as response:
            return HTTPResponse(
                body=await response.json(),
                headers=response.headers,
                status=response.status,
            )
    return inner


@pytest.fixture
def make_put_request(session):
    async def inner(
            method: str,
            params: Optional[dict] = None,
            headers: Optional[dict] = None
    ) -> HTTPResponse:
        params = params or {}
        headers = headers or {}
        url = 'http://' + SERVICE_URL + method
        async with session.put(url, params=params, headers=headers) as response:
            return HTTPResponse(
                body=await response.json(),
                headers=response.headers,
                status=response.status,
            )
    return inner

@pytest.fixture
def make_delete_request(session):
    async def inner(
            method: str,
            params: Optional[dict] = None,
            headers: Optional[dict] = None
    ) -> HTTPResponse:
        params = params or {}
        headers = headers or {}
        url = 'http://' + SERVICE_URL + method
        async with session.delete(url, params=params, headers=headers) as response:
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
