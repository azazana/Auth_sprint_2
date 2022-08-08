import orjson
from typing import Optional
from pydantic import BaseModel, Field


def orjson_dumps(v, *, default):
    # orjson.dumps возвращает bytes, а pydantic требует unicode, поэтому декодируем
    return orjson.dumps(v, default=default).decode()


class BaseOrjsonModel(BaseModel):
    id: str

    class Config:
        # Заменяем стандартную работу с json на более быструю
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class Pagination(BaseModel):
    page_number: Optional[int] = Field(alias="page[number]", default=1)
    page_size: Optional[int] = Field(alias="page[size]", default=16)

    class Config:
        allow_population_by_field_name = True
