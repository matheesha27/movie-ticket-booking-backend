from app.database.session import engine, Base

from app.modules.users.model import User
from app.modules.cinemas.model import Cinema
from app.modules.movies.model import Movie
from app.modules.seats.model import Section
from app.modules.seats.model import Seat
from app.modules.seats.model import MovieSeat

Base.metadata.create_all(bind=engine)