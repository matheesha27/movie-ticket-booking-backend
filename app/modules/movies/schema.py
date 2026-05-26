from pydantic import BaseModel
from datetime import datetime

class MovieCreate(BaseModel):

    cinema_id: int
    title: str
    description: str
    category: str
    duration: int
    banner_image: str
    trailer: str
    show_time: datetime
