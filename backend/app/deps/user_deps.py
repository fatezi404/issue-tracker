from typing import Annotated

from redis.asyncio import Redis
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from jose.exceptions import ExpiredSignatureError, JWTError

from app.models.user_model import User
from app.core.security import decode_token
from app.schemas.user_schema import UserResponse, UserCreate, UserUpdate
from app.db.session import get_db, get_redis_db
from app.crud.user_crud import user
from app.core.config import TokenType
from app.utils.token import get_valid_tokens, delete_tokens, add_tokens_to_redis


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/v1/login/access-token')


async def get_current_user(
    access_token: Annotated[str, Depends(oauth2_scheme)],
    redis_client: Annotated[Redis, Depends(get_redis_db)],
) -> User:
    try:
        payload = decode_token(access_token)
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Token is expired'
        )

    user_id = payload['sub']
    valid_access_token = await get_valid_tokens(redis_client, user_id, TokenType.ACCESS)
    if not valid_access_token and access_token not in valid_access_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Wrong credentials'
        )
    user_in_db: User = await user.get(db=Annotated[AsyncSession, Depends(get_db)], id=User.id)

    if not user_in_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='User does not exist'
        )

    if not user_in_db.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='User is inactive'
        )

    return user_in_db
