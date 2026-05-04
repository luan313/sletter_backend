from pydantic import BaseModel
from typing import Optional, Literal

class MediaToSave(BaseModel):
    tmdb_id: str
    media_type: Literal["movie", "tv"]
    watched: bool = False 
    collection_id: Optional[str] = None