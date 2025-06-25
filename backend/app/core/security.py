import bcrypt
from datetime import datetime, timedelta
from jose import ExpiredSignatureError, jwt

from app.core.config import settings

ALGORITHM = 'HS256'

def create_access_token(subject: int, expire_time: timedelta = None) -> str:
    if expire_time:
        expire = datetime.now() + timedelta(expire_time)
    else:
        expire = datetime.now() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        'sub': str(subject),
        'exp': expire,
        'type': 'access'
    }
    return jwt.encode(to_encode, settings.SECRET_KEY, ALGORITHM)


def create_refresh_token(subject: int, expire_time: timedelta = None) -> str:
    if expire_time:
        expire = datetime.now() + timedelta(expire_time)
    else:
        expire = datetime.now() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        'sub': str(subject),
        'exp': expire,
        'type': 'refresh'
    }
    return jwt.encode(to_encode, settings.SECRET_KEY, ALGORITHM)


def decode_token(token: str) -> dict | None:
    return jwt.decode(token, settings.SECRET_KEY, [ALGORITHM])


def get_hashed_password(plain_password: str | bytes) -> str:
    if isinstance(plain_password, str):
        plain_password = plain_password.encode()
    return bcrypt.hashpw(plain_password, bcrypt.gensalt()).decode()


def verify_password(plain_password: str | bytes, hashed_password: str | bytes) -> bool:
    if isinstance(plain_password, str):
        plain_password = plain_password.encode()
    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode()
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())
