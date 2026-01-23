import os
from dotenv import load_dotenv
from pathlib import Path
import jwt
from datetime import datetime, timedelta

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"
EXPIRE_MINUTES = 60 * 24

if not SECRET_KEY:
    raise RuntimeError("JWT_SECRET_KEY is not set in environment vairables")

def create_jwt(payload: dict):
    payload = payload.copy()
    payload["exp"] = datetime.utcnow() + timedelta(minutes=EXPIRE_MINUTES)
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

def decode_jwt(token: str):
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])