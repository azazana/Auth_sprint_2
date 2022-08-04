import logging
import time
from functools import wraps

import psycopg2
from elasticsearch import exceptions

logger_root = logging.getLogger()


def retry(
    fn,
    logger: logging.Logger = logger_root,
    start_sleep_time: float = 0.5,
    factor: int = 2,
    border_sleep_time: int = 60,
    max_tries: int = 1000,
):
    """
    Функция для повторного выполнения функции через некоторое время,
    если возникла ошибка. Использует наивный экспоненциальный рост
    времени повтора (factor) до граничного времени ожидания (border_sleep_time)

    Формула:
        t = start_sleep_time * 2^(n) if t < border_sleep_time
        t = border_sleep_time if t >= border_sleep_time
    :fn: оборачиваемая функция
    :param start_sleep_time: начальное время повтора
    :param factor: во сколько раз нужно увеличить время ожидания
    :param border_sleep_time: граничное время ожидания
    :param max_tries: максимальное количество попыток
    :param logger: текущий логер для обраборки
    :return: результат выполнения функции
    """

    @wraps(fn)
    def wrapper(*args, **kw):
        cls = args[0]
        t = start_sleep_time
        for x in range(max_tries):
            t = (
                start_sleep_time * factor**x
                if t < border_sleep_time
                else border_sleep_time
            )
            try:
                return fn(*args, **kw)
            except (psycopg2.InterfaceError, psycopg2.OperationalError) as e:
                logger.info(f"Try reconnect {x}/{max_tries}")
                logger.info("Postgres Connection [InterfaceError or OperationalError]")
                logger.info(f"Idle for {t} seconds")
                time.sleep(t)
                try:
                    cls._connect()
                except (psycopg2.InterfaceError, psycopg2.OperationalError) as e:
                    continue
            except exceptions.ConnectionError:
                logger.info(f"Try reconnect {x}/{max_tries}")
                logger.info("Elasticsearch Connection [InterfaceError or OperationalError]")
                logger.info(f"Idle for {t} seconds")
                time.sleep(t)
                try:
                    cls._connect()
                except (exceptions.ConnectionError, exceptions.ConnectionTimeout) as e:
                    continue

    return wrapper