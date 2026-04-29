from fastapi import APIRouter, Request, Query
import logging
import requests
import os
from dotenv import load_dotenv

from app.main import limiter

logger = logging.getLogger(__name__)

load_dotenv()
router = APIRouter()

TMDB_TOKEN = os.getenv("TMDB_TOKEN", "DEFAULT_TMDB_TOKEN")

@router.post("/search/new_movie")
@limiter.limit("60/minute")
async def search_new_movie(
    request: Request,
    title: str = Query(..., min_length=2, max_length=100)
):
    url = f"https://api.themoviedb.org/3/search/multi?query={title}&language=pt-BR"

    headers = {
        "Authorization": f"Bearer {TMDB_TOKEN}",
        "accept": "application/json"
    }

    response = requests.get(url, headers=headers)

    return response.json()