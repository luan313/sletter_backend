from pydantic import BaseModel
from datetime import date

class Movie(BaseModel):
    tmdb_id: int
    title:str
    release_date: date
    poster_path: str
    watched: bool = False