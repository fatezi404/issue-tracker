from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.user_crud import user
from app.db.session import get_db
from app.models.user_model import User
from app.schemas.user_schema import UserResponse
from app.schemas.token_schema import TokenResponse, RefreshToken, Token

router = APIRouter()


@router.post('/login', response_model=UserResponse, tags=['user'])
async def authenticate_user(email: EmailStr, password: str, db: Annotated[AsyncSession, Depends(get_db)]) -> User:
    auth_user = user.authenticate_user(email=email, password=password, db=db)
    if not auth_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Wrong email or password')
    elif not auth_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='User has inactive status')
