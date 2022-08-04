import logging

from elasticsearch import Elasticsearch, exceptions, helpers
from services.retry import retry

logger_root = logging.getLogger()


class MyElasticsearch:
    """Class to work witch Elasticsearch.
    init params:

    host: 'url:port'."""

    def __init__(self, hosts: str):
        self.hosts = hosts
        self._first_connect()
        self.settings = {
            "settings": {
                "refresh_interval": "1s",
                "analysis": {
                    "filter": {
                        "english_stop": {"type": "stop", "stopwords": "_english_"},
                        "english_stemmer": {"type": "stemmer", "language": "english"},
                        "english_possessive_stemmer": {
                            "type": "stemmer",
                            "language": "possessive_english",
                        },
                        "russian_stop": {"type": "stop", "stopwords": "_russian_"},
                        "russian_stemmer": {"type": "stemmer", "language": "russian"},
                    },
                    "analyzer": {
                        "ru_en": {
                            "tokenizer": "standard",
                            "filter": [
                                "lowercase",
                                "english_stop",
                                "english_stemmer",
                                "english_possessive_stemmer",
                                "russian_stop",
                                "russian_stemmer",
                            ],
                        }
                    },
                },
            }
        }

    def _connect(self):
        self.es = Elasticsearch(hosts=self.hosts)
        if not self.es.ping():
            raise exceptions.ConnectionError

    @retry
    def _first_connect(self):
        self._connect()
        logger_root.info("Connect to ES success")

    # @retry
    # def search_data_all(self, index: str):
    #     r = requests.get(f"http://127.0.0.1:9200/{index}/_search")
    #     return pprint(r.json())

    @retry
    def search_data_all_two(self, index: str) -> dict:
        return self.es.search(index=index)

    @retry
    def create_index_movies(self, index: str) -> dict:
        request_body = {
            "settings": self.settings["settings"],
            "mappings": {
                "dynamic": "strict",
                "properties": {
                    "id": {"type": "keyword"},
                    "imdb_rating": {"type": "float"},
                    "genres": {
                        "type": "nested",
                        "dynamic": "strict",
                        "properties": {
                            "id": {"type": "keyword"},
                            "name": {"type": "text", "analyzer": "ru_en"},
                        },
                    },
                    "title": {
                        "type": "text",
                        "analyzer": "ru_en",
                        "fields": {"raw": {"type": "keyword"}},
                    },
                    "description": {"type": "text", "analyzer": "ru_en"},
                    "directors_names": {"type": "text", "analyzer": "ru_en"},
                    "actors_names": {"type": "text", "analyzer": "ru_en"},
                    "writers_names": {"type": "text", "analyzer": "ru_en"},
                    "directors": {
                        "type": "nested",
                        "dynamic": "strict",
                        "properties": {
                            "id": {"type": "keyword"},
                            "full_name": {"type": "text", "analyzer": "ru_en"},
                        },
                    },
                    "actors": {
                        "type": "nested",
                        "dynamic": "strict",
                        "properties": {
                            "id": {"type": "keyword"},
                            "full_name": {"type": "text", "analyzer": "ru_en"},
                        },
                    },
                    "writers": {
                        "type": "nested",
                        "dynamic": "strict",
                        "properties": {
                            "id": {"type": "keyword"},
                            "full_name": {"type": "text", "analyzer": "ru_en"},
                        },
                    },
                },
            },
        }
        try:
            return self.es.indices.create(index=index, body=request_body)
        except exceptions.RequestError:
            logger_root.info("Index already exists")

    @retry
    def create_index_genres(self, index: str) -> dict:
        request_body = {
            "settings": self.settings["settings"],
            "mappings": {
                "dynamic": "strict",
                "properties": {
                    "id": {"type": "keyword"},
                    "name": {"type": "keyword"},
                },
            },
        }
        try:
            return self.es.indices.create(index=index, body=request_body)
        except exceptions.RequestError:
            logger_root.info("Index already exists")

    @retry
    def create_index_persons(self, index: str) -> dict:
        request_body = {
            "settings": self.settings["settings"],
            "mappings": {
                "dynamic": "strict",
                "properties": {
                    "id": {"type": "keyword"},
                    "full_name": {"type": "text"},
                },
            },
        }
        try:
            return self.es.indices.create(index=index, body=request_body)
        except exceptions.RequestError:
            logger_root.info("Index already exists")

    @retry
    def delete_index(self, index: str) -> dict:
        return self.es.indices.delete(index=index, ignore=[400, 404])

    @retry
    def load_data(self, data: list[dict], chunk_size: int) -> None:
        """Save data in elastic, bulk query.

        :param data: data list for query
        :param chunk_size: size batch data"""
        helpers.bulk(
            client=self.es,
            actions=data,
            chunk_size=chunk_size,
            max_chunk_bytes=100,
            max_retries=1000,
            initial_backoff=0.5,
            max_backoff=100,
            yield_ok=False,
        )
