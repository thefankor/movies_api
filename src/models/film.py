from typing import Optional

import orjson

from pydantic import BaseModel, Field

from models.genre import Genre
from models.person import PersonMini


class Film(BaseModel):
    __title__ = "movies"

    id: str
    title: str
    description: Optional[str]
    rating: float = Field(default=0.0)
    genres: list[Genre]
    directors: list[PersonMini]
    writers: list[PersonMini]
    actors: list[PersonMini]

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson.dumps


