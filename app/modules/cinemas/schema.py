from pydantic import BaseModel

class CinemaCreate(BaseModel):

    name: str
    city: str
    total_capacity: int