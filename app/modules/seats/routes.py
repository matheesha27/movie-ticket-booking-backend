from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.database.dependencies import get_db

from app.modules.seats.model import Section
from app.modules.seats.model import Seat
from app.modules.seats.model import MovieSeat

from app.modules.movies.model import Movie
from app.modules.cinemas.model import Cinema

from app.modules.seats.schema import SectionCreate, BulkSeatCreate
from app.modules.seats.schema import SeatCreate

from app.modules.auth.dependencies import get_current_user

router = APIRouter()

@router.post("/sections")
def create_section(request: SectionCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):

    cinema = db.query(Cinema).filter(
        Cinema.id == request.cinema_id
    ).first()

    if not cinema:
        raise HTTPException(
            status_code=404,
            detail="Cinema not found"
        )

    section = Section(
        cinema_id=request.cinema_id,
        name=request.name,
        price=request.price
    )
    db.add(section)
    db.commit()
    db.refresh(section)

    return section


@router.post("/")
def create_seat(request: SeatCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):

    seat = Seat(
        cinema_id=request.cinema_id,
        section_id=request.section_id,
        row_name=request.row_name,
        seat_number=request.seat_number
    )

    db.add(seat)
    db.commit()
    db.refresh(seat)

    return seat


# Populate seats for the seat capacity in cinemas
# Bulk update seats
@router.post("/bulk")
def bulk_create_seats(request: BulkSeatCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):

    seats = []
    for row in range(ord(request.start_row), ord(request.end_row) + 1):
        row_letter = chr(row)
        for seat_no in range(1, request.seats_per_row + 1):
            seat = Seat(
                cinema_id=request.cinema_id,
                section_id=request.section_id,
                row_name=row_letter,
                seat_number=str(seat_no)
            )
            seats.append(seat)

    db.add_all(seats)
    db.commit()

    return {
        "message": f"{len(seats)} seats created"
    }


# All seats in the cinema will be copied to 'movie_seats' table
# Copies Cinema seats --> Movie seats
@router.post("/initialize-event/{movie_id}")
def initialize_movie_seats(movie_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):

    # Check whether the movie exists & get into 'movie' variable if so.
    movie = db.query(Movie).filter(
        Movie.id == movie_id
    ).first()
    if not movie:
        raise HTTPException(
            status_code=404,
            detail="Movie not found"
        )

    cinema_seats = db.query(Seat).filter(
        Seat.cinema_id == movie.cinema_id
    ).all()
    if not cinema_seats:
        raise HTTPException(
            status_code=404,
            detail="No seats found for cinema"
        )

    movie_seats = []

    for seat in cinema_seats:
        existing = db.query(MovieSeat).filter(
            MovieSeat.movie_id == movie.id,
            MovieSeat.seat_id == seat.id
        ).first()
        if existing:
            continue

        movie_seat = MovieSeat(
            movie_id=movie.id,
            seat_id=seat.id,
            status="AVAILABLE"
        )
        movie_seats.append(movie_seat)

    db.add_all(movie_seats)
    db.commit()

    return {
        "message": f"{len(movie_seats)} movie seats initialized"
    }


# Fetch all seats and their section details for a specific movie using table joins
@router.get("/movie/{movie_id}")
def get_movie_seats(movie_id: int, db: Session = Depends(get_db)):

    movie = db.query(Movie).filter(
        Movie.id == movie_id
    ).first()
    if not movie:
        raise HTTPException(
            status_code=404,
            detail="Movie not found"
        )

    movie_seats = db.query(
        MovieSeat,
        Seat,
        Section
    ).join(
        Seat,
        MovieSeat.seat_id == Seat.id
    ).join(
        Section,
        Seat.section_id == Section.id
    ).filter(
        MovieSeat.movie_id == movie_id
    ).all()

    result = []

    for movie_seat, seat, section in movie_seats:
        result.append({
            "movie_seat_id": movie_seat.id,
            "seat_id": seat.id,
            "section": section.name,
            "price": section.price,
            "row": seat.row_name,
            "seat_number": seat.seat_number,
            "status": movie_seat.status
        })

    return result


# Fetch all AVAILABLE seats and their section details for a specific movie using table joins
@router.get("/movie/{movie_id}/available")
def get_available_seats(movie_id: int, db: Session = Depends(get_db)):

    movie = db.query(Movie).filter(
        Movie.id == movie_id
    ).first()
    if not movie:
        raise HTTPException(
            status_code=404,
            detail="Movie not found"
        )

    available_seats = db.query(
        MovieSeat,
        Seat,
        Section
    ).join(
        Seat,
        MovieSeat.seat_id == Seat.id
    ).join(
        Section,
        Seat.section_id == Section.id
    ).filter(
        MovieSeat.movie_id == movie_id,
        MovieSeat.status == "AVAILABLE"
    ).all()

    result = []

    for movie_seat, seat, section in available_seats:
        result.append({
            "movie_seat_id": movie_seat.id,
            "section": section.name,
            "price": section.price,
            "row": seat.row_name,
            "seat_number": seat.seat_number
        })

    return result


# Fetch all BOOKED seats and their section details for a specific movie using table joins
@router.get("/movie/{movie_id}/booked")
def get_booked_seats(movie_id: int, db: Session = Depends(get_db)):

    movie = db.query(Movie).filter(
        Movie.id == movie_id
    ).first()
    if not movie:
        raise HTTPException(
            status_code=404,
            detail="Movie not found"
        )

    booked_seats= db.query(
        MovieSeat,
        Seat
    ).join(
        Seat,
        MovieSeat.seat_id == Seat.id
    ).filter(
        MovieSeat.movie_id == movie_id,
        MovieSeat.status == "BOOKED"
    ).all()

    result = []

    for movie_seat, seat in booked_seats:
        result.append({
            "row": seat.row_name,
            "seat_number": seat.seat_number
        })

    return result
