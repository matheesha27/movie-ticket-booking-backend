from pydantic import BaseModel
from datetime import datetime

class MovieCreate(BaseModel):

    cinema_id: int
    title: str
    description: str
    category: str
    banner_image: str
    show_time: datetime
