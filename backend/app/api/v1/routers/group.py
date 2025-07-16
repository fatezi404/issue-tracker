from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from app.models.user_model import User
from app.models.group_model import Group
from app.schemas.group_schema import GroupCreate, GroupUpdate, GroupResponse, GroupWithUsers
from app.deps.user_deps import get_current_user
from app.db.session import get_db
from app.crud.group_crud import group

router = APIRouter()

@router.post('', response_model=GroupResponse, tags=['group'], status_code=status.HTTP_201_CREATED)
async def create_group(
    obj_in: GroupCreate,
    creator: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    return await group.create_group(obj_in=obj_in, creator=creator, db=db)


@router.delete('/{id}', tags=['group'], status_code=status.HTTP_204_NO_CONTENT)
async def delete_group(
    id: int,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    return await group.delete_group(id=id, db=db)


@router.get('/{id}', response_model=GroupWithUsers, tags=['group'])
async def get_all_users_from_group(
    id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    users_in_association_db = await group.get_all_users(id=id, db=db)
    if not users_in_association_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Group not found'
        )
    users_in_db = await group.get(db=db, id=id)
    if current_user.id not in users_in_association_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='You have no permission or not authenticated'
        )
    return GroupWithUsers(
        id=id,
        title=users_in_db.title,
        created_at=users_in_db.created_at,
        users=users_in_association_db
    )

