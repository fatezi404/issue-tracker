from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from app.models.user_model import User
from app.models.group_model import Group
from app.schemas.group_schema import GroupCreate, GroupUpdate, GroupResponse, GroupWithUsers
from app.deps.user_deps import get_current_user
from app.db.session import get_db
from app.crud.group_crud import group
from app.utils.exceptions import UserAlreadyInGroupError

router = APIRouter()

@router.post('', response_model=GroupResponse, tags=['group'], status_code=status.HTTP_201_CREATED)
async def create_group(
    obj_in: GroupCreate,
    creator: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    return await group.create_group(obj_in=obj_in, creator=creator, db=db)


@router.delete('/{group_id}', tags=['group'], status_code=status.HTTP_204_NO_CONTENT)
async def delete_group(
    group_id: int,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    return await group.delete_group(id=group_id, db=db)


@router.get('/{group_id}', response_model=GroupWithUsers, tags=['group'])
async def get_all_users_from_group(
    group_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    users_in_group = await group.get_all_users(id=group_id, db=db)
    if not users_in_group:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Group not found'
        )
    if current_user.id not in [user.id for user in users_in_group.users]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Not authenticated'
        )
    return users_in_group


@router.post('/{group_id}', response_model=GroupWithUsers, tags=['group'])
async def add_users_to_group(
    group_id: int,
    user_ids: List[int],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    try:
        add_users = await group.add_user_to_group(id=group_id, user_ids=user_ids, db=db)
    except UserAlreadyInGroupError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'User {e.user_id} already in group {e.group_id}'
        )

    return add_users
