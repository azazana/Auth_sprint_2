from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Request
from models.enums import NotFoundText, ESIndexName
from models.input_base import Pagination
from models.input_models import ListForChash, Genre as Genre_input
from models.output_models import Genre
from services.genres import GenreService, get_genre_service
from services.private_policy import check_role_user
router = APIRouter()
ES_INDEX_NAME = ESIndexName.genre.value
NOT_FOUND_TEXT = NotFoundText.genre.value


@router.get(
    "/",
    response_model=list[Genre],
    summary="Список всех жанров"
)
@check_role_user('admin')
async def genres_list(
        request: Request,
        token: str,
        genre_service: GenreService = Depends(get_genre_service),
        pagination: Pagination = Depends()
) -> list[Genre]:
    response = [
        Genre(**data.dict())
        async for data in genre_service.get_genres_from_elastic(
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
    "/{genre_id}/",
    response_model=Genre,
    summary="Подробная инфомация о жанре"
)
async def genre_details(
        request: Request,
        genre_id: str,
        genre_service: GenreService = Depends(get_genre_service)
) -> Genre:
    """
    - **genre_id**: UUID жанра
    """
    async for genre in genre_service.get_model_by_id_from_elastic(
            model_id=genre_id,
            model=Genre_input,
            index=ES_INDEX_NAME,
            url=str(request.url),
    ):
        if not genre:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=NOT_FOUND_TEXT)
        return Genre(id=genre.id, name=genre.name)
