from .person_test_data import test_person_data_dict_for_index
from .genre_test_data import test_genres_data_dict
from ..utils.models_pydantic import FilmShort


test_film_data_dict_for_index = [
    {
        "id": "3d8d9bf5-1111-4353-88ba-4ccc5d2c07ff",
        "title": "First film",
        "imdb_rating": 7.7,
        "description": "todo: add faker data",
        "genres": test_genres_data_dict[0:2],
        "actors": [
            test_person_data_dict_for_index[0],
        ],
        "writers": [],
        "directors": [],
    },
    {
        "id": "120a21cf-2222-479e-904a-13dd7198c1dd",
        "title": "Film number two",
        "imdb_rating": 2.2,
        "description": "todo: add faker data",
        "genres": test_genres_data_dict[1:3],
        "actors": [
            test_person_data_dict_for_index[0],
        ],
        "writers": [
            test_person_data_dict_for_index[1],
        ],
        "directors": [],
    },
    {
        "id": "b92ef010-3333-4fd0-99d6-41b6456272cd",
        "title": "Film number three",
        "imdb_rating": 9.5,
        "description": "todo: add faker data",
        "genres": [
            test_genres_data_dict[-1],
        ],
        "actors": [
            test_person_data_dict_for_index[2],
        ],
        "writers": [
            test_person_data_dict_for_index[2],
        ],
        "directors": [
            test_person_data_dict_for_index[2],
        ],
    },
]

test_shortfilm_data_dict = [FilmShort(**item) for item in test_film_data_dict_for_index]
