from sqlalchemy import Column, Boolean
from sqlalchemy import BigInteger
from sqlalchemy import String
from sqlalchemy import Integer
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Identity

from datetime import datetime

from app.database.session import Base

class Booking(Base):

    __tablename__ = "bookings"

    id = Column(
        BigInteger,
        Identity(start=1),
        primary_key=True,
        index=True
    )

    user_id = Column(BigInteger, ForeignKey("users.id"))
    movie_id = Column(BigInteger, ForeignKey("movies.id"))

    booking_reference = Column(String, unique=True, nullable=False)
    status = Column(
        String,
        default="PENDING"
    )
    # PENDING
    # PAID
    # CANCELLED
    # FAILED

    payment_reference = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class BookingItem(Base):

    __tablename__ = "booking_items"

    id = Column(BigInteger, Identity(start=1), primary_key=True, index=True)
    booking_id = Column(BigInteger, ForeignKey("bookings.id"))
    movie_seat_id = Column(BigInteger, ForeignKey("movie_seats.id"))

    created_at = Column(DateTime, default=datetime.utcnow)


class OTPVerification(Base):

    __tablename__ = "otp_verifications"

    id = Column(BigInteger, primary_key=True)

    email = Column(String)
    otp = Column(String)
    expires_at = Column(DateTime)
    verified = Column(Boolean, default=False)
