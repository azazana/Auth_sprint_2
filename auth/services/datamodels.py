from typing import TypedDict


class JWTTokens(TypedDict):
    access_token: str
    refresh_token: str


class JWTIdentity(TypedDict):
    user_id: str


class Msg(TypedDict):
    msg: str


class LoginHistory(TypedDict):
    history: list[str]
