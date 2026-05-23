from app.database.session import engine, Base

from app.modules.users.model import User
from app.modules.cinemas.model import Cinema
from app.modules.movies.model import Movie

Base.metadata.create_all(bind=engine)