from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from app.models.user_model import User
from app.models.task_model import Task
from app.schemas.task_schema import TaskResponse, TaskCreate, TaskUpdate
from app.deps.user_deps import get_current_user
from app.db.session import get_db
from app.crud.task_crud import task
from app.crud.group_crud import group
from app.utils.exceptions import TaskNotInDatabaseError


router = APIRouter()

@router.post('', response_model=TaskResponse, tags=['task'], status_code=status.HTTP_201_CREATED)
async def create_task(
    obj_in: TaskCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> Task:
    obj_with_reporter = TaskCreate(
        **obj_in.model_dump(exclude_none=True),
        reporter_id=current_user.id
    )
    group_in = await group.get_all_users(id=obj_in.group_id, db=db)
    if current_user.id not in [user.id for user in group_in.users]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Not authenticated'
        )
    return await task.create_task(obj_in=obj_with_reporter, db=db, current_user=current_user)


@router.patch('/{id}', response_model=TaskResponse, tags=['task'])
async def update_task(
    id: int,
    obj_in: TaskUpdate,
    db: Annotated[AsyncSession, Depends(get_db)]
) -> Task:
    updated_task = await task.update_task(id=id, obj_in=obj_in, db=db)
    if not updated_task:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Task does not exist'
        )
    return updated_task


@router.delete('/{id}', tags=['task'], status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    chosen_task = task.get(db=db, id=id)
    if not chosen_task:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Task does not exist'
        )
    await task.delete_task(id=id, db=db)
    return JSONResponse(
        status_code=status.HTTP_204_NO_CONTENT,
        content='Task deleted'
    )

@router.get('/{id}', response_model=TaskResponse, tags=['task']) # get by id
async def get_tasks_by_id(id: int, db: Annotated[AsyncSession, Depends(get_db)]) -> Task | None:
    task_db = await task.get(db=db, id=id)
    if not task_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Task does not exist'
        )
    return task_db

@router.post('/{task_id}', tags=['task'])
async def assign_task_to_user(
    task_id: int,
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    try:
        assign_task = await task.assign_user_to_task(task_id=task_id, user_id=user_id, db=db)
    except TaskNotInDatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Task {e.task_id} was not found'
        )
    return assign_task # todo: add current_user check

