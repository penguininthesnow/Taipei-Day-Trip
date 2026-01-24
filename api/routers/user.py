from api.utils.jwt import create_jwt, decode_jwt
from fastapi import APIRouter, Request, Depends
from api.deps import get_current_user
from pydantic import BaseModel, EmailStr, field_validator
import re
import bcrypt
from api.db_connect import get_connection


router = APIRouter()

# 定義登入、註冊資料格式
class UserSignUp(BaseModel):
    name: str
    email: EmailStr
    password: str 
    
    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str):
        if len(v) < 6:
            raise ValueError("密碼至少6碼")
        if not re.search(r"[a-z]", v):
            raise ValueError("密碼需包含小寫英文字母")
        if not re.search(r"[A-Z]", v):
            raise ValueError("密碼需包含大寫英文字母")
        if not re.search(r"\d", v):
            raise ValueError("密碼需包含數字")
        if not re.search(r"[^A-Za-z0-9]", v):
            raise ValueError("密碼需包含特殊符號")
        
        return v
        # = Field(
        # min_length=6,
        # pattern=r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).+$'

class UserSignIn(BaseModel):
    email: EmailStr
    password: str

@router.post("/api/user")
def signup(user: UserSignUp):
    db = get_connection()
    cursor = db.cursor(dictionary=True)

    # 檢查email是否重複
    try:
        cursor.execute(
            "SELECT id FROM user WHERE email = %s",(user.email,)
        )
        if cursor.fetchone():
            return {
                "error": True,
                "message": "Email已經註冊帳戶"
            }
        
        # 密碼加密hash
        hashed_pw = bcrypt.hashpw(
            user.password.encode("utf-8"),
            bcrypt.gensalt()
        )
        cursor.execute(
            "INSERT INTO user (name, email, password) VALUES (%s, %s, %s)", (user.name, user.email, hashed_pw.decode("utf-8"))
        )
        db.commit()

        return {"ok":True}
    
    finally:
        cursor.close()
        db.close()


# pyjwt--取得當前登入會員資訊設定
@router.put("/api/user/auth")
def signin(user: UserSignIn):
    db = get_connection()
    cursor = db.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT id, name, email, password FROM user WHERE email=%s", (user.email,)
        )
        result = cursor.fetchone()

        if not result:
            cursor.close()
            db.close()
            return {
                "error":True,
                "message":"電子郵件或密碼錯誤"
            }
        if not bcrypt.checkpw(
            user.password.encode("utf-8"),
            result["password"].encode("utf-8")
        ):
            cursor.close()
            db.close()
            return {
                "error": True,
                "message": "電子郵件或密碼錯誤"
            }
        token = create_jwt({
            "id": result["id"],
            "name": result["name"],
            "email": result["email"]
        })

        return {"token": token}
    
    finally:
        cursor.close()
        db.close()

@router.get("/api/user/auth")
def auth_status(user=Depends(get_current_user)):
    return {
        "data": {
            "id": user["id"],
            "name": user.get("name"),
            "email": user.get("email")
        }
    }
