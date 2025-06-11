from datetime import datetime, timedelta

import bcrypt
from jose import ExpiredSignatureError, jwt

from app.core.config import settings

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(data: dict, remember_me: bool = False) -> str:
    to_encode = data.copy()
    if remember_me:
        expire = datetime.now() + timedelta(days=7)
    else:
        expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({'exp': expire})
    return jwt.encode(to_encode, SECRET_KEY, ALGORITHM)


def decode_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, SECRET_KEY, [ALGORITHM])
    except ExpiredSignatureError:
        print('LOG: expired token')
    return None


def get_hashed_password(plain_password: str | bytes) -> str:
    if isinstance(plain_password, str):
        plain_password = plain_password.encode()
    return bcrypt.hashpw(plain_password, bcrypt.gensalt()).decode()


def verify_password(plain_password: str | bytes, hashed_password: str | bytes) -> bool:
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())
