from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.user_crud import user
from app.db.session import get_db
from app.models.user_model import User
from app.schemas.user_schema import UserResponse

router = APIRouter()


@router.post('/auth', response_model=UserResponse, tags=['user'])
async def authenticate_user(email: EmailStr, password: str, db: Annotated[AsyncSession, Depends(get_db)]) -> User:
    return user.authenticate_user(email=email, password=password, db=db)
