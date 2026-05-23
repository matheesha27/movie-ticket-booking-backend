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

from app.modules.seats.schema import SectionCreate
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
