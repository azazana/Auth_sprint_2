FROM python:3.9

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./src /code
COPY ./tests /code/tests

CMD ["gunicorn", "--config", "gunicorn.py", "main:app"]
