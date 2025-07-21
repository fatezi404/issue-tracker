from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base_crud import CRUDBase
from app.models.task_model import Task
from app.schemas.task_schema import TaskUpdate, TaskCreate
from app.models.user_model import User
from app.utils.exceptions import TaskNotInDatabaseError
from app.crud.group_crud import group


class CRUDTask(CRUDBase[Task, TaskCreate, TaskUpdate]):
    async def create_task(
        self,
        *,
        obj_in: TaskCreate,
        current_user: User,
        db: AsyncSession
    ) -> Task:
        db_task = Task(**obj_in.model_dump(exclude_unset=True))
        db_task.reporter_id = current_user.id
        db.add(db_task)
        await db.commit()
        await db.refresh(db_task)
        return db_task

    async def update_task(
        self,
        *,
        id: int,
        obj_in: TaskUpdate,
        db: AsyncSession
    ) -> Task | None:
        existing_task = await self.get(db=db, id=id)
        if not existing_task:
            return None
        return await self.update(obj_current=existing_task, obj_in=obj_in, db=db)

    async def delete_task(
        self,
        *,
        id: int,
        db: AsyncSession
    ):
        return await self.delete(db=db, id=id)

    async def assign_user_to_task(
        self,
        *,
        task_id: int,
        user_id: int,
        db: AsyncSession
    ):
        task_db = await self.get(db=db, id=task_id)
        if not task_db:
            raise TaskNotInDatabaseError(task_id=task_id)
        task_db.assignee_id = user_id
        await db.commit()
        await db.refresh(task_db)
        return task_db

task = CRUDTask(Task)