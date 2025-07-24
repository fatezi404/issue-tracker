from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from app.models.user_model import User
from app.schemas.group_schema import GroupCreate, GroupResponse, GroupWithUsers
from app.deps.user_deps import get_current_user
from app.db.session import get_db
from app.crud.group_crud import group
from app.utils.exceptions import (
    UserAlreadyInGroupError,
    UserNotInGroupError,
    GroupNotInDatabaseError,
    UserHaveNoRightsError,
    UserIsGroupCreator
)

router = APIRouter()

@router.post('', response_model=GroupResponse, tags=['group'], status_code=status.HTTP_201_CREATED)
async def create_group(
    obj_in: GroupCreate,
    creator: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    return await group.create_group(obj_in=obj_in, creator=creator, db=db)


@router.delete('', tags=['group'], status_code=status.HTTP_200_OK)
async def delete_group(
    group_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    try:
        group_del = await group.delete_group(id=group_id, db=db, current_user=current_user)
    except UserHaveNoRightsError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'User {current_user.id} have no rights to do such actions in group {group_id}'
        )
    except GroupNotInDatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Group {e.group_id} not found'
        )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=f'Group {group_id} successfully deleted'
    )


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


@router.post('/{group_id}', response_model=GroupWithUsers, tags=['group'], status_code=status.HTTP_200_OK)
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

@router.delete('/{group_id}', tags=['group'], status_code=status.HTTP_200_OK)
async def delete_users_from_group(
    group_id: int,
    user_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    try:
        delete_user = await group.delete_user_from_group(
            group_id=group_id,
            user_id=user_id,
            db=db,
            current_user=current_user
        )
    except GroupNotInDatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Group {e.group_id} not found'
        )
    except UserHaveNoRightsError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'User {current_user.id} have no rights to do such actions in group {group_id}'
        )
    except UserNotInGroupError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'User {e.user_id} not in group'
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Wrong ID {user_id}. You cannot delete yourself'
        )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=f'Successfully deleted user {user_id}'
    )

@router.delete('/leave-group/{group_id}', tags=['group'], status_code=status.HTTP_200_OK)
async def leave_group(
    group_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    try:
        await group.leave_group(group_id=group_id, current_user=current_user, db=db)
    except GroupNotInDatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Group {e.group_id} not found'
        )
    except UserNotInGroupError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'User {e.user_id} not in group'
        )
    except UserIsGroupCreator as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'User {e.user_id} is a creator of group {e.group_id}. You can just delete the group'
        )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=f'You successfully left group {group_id}'
    )