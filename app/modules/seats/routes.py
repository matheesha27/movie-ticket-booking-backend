from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi.params import Query
import logging

from sqlalchemy.orm import Session

from app.database.dependencies import get_db

from app.modules.seats.model import Section, Seat, MovieSeat, SeatHold

from app.modules.movies.model import Movie
from app.modules.cinemas.model import Cinema

from app.modules.seats.schema import SectionCreate, BulkSeatCreate, MovieSeatCreate, HoldSeatsRequest
from app.modules.seats.schema import SeatCreate

from app.modules.auth.dependencies import get_current_user

from datetime import datetime, timedelta
from app.modules.seats.service import generate_unique_seat_id

router = APIRouter()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# ADMIN only access
@router.post("/sections")
def create_section(request: SectionCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """
    params: cinema_id, name, price
    Creates a section for a cinema hall.
    Eg: Creates a section named "ODC" and priced Rs.700 in cinema_id 1
    return: Section
    """
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
    """
    params: cinema_id, section_id, row_name, seat_number
    Creates a seat under a specific Section.
    Eg: Creates a seat named "G7" under the section_id 1 (ODC) in cinema_id 1
    return: Seat
    """
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


# ADMIN only access - Populate seats for the seat capacity in cinemas
# Bulk update seats
@router.post("/bulk")
def bulk_create_seats(request: BulkSeatCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """
    Create multiple seats under a specific Section.
    Eg: Creates seats from A1-F20 under the section_id 1 (ODC) in cinema_id 1
    return: str
    """
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


@router.post("/allocate-movie-seats")
def allocate_movie_seats(request: MovieSeatCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """
    Allocate all seats for a cinema_id, movie_id, date (range) and show_time.
    date(s) format: YYYYMMDD - "20260531" for 2026-May-31
    show_time format: "7.30pm" for 7.30pm
    This generates a globally unique unique_movie_seat in movie_seats table.
    return: MovieSeat array
    """
    start_date = datetime.strptime(request.start_date, "%Y%m%d")
    end_date = datetime.strptime(request.end_date, "%Y%m%d")
    total_days = (end_date - start_date).days + 1

    parsed_time = datetime.strptime(request.show_time, "%I.%M%p")
    show_time = parsed_time.strftime("%H%M")

    cinema_seats = db.query(Seat).filter(
        Seat.cinema_id == request.cinema_id
    ).all()
    if not cinema_seats:
        raise HTTPException(
            status_code=404,
            detail="No seats found in cinema"
        )

    movie_seats = []
    for i in range(total_days):
        current_date = start_date + timedelta(days=i)
        date_str = current_date.strftime("%Y%m%d")

        for cinema_seat in cinema_seats:
            seat_name = cinema_seat.row_name + cinema_seat.seat_number
            unique_movie_seat_id = generate_unique_seat_id(
                request.cinema_id,
                request.movie_id,
                date_str,
                show_time,
                seat_name)
            movie_seat = MovieSeat(
                movie_id=request.movie_id,
                seat_id=cinema_seat.id,
                unique_movie_seat= unique_movie_seat_id
            )
            movie_seats.append(movie_seat)

    db.add_all(movie_seats)
    db.commit()

    return {
        "message": f"{len(movie_seats)} seats allocated"
    }


# ADMIN only access - All seats in the cinema will be copied to 'movie_seats' table
# Copies Cinema seats --> Movie seats (Movie specific)
@router.post("/initialize-event/{movie_id}")
def initialize_movie_seats(movie_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """
    Allocate cinema seats for a particular movie (dedicate).
    Eg: Allocate seats from A1-F20 under the section_id 1 (VIP) in cinema_id 1 for movie_id 2
    return: str - movie_seats table is updated.
    """
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
            detail="No seats found in cinema"
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
# CHANGE THIS TO RETRIEVE UNIQUE SEATS MAP
@router.get("/movie/{movie_id}")
def get_movie_seats(movie_id: int, db: Session = Depends(get_db)):
    """
    View all seats allocated for the movie (via initialize seats or bulk update).
    Eg: View all seats allocated for the movie_id 2
    return: movie_seat object.
    """
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
            "id": movie_seat.id + 1,
            "unique_movie_seat_id": movie_seat.unique_movie_seat,
            "movie_seat_id": movie_seat.id,
            "seat_id": seat.id,
            "section": section.name,
            "price": section.price,
            "row": seat.row_name,
            "seat_number": seat.seat_number,
            "status": movie_seat.status
        })

    return result


@router.get("/unique-movie-seats")
def get_unique_movie_seats(
    cinema_id: int = Query(...),
    movie_id: int = Query(...),
    date: str = Query(...),
    show_time: str = Query(...),
    db: Session = Depends(get_db)
):
    """
    Returns all seats allocated in the cinema for the movie, date and showtime with the status.
    "date" field is passed in YYYY-MM-DD format, and it is converted to YYYYMMDD format.
    "show_time" is passed in H.MMpm format, and it is converted to HHMM format.
    Eg: View all seats allocated for the cinema_id 1, movie_id 2, date 2026-06-02 and showtime 7.00pm with booking status.
    return: object
    """

    movie = db.query(Movie).filter(
        Movie.cinema_id == cinema_id
    ).first()
    if not movie:
        raise HTTPException(
            status_code=404,
            detail="Movie not found"
        )

    date_obj = datetime.strptime(date, "%Y-%m-%d")
    formatted_date = date_obj.strftime("%Y%m%d")

    parsed_time = datetime.strptime(show_time, "%I.%M%p")
    formatted_time = parsed_time.strftime("%H%M")

    prefix = f"{cinema_id}/{movie_id}/{formatted_date}/{formatted_time}/"
    logger.info(f"prefix = {prefix}")

    movie_seats = (
        db.query(MovieSeat, Seat, Section)
        .join(Seat, MovieSeat.seat_id == Seat.id)
        .join(Section, Seat.section_id == Section.id)
        .filter(MovieSeat.unique_movie_seat.like(f"{prefix}%"))
        .all()
    )

    return [
        {
            "id": movie_seat.id,
            "unique_movie_seat_id": movie_seat.unique_movie_seat,
            "movie_seat_id": movie_seat.id,
            "seat_id": seat.id,
            "section": section.name,
            "price": section.price,
            "row": seat.row_name,
            "seat_number": seat.seat_number,
            "status": movie_seat.status
        }
        for movie_seat, seat, section in movie_seats
    ]


# Fetch all AVAILABLE seats and their section details for a specific movie using table joins
@router.get("/movie/{movie_id}/available")
def get_available_seats(movie_id: int, db: Session = Depends(get_db)):
    """
    View all AVAILABLE status seats allocated of the movie.
    Eg: View all AVAILABLE status seats allocated for the movie_id 2
    return: movie_seat object.
    """
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
    """
    View all BOOKED status seats allocated of the movie.
    Eg: View all BOOKED status seats allocated for the movie_id 2
    return: movie_seat object.
    """
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


@router.post("/hold")
def hold_seat(
        request: HoldSeatsRequest,
        db: Session = Depends(get_db)
):
    """
    Update the status of selected_seats to HELD using the unique_movie_seat field.
    Updates movie_seats table status and, pushes new row to seat_holds table.
    Eg: Update the status of selected_seats list seats to HELD by generating the corresponding unique_movie_seat field.
    return: boolean.
    """
    try:
        with db.begin(): # Atomic transaction

            parsed_date = datetime.strptime(request.date, "%Y-%m-%d")
            formatted_date = parsed_date.strftime("%Y%m%d")

            parsed_time = datetime.strptime(request.show_time, "%I.%M%p")
            formatted_time = parsed_time.strftime("%H%M")

            seat_holds = []

            for seat_label in request.selected_seats:

                unique_seat_id = generate_unique_seat_id(
                    request.cinema_id,
                    request.movie_id,
                    parsed_date,
                    formatted_time,
                    seat_label
                )

                # Protection Level 1 - FOR ... UPDATE
                movie_seat = (
                    db.query(MovieSeat)
                    .filter(MovieSeat.unique_movie_seat == unique_seat_id)
                    .with_for_update()
                    .first()
                )

                # Protection Level 2 - Status check
                if not movie_seat:
                    raise HTTPException(404, f"Seat {seat_label} not found")

                if movie_seat.status != "AVAILABLE":
                    raise HTTPException(400, f"Seat {seat_label} not available")

                # Protection Level 3 - Change status (Concurrency)
                movie_seat.status = "HELD"
                movie_seat.held_until = datetime.utcnow() + timedelta(minutes=5)

                # Push new row to seat_holds table
                seat_hold = SeatHold(
                    unique_movie_seat_id=unique_seat_id,
                    created_at=movie_seat.held_until - timedelta(minutes=5),
                    expires_at=movie_seat.held_until
                )
                seat_holds.append(seat_hold)

            db.add_all(seat_holds)
            db.commit()

        return {"status": "SUCCESS"}

    except Exception as e:
        db.rollback()
        raise


@router.post("/confirm-booking")
def confirm_booking(movie_seat_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """
    View the booking confirmed details of the movie_seat_id.
    return: message, movie_seat_id, status object.
    """
    # Protection Level 1 - FOR UPDATE
    movie_seat = db.query(MovieSeat).filter(
        MovieSeat.id == movie_seat_id
    ).with_for_update().first()

    # Protection Level 2 - Status
    hold = db.query(SeatHold).filter(
        SeatHold.movie_seat_id == movie_seat_id,
        SeatHold.user_id == current_user.id
    ).first()
    if not hold:
        raise HTTPException(400, "Seat not held")

    # Protection Level 3 - Create BOOKED (Confirm Booking)
    movie_seat.status = "BOOKED"
    movie_seat.booked_by = current_user.id
    movie_seat.booked_at = datetime.utcnow()

    # Delete temporary hold
    db.delete(hold)
    db.commit()

    return {
        "message": "Seat booked successfully",
        "movie_seat_id": movie_seat_id,
        "status": movie_seat.status
    }
