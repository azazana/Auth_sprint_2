#!/bin/sh

if [ "$POSTGRES_DB" = "movies_database" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

python load_data.py
python ./src/ETL.py

exec "$@"
