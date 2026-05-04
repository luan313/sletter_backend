# app/collections/models.py
from pydantic import BaseModel, Field

class CollectionToCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50, description="Nome da coleção")