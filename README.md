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

Создать базу данных внутри контейнера и создать супер юзера

```
alembic upgrade head
python manage.py create_superuser
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
docker exec <id_auth_container> python manage.py create_db
docker exec <id_auth_container> python manage.py create_superuser
```

Документация доступна по ссылке

http://0.0.0.0:5005/apidocs/

***

Для запуска тестов существует 2 варианта, запустить локально тестовые контейнеры

```
docker-compose --env-file .env.example -f docker-compose-tests.yml build
docker-compose --env-file .env.example -f docker-compose-tests.yml up
```

Можно так же запустить локально для отладки (приложения или самих тестов)
с запуском тестовой среды на 0.0.0.0:5000 (локально должны быть установлены пакеты из requirements из корня и из тестов)

`pytest ./tests`

***

С этого модуля вы больше не будете получать чётко расписанное ТЗ, а задания для каждого спринта вы найдёте внутри уроков. Перед тем как начать программировать, вам предстоит продумать архитектуру решения, декомпозировать задачи и распределить их между командой.

В первом спринте модуля вы напишете основу вашего сервиса и реализуете все базовые требования к нему. Старайтесь избегать ситуаций, в которых один из ваших коллег сидит без дела. Для этого вам придётся составлять задачи, которые можно выполнить параллельно и выбрать единый стиль написания кода.

К концу спринта у вас должен получиться сервис авторизации с системой ролей, написанный на Flask с использованием gevent. Первый шаг к этому — проработать и описать архитектуру вашего сервиса. Это значит, что перед тем, как приступить к разработке, нужно составить план действий: из чего будет состоять сервис, каким будет его API, какие хранилища он будет использовать и какой будет его схема данных. Описание нужно сдать на проверку. Вам предстоит выбрать, какой метод организации доступов использовать для онлайн-кинотеатра, и систему прав, которая позволит ограничить доступ к ресурсам. 

Для описания API рекомендуем использовать [OpenAPI](https://editor.swagger.io){target="_blank"}, если вы выберете путь REST. Или используйте текстовое описание, если вы планируете использовать gRPC. С этими инструментами вы познакомились в предыдущих модулях. Обязательно продумайте и опишите обработку ошибок. Например, как отреагирует ваш API, если обратиться к нему с истёкшим токеном? Будет ли отличаться ответ API, если передать ему токен с неверной подписью? А если имя пользователя уже занято? Документация вашего API должна включать не только ответы сервера при успешном завершении запроса, но и понятное описание возможных ответов с ошибкой.

После прохождения ревью вы можете приступать к программированию. 

Для успешного завершения первой части модуля в вашем сервисе должны быть реализованы API для аутентификации и система управления ролями. Роли понадобятся, чтобы ограничить доступ к некоторым категориям фильмов. Например, «Фильмы, выпущенные менее 3 лет назад» могут просматривать только пользователи из группы 'subscribers'.  

## API для сайта и личного кабинета

- регистрация пользователя;
- вход пользователя в аккаунт (обмен логина и пароля на пару токенов: JWT-access токен и refresh токен); 
- обновление access-токена;
- выход пользователя из аккаунта;
- изменение логина или пароля (с отправкой email вы познакомитесь в следующих модулях, поэтому пока ваш сервис должен позволять изменять личные данные без дополнительных подтверждений);
- получение пользователем своей истории входов в аккаунт;

## API для управления доступами

- CRUD для управления ролями:
  - создание роли,
  - удаление роли,
  - изменение роли,
  - просмотр всех ролей.
- назначить пользователю роль;
- отобрать у пользователя роль;
- метод для проверки наличия прав у пользователя. 

***

Реализация взаимоотношений между **fastapi** и **auth** сделана 2 способами:
1) либо декоратор на ручку **fastapi** проверяющая роль пользователя 
(пока реализовано в ручке всех жанров, как дополнительный параметр, 
ТОДО: добавить реализацию через параметры заголовка Авторизации),
2) либо функция чек юзер роль которая проверяет принадлежит ли пользователь к конкретной роли.
   (реализовано в поиске фильмов, в примере добавлено поле 'premium' в базу фильмов и пользователю без подписки показываются только обычные фильмы, 
пользователю с подпиской только премиальные, ТОДО: премиум юзер должен мочь смотреть и обычные фильмы:) )

При отсутствии взаимосвязи с **auth** пользователю возвращается
стандартная роль гостя, возможна вторая реализация с добавлением
списка ролей в jwt-token и при нарушении связи доверять информации 
в токене.

***

## Подсказки

1. Продумайте, что делать с анонимными пользователями, которым доступно всё, что не запрещено отдельными правами.
2. Метод проверки авторизации будет всегда нужен пользователям. Ходить каждый раз в БД — не очень хорошая идея. Подумайте, как улучшить производительность системы.
3. Добавьте консольную команду для создания суперпользователя, которому всегда разрешено делать все действия в системе.
4. Чтобы упростить себе жизнь с настройкой суперпользователя, продумайте, как сделать так, чтобы при авторизации ему всегда отдавался успех при всех запросах.
5. Для реализации ограничения по фильмам подумайте о присвоении им какой-либо метки. Это потребует небольшой доработки ETL-процесса.


## Дополнительное задание

Реализуйте кнопку «Выйти из остальных аккаунтов», не прибегая к хранению в БД активных access-токенов.

## Напоминаем о требованиях к качеству

Перед тем как сдать ваш код на проверку, убедитесь, что 

- Код написан по правилам pep8: при запуске [линтера](https://semakin.dev/2020/05/python_linters/){target="_blank"} в консоли не появляется предупреждений и возмущений;
- Все ключевые методы покрыты тестами: каждый ответ каждой ручки API и важная бизнес-логика тщательно проверены;
- У тестов есть понятное описание, что именно проверяется внутри. Используйте [pep257](https://www.python.org/dev/peps/pep-0257/){target="_blank"}; 
- Заполните README.md так, чтобы по нему можно было легко познакомиться с вашим проектом. Добавьте короткое, но ёмкое описание проекта. По пунктам опишите как запустить приложения с нуля, перечислив полезные команды. Упомяните людей, которые занимаются проектом и их роли. Ведите changelog: описывайте, что именно из задания модуля уже реализовано в вашем сервисе и пополняйте список по мере развития.
- Вы воспользовались лучшими практиками описания конфигурации приложений из урока. 
