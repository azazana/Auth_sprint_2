import logging
from datetime import datetime

import psycopg2
from psycopg2.extensions import cursor as _cursor
from psycopg2.extras import DictCursor
from services.retry import retry

logger_root = logging.getLogger()


class MyPostgres:
    """Postgres database class with retry connection backoff decorator.
    initial params:
    :dsl: initial postgres dict params
    :arraysize: size batch data to select
    """

    def __init__(self, dsl: dict, arraysize: int = 1000):
        self.my_connection = None
        self.my_cursor = None
        self.params = dsl
        self.arraysize = arraysize
        self._first_connect()

    def __del__(self):
        for c in (self.my_cursor, self.my_connection):
            try:
                c.close()
            except:
                pass

    def _connect(self):
        self.my_connection = psycopg2.connect(**self.params, cursor_factory=DictCursor)
        self.my_cursor = self.my_connection.cursor()
        self.my_cursor.arraysize = self.arraysize

    @retry
    def _first_connect(self):
        self._connect()

    @retry
    def select_film_work_data(
        self, film_list: set = None, all_data: bool = False
    ) -> _cursor:
        """Выбирает все небходимые данные из Postgres:
        2 вариата работы:
            1) all_data = True -> выбирает все фильмы
            2) all_data = False -> по списку заданных id фильмов: film_list

        :param film_list: Список для выбора только изменённых данных
        :param all_data: Флаг для выбора всех данных
        :return: Курсор Postgres
        """
        if all_data:
            add_query = ""
        else:
            add_query = "WHERE fw.id IN ('{}')".format("', '".join(film_list))
        self.my_cursor.execute(
            " \
                SELECT \
                    fw.id, \
                    fw.title, \
                    fw.description, \
                    fw.rating, \
                    fw.created, \
                    fw.premium, \
                    fw.modified, \
                    COALESCE ( \
                        json_agg( \
                            DISTINCT jsonb_build_object( \
                                'person_role', pfw.role, \
                                'person_id', p.id, \
                                'person_name', p.full_name \
                            ) \
                        ) FILTER (WHERE p.id is not null), \
                        '[]' \
                    ) as persons, \
                    COALESCE ( \
                        json_agg( \
                            DISTINCT jsonb_build_object( \
                                'genre_id', g.id, \
                                'name', g.name \
                            ) \
                        ) FILTER (WHERE g.id is not null), \
                        '[]' \
                    ) as genres, \
                    array_agg(DISTINCT t.name) as type \
                FROM content.film_work fw \
                LEFT JOIN content.person_film_work pfw ON pfw.film_work_id = fw.id \
                LEFT JOIN content.person p ON p.id = pfw.person_id \
                LEFT JOIN content.genre_film_work gfw ON gfw.film_work_id = fw.id \
                LEFT JOIN content.genre g ON g.id = gfw.genre_id \
                LEFT JOIN content.type t ON t.id = fw.type_id \
                {} \
                GROUP BY fw.id \
            ".format(
                add_query
            )
        )
        return self.my_cursor

    @retry
    def get_modified_film_work_id_list_in_table(
        self, modified: datetime, table: str, m2m_table: str = None
    ) -> list:
        """Возвращает список изменённых фильмов где поменялись участники
        или жанры или сами фильмы

        :param modified: поле str в формате datetime
        :param table: проверяемая на изменения таблица
        :param m2m_table: смежная таблица ManyToMany к film_work
        :return: список id из таблицы film_work."""
        self.my_cursor.execute(
            """
            SELECT id, modified
            FROM content.{table}
            WHERE modified > '{modified}';""".format(
                modified=modified,
                table=table,
            )
        )
        id_modified_list = [str(i["id"]) for i in self.my_cursor.fetchall()]
        if table == "film_work":
            logger_root.info(id_modified_list)  # debug info
            return id_modified_list
        elif not id_modified_list:
            return []
        self.my_cursor.execute(
            """
            SELECT fw.id, fw.modified
            FROM content.film_work fw
            LEFT JOIN content.{m2m} ON content.{m2m}.film_work_id = fw.id
            WHERE content.{m2m}.{table}_id IN ('{id_list}');""".format(
                m2m=m2m_table, table=table, id_list="', '".join(id_modified_list)
            )
        )
        film_work_list_id = [str(f["id"]) for f in self.my_cursor.fetchall()]
        logger_root.info(len(film_work_list_id), "  ", table)
        return film_work_list_id

    @retry
    def get_modified_film_work_id_list(self, modified: datetime) -> set:
        """Собирает все id видео в один список(множество) исключая повторения.

        :param modified: дата последнего изменения с которого ведется проверка
        :return: Список уникальных фильмов в которых произошли изменения."""
        modified_film_work_id_list = (
            self.get_modified_film_work_id_list_in_table(
                modified, "person", "person_film_work"
            )
            + self.get_modified_film_work_id_list_in_table(
                modified, "genre", "genre_film_work"
            )
            + self.get_modified_film_work_id_list_in_table(modified, "film_work")
        )
        return set(modified_film_work_id_list)

    @retry
    def select_genres_data(self, modified: datetime, all_data: bool = False) -> _cursor:
        """Выбирает все небходимые данные из Postgres:
        2 вариата работы:
            1) all_data = True -> выбирает все жанры
            2) all_data = False -> по состоянию даты из redis

        :param modified: Дата последнего изменения (из redis)
        :param all_data: Флаг для выбора всех данных
        :return: Курсор Postgres
        """
        if all_data:
            add_query = ""
        else:
            add_query = "WHERE g.modified > '{}'".format(modified)
        self.my_cursor.execute(
            " \
                SELECT \
                    g.id, \
                    g.name \
                FROM content.genre g \
                {};\
            ".format(
                add_query
            )
        )
        return self.my_cursor

    @retry
    def select_persons_data(
        self, modified: datetime, all_data: bool = False
    ) -> _cursor:
        """Выбирает все небходимые данные из Postgres:
        2 вариата работы:
            1) all_data = True -> выбирает все персоны
            2) all_data = False -> по состоянию даты из redis

        :param modified: Дата последнего изменения (из redis)
        :param all_data: Флаг для выбора всех данных
        :return: Курсор Postgres
        """
        if all_data:
            add_query = ""
        else:
            add_query = "WHERE p.modified > '{}'".format(modified)
        self.my_cursor.execute(
            " \
                SELECT \
                    p.id, \
                    p.full_name \
                FROM content.person p \
                {};\
            ".format(
                add_query
            )
        )
        return self.my_cursor
