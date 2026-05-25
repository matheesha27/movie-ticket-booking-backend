from fastapi import FastAPI
from app.modules.users.routes import router as user_router
from app.modules.auth.routes import router as auth_router
from app.modules.cinemas.routes import router as cinema_router
from app.modules.movies.routes import router as movie_router
from app.modules.seats.routes import router as seat_router

app = FastAPI()

app.include_router(
    user_router,
    prefix="/users"
)

app.include_router(
    auth_router,
    prefix="/auth",
    tags=["Authentication"]
)

app.include_router(
    cinema_router,
    prefix="/cinemas",
    tags=["Cinemas"]
)

app.include_router(
    movie_router,
    prefix="/movies",
    tags=["Movies"]
)

app.include_router(
    seat_router,
    prefix="/seats",
    tags=["Seats"]
)

@app.get("/")
def root():
    return {"message": "Ticket Booking API Running"}
