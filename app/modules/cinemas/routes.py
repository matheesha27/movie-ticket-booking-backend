from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session

from app.database.dependencies import get_db

from app.modules.cinemas.model import Cinema
from app.modules.cinemas.schema import CinemaCreate

router = APIRouter()

@router.post("/")
def create_cinema(request: CinemaCreate, db: Session = Depends(get_db)):

    cinema = Cinema(
        name=request.name,
        city=request.city,
        total_capacity=request.total_capacity
    )
    db.add(cinema)
    db.commit()
    db.refresh(cinema)

    return cinema

@router.get("/")
def get_cinema(db: Session = Depends(get_db)):

    cinemas = db.query(Cinema).all()

    return cinemas
