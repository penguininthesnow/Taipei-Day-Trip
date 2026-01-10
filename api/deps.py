# 建立一個共同登入驗證 booking API
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from api.utils.jwt import decode_jwt

security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    try:
        token = credentials.credentials
        payload = decode_jwt(token)

        # payload 內至少要有 id
        if "id" not in payload:
            raise HTTPException(status_code=403)
        
        return payload
    except:
        raise HTTPException(status_code=403)