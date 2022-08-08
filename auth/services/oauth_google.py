import os
from requests_oauthlib import OAuth2Session

google_client_id = os.getenv(
    "GOOGLE_CLIENT_ID",
    "720205541120-shsq0bbpdsm9d3l1vnre7aa1h5go0jrj.apps.googleusercontent.com",
)
google_client_secret = os.getenv(
    "GOOGLE_CLIENT_SECRET", "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"
)
redirect_uri = os.getenv("REDIRECT_URI", "http://127.0.0.1:5000/v1/oauth/callback")
authorization_base_url = "https://accounts.google.com/o/oauth2/v2/auth"
token_url = "https://www.googleapis.com/oauth2/v4/token"
scope = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
]
google = OAuth2Session(google_client_id, scope=scope, redirect_uri=redirect_uri)

authorization_url, state = google.authorization_url(
    authorization_base_url, access_type="offline", prompt="select_account"
)


def get_user_scope(redirect_response: str) -> dict:
    google.fetch_token(
        token_url,
        client_secret=google_client_secret,
        authorization_response=redirect_response,
    )

    r = google.get("https://www.googleapis.com/oauth2/v1/userinfo")
    return r.json()
