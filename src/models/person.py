import uuid

from pydantic import BaseModel


class PersonMini(BaseModel):
    id: uuid.UUID
    name: str


class Person(BaseModel):
    id: uuid.UUID
    full_name: str
    film_ids: list[uuid.UUID]