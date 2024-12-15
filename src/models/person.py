import uuid

from pydantic import BaseModel


class Person(BaseModel):
    id: uuid.UUID
    name: str
