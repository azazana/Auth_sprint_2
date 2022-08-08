from config import BaseConfig
from services.exceptions import OauthProviderError
from services.oauth_base import RequestsOauthlibProvider

google = RequestsOauthlibProvider(
    client_id=BaseConfig.GOOGLE_CLIENT_ID,
    client_secret=BaseConfig.GOOGLE_CLIENT_SECRET,
    authorization_base_url=BaseConfig.GOOGLE_AUTHORIZATION_BASE_URL,
    token_url=BaseConfig.GOOGLE_TOKEN_URL,
    redirect_uri=BaseConfig.GOOGLE_REDIRECT_URI,
    scope=BaseConfig.GOOGLE_SCOPE
)


def match_oauth_provider(provider: str) -> RequestsOauthlibProvider:
    if provider == "google":
        return google
    else:
        raise OauthProviderError("Please enter correct provider Oauth", status_code=404)
