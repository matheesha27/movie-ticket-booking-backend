from pydantic import BaseModel

class SectionCreate(BaseModel):

    cinema_id: int
    name: str
    price: int

class SeatCreate(BaseModel):

    cinema_id: int
    section_id: int

    row_name: str
    seat_number: str
