import sys
import logging

from elasticsearch import AsyncElasticsearch, exceptions, helpers

if sys.path[0].startswith("/home/"):
    sys.path.append("....")
    from src.models.enums import ESIndexName
else:
    from models.enums import ESIndexName

logger_root = logging.getLogger()


class MyElasticsearch:
    """Class to work witch Elasticsearch.
    init params:

    host: 'url:port'."""

    def __init__(self, hosts: str):
        self.es = AsyncElasticsearch(hosts=hosts)
        logger_root.info("Connect to ES success")
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

    async def close(self):
        await self.es.close()

    def search_data_all_two(self, index: str):
        return self.es.search(index=index)

    async def create_index_movies(self):
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
            await self.es.indices.create(
                index=ESIndexName.film.value, body=request_body
            )
        except exceptions.RequestError:
            logger_root.info("Index already exists")

    async def create_index_genres(self):
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
            await self.es.indices.create(
                index=ESIndexName.genre.value, body=request_body
            )
        except exceptions.RequestError:
            logger_root.info("Index already exists")

    async def create_index_persons(self):
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
            await self.es.indices.create(
                index=ESIndexName.person.value, body=request_body
            )
        except exceptions.RequestError:
            logger_root.info("Index already exists")

    async def delete_index(self, index: str):
        await self.es.indices.delete(index=index, ignore=[400, 404])

    async def load_data(self, data: list[dict]):
        """Save data in elastic, bulk query.

        :param data: data list for query"""
        await helpers.async_bulk(client=self.es, actions=data, refresh=True)
