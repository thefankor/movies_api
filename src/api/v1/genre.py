import uuid
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from services.genre import GenreService, get_genre_service

router = APIRouter()


class Genre(BaseModel):
    id: uuid.UUID
    name: str


class ErrorResponse(BaseModel):
    detail: str = 'genre not found'


resp = {
        404: {
            "model": ErrorResponse,  # Используем модель для описания ответа
            "description": "Item not found"
        }
    }


@router.get('/')
async def genres_list(genre_service: GenreService = Depends(get_genre_service)) -> list[Genre]:
    films = await genre_service.get_genre_list()
    return films


@router.get('/{genre_id}', responses=resp)
async def genres_list(genre_id: str, genre_service: GenreService = Depends(get_genre_service)) -> Genre:
    genre = await genre_service.get_by_id(genre_id)
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='genre not found')
    return genre
