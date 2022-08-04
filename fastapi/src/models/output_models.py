from pydantic import BaseModel
from typing import Optional


class Genre(BaseModel):
    id: str
    name: str


class Person(BaseModel):
    id: str
    full_name: str
    role: Optional[str]
    film_ids: Optional[list[str]]


class FilmShort(BaseModel):
    id: str
    title: str
    imdb_rating: Optional[float]


class Film(FilmShort):
    description: Optional[str]
    genres: Optional[list[Genre]]
    actors: Optional[list[Person]]
    writers: Optional[list[Person]]
    directors: Optional[list[Person]]
