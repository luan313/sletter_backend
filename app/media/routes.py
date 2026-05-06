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
router = APIRouter(prefix="/media", tags=["Media"])

TMDB_TOKEN = os.getenv("TMDB_TOKEN").strip()

if not TMDB_TOKEN:
    raise ValueError("Token TMDB não encontrado!")

@router.post("/")
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
            logger.warning(f"Tentativa de injeção em coleção! Usuário: {user_id} | Coleção: {media.collection_id}")
            
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
    }

    try:
        response = supabase.table("user_library").insert(db_data).execute()
        saved_media = response.data[0]

        if media.collection_id:
            link_data = {
                "collection_id": media.collection_id,
                "library_item_id": saved_media["id"]
            }

            supabase.table("collection_media").insert(link_data).execute()

            saved_media["collection_ids"] = [media.collection_id]

        else:
            saved_media["collection_ids"] = []

        return {
            "status": "sucesso",
            "message": "Item adicionada à sua biblioteca!",
            "media_saved": saved_media
        }

    except Exception as e:
        logger.error(f"Erro ao salvar Item para o usuário {user_id}: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Erro ao salvar Item no banco de dados."
        )
    
@router.put('/{media_id}')
@limiter.limit("30/minute")
async def edit_media_on_lib(
    request: Request,
    media_id: str,
    media: MediaToSave,
    user = Depends(get_login_user)
):
    user_id = user["user_id"]

    media_check = supabase.table("user_library") \
        .select("id") \
        .eq("id", media_id) \
        .eq("user_id", user_id) \
        .execute()
    
    if not media_check.data:
        raise HTTPException(status_code=404, detail="Item não encontrado na sua biblioteca.")
    
    media_data = media.model_dump(exclude_unset=True)
    
    try:
        response = supabase.table("user_library").update(media_data).eq("id", media_id).execute()
        updated_media = response.data[0]

        return {
            "status": "sucesso",
            "message": "Item editado com sucesso!",
            "media_updated": updated_media
        }
    
    except Exception as e:
        logger.error(f"Erro ao editar Item para o usuário {user_id}: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Erro ao editar Item no banco de dados."
        )

@router.delete('/{media_id}')
@limiter.limit("30/minute")
async def delete_media_on_lib(
    request: Request,
    media_id: str,
    user = Depends(get_login_user)
):
    user_id = user["user_id"]
    
    try:
        media_check = supabase.table("user_library") \
            .delete() \
            .eq("id", media_id) \
            .eq("user_id", user_id) \
            .execute()
        
        if not media_check.data:
            raise HTTPException(status_code=404, detail="Item não encontrado na sua biblioteca.")

        deleted_media = media_check.data[0]

        return {
            "status": "sucesso",
            "message": "Item deletado com sucesso!",
            "media_deleted": deleted_media
        }

    except Exception:
        raise

    except Exception as e:
        logger.error(f"Erro ao deletar Item para o usuário {user_id}: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Erro ao deletar Item no banco de dados."
        )