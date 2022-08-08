[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
# Проектная работа 7 спринта

https://github.com/azazana/Auth_sprint_2

**Груздев Александр aka @oocemb и Анна Борзенкова aka @azazana**

***
Для запуска проекта локально нужно прописать переменные окружения для Фласка.

```
export FLASK_APP=api
export FLASK_ENV=development
export OAUTHLIB_INSECURE_TRANSPORT=1
```

Запустить необходимые контейнеры баз данных

```
docker run -d \
  --name postgres_auth \
  -p 5432:5432 \
  -e POSTGRES_PASSWORD=admin \
  -e POSTGRES_USER=admin \
  -e POSTGRES_DB=auth  \
  postgres:13.0-alpine
```

`docker run -p 6379:6379 --name auth-redis -d redis:7.0.2`

Создать базу данных внутри контейнера и создать супер юзера и таблицы патриции

```
alembic upgrade head
python manage.py create_superuser
python manage.py create_partition_year 2022
```

Запустить проект

`python manage.py run -h 0.0.0.0 -p 5000`

Документация доступна по ссылке

http://0.0.0.0:5000/apidocs/

***
**Второй вариант запуска через докер компоуз**

```
docker-compose --env-file .env.example build
docker-compose --env-file .env.example up
```

Создать базу данных внутри контейнера и создать супер юзера

```
docker exec auth_auth alembic upgrade head
docker exec auth_auth python manage.py create_superuser
docker exec auth_auth python manage.py create_partition_year 2022
```

Документация доступна по ссылке

http://0.0.0.0:5005/apidocs/

***

Реализация взаимоотношений между **fastapi** и **auth** сделана 2 способами:
1) либо декоратор на ручку **fastapi** проверяющая роль пользователя 
(пока реализовано в ручке всех жанров, как дополнительный параметр, 

2) либо функция чек юзер роль которая проверяет принадлежит ли пользователь к конкретной роли.
   (реализовано в поиске фильмов, в примере добавлено поле 'premium' в базу фильмов и пользователю без подписки показываются только обычные фильмы, 
пользователю с подпиской все)

При отсутствии взаимосвязи с **auth** пользователю возвращается
стандартная роль гостя, возможна вторая реализация с добавлением
списка ролей в jwt-token и при нарушении связи доверять информации 
в токене.

***

Для запуска тестов существует 2 варианта, запустить локально тестовые контейнеры

```
docker-compose --env-file .env.example -f docker-compose-tests.yml build
docker-compose --env-file .env.example -f docker-compose-tests.yml up
```

Можно так же запустить локально для отладки (приложения или самих тестов)
с запуском тестовой среды на 0.0.0.0:5000 (локально должны быть установлены пакеты из requirements из корня и из тестов)

`pytest ./auth/tests`

***

