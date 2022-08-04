from http import HTTPStatus
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from models.enums import NotFoundText, ESIndexName
from models.input_base import Pagination
from models.input_models import ListForChash, Film as Film_input
from models.output_models import Film, FilmShort
from services.films import FilmService, get_film_service

router = APIRouter()
ES_INDEX_NAME = ESIndexName.film.value
NOT_FOUND_TEXT = NotFoundText.film.value


@router.get(
    "/",
    response_model=list[FilmShort],
    response_model_exclude_none=True,
    summary="Список всех фильмов",
    response_description="Фильмы в коротком формате (id, title, imdb_rating)"
)
async def films_list(
        request: Request,
        film_service: FilmService = Depends(get_film_service),
        sort: Optional[str] = None,
        genre_id: Optional[str] = Query(default=None, alias="filter[genre]"),
        pagination: Pagination = Depends()
) -> list[FilmShort]:
    """
    Список всех фильмов поддерживает фильтрацию по UUID жанра, и сортировку по рейтингу imdb_rating
    - **sort**: сортировка по imdb_rating  (example = "-imdb_rating" or "imdb_rating")
    - **genre_id**: UUID жанра для фильтрации
    - **page_size**: количество результатов на одной странице
    - **page_number**: номер текущей страницы

    **return**: Фильмы в коротком формате (id, title, imdb_rating)
    """
    response = [
        FilmShort(**film.dict())
        async for film in film_service.get_films(
            sort=sort,
            genre_id=genre_id,
            url=str(request.url),
            model=ListForChash,
            index=ES_INDEX_NAME,
            pagination=pagination,
        )
    ]
    if not response:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=NOT_FOUND_TEXT)
    return response


@router.get(
    "/search/",
    response_model=list[FilmShort],
    response_model_exclude_none=True,
    summary="Полнотекстовый поиск фильмов",
    response_description="Фильмы в коротком формате (id, title, imdb_rating)"
)
async def films_search(
        request: Request,
        film_service: FilmService = Depends(get_film_service),
        query: Optional[str] = None,
        pagination: Pagination = Depends()
) -> list[FilmShort]:
    """
    - **query**: текст для запроса для поиска
    - **page_size**: количество результатов на одной странице
    - **page_number**: номер текущей страницы

    **return**: Фильмы в коротком формате (id, title, imdb_rating)
    """
    response = [
        FilmShort(**film.dict())
        async for film in film_service.get_films(
            search=query,
            pagination=pagination,
            url=str(request.url),
            model=ListForChash,
            index=ES_INDEX_NAME,
        )
    ]
    if not response:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=NOT_FOUND_TEXT)
    return response


@router.get(
    "/{film_id}/",
    response_model=Film,
    response_model_exclude_none=True,
    summary="Подробная информация о фильме",
    response_description="Подробная информация о фильме"
)
async def film_details(
        film_id: str, request: Request,
        film_service: FilmService = Depends(get_film_service)
) -> Film:
    """
    - **film_id**: UUID Фильма

    **return**: Подробная информация о фильме
    """
    async for film in film_service.get_model_by_id_from_elastic(
            model_id=film_id,
            model=Film_input,
            index=ES_INDEX_NAME,
            url=str(request.url),
    ):
        if not film:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=NOT_FOUND_TEXT)
        return Film(**film.dict())
