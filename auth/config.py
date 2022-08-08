import os
from datetime import timedelta

app_dir = os.path.abspath(os.path.dirname(__file__))
DB_DEFAULT_URI = "postgresql://admin:admin@0.0.0.0/auth"


class BaseConfig:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "TEST_SECRET_KEY"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY") or "TEST_SECRET_KEY"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=20)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)
    AUTHORIZE_ALLOW_ANONYMOUS_ACTIONS = True
    AUTHORIZE_IGNORE_PROPERTY = ""

    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME") or "<mymail>@gmail.com"
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD") or "secret_pass"
    MAIL_DEFAULT_SENDER = MAIL_USERNAME

    GOOGLE_CLIENT_ID = os.getenv(
        "GOOGLE_CLIENT_ID",
        "720205541120-shsq0bbpdsm9d3l1vnre7aa1h5go0jrj.apps.googleusercontent.com",
    )
    GOOGLE_CLIENT_SECRET = os.getenv(
        "GOOGLE_CLIENT_SECRET", "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"
    )
    GOOGLE_REDIRECT_URI = os.getenv("REDIRECT_URI", "http://127.0.0.1:5000/auth/v1/oauth/callback/google")
    GOOGLE_AUTHORIZATION_BASE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    GOOGLE_TOKEN_URL = "https://www.googleapis.com/oauth2/v4/token"
    GOOGLE_SCOPE = [
        "openid",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
    ]


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("DEVELOPMENT_DATABASE_URI") or DB_DEFAULT_URI
    )


class TestingConfig(BaseConfig):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("TESTING_DATABASE_URI") or DB_DEFAULT_URI


class ProductionConfig(BaseConfig):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("PRODUCTION_DATABASE_URI") or DB_DEFAULT_URI
    )
