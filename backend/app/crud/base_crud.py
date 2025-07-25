from typing import Any, Generic, TypeVar

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import Base

ModelType = TypeVar('ModelType', bound=Base)
CreateSchemaType = TypeVar('CreateSchemaType', bound=BaseModel)
UpdateSchemaType = TypeVar('UpdateSchemaType', bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: type[ModelType]):
        self.model = model

    async def create(self, *, obj_in: CreateSchemaType, db: AsyncSession) -> ModelType:
        db_obj = self.model(**obj_in.model_dump())
        try:
            db.add(db_obj)
            await db.commit()
        except IntegrityError:
            await db.rollback()
        return db_obj

    async def get(self, *, db: AsyncSession, **filters) -> ModelType | None:
        response = await db.execute(select(self.model).filter_by(**filters))
        return response.scalar_one_or_none()

    async def delete(self, *, id: int, db: AsyncSession) -> ModelType | None:
        response = await db.execute(select(self.model).where(self.model.id == id))
        db_obj = response.scalar_one_or_none()
        if not db_obj:
            return None
        await db.delete(db_obj)
        await db.commit()
        return db_obj

    async def update(
        self,
        *,
        obj_current: ModelType,
        obj_in: UpdateSchemaType | dict[str, Any],
        db: AsyncSession
    ) -> ModelType | None:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        for field in update_data:
            setattr(obj_current, field, update_data[field])
        try:
            db.add(obj_current)
            await db.commit()
        except IntegrityError:
            await db.rollback()
        return obj_current
