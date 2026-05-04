from fastapi import APIRouter, Request, Depends, HTTPException
import logging
import requests
import os
from dotenv import load_dotenv

from app.limiter.limiter import limiter
from app.auth.auth import get_login_user
from app.database.database import supabase

from app.media.models import MediaToSave

logger = logging.getLogger(__name__)

load_dotenv()
router = APIRouter()

TMDB_TOKEN = os.getenv("TMDB_TOKEN").strip()

if not TMDB_TOKEN:
    raise ValueError("Token TMDB não encontrado!")

@router.post("/add/media")
@limiter.limit("30/minute")
async def add_media_on_lib(
    request: Request,
    media: MediaToSave, 
    user = Depends(get_login_user) 
):
    user_id = user["user_id"]

    url = f"https://api.themoviedb.org/3/{media.media_type}/{media.tmdb_id}"

    headers = {
        "Authorization": f"Bearer {TMDB_TOKEN}",
        "accept": "application/json"
    }

    tmdb_response = requests.get(url, headers=headers, params={"language": "pt-BR"})
    
    if tmdb_response.status_code != 200:
        raise HTTPException(status_code=400, detail="Mídia não encontrado na base oficial.")
        
    tmdb_oficial = tmdb_response.json()

    official_title = tmdb_oficial.get("title") if media.media_type == "movie" else tmdb_oficial.get("name")

    if media.collection_id:
        collection_check = supabase.table("collections") \
            .select("id") \
            .eq("id", media.collection_id) \
            .eq("user_id", user_id) \
            .execute()
        
        if not collection_check.data:
            logger.warning(f"Tentativa de injeção em coleção! Usuário: {user_id} | Coleção: {movie.collection_id}")
            
            raise HTTPException(
                status_code=403,
                detail="Coleção inválida ou você não tem permissão para adicionar mídias nela."
            )

    db_data = {
        "user_id": user_id,            
        "tmdb_id": media.tmdb_id,   
        "media_type": media.media_type,   
        "title": official_title,
        "poster_path": tmdb_oficial.get("poster_path"),
        "watched": media.watched,    
        "collection_id": media.collection_id,
    }

    try:
        response = supabase.table("user_library").insert(db_data).execute()

        return {
            "status": "sucesso",
            "message": "Item adicionada à sua biblioteca!",
            "media_saved": response.data[0]
        }

    except Exception as e:
        logger.error(f"Erro ao salvar Item para o usuário {user_id}: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Erro ao salvar Item no banco de dados."
        )
    
