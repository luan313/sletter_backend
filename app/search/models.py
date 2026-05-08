from pydantic import BaseModel
from typing import Literal, List

class FilterModel(BaseModel):
    type: List[Literal["collections", "media", "games"]] = ["collections", "media", "games"]