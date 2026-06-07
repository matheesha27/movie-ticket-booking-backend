from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.dependencies import get_db

from app.modules.movies.model import Movie
from app.modules.movies.schema import MovieCreate, ShowTimeRequest, MovieCinemasRequest

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
        duration=request.duration,
        language=request.language,
        banner_image=request.banner_image,
        trailer=request.trailer,
        show_time=request.show_time
    )
    db.add(movie)
    db.commit()
    db.refresh(movie)

    return movie

@router.get("/")
def get_movies(db: Session = Depends(get_db)):

    movies = db.query(Movie).all()

    print(movies)

    return movies

@router.get("/{movie_id}")
def get_movie(movie_id: int, db: Session = Depends(get_db)):

    movie = db.query(Movie).filter(
        Movie.id == movie_id
    ).first()

    if not movie:
        raise HTTPException(
            status_code=404,
            detail="Movie not found"
        )

    return movie

@router.post("/cinemas")
def get_movie_cinemas(request: MovieCinemasRequest, db: Session = Depends(get_db)):
    # SELECT name, city FROM public.cinemas
    # WHERE id IN(
    #     SELECT DISTINCT cinema_id FROM public.movies
    #     WHERE title = 'OIC Gadafi'
    # );
    cinema_ids = db.query(
        Movie.cinema_id
    ).filter(
        Movie.title == request.movie_title
    ).distinct()

    cinemas = db.query(Cinema).filter(
        Cinema.id.in_(cinema_ids)
    ).all()

    return cinemas

@router.post("/showtime")
def get_movie_showtime(request: ShowTimeRequest, db: Session = Depends(get_db)):
    # SELECT show_time FROM public.movies
    # WHERE cinema_id = 2 AND title = 'OIC Gadafi';
    movie = (
        db.query(Movie)
        .filter(
            Movie.cinema_id == request.cinema_id,
            Movie.title == request.movie_title
        )
        .first()
    )

    return {
        "show_time": movie.show_time if movie else None
    }

@router.get("/banners/urls")
def get_movie_banners(db: Session = Depends(get_db)):

    subquery = (
        db.query(
            func.min(Movie.id).label("movie_id")
        )
        .group_by(Movie.title)
        .subquery()
    )

    movie_banners = (
        db.query(Movie)
        .join(subquery, Movie.id == subquery.c.movie_id)
        .all()
    )

    return [
        {
            "id": movie.id,
            "title": movie.title,
            "banner_image": movie.banner_image
        }
        for movie in movie_banners
    ]

@router.get("/movie")
def get_exact_movie(
    cinema_id: int,
    show_time: str,
    db: Session = Depends(get_db)
):
    movie = (
        db.query(Movie)
        .filter(
            Movie.cinema_id == cinema_id,
            Movie.show_time == show_time
        )
        .first()
    )

    if not movie:
        raise HTTPException(
            status_code=404,
            detail="Movie not found"
        )

    return movie

@router.get("/movie-by-cinema")
def get_movie_by_cinema(
    cinema_id: int,
    movie_title: str,
    show_time: str,
    db: Session = Depends(get_db)
):
    movie = (
        db.query(Movie)
        .filter(
            Movie.cinema_id == cinema_id,
            Movie.title == movie_title,
            Movie.show_time == show_time
        )
        .first()
    )

    return movie
