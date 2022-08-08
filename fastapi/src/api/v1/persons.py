from http import HTTPStatus
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from models.enums import NotFoundText, ESIndexName, PersonRole
from models.input_base import Pagination
from models.input_models import ListForChash
from models.output_models import Person, FilmShort
from services.films import FilmService, get_film_service
from services.persons import PersonService, get_person_service

router = APIRouter()
ES_INDEX_NAME = ESIndexName.person.value
NOT_FOUND_TEXT = NotFoundText.person.value


@router.get(
    "/{person_id}/films/",
    response_model=list[FilmShort],
    response_model_exclude_none=True,
    summary="Список фильмов в которых учавствовала персона",
    response_description="Фильмы в коротком формате (id, title, imdb_rating)",
)
async def person_films_list(
    request: Request,
    person_id: str,
    pagination: Pagination = Depends(),
    film_service: FilmService = Depends(get_film_service),
) -> list[FilmShort]:
    """
    - **person_id**: UUID Персоны

    **return**: Фильмы в коротком формате (id, title, imdb_rating)
    """
    response = []
    for role in PersonRole:
        response += [
            FilmShort(**film.dict())
            async for film in film_service.get_films(
                person_id=person_id,
                url=str(request.url),
                model=ListForChash,
                index=ES_INDEX_NAME,
                role=role.value,
            )
            if FilmShort(**film.dict()) not in response
        ]
    if not response:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=NOT_FOUND_TEXT)
    p_from = (pagination.page_number - 1) * pagination.page_size
    return response[p_from : p_from + pagination.page_size]


@router.get(
    "/search/",
    response_model=list[Person],
    summary="Полнотекстовый поиск персон",
    response_description="Персоны с списом фильмов в котором она участвовала",
)
async def persons_search(
    request: Request,
    persons_service: PersonService = Depends(get_person_service),
    film_service: FilmService = Depends(get_film_service),
    query: Optional[str] = None,
    pagination: Pagination = Depends(),
) -> list[Person]:
    """
    - **query**: текст для запроса для поиска
    - **page_size**: количество результатов на одной странице
    - **page_number**: номер текущей страницы

    **return**: Персоны с списом фильмов в котором она участвовала
    """
    response = []
    async for person in persons_service.search_persons(
        query=query,
        pagination=pagination,
        url=str(request.url),
        index=ES_INDEX_NAME,
        model=ListForChash,
    ):
        # Можно ли одним запросом вытаскивать фильмы по всем ролям
        film_ids_list = []
        for role in PersonRole:
            film_ids_list += await film_service.get_role_film_ids_list(
                url=str(request.url),
                index=ES_INDEX_NAME,
                model=ListForChash,
                person_id=person.id,
                role=role.value,
            )
        film_ids_list = list(set(film_ids_list))
        response.append(
            Person(id=person.id, full_name=person.full_name, film_ids=film_ids_list)
        )
    if not response:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=NOT_FOUND_TEXT)
    return response


@router.get(
    "/{person_id}/",
    response_model=list[Person],
    summary="Подробная инфомация о персоне",
    response_description="Список фильмов для каждой роли персоны в которых она участвовала",
)
async def person_details(
    person_id: str,
    request: Request,
    persons_service: PersonService = Depends(get_person_service),
    film_service: FilmService = Depends(get_film_service),
) -> list[Person]:
    """
    - **person_id**: UUID Персоны

    **return**: Список фильмов для каждой роли персоны в которых она участвовала
    """
    async for person in persons_service.get_model_by_id_from_elastic(
        model_id=person_id, url=str(request.url), model=Person, index=ES_INDEX_NAME
    ):

        if not person:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=NOT_FOUND_TEXT)
        response = [
            Person(
                id=person.id,
                full_name=person.full_name,
                role=role.name,
                film_ids=await film_service.get_role_film_ids_list(
                    person_id=person.id,
                    role=role.value,
                    url=str(request.url),
                    model=Person,
                    index=ES_INDEX_NAME,
                ),
            )
            for role in PersonRole
        ]
        return response
