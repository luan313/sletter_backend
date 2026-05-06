from fastapi import APIRouter, Request, Depends, HTTPException
import logging

from app.limiter.limiter import limiter
from app.auth.auth import get_login_user
from app.database.database import supabase

from app.collections.models import CollectionToCreate

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/collections", tags=["Collections"])

@router.post("/create")
@limiter.limit("20/minute")
async def create_collection(
    request: Request,
    collection: CollectionToCreate,
    user = Depends(get_login_user)
):
    user_id = user["user_id"]
    logger.info(f"Usuário {user_id} está criando a coleção: {collection.name}")

    existing_collection = supabase.table("collections") \
        .select("id") \
        .eq("user_id", user_id) \
        .ilike("name", collection.name) \
        .execute()
    
    if existing_collection.data:
        logger.warning(f"Usuário {user_id} tentou duplicar a coleção '{collection.name}'")
        raise HTTPException(
            status_code=409,
            detail="Você já possui uma coleção com este nome."
        )

    db_data = {
        "user_id": user_id,
        "name": collection.name
    }

    try:
        response = supabase.table("collections").insert(db_data).execute()

        return {
            "status": "sucesso",
            "message": f"Coleção '{collection.name}' criada com sucesso!",
            "collection": response.data[0] 
        }

    except Exception as e:
        logger.error(f"Erro ao criar coleção para o usuário {user_id}: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Não foi possível criar a coleção no momento."
        )
    
@router.get("/")
@limiter.limit("60/minute")
async def list_user_collections(
    request: Request,
    user = Depends(get_login_user)
):
    user_id = user["user_id"]
    logger.info(f"Usuário {user_id} buscando todas as suas coleções.")

    try:
        collections_response = supabase.table("collections") \
            .select("*") \
            .eq("user_id", user_id) \
            .execute()
        
        collections = collections_response.data

        if not collections:
            return {"collections": []}

        collection_ids = [c["id"] for c in collections]

        library_response = supabase.table("user_library") \
            .select("*, collection_media!inner(collection_id)") \
            .in_("collection_media.collection_id", collection_ids) \
            .execute()

        games_response = supabase.table("games") \
            .select("*, collection_games!inner(collection_id)") \
            .in_("collection_games.collection_id", collection_ids) \
            .execute()

        items_by_collection = {c["id"]: [] for c in collections}

        for item in library_response.data:
            col_media = item.pop("collection_media", [])
            if isinstance(col_media, list):
                for cm in col_media:
                    c_id = cm.get("collection_id")
                    if c_id in items_by_collection:
                        items_by_collection[c_id].append(item.copy())
            elif isinstance(col_media, dict):
                c_id = col_media.get("collection_id")
                if c_id in items_by_collection:
                    items_by_collection[c_id].append(item.copy())

        for game in games_response.data:
            col_games = game.pop("collection_games", [])
            if isinstance(col_games, list):
                for cg in col_games:
                    c_id = cg.get("collection_id")
                    if c_id in items_by_collection:
                        items_by_collection[c_id].append(game.copy())
            elif isinstance(col_games, dict):
                c_id = col_games.get("collection_id")
                if c_id in items_by_collection:
                    items_by_collection[c_id].append(game.copy())

        for collection in collections:
            c_id = collection["id"]
            collection["preview_items"] = items_by_collection[c_id][:5]

        return {"collections": collections}

    except Exception as e:
        logger.error(f"Erro ao buscar coleções do usuário {user_id}: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Não foi possível buscar as coleções no momento."
        )

@router.get("/{collection_id}")
@limiter.limit("60/minute")
async def show_collection(
    request: Request,
    collection_id: str,
    user = Depends(get_login_user)
):
    user_id = user["user_id"]
    logger.info(f"Usuário {user_id} buscando a coleção: {collection_id}")

    try:
        col_check = supabase.table("collections") \
            .select("*") \
            .eq("id", collection_id) \
            .eq("user_id", user_id) \
            .execute()
        
        if not col_check.data:
            logger.warning(f"Acesso negado ou coleção inexistente: {collection_id} | User: {user_id}")
            raise HTTPException(
                status_code=404, 
                detail="Coleção não encontrada ou você não tem permissão para acessá-la."
            )
        
        collection_info = col_check.data[0]

        library_response = supabase.table("user_library") \
            .select("*, collection_media!inner(collection_id)") \
            .eq("collection_media.collection_id", collection_id) \
            .execute()

        games_response = supabase.table("games") \
            .select("*, collection_games!inner(collection_id)") \
            .eq("collection_games.collection_id", collection_id) \
            .execute()

        all_items = library_response.data

        for item in all_items:
            item.pop("collection_media", None)

        movies = [item for item in all_items if item.get("media_type") == "movie"]
        series = [item for item in all_items if item.get("media_type") == "tv"]

        all_games = games_response.data

        for game in all_games:
            game.pop("collection_games", None)

        return {
            "collection_details": collection_info,
            "items": {
                "movies": movies,
                "series": series,
                "games": all_games
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao carregar os itens da coleção {collection_id}: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Erro ao carregar a sua coleção. Tente novamente."
        )

