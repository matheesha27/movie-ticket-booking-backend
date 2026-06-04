from app.database.session import engine, Base

from app.modules.users.model import User
from app.modules.cinemas.model import Cinema
from app.modules.movies.model import Movie
from app.modules.seats.model import Section
from app.modules.seats.model import Seat
from app.modules.seats.model import MovieSeat
from app.modules.seats.model import SeatHold
from app.modules.bookings.model import Booking
from app.modules.bookings.model import BookingItem

Base.metadata.create_all(bind=engine)
