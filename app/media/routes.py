from fastapi import APIRouter, Request, Depends, HTTPException
import logging
import requests
import os
from dotenv import load_dotenv
from typing import List, Annotated
from pydantic import Field

from app.limiter.limiter import limiter
from app.auth.auth import get_login_user
from app.database.database import supabase

from app.media.models import MediaToSave, MediaToCollection, WatchedStatus

logger = logging.getLogger(__name__)

load_dotenv()
router = APIRouter(prefix="/media", tags=["Media"])

TMDB_TOKEN = os.getenv("TMDB_TOKEN").strip()

if not TMDB_TOKEN:
    raise ValueError("Token TMDB não encontrado!")

@router.post("/add_on_lib")
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

@router.post('/add_on_collection')
@limiter.limit("30/minute")
async def add_media_on_collection(
    request: Request,
    medias: Annotated[List[MediaToCollection], Field(max_length=50)],
    user = Depends(get_login_user),
):
    user_id = user["user_id"]

    if not medias:
        raise HTTPException(status_code=400, detail = "A lista de mídias está vazia.")

    try:
        target_collection_id = medias[0].collection_id

        if not target_collection_id:
            raise HTTPException(status_code=400 ,detail="ID da coleção não fornecido.")

        collection_check = supabase.table("collections") \
            .select("id") \
            .eq("id", target_collection_id) \
            .eq("user_id", user_id) \
            .execute()

        if not collection_check.data:
            raise HTTPException(status_code=404, detail="Coleção não encontrada.")

        processed_media = []

        for media in medias:
            if media.collection_id != target_collection_id:
                raise HTTPException(status_code=400, detail="Todas as mídias devem pertencer a mesma coleção.")

            media_check = supabase.table("user_library") \
                .select("id") \
                .eq("id", media.id) \
                .eq("user_id", user_id) \
                .execute()

            if not media_check.data:
                raise HTTPException(status_code=404, detail="Mídia não encontrada na sua biblioteca.")

            db_media_id = media_check.data[0]["id"]

            link_data = {
                "collection_id": media.collection_id,
                "library_item_id": db_media_id,
            }

            supabase.table("collection_media").insert(link_data).execute()

            processed_media.append(media.model_dump())

        return {
            "status": "sucesso",
            "message": f"{len(processed_media)} mídia(s) adicionada(s) à coleção com sucesso!",
            "media_added": processed_media
        }

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Erro ao adicionar Mídia à coleção para o usuário {user_id}: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Erro ao adicionar Mídia à coleção no banco de dados."
        )

@router.get('/{tmdb_id}')
@limiter.limit("100/minute")
async def get_media_details(
    request:Request,
    tmdb_id: str,
    user = Depends(get_login_user)
):
    user_id = user["user_id"]

    try:
        media_query = supabase.table("user_library") \
            .select("id, tmdb_id, media_type, title, poster_path, watched, created_at") \
            .eq("tmdb_id", tmdb_id) \
            .eq("user_id", user_id) \
            .execute()

        if not media_query.data:
            raise HTTPException(
                status_code=404,
                detail="Esta mídia não está na sua biblioteca."
            )

        media_data = media_query.data[0]
        db_media_id = media_data["id"]

        collections_query = supabase.table("collection_media") \
            .select("collection_id") \
            .eq("library_item_id", db_media_id) \
            .execute()

        collection_ids = [col["collection_id"] for col in collections_query.data] if collections_query.data else []

        media_data["in_collections"] = collection_ids

        return {
            "status": "sucesso",
            "media_details": media_data
        }
    
    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Erro ao buscar detalhes da mídia {tmdb_id} para o usuário {user_id}: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Erro interno ao buscar detalhes da mídia."
        )
    
@router.put('/{tmdb_id}')
@limiter.limit("30/minute")
async def edit_media_on_lib(
    request: Request,
    tmdb_id: int,
    status: WatchedStatus,
    user = Depends(get_login_user)
):
    user_id = user["user_id"]

    media_check = supabase.table("user_library") \
        .select("id") \
        .eq("tmdb_id", tmdb_id) \
        .eq("user_id", user_id) \
        .execute()
    
    if not media_check.data:
        raise HTTPException(status_code=404, detail="Item não encontrado na sua biblioteca.")
    
    try:
        supabase.table("user_library").update(status.model_dump()).eq("tmdb_id", tmdb_id).eq("user_id", user_id).execute()

        return {
            "status": "sucesso",
            "message": "Status do item atualizado com sucesso!"
        }
    
    except Exception as e:
        logger.error(f"Erro ao editar status do Item para o usuário {user_id}: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Erro ao editar status do Item no banco de dados."
        )

@router.delete('/{tmdb_id}')
@limiter.limit("30/minute")
async def delete_media_on_lib(
    request: Request,
    tmdb_id: int,
    user = Depends(get_login_user)
):
    user_id = user["user_id"]
    
    try:
        media_check = supabase.table("user_library") \
            .delete() \
            .eq("tmdb_id", tmdb_id) \
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

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Erro ao deletar Item para o usuário {user_id}: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Erro ao deletar Item no banco de dados."
        )