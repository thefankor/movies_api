import uuid

from pydantic import BaseModel


class PersonMini(BaseModel):
    __title__ = "person"

    id: uuid.UUID
    name: str


class Person(BaseModel):
    __title__ = "person"

    id: uuid.UUID
    full_name: str
    film_ids: list[uuid.UUID]