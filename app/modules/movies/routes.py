from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.dependencies import get_db

from app.modules.movies.model import Movie
from app.modules.movies.schema import MovieCreate

from app.modules.cinemas.model import Cinema

from app.modules.auth.dependencies import get_current_user

router = APIRouter()

@router.post("/")
def create_movie(request: MovieCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):

    cinema = db.query(Cinema).filter(
        Cinema.id == request.cinema_id
    ).first()

    if not cinema:
        raise HTTPException(
            status_code=404,
            detail="Cinema not found"
        )

    movie = Movie(
        cinema_id=request.cinema_id,
        title=request.title,
        description=request.description,
        category=request.category,
        banner_image=request.banner_image,
        show_time=request.show_time
    )
    db.add(movie)
    db.commit()
    db.refresh(movie)

    return movie

@router.get("/")
def get_movie(db: Session = Depends(get_db)):

    movies = db.query(Movie).all()

    return movies

@router.get("/{movie_id}")
def get_movie(movie_id: int, db: Session = Depends(get_db)):

    movie = db.query(Movie).filter(
        Movie.id == movie_id
    ).first()

    if not movie:
        raise HTTPException(
            status_code=404,
            detail="Event not found"
        )

    return movie
