from pydantic import BaseSettings, Field


class TestSettings(BaseSettings):
    pg_host: str = Field('0.0.0.0', env='POSTGRES_HOST')
    pg_port: str = Field('5432', env='POSTGRES_PORT')

    redis_host: str = Field('0.0.0.0', env='REDIS_HOST')
    redis_port: str = Field('6379', env='REDIS_PORT')

    auth_url: str = Field('0.0.0.0:5000', env='AUTH_TEST_URL')


settings = TestSettings()
