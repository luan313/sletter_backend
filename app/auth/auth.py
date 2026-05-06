from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging

logger = logging.getLogger(__name__)

from app.database.database import supabase 

security = HTTPBearer()

async def get_login_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials

    try:
        response = supabase.auth.get_user(token)

        if not response or not response.user:
            raise HTTPException(
                status_code=403,
                detail="Usuário não encontrado ou inativo."
            )

        return {'user_id': response.user.id}
    
    except Exception as e:
        raise HTTPException(
            status_code=401, 
            detail="Sessão inválida ou expirada. Faça login novamente."
        )

async def verify_data_owner(
        id_on_url: str,
        login_user = Depends(get_login_user)
):
    if id_on_url != login_user["user_id"]:
        raise HTTPException(
            status_code=403,
            detail="Acesso negado: Você só pode acessar seus próprios dados."
        )
    
    return login_user