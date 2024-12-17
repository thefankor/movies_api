from typing import Optional

import orjson

from pydantic import BaseModel, Field

from models.genre import Genre
from models.person import Person


class Film(BaseModel):
    id: str
    title: str
    description: Optional[str]
    rating: float = Field(default=0.0)
    genres: list[Genre]
    directors: list[Person]
    writers: list[Person]
    actors: list[Person]

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson.dumps
