# 建立一個共同登入驗證 booking API
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from api.utils.jwt import decode_jwt

security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    print("credentials:", credentials) # 驗證用
    try:
        token = credentials.credentials
        payload = decode_jwt(token)

        print("JWT payload:", payload)

        # payload 內至少要有 id
        if "id" not in payload:
            raise HTTPException(status_code=403)
        
        return {
            "id": payload["id"],
            "name": payload.get("name"),
            "email": payload.get("email")
        }
    except Exception as e:
        print("JWT decode error:", e)
        raise HTTPException(status_code=403)
