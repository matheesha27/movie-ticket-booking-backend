from sqlalchemy import Column, UniqueConstraint, Identity
from sqlalchemy import BigInteger
from sqlalchemy import String
from sqlalchemy import Integer
from sqlalchemy import ForeignKey
from sqlalchemy import DateTime
from datetime import datetime

from app.database.session import Base

class Section(Base):

    __tablename__ = "sections"

    id = Column(BigInteger, primary_key=True, index=True)
    cinema_id = Column(BigInteger, ForeignKey("cinemas.id"))

    name = Column(String, nullable=False)
    price = Column(Integer)


class Seat(Base):

    __tablename__ = "seats"

    __table_args__ = (
        UniqueConstraint(
            'cinema_id',
            'row_name',
            'seat_number'
        ),
    )

    id = Column(BigInteger, primary_key=True, index=True)
    cinema_id = Column(BigInteger, ForeignKey("cinemas.id"))
    section_id = Column(BigInteger, ForeignKey("sections.id"))

    row_name = Column(String)
    seat_number = Column(String)


class MovieSeat(Base):

    __tablename__ = "movie_seats"

    id = Column(BigInteger, Identity(start=1), primary_key=True, index=True)
    movie_id = Column(BigInteger, ForeignKey("movies.id"))
    seat_id = Column(BigInteger, ForeignKey("seats.id"))

    status = Column(
        String,
        default="AVAILABLE"
    )
    # AVAILABLE
    # HELD
    # BOOKED

    __table_args__ = (
        UniqueConstraint(
            'movie_id',
            'seat_id'
        ),
    )

    held_by = Column(BigInteger, nullable=True)
    held_at = Column(DateTime, nullable=True)
    booked_by = Column(BigInteger, nullable=True)
    booked_at = Column(DateTime, nullable=True)
