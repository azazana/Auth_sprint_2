from abc import ABC, abstractmethod
from requests_oauthlib import OAuth2Session


class OauthProvider(ABC):
    @abstractmethod
    async def get_authorization_url(self) -> str:
        pass

    @abstractmethod
    async def get_user_scope(self, redirect_response: str) -> dict:
        pass


class RequestsOauthlibProvider(OauthProvider):
    def __init__(self, authorization_base_url, token_url, redirect_uri, scope, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.authorization_base_url = authorization_base_url
        self.token_url = token_url
        self.redirect_uri = redirect_uri
        self.scope = scope
        self.provider = OAuth2Session(self.client_id, scope=self.scope, redirect_uri=self.redirect_uri)

    def get_authorization_url(self) -> str:
        authorization_url, state = self.provider.authorization_url(
            self.authorization_base_url, access_type="offline", prompt="select_account"
        )
        return authorization_url

    def get_user_scope(self, redirect_response: str) -> dict:
        self.provider.fetch_token(
            self.token_url,
            client_secret=self.client_secret,
            authorization_response=redirect_response,
        )
        r = self.provider.get("https://www.googleapis.com/oauth2/v1/userinfo")
        return r.json()
