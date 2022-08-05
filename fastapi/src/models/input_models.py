from typing import Optional, Union

from .input_base import BaseOrjsonModel
from pydantic import BaseModel


class Genre(BaseOrjsonModel):
    name: str


class Person(BaseOrjsonModel):
    full_name: str


class Film(BaseOrjsonModel):
    title: str
    imdb_rating: Optional[float]
    description: Optional[str]
    genres: Optional[list[Genre]]
    actors: Optional[list[Person]]
    writers: Optional[list[Person]]
    directors: Optional[list[Person]]
    premium: bool


class ListForChash(BaseModel):
    data: Optional[list[Union[Genre, Film, Person]]]
