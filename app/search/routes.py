from fastapi import APIRouter, Request, Depends, HTTPException, Query
import logging
from dotenv import load_dotenv
from typing import List

from app.limiter.limiter import limiter
from app.auth.auth import get_login_user

from app.database.database import supabase

from app.search.models import FilterModel

logger = logging.getLogger(__name__)

load_dotenv()
router = APIRouter(prefix="/search", tags=["Search"])

@router.get("/")
@limiter.limit("60/minute")
async def search_all(
    request: Request,
    query: str = Query(..., min_length=2, max_length=100),
    filter: FilterModel = Depends(),
    user = Depends(get_login_user),
):
    user_id = user["user_id"]

    query_string = query.strip().lower()
    search_term = f"%{query_string}%"
    
    logger.info(f"Buscando na biblioteca do usuário: {user_id}")

    try:
        results = {}

        if "media" in filter.type:
            media_response = supabase.table("user_library") \
                .select("id, tmdb_id, title, media_type, poster_path, watched") \
                .eq("user_id", user_id) \
                .ilike("title", search_term) \
                .limit(5) \
                .execute()

            results["media"] = media_response.data

        if "games" in filter.type:
            games_response = supabase.table("games") \
                .select("id, rawg_id, title, background_image, status") \
                .eq("user_id", user_id) \
                .ilike("title", search_term) \
                .limit(5) \
                .execute()

            results["games"] = games_response.data

        if "collections" in filter.type:
            collections_response = supabase.table("collections") \
                .select("id, name") \
                .eq("user_id", user_id) \
                .ilike("name", search_term) \
                .limit(5) \
                .execute()
            
            results["collections"] = collections_response.data
        
        return {
            "status": "sucesso",
            "message": "Busca realizada com sucesso!",
            "results": results
        }

    except Exception as e:
        logger.error(f"Erro ao buscar na biblioteca do usuário {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro ao buscar na biblioteca.")