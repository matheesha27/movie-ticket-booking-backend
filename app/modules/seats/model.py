from sqlalchemy import Column, UniqueConstraint
from sqlalchemy import BigInteger
from sqlalchemy import String
from sqlalchemy import Integer
from sqlalchemy import ForeignKey

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

    __table_args__ = (
        UniqueConstraint(
            'movie_id',
            'seat_id'
        ),
    )

    id = Column(BigInteger, primary_key=True, index=True)
    movie_id = Column(BigInteger, ForeignKey("movies.id"))
    seat_id = Column(BigInteger, ForeignKey("seats.id"))

    status = Column(
        String,
        default="AVAILABLE"
    )

    # AVAILABLE
    # HELD
    # BOOKED
