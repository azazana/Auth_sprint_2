import datetime
import logging
import os
import time
from logging import config
import random

from MyElasticsearch import MyElasticsearch
from MyPostgres import MyPostgres
from services.logging import LOGGING
from services.state import RedisStorage, State

import redis

config.dictConfig(LOGGING)
logger = logging.getLogger()


class PersonRole:
    """Модель ролей участников фильмов/видео."""
    def __init__(self):
        self.ACTOR = "actor"
        self.DIRECTOR = "director"
        self.WRITER = "writer"


def random_premium():
    if random.randint(1, 100) > 50:
        return 1
    else:
        return 0


def transform_data_pg_in_es(index: str, data: list[dict]) -> list[dict]:
    person = PersonRole()
    actions = [
        {
            "_index": index,
            "_id": item["id"],
            "id": item["id"],
            "title": item["title"],
            "description": item["description"],
            "imdb_rating": item["rating"],
            "premium": random_premium(),
            "genres": [
                {"id": g["genre_id"], "name": g["name"]}
                for g in item["genres"]
            ],
            "directors_names": [
                p["person_name"]
                for p in item["persons"]
                if p["person_role"] == person.DIRECTOR
            ],
            "actors_names": [
                p["person_name"] for p in item["persons"]
                if p["person_role"] == person.ACTOR
            ],
            "writers_names": [
                p["person_name"]
                for p in item["persons"]
                if p["person_role"] == person.WRITER
            ],
            "directors": [
                {"id": p["person_id"], "full_name": p["person_name"]}
                for p in item["persons"]
                if p["person_role"] == person.DIRECTOR
            ],
            "actors": [
                {"id": p["person_id"], "full_name": p["person_name"]}
                for p in item["persons"]
                if p["person_role"] == person.ACTOR
            ],
            "writers": [
                {"id": p["person_id"], "full_name": p["person_name"]}
                for p in item["persons"]
                if p["person_role"] == person.WRITER
            ],
        }
        for item in data
    ]
    return actions


def transform_data_genres(index: str, data: list[dict]) -> list[dict]:
    actions = [
        {
            "_index": index,
            "_id": item["id"],
            "id": item["id"],
            "name": item["name"],
        }
        for item in data
    ]
    return actions


def transform_data_persons(index: str, data: list[dict]) -> list[dict]:
    actions = [
        {
            "_index": index,
            "_id": item["id"],
            "id": item["id"],
            "full_name": item["full_name"],
        }
        for item in data
    ]
    return actions


def main_loop_ETL(elastic: MyElasticsearch, sleep: int, all_data: bool = False) -> None:

    PAGE_SIZE = int(os.environ.get("PAGE_SIZE"))
    dsl = {
        "dbname": os.environ.get("POSTGRES_DB"),
        "user": os.environ.get("POSTGRES_USER"),
        "password": os.environ.get("POSTGRES_PASSWORD"),
        "host": os.environ.get("POSTGRES_HOST"),
        "port": os.environ.get("POSTGRES_PORT"),
        "options": "-c search_path=content",
    }
    redis_client = redis.Redis(
        host=os.environ.get("REDIS_HOST"),
        port=int(os.environ.get("REDIS_PORT")),
        db=int(os.environ.get("REDIS_DB")),
    )
    redis_s = RedisStorage(redis_client)
    state = State(redis_s)
    pg = MyPostgres(dsl=dsl, arraysize=PAGE_SIZE)

    # loading all films data TODO: genres, persons
    if all_data:
        pg_curs = pg.select_film_work_data(all_data=all_data)
        raw_data = pg_curs.fetchmany()
        while raw_data:
            transform_data = transform_data_pg_in_es("movies", raw_data)
            elastic.load_data(transform_data, PAGE_SIZE)
            raw_data = pg_curs.fetchmany()
        else:
            logger.info("All_data complete loaded in ES")
    else:
        # get state
        try:
            modified = state.get_state("begin").decode("utf-8")
        except:
            modified = False
        if not modified:
            modified = datetime.datetime.min
        date_now = datetime.datetime.utcnow()

        # movies index load
        id_list = pg.get_modified_film_work_id_list(modified)
        if id_list:
            pg_curs = pg.select_film_work_data(film_list=id_list)
            raw_data = pg_curs.fetchmany()
            # while raw_data := pg_curs.fetchmany()  # for python 3.10
            while raw_data:
                transform_data = transform_data_pg_in_es("movies", raw_data)
                elastic.load_data(transform_data, PAGE_SIZE)
                raw_data = pg_curs.fetchmany()
            else:
                logger.info("modified {} movies".format(len(id_list)))
        else:
            logger.info("No movies to modified")

        # genres index load
        pg_curs = pg.select_genres_data(modified)
        raw_data = pg_curs.fetchmany()
        if raw_data:
            while raw_data:
                transform_data = transform_data_genres("genres", raw_data)
                elastic.load_data(transform_data, PAGE_SIZE)
                raw_data = pg_curs.fetchmany()
            else:
                logger.info("modified genres")
        else:
            logger.info("No genres to modified")

        # persons index load
        pg_curs = pg.select_persons_data(modified)
        raw_data = pg_curs.fetchmany()
        if raw_data:
            while raw_data:
                transform_data = transform_data_persons("persons", raw_data)
                elastic.load_data(transform_data, PAGE_SIZE)
                raw_data = pg_curs.fetchmany()
            else:
                logger.info("modified persons")
        else:
            logger.info("No genres to modified")

        # set state
        state.set_state("begin", str(date_now))

    time.sleep(sleep)


if __name__ == "__main__":
    logger.info("wait loading ES (20 sec)")
    time.sleep(20)
    # init index
    elastic = MyElasticsearch(
        hosts=os.environ.get("ELASTIC_HOST")+':'+os.environ.get("ELASTIC_PORT"))
    elastic.create_index_movies('movies')
    elastic.create_index_genres('genres')
    elastic.create_index_persons('persons')
    # TODO: не дублирующийся сервис (при случайном двойном запуске)
    while True:
        main_loop_ETL(elastic=elastic, sleep=120)
