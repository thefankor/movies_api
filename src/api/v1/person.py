import uuid
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from services.person import PersonService, get_person_service


class ErrorResponse(BaseModel):
    detail: str = 'genre not found'


resp = {
        404: {
            "model": ErrorResponse,  # Используем модель для описания ответа
            "description": "Item not found"
        }
    }

router = APIRouter()


class Person(BaseModel):
    id: uuid.UUID
    full_name: str
    film_ids: list[uuid.UUID]


class FilmPreview(BaseModel):
    id: str
    title: str
    rating: float = Field(default=0.0)


@router.get('/search')
async def persons_list(query: str, page_size: int = 10, page_number: int = 1, person_service: PersonService = Depends(get_person_service)) -> list[Person]:
    persons = await person_service.get_person_list(query, page_size, page_number)
    return persons


@router.get('/{person_id}', responses=resp)
async def get_person(person_id: str, person_service: PersonService = Depends(get_person_service)) -> Person:
    genre = await person_service.get_by_id(person_id)
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='person not found')
    return genre


@router.get('/{person_id}/films', responses=resp)
async def get_person_films(person_id: str, person_service: PersonService = Depends(get_person_service)) -> list[FilmPreview]:
    films = await person_service.get_films_by_person(person_id)
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='person not found')
    return [FilmPreview(id=film.id, title=film.title, rating=film.rating) for film in films]


