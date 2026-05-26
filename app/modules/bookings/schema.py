from pydantic import BaseModel
from typing import List

class BookingCreate(BaseModel):

    movie_seat_ids: List[int]