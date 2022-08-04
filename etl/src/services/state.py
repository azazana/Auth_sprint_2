import abc
import json
from typing import Any

from redis import Redis


class BaseStorage:
    @abc.abstractmethod
    def save_state(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def retrieve_state(self, *args, **kwargs):
        pass


class RedisStorage(BaseStorage):
    """Class to save and retrieve state in redis.
    init params:
    :redis_adapter: redis client connection"""

    def __init__(self, redis_adapter: Redis):
        self.redis_adapter = redis_adapter

    def retrieve_state(self, key: str) -> Any:
        return self.redis_adapter.get(key)

    def save_state(self, key: str, state: Any) -> bool:
        return self.redis_adapter.set(name=key, value=state)


class JsonFileStorage(BaseStorage):
    """Class to save and retrieve state in json file.
    init params:
    :file_path: path to json file example: '/name_file.json'"""

    def __init__(self, file_path: str):
        self.file_path = file_path

    def retrieve_state(self, key: str) -> Any:
        try:
            with open(f"{self.file_path}") as data_file:
                try:
                    data_loaded = json.load(data_file)
                    if key in data_loaded.keys():
                        return data_loaded[key]
                    else:
                        return None
                except json.decoder.JSONDecodeError:
                    raise FileNotFoundError
        except FileNotFoundError:
            return None

    def save_state(self, key: str, value: Any) -> None:
        with open(f"{self.file_path}", "w", encoding="utf-8") as data_file:
            json.dump({key: value}, data_file, ensure_ascii=False, indent=4)


class State:
    """
    Класс для хранения состояния при работе с данными, чтобы постоянно не перечитывать данные с начала.
    init params:
    :storage: storage to save state (Json, Redis)
    """

    def __init__(self, storage: BaseStorage):
        self.storage = storage

    def set_state(self, key: str, value: Any) -> None:
        """Установить состояние для определённого ключа"""
        self.storage.save_state(key, value)

    def get_state(self, key: str) -> Any:
        """Получить состояние по определённому ключу"""
        return self.storage.retrieve_state(key)
