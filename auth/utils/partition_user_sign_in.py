import datetime


def create_partition_year(connection, year: int) -> None:
    year = int(year)  # for console run
    for y in (year, year+1, year-1):
        connection.execute(
            f"""CREATE TABLE IF NOT EXISTS "users_sign_in_{y}" 
            PARTITION OF "users_sign_in" 
            FOR VALUES FROM ('{y}-01-01') TO ('{y+1}-01-01');"""
        )


def create_partition(target, connection, year: int = 0, **kw) -> None:
    """ creating partition by user_sign_in """
    if not year:
        year = datetime.datetime.now()
        year = year.year
    create_partition_year(connection=connection, year=year)
