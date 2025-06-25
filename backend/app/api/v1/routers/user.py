from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_model import User
from app.schemas.user_schema import UserResponse, UserCreate, UserUpdate
from app.db.session import get_db
from app.crud.user_crud import user

router = APIRouter()


@router.post('/register', response_model=UserResponse, tags=['user'])
async def create_user(obj_in: UserCreate, db: Annotated[AsyncSession, Depends(get_db)]) -> User:
    if await user.get(db=db, email=obj_in.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='User already exists')
    return await user.create_user(obj_in=obj_in, db=db)

@router.get('', response_model=UserResponse, tags=['user'])
async def get_user_by_id(id: Annotated[int, Query()], db: Annotated[AsyncSession, Depends(get_db)]) -> User:
    user_db = await user.get(db=db, id=id)
    if not user_db:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='User does not exist')
    return user_db

@router.delete('', response_model=UserResponse, tags=['user'])
async def delete_user(id: int, db: Annotated[AsyncSession, Depends(get_db)], freeze_user: bool = False) -> User:
    if freeze_user:
        updated_user = await user.update_user_is_active(id=id, db=db)
        if not updated_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='User does not exist')
        return updated_user

    deleted_user = await user.delete_user(id=id, db=db)
    if not deleted_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='User does not exist')
    return deleted_user


@router.patch('', response_model=UserResponse, tags=['user'])
async def update_user(id: int, obj_in: UserUpdate, db: Annotated[AsyncSession, Depends(get_db)]) -> User:
    updated_user = await user.update_user(id=id, obj_in=obj_in, db=db)
    if not updated_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='User does not exist')
    return updated_user
