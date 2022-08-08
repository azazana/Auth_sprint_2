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
