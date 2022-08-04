import logging
import os
import time
import uuid
from datetime import datetime

from contextmanager_db import open_postgres, open_sqlite
from psycopg2.extensions import connection as _connection
from psycopg2.extras import execute_batch

logger = logging.getLogger()

PAGE_SIZE = 5000


def maping_type_filmwork(data: list, pg_conn: _connection) -> list:
    """Сопоставляет строковое значение type (таблица film_work) из базы Sqlite,
    с ID в базе Postgres или создаёт новый тип при необходимости,
    (так как в pg данное поле сделано отдельной таблицей)."""

    pg_curs = pg_conn.cursor()
    now = datetime.utcnow()
    name_dict = dict()

    for i, sq_data in enumerate(data):
        if sq_data[6] not in name_dict.keys():
            pg_curs.execute(
                "SELECT id FROM type WHERE name = '{name}';".format(name=sq_data[6])
            )
            type_id = pg_curs.fetchall()
            if type_id == []:
                query = """INSERT INTO type (id, name, created, modified)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING;"""
                new_type_data = [(str(uuid.uuid4()), sq_data[6], now, now)]
                execute_batch(pg_curs, query, new_type_data, page_size=PAGE_SIZE)
                pg_conn.commit()
                pg_curs.execute(
                    "SELECT id FROM type WHERE name = '{name}';".format(name=sq_data[6])
                )
                type_id = pg_curs.fetchall()
            list_sq_data = list(sq_data)
            list_sq_data[6] = type_id[0][0]
            name_dict[sq_data[6]] = type_id[0][0]
            data[i] = tuple(list_sq_data)
        else:
            list_sq_data = list(sq_data)
            list_sq_data[6] = name_dict[sq_data[6]]
            data[i] = tuple(list_sq_data)
    return data


if __name__ == "__main__":
    now = time.perf_counter()
    db_sqlite_path = os.environ.get("PATH_DB_SQLITE")

    dsl = {
        "dbname": os.environ.get("POSTGRES_DB"),
        "user": os.environ.get("POSTGRES_USER"),
        "password": os.environ.get("POSTGRES_PASSWORD"),
        "host": os.environ.get("POSTGRES_HOST"),
        "port": os.environ.get("POSTGRES_PORT"),
        "options": "-c search_path=content",
    }
    query_list = [
        "INSERT INTO film_work (id, title, description, creation_date, file_path, rating, type_id, created, modified) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (id) DO NOTHING;",
        "INSERT INTO person (id, full_name, created, modified) VALUES (%s, %s, %s, %s) ON CONFLICT (id) DO NOTHING;",
        "INSERT INTO genre (id, name, description, created, modified) VALUES (%s, %s, %s, %s, %s) ON CONFLICT (id) DO NOTHING;",
        "INSERT INTO person_film_work (id, film_work_id, person_id, role, created) VALUES (%s, %s, %s, %s, %s) ON CONFLICT (id) DO NOTHING;",
        "INSERT INTO genre_film_work (id, film_work_id, genre_id, created) VALUES (%s, %s, %s, %s) ON CONFLICT (id) DO NOTHING;",
    ]
    table_list = [
        "film_work",
        "person",
        "genre",
        "person_film_work",
        "genre_film_work",
    ]

    with open_sqlite(db_sqlite_path) as sqlite_conn, open_postgres(dsl) as pg_conn:

        sqlite_curs = sqlite_conn.cursor()
        pg_curs = pg_conn.cursor()
        sqlite_curs.arraysize = PAGE_SIZE

        for table, query in zip(table_list, query_list):
            try:
                n = 0
                sqlite_curs.execute("select * from {table};".format(table=table))
                sqlite_data = sqlite_curs.fetchmany()
                while sqlite_data:
                    if table == "film_work":
                        sqlite_data = maping_type_filmwork(sqlite_data, pg_conn)

                    execute_batch(pg_curs, query, sqlite_data, page_size=PAGE_SIZE)
                    pg_conn.commit()
                    logger.info("Success load data from table: %s, batch %s", table, n)
                    n += 1
                    sqlite_data = sqlite_curs.fetchmany()

            except Exception:
                print(table)
                logger.warning("Error load data from table: %s", table)

    logger.info("Timeleft - %s", round(time.perf_counter() - now, 2))
