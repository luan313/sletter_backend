from fastapi import APIRouter, Request, Depends, HTTPException
import logging

from app.limiter.limiter import limiter
from app.auth.auth import get_login_user
from app.database.database import supabase

logger = logging.getLogger(__name__)

router  = APIRouter(prefix="/catalog", tags=["Catalog"])

@router.get("/all")
@limiter.limit("60/minute")
async def get_full_catalog(
    request: Request,
    user = Depends(get_login_user)
):
    user_id = user["user_id"]
    logger.info(f"Buscando a biblioteca pessoal do usuário: {user_id}")

    try:
        library_response = supabase.table("user_library") \
            .select("*, collection_media(collection_id)") \
            .eq("user_id", user_id) \
            .execute()
        
        games_response = supabase.table("games") \
            .select("*, collection_games(collection_id)") \
            .eq("user_id", user_id) \
            .execute()

        all_media = library_response.data
        for media in all_media:
            connections = media.pop("collection_media", []) 
            media["collection_ids"] = [c["collection_id"] for c in connections if c]

        all_games = games_response.data
        for game in all_games:
            connections = game.pop("collection_games", [])
            game["collection_ids"] = [c["collection_id"] for c in connections if c]

        movies = [media for media in all_media if media.get("media_type") == "movie"]
        series = [media for media in all_media if media.get("media_type") == "tv"]

        return {
            "movies": movies,
            "series": series,
            "games": games_response.data
        }

    except Exception as e:
        logger.error(f"Erro ao buscar o catálogo do usuário {user_id}: {e}")
        
        raise HTTPException(
            status_code=500, 
            detail="Não foi possível carregar a sua biblioteca. Tente novamente."
        )