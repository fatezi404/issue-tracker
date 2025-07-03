from typing import Annotated

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from jose import ExpiredSignatureError
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, verify_password, get_hashed_password, create_refresh_token, \
    decode_token
from app.deps.user_deps import get_current_user
from app.crud.user_crud import user
from app.db.session import get_db, get_redis_db
from app.core.config import settings, TokenType
from app.models.user_model import User
from app.schemas.token_schema import TokenResponse, RefreshToken, Token
from app.schemas.user_schema import UserUpdate
from app.utils.token import get_valid_tokens, add_tokens_to_redis, delete_tokens

router = APIRouter()


@router.post('/access-token', response_model=TokenResponse, tags=['login'])
async def login_access_token(
    redis_client: Annotated[Redis, Depends(get_redis_db)],
    db: Annotated[AsyncSession, Depends(get_db)],
    oauth_form: OAuth2PasswordRequestForm = Depends()
):
    user_auth = await user.authenticate(
        email=oauth_form.username,
        password=oauth_form.password,
        db=db
    )
    if not user_auth:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='User does not exist'
        )
    if not user_auth.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='User is inactive'
        )
    access_token = create_access_token(
        user_auth.id,
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    refresh_token = create_refresh_token(
        user_auth.id,
        timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    )
    await delete_tokens(
        redis_client,
        user_auth.id,
        TokenType.access
    )
    await delete_tokens(
        redis_client,
        user_auth.id,
        TokenType.refresh
    )
    await add_tokens_to_redis(
        redis_client,
        user_auth,
        access_token,
        TokenType.access,
        settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    await add_tokens_to_redis(
        redis_client,
        user_auth,
        refresh_token,
        TokenType.refresh,
        settings.REFRESH_TOKEN_EXPIRE_MINUTES
    )
    return TokenResponse(access_token=access_token, token_type='bearer')


@router.post('/new-access-token', tags=['login'])
async def create_new_access_token(
    redis_client: Annotated[Redis, Depends(get_redis_db)],
    db: Annotated[AsyncSession, Depends(get_db)],
    body: RefreshToken = Body(...)
):
    try:
        payload = decode_token(body.refresh_token)
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Token is expired'
        )
    if payload['type'] == 'refresh':
        user_id = payload['sub']
        valid_refresh_token = await get_valid_tokens(
            redis_client,
            user_id,
            TokenType.refresh
        )
        if not valid_refresh_token or body.refresh_token not in valid_refresh_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Wrong credentials or invalid refresh token'
            )

        user_in_db: User = await user.get(db=db, id=int(user_id))
        if user_in_db.is_active:
            access_token = create_access_token(
                payload['sub'],
                timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            )
            await delete_tokens(
                redis_client,
                user_id,
                TokenType.access
            )
            await add_tokens_to_redis(
                redis_client,
                user_in_db,
                access_token,
                TokenType.access,
                settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='User is inactive'
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Incorrect token'
        )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content='Access token created'
    )



@router.post('/change-password', tags=['login'])
async def change_password(
    redis_client: Annotated[Redis, Depends(get_redis_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    current_password: str = Body(...),
    new_password: str = Body(...),
):
    if not verify_password(current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Wrong current password'
        )

    new_password_hashed = get_hashed_password(new_password)

    await user.update_user(
        id=current_user.id,
        obj_in={'hashed_password': new_password_hashed},
        db=db
    )

    access_token = create_access_token(
        current_user.id,
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    refresh_token = create_refresh_token(
        current_user.id,
        timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    )

    await delete_tokens(
        redis_client,
        current_user.id,
        TokenType.access
    )

    await delete_tokens(
        redis_client,
        current_user.id,
        TokenType.refresh
    )

    await add_tokens_to_redis(
        redis_client=redis_client,
        user=current_user,
        token=access_token,
        token_type=TokenType.access,
        expire_time=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    await add_tokens_to_redis(
        redis_client=redis_client,
        user=current_user,
        token=refresh_token,
        token_type=TokenType.refresh,
        expire_time=settings.REFRESH_TOKEN_EXPIRE_MINUTES
    )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={'message': 'Password has been changed'}
    )