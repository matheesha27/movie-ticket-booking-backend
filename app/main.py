from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.modules.users.routes import router as user_router
from app.modules.auth.routes import router as auth_router
from app.modules.cinemas.routes import router as cinema_router
from app.modules.movies.routes import router as movie_router
from app.modules.seats.routes import router as seat_router
from app.modules.bookings.routes import router as booking_router


app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

app.include_router(
    booking_router,
    prefix="/bookings",
    tags=["Bookings"]
)

@app.get("/")
def root():
    return {"message": "Ticket Booking API Running"}
