from pydantic import BaseModel
from typing import Optional, Literal

class WatchedStatus(BaseModel):
    watched: Literal["watched", "not_watched", "in_progress"]

class MediaToSave(BaseModel):
    tmdb_id: str
    media_type: Literal["movie", "tv"]
    watched: Literal["watched", "not_watched", "in_progress"] = "not_watched"
    collection_id: Optional[str] = None

class MediaToCollection(BaseModel):
    id: str
    collection_id: str
