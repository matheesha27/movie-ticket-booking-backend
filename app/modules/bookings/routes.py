from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.database.dependencies import get_db

from app.modules.bookings.model import Booking, OTPVerification
from app.modules.bookings.model import BookingItem
from app.modules.bookings.service import send_otp_email

from app.modules.seats.model import MovieSeat
from app.modules.auth.dependencies import get_current_user

from app.modules.bookings.schema import BookingCreate

from datetime import datetime, timedelta

import uuid

from app.modules.utils.otp import generate_otp
from app.modules.utils.booking_reference import generate_booking_reference

router = APIRouter()


@router.post("/")
def create_booking(request: BookingCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """
    Create a booking with movie_seat_ids array.
    Eg: View all HELD status seats allocated of the movie_seat_id.
        input: { "movie_seat_ids": [1, 2, 3] }
    return: booking object with a unique booking reference.
    """
    seats = db.query(MovieSeat).filter(
        MovieSeat.id.in_(request.movie_seat_ids)
    ).with_for_update().all()  # Lock seat rows until transaction finishes - SELECT ... FOR UPDATE

    # Validate seats
    if len(seats) != len(request.movie_seat_ids):
        raise HTTPException(
            404,
            "Some seats not found"
        )
    for seat in seats:
        if seat.status != "HELD":  # Prevents direct booking
            raise HTTPException(
                400,
                f"Seat {seat.id} not held"
            )
        if seat.held_by != current_user.id:  # Chck the seat belongs to the current user
            raise HTTPException(
                403,
                "Seat held by another user"
            )

    booking = Booking(
        user_id=current_user.id,
        movie_id=seats[0].movie_id,
        booking_reference=str(uuid.uuid4())[:8],  # Generate a unique booking reference
        status="PENDING"
    )
    db.add(booking)
    db.flush()  # INSERT booking INTO db without committing - this gives booking.id to put in BookingItem

    booking_items = []
    for seat in seats:
        item = BookingItem(
            booking_id=booking.id,
            movie_seat_id=seat.id
        )
        booking_items.append(item)
        # Book the seat
        seat.status = "BOOKED"  # Permanently reserves the seat
        seat.booked_by = current_user.id
        seat.booked_at = datetime.utcnow()

    db.add_all(booking_items)
    db.commit()  # All happens in ONE transaction. ALL SUCCESS OR ALL FAIL So, we read before commit and, then commit.
    db.refresh(booking)

    return booking


@router.post("/send-otp")
async def send_otp(payload: dict, db: Session = Depends(get_db)):

    email = payload.get("email")
    otp = generate_otp()
    expires_at = datetime.utcnow() + timedelta(minutes=5)
    otp_record = OTPVerification(
        email=email,
        otp=otp,
        expires_at=expires_at
    )
    db.add(otp_record)
    db.commit()

    await send_otp_email(email, otp)

    return {
        "message": "OTP sent successfully"
    }


@router.post("/verify-otp")
async def verify_otp(payload: dict, db: Session = Depends(get_db)):

    email = payload.get("email")
    otp = payload.get("otp")

    otp_record = db.query(
        OTPVerification
    ).filter(
        OTPVerification.email == email,
        OTPVerification.otp == otp,
        OTPVerification.verified == False
    ).first()

    # Verify OTP
    if not otp_record:
        return {
            "success": False,
            "message": "Invalid OTP"
        }
    if otp_record.expires_at < datetime.utcnow():
        return {
            "success": False,
            "message": "OTP expired"
        }

    otp_record.verified = True
    db.commit()
    booking_reference = generate_booking_reference()

    return {
        "success": True,
        "booking_reference": booking_reference
    }
