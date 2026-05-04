from fastapi import APIRouter, Query, Depends, Request, HTTPException
import logging
import os
import requests
from dotenv import load_dotenv

from app.limiter.limiter import limiter
from app.auth.auth import get_login_user

logger = logging.getLogger(__name__)

load_dotenv()
router = APIRouter(prefix="/discover", tags=["Discover New"])

TMDB_TOKEN = os.getenv("TMDB_TOKEN").strip()
if not TMDB_TOKEN:
    raise ValueError("Token TMDB não encontrado!")

RAWG_API_KEY = os.getenv("RAWG_API_KEY", "").strip()
if not RAWG_API_KEY:
    logger.warning("Chave da API RAWG não encontrada! A busca de jogos falhará.")

@router.get("/new_movie")
@limiter.limit("60/minute")
async def discover_new_movie(
    request: Request,
    title: str = Query(..., min_length=2, max_length=100),
    user = Depends(get_login_user),
):
    url = f"https://api.themoviedb.org/3/search/multi"

    headers = {
        "Authorization": f"Bearer {TMDB_TOKEN}",
        "accept": "application/json"
    }

    params = {
        "query": title,
        "language": "pt-BR"
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        raise HTTPException(status_code=502, detail="Erro ao buscar no TMDB")

    return response.json()

@router.get("/new_game")
@limiter.limit("60/minute")
async def new_game(
    request: Request,
    title: str = Query(..., min_length=2, max_length=100),
    user = Depends(get_login_user),
):
    url = "https://api.rawg.io/api/games"

    params = {
        "search": title,
        "key": RAWG_API_KEY,
        "page_size": 10,
        "search_precise": True
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        logger.error(f"Erro na RAWG: {response.text}")
        raise HTTPException(status_code=502, detail="Erro ao buscar na base de jogos.")
    
    return response.json()