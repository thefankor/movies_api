import logging
import uuid
from http import HTTPStatus
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from services.film import FilmService, get_film_service


# Объект router, в котором регистрируем обработчики
router = APIRouter()


class Person(BaseModel):
    id: uuid.UUID
    name: str


class Genre(BaseModel):
    id: uuid.UUID
    name: str


class Film(BaseModel):
    id: str
    title: str
    description: Optional[str]
    rating: float = Field(default=0.0)
    genres: list[Genre]
    directors: list[Person]
    writers: list[Person]
    actors: list[Person]


class FilmPreview(BaseModel):
    id: str
    title: str
    rating: float = Field(default=0.0)


@router.get('/')
async def films_list(sort: str = None, page_size: int = 10, page_number: int = 1, genre_id: str = None,
                     film_service: FilmService = Depends(get_film_service)) -> list[Film]:
    films = await film_service.get_film_list(q=None, sort=sort, page_size=page_size, page_number=page_number, genre=genre_id)
    return films


@router.get('/search')
async def film_search(query: str, sort: str = '-rating', page_size: int = 10, page_number: int = 1,
                      film_service: FilmService = Depends(get_film_service)) -> list[FilmPreview]:
    films = await film_service.get_film_list(q=query, sort=sort, page_size=page_size, page_number=page_number, genre=None)
    return [FilmPreview(id=film.id, title=film.title, rating=film.rating) for film in films]


@router.get('/{film_id}', response_model=Film)
async def film_details(film_id: str, film_service: FilmService = Depends(get_film_service)) -> Film:
    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='film not found!')

    return film



