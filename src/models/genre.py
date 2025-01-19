import uuid

from pydantic import BaseModel


class Genre(BaseModel):
    __title__ = "genres"

    id: uuid.UUID
    name: str
