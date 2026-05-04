from pydantic import BaseModel
from typing import Optional, Literal

class GameToSave(BaseModel):
    rawg_id: int
    status: Literal["unplayed", "playing", "completed"] = "unplayed"
    collection_id: Optional[str] = None