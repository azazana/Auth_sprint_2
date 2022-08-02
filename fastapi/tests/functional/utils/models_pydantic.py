from typing import Optional

from pydantic import Field, BaseModel


class Base(BaseModel):
    id: str


class ElasticLoad(BaseModel):
    id_for_es: str = Field(None, alias='_id')
    index_for_es: str = Field(None, alias='_index')


class Genre(Base):
    name: str


class Person(Base):
    full_name: str


class FilmShort(Base):
    title: str
    imdb_rating: Optional[float]


class Film(FilmShort):
    description: Optional[str]
    genres: Optional[list[Genre]]
    actors: Optional[list[Person]]
    writers: Optional[list[Person]]
    directors: Optional[list[Person]]


class FilmForValidation(ElasticLoad, Film):
    directors_names: Optional[str]
    actors_names: Optional[str]
    writers_names: Optional[str]


class GenreForValidation(ElasticLoad, Genre):
    pass


class PersonForValidation(ElasticLoad, Person):
    pass
