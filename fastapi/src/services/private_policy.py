import os
from functools import wraps
from http import HTTPStatus
from fastapi import HTTPException
import aiohttp

URL_CHECK_ROLE = os.getenv("URL_CHECK_ROLE", "http://auth:5000/auth/v1/check_roles")


async def get_user_roles(token):
    session = aiohttp.ClientSession()
    async with session.get(
            URL_CHECK_ROLE,
            headers={'Authorization': f'Bearer {token}'}
    ) as response:
        roles = await response.json()
        await session.close()
        return roles


def check_role_user(role: str):
    def checking(fn):
        @wraps(fn)
        async def wrapper(*args, **kwargs):
            roles = await get_user_roles(token=kwargs.get('token', ''))
            if role in roles:
                return await fn(*args, **kwargs)
            else:
                raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="No money, no honey")
        return wrapper
    return checking
