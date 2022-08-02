import logging
import sqlite3
from contextlib import contextmanager
from logging import config
from typing import Any

import psycopg2
from psycopg2.extras import DictCursor
from src.services.logging import LOGGING

config.dictConfig(LOGGING)
logger_root = logging.getLogger()


@contextmanager
def open_sqlite(file_path: str):
    conn = sqlite3.connect(file_path)
    try:
        logger_root.info("Creating connection to SQLite")
        yield conn
    finally:
        logger_root.info("Closing connection to SQLite")
        conn.commit()
        conn.close()


@contextmanager
def open_postgres(dsl: dict[str:Any]):
    conn = psycopg2.connect(**dsl, cursor_factory=DictCursor)
    try:
        logger_root.info("Creating connection to Postgres")
        yield conn
    finally:
        logger_root.info("Closing connection to Postgres")
        conn.commit()
        conn.close()
