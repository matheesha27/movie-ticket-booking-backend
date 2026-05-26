from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.database.dependencies import get_db

from app.modules.bookings.model import Booking
from app.modules.bookings.model import BookingItem

from app.modules.seats.model import MovieSeat
from app.modules.auth.dependencies import get_current_user

from app.modules.bookings.schema import BookingCreate

from datetime import datetime

import uuid

router = APIRouter()


@router.post("/")
def create_booking(request: BookingCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):

    seats = db.query(MovieSeat).filter(
        MovieSeat.id.in_(request.movie_seat_ids)
    ).with_for_update().all()

    # Validate seats
    if len(seats) != len(request.movie_seat_ids):
        raise HTTPException(
            404,
            "Some seats not found"
        )

    for seat in seats:
        if seat.status != "HELD":
            raise HTTPException(
                400,
                f"Seat {seat.id} not held"
            )
        if seat.held_by != current_user.id:
            raise HTTPException(
                403,
                "Seat held by another user"
            )

    booking = Booking(
        user_id=current_user.id,
        movie_id=seats[0].movie_id,
        booking_reference=str(uuid.uuid4())[:8],
        status="PENDING"
    )
    db.add(booking)
    db.flush()

    booking_items = []
    for seat in seats:
        item = BookingItem(
            booking_id=booking.id,
            movie_seat_id=seat.id
        )
        booking_items.append(item)

    seat.status = "BOOKED"
    seat.booked_by = current_user.id
    seat.booked_at = datetime.utcnow()

    db.add_all(booking_items)
    db.commit()  # all happens in ONE transaction. So, we read before commit and commit.
    db.refresh(booking)

    return booking
