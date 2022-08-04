import enum


class ESIndexName(enum.Enum):
    film = "movies"
    genre = "genres"
    person = "persons"


class URLIndexName(enum.Enum):
    film = "films"
    genre = "genres"
    person = "persons"


class NotFoundText(enum.Enum):
    film = "Film not found"
    genre = "Genre not found"
    person = "Person not found"


class PersonRole(enum.Enum):
    actor = "actors"
    writer = "writers"
    director = "directors"
