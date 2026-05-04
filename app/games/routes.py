from fastapi import APIRouter, Request, Depends, HTTPException
import logging
import requests
import os
from dotenv import load_dotenv

from app.limiter.limiter import limiter
from app.auth.auth import get_login_user
from app.database.database import supabase

from app.games.models import GameToSave

logger = logging.getLogger(__name__)

load_dotenv()
router = APIRouter()

RAWG_API_KEY = os.getenv("RAWG_API_KEY", "").strip()

if not RAWG_API_KEY:
    raise ValueError("Chave RAWG não encontrada!")

@router.post("/add/game")
@limiter.limit("30/minute") 
async def add_game_on_lib(
    request: Request,
    game: GameToSave, 
    user = Depends(get_login_user) 
):
    user_id = user["user_id"]

    url = f"https://api.rawg.io/api/games/{game.rawg_id}"
    params = {"key": RAWG_API_KEY}

    rawg_response = requests.get(url, params=params)
    
    if rawg_response.status_code != 200:
        raise HTTPException(status_code=400, detail="Jogo não encontrado na base oficial.")
        
    rawg_oficial = rawg_response.json()

    if game.collection_id:
        collection_check = supabase.table("collections") \
            .select("id") \
            .eq("id", game.collection_id) \
            .eq("user_id", user_id) \
            .execute()
        
        if not collection_check.data:
            logger.warning(f"Tentativa de injeção em coleção! Usuário: {user_id} | Coleção: {game.collection_id}")
            
            raise HTTPException(
                status_code=403,
                detail="Coleção inválida ou você não tem permissão para adicionar jogos nela."
            )

    db_data = {
        "user_id": user_id,            
        "rawg_id": game.rawg_id,   
        "title": rawg_oficial.get("name"),
        "background_image": rawg_oficial.get("background_image"),
        "status": game.status,     
        "collection_id": game.collection_id,
    }

    try:
        response = supabase.table("games").insert(db_data).execute()

        return {
            "status": "sucesso",
            "message": "Jogo adicionado à sua biblioteca!",
            "game_saved": response.data[0]
        }

    except Exception as e:
        logger.error(f"Erro ao salvar Jogo para o usuário {user_id}: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Erro ao salvar o Jogo no banco de dados."
        )