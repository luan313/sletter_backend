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

from app.games.models import GameToSave, GameToCollection

logger = logging.getLogger(__name__)

load_dotenv()
router = APIRouter(prefix="/game", tags=["Game"])

RAWG_API_KEY = os.getenv("RAWG_API_KEY", "").strip()

if not RAWG_API_KEY:
    raise ValueError("Chave RAWG não encontrada!")

@router.post("/add_on_lib")
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
    }

    try:
        response = supabase.table("games").insert(db_data).execute()
        saved_game = response.data[0]

        if game.collection_id:
            link_data = {
                "collection_id": game.collection_id,
                "game_id": saved_game["id"],
            }

            supabase.table("collection_games").insert(link_data).execute()

            saved_game["collection_ids"] = [game.collection_id]

        else:
            saved_game["collection_ids"] = []

        return {
            "status": "sucesso",
            "message": "Jogo adicionado à sua biblioteca!",
            "game_saved": saved_game
        }

    except Exception as e:
        logger.error(f"Erro ao salvar Jogo para o usuário {user_id}: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Erro ao salvar o Jogo no banco de dados."
        )

@router.post("/add_on_collection")
@limiter.limit("30/minute")
async def add_game_on_collection(
    request: Request,
    games: Annotated[List[GameToCollection], Field(max_length=50)],
    user = Depends(get_login_user)
):
    user_id = user["user_id"]

    if not games:
        raise HTTPException(status_code=400, detail="A lista de jogos está vazia.")
    
    try:
        target_collection_id = games[0].collection_id

        if not target_collection_id:
            raise HTTPException(status_code=400, detail="ID da coleção não fornecido.")

        collection_check = supabase.table("collections") \
            .select("id") \
            .eq("id", target_collection_id) \
            .eq("user_id", user_id) \
            .execute()

        if not collection_check.data:
            raise HTTPException(status_code=404, detail="Coleção não encontrada.")

        processed_games = []

        for game in games:
            if game.collection_id != target_collection_id:
                raise HTTPException(status_code=400, detail="Todos os jogos devem pertencer a mesma coleção.")

            game_check = supabase.table("games") \
                .select("id") \
                .eq("id", game.id) \
                .eq("user_id", user_id) \
                .execute()
            
            if not game_check.data:
                raise HTTPException(status_code=404, detail="Jogo não encontrado na sua biblioteca.")

            db_game_id = game_check.data[0]["id"]

            link_data = {
                "collection_id": game.collection_id,
                "game_id": db_game_id,
            }

            supabase.table("collection_games").insert(link_data).execute()

            processed_games.append(game.model_dump())

        return {
            "status": "sucesso",
            "message": f"{len(processed_games)} jogo(s) adicionado(s) à coleção com sucesso!",
            "game_added": processed_games
        }

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Erro ao adicionar Jogo à coleção para o usuário {user_id}: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Erro ao adicionar Jogo à coleção no banco de dados."
        )

@router.get('/{rawg_id}')
@limiter.limit("100/minute")
async def get_game_details(
    request: Request,
    rawg_id: str,
    user = Depends(get_login_user)
):
    user_id = user["user_id"]

    try:
        game_query = supabase.table("games") \
            .select("id, rawg_id, title, background_image, status, created_at") \
            .eq("rawg_id", rawg_id) \
            .eq("user_id", user_id) \
            .execute()

        if not game_query.data:
            raise HTTPException(
                status_code=404,
                detail="Este jogo não está na sua biblioteca."
            )

        game_data = game_query.data[0]
        db_game_id = game_data["id"]

        collections_query = supabase.table("collection_games") \
            .select("collection_id") \
            .eq("game_id", db_game_id) \
            .execute()

        collection_ids = [col["collection_id"] for col in collections_query.data] if collections_query.data else []

        game_data["in_collections"] = collection_ids

        return {
            "status": "sucesso",
            "game_details": game_data
        }

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Erro ao buscar detalhes do jogo {rawg_id} para o usuário {user_id}: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Erro interno ao buscar detalhes do jogo."
        )

@router.put('/{rawg_id}')
@limiter.limit("30/minute")
async def edit_game_on_lib(
    request: Request,
    rawg_id: str,
    game: GameToSave,
    user = Depends(get_login_user)
):
    user_id = user["user_id"]
    
    game_check = supabase.table("games") \
        .select("id") \
        .eq("id", rawg_id) \
        .eq("user_id", user_id) \
        .execute()
    
    if not game_check.data:
        raise HTTPException(status_code=404, detail="Jogo não encontrado na sua biblioteca.")
    
    game_data = game.model_dump(exclude_unset=True)
    
    try:
        response = supabase.table("games").update(game_data).eq("id", rawg_id).execute()
        updated_game = response.data[0]
        return {
            "status": "sucesso",
            "message": "Jogo editado com sucesso!",
            "game_updated": updated_game
        }
    
    except Exception as e:
        logger.error(f"Erro ao editar Jogo para o usuário {user_id}: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Erro ao editar Jogo no banco de dados."
        )

@router.delete('/{rawg_id}')
@limiter.limit("30/minute")
async def delete_game_on_lib(
    request: Request,
    rawg_id: str,
    user = Depends(get_login_user)
):
    user_id = user["user_id"]

    try:
        game_check = supabase.table("games") \
            .delete() \
            .eq("id", rawg_id) \
            .eq("user_id", user_id) \
            .execute()
        
        if not game_check.data:
            raise HTTPException(status_code=404, detail="Jogo não encontrado na sua biblioteca.")
        
        deleted_game = game_check.data[0]
        
        return {
            "status": "sucesso",
            "message": "Jogo deletado com sucesso!",
            "game_deleted": deleted_game
        }

    except Exception:
        raise
    
    except Exception as e:
        logger.error(f"Erro ao deletar Jogo para o usuário {user_id}: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Erro ao deletar Jogo no banco de dados."
        )
