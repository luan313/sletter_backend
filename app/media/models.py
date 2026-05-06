from pydantic import BaseModel
from typing import Optional, Literal

class MediaToSave(BaseModel):
    tmdb_id: str
    media_type: Literal["movie", "tv"]
    watched: Literal["watched", "not_watched", "in_progress"] = "not_watched"
    collection_id: Optional[str] = None