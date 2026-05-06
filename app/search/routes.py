from fastapi import APIRouter, Request, Depends, HTTPException
import logging
import os
import requests
from dotenv import load_dotenv

from app.limiter.limiter import limiter
from app.auth.auth import get_login_user

logger = logging.getLogger(__name__)

load_dotenv()
router = APIRouter(prefix="/search", tags=["Search"])

@router.get("/all")
@limiter.limit("60/minute")
async def search_all(
    request: Request,
    query: str = Query(..., min_length=2, max_length=100),
    user = Depends(get_login_user),
):
    user_id = user["user_id"]
    logger.info(f"Buscando na biblioteca do usuário: {user_id}")

    query_string = query.strip().lower()
    if not query_string or len(query_string) < 2:
        raise HTTPException(status_code=400, detail="A consulta deve ter pelo menos 2 caracteres.")
    
    try:
        response = supabase.table("user_library") \
            .select("*") \
            .eq("user_id", user_id) \
            .ilike("title", f"%{query_string}%") \
            .execute()
        
        results = response.data
        
        return {
            "status": "sucesso",
            "message": "Busca realizada com sucesso!",
            "results": results
        }
    except Exception as e:
        logger.error(f"Erro ao buscar na biblioteca do usuário {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro ao buscar na biblioteca.")