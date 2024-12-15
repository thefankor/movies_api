import uuid

from pydantic import BaseModel


class Genre(BaseModel):
    id: uuid.UUID
    name: str
