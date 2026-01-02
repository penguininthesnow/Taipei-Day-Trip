import jwt
from datetime import datetime, timedelta

SECRET_KEY = "wehelp"
ALGORITHM = "HS256"
EXPIRE_MINUTES = 60 * 24

def create_jwt(payload: dict):
    payload = payload.copy()
    payload["exp"] = datetime.utcnow() + timedelta(minutes=EXPIRE_MINUTES)
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

def decode_jwt(token: str):
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])