from fastapi import APIRouter
from pydantic import BaseModel
import bcrypt
from api.db_connect import get_connection


router = APIRouter()

# 定義登入註冊資料格式
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
            "message": "Email 已被註冊"
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