from pydantic import BaseModel
from datetime import datetime

class MovieCreate(BaseModel):

    cinema_id: int
    title: str
    description: str
    category: str
    language: str
    duration: int
    banner_image: str
    trailer: str
    show_time: str

class MovieCinemasCreate(BaseModel):
    cinema_id: int
    title: str
    city: str
    show_time: str

class MovieCinemasRequest(BaseModel):
    movie_title: str

class ShowTimeRequest(BaseModel):
    cinema_id: int
    movie_title: str
