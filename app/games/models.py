from pydantic import BaseModel
from typing import Optional, Literal

class GameStatus(BaseModel):
    status: Literal["unplayed", "playing", "completed"]

class GameToSave(BaseModel):
    rawg_id: int
    status: Literal["unplayed", "playing", "completed"] = "unplayed"
    collection_id: Optional[str] = None

class GameToCollection(BaseModel):
    id: str
    collection_id: str
