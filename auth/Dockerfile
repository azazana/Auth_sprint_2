FROM python:3.9

WORKDIR /code

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /code/requirements.txt

RUN pip install --upgrade pip
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY . /code

# CMD ["python", "manage.py", "run", "-h", "0.0.0.0"]
#CMD ["gunicorn", "--bind", "0.0.0.0:5000", "manage:app"]
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "manage:app"]
#CMD ["alembic", "upgrade", "head"]
#CMD ["python", "manage.py", "create_superuser"]
