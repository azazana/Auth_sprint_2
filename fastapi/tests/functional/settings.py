from pydantic import BaseSettings, Field


class TestSettings(BaseSettings):
    es_host: str = Field('0.0.0.0', env='ELASTIC_HOST')
    es_port: str = Field('9200', env='ELASTIC_PORT')

    redis_host: str = Field('0.0.0.0', env='REDIS_HOST')
    redis_port: str = Field('6379', env='REDIS_PORT')

    fastapi_url: str = Field('0.0.0.0:8001', env='FASTAPI_TEST_URL')


settings = TestSettings()
