import os
import logging
from logging import config as logging_config
from pydantic import BaseSettings

from core.logger import LOGGING

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)
logger = logging.getLogger()


class Settings(BaseSettings):
    # Название проекта. Используется в Swagger-документации
    PROJECT_NAME: str = "movies"

    REDIS_HOST: str = "127.0.0.1"
    REDIS_PORT: int = 6379

    ELASTIC_HOST: str = "127.0.0.1"
    ELASTIC_PORT: int = 9200

    CACHE_EXPIRE: int = 60 * 5  # 5 минут

    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


settings = Settings()
logger.info(settings.dict())

