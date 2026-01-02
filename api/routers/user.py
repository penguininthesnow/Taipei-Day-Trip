from api.utils.jwt import create_jwt
from fastapi import APIRouter
from pydantic import BaseModel
import bcrypt
from api.db_connect import get_connection


router = APIRouter()

# 定義登入、註冊資料格式
class UserSignUp(BaseModel):
    name:str
    email:str
    password:str

class UserSignIn(BaseModel):
    email: str
    password: str

@router.post("/api/user")
def signup(user: UserSignUp):
    db = get_connection()
    cursor = db.cursor(dictionary=True)

    # 檢查email是否重複
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
    cursor.close()
    db.close()

    return {"ok": True}


# pyjwt--取得當前登入會員資訊設定
@router.put("/api/user/auth")
def signin(user: UserSignIn):
    db = get_connection()
    cursor = db.cursor(dictionary=True)

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

    cursor.close()
    db.close()

    return {"token": token}