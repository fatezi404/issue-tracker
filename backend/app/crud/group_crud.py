from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.crud.base_crud import CRUDBase
from app.models.user_model import User
from app.models.group_model import Group, user_group
from app.schemas.group_schema import GroupCreate, GroupUpdate
from app.utils.exceptions import UserAlreadyInGroupError, GroupNotInDatabaseError, UserNotInGroupError


class CRUDGroup(CRUDBase[Group, GroupCreate, GroupUpdate]):
    async def create_group(
        self,
        *,
        obj_in: GroupCreate,
        creator: User,
        db: AsyncSession
    ) -> Group:
        db_group = Group(title=obj_in.title)
        db_group.users.append(creator)
        if obj_in.users:
            response = await db.execute(select(User).where(User.id.in_(obj_in.users)))
            users = response.scalars().all()
            db_group.users.extend(users)
        db_group.creator_id = creator.id
        db.add(db_group)
        await db.commit()
        await db.refresh(db_group)
        return db_group

    async def delete_group(
        self,
        *,
        id: int,
        db: AsyncSession
    ):
        await self.delete(db=db, id=id)
        response = await db.execute(select(user_group).where(user_group.c.group_id == id))
        db_obj = response.scalar_one_or_none()
        if not db_obj:
            return None
        await db.delete(db_obj)
        await db.commit()
        return db_obj


    async def get_all_users(
        self,
        *,
        id: int,
        db: AsyncSession
    ):
        response = await db.execute(select(Group).where(Group.id == id).options(selectinload(Group.users)))
        group = response.scalar_one_or_none()
        if not group:
            return None
        return group


    async def add_user_to_group(
        self,
        *,
        id: int,
        user_ids: List[int],
        db: AsyncSession
    ):
        response = await db.execute(select(Group).where(Group.id == id).options(selectinload(Group.users)))
        group = response.scalar_one_or_none()
        if not group:
            return None

        response = await db.execute(select(User).where(User.id.in_(user_ids)))
        users = response.scalars().all()
        if not users:
            return None
        for user in users:
            if user in group.users:
                raise UserAlreadyInGroupError(user_id=user.id, group_id=group.id)
            else:
                group.users.append(user)
        await db.commit()
        await db.refresh(group)
        return group


    async def delete_user_from_group(
        self,
        *,
        group_id: int,
        user_id: int,
        db: AsyncSession
    ):
        groups = await self.get(db=db, id=group_id)
        if not groups:
            raise GroupNotInDatabaseError(group_id=group_id)

        users_in_group = await self.get_all_users(db=db, id=group_id)
        if user_id not in [user.id for user in users_in_group]:
            raise UserNotInGroupError(user_id=user_id)
        response = await db.execute(
            select(user_group)
            .where(user_group.c.user_id == user_id)
            .where(user_group.c.group_id == group_id))
        db_user = response.scalar_one_or_none()
        await db.delete(db_user)
        await db.commit()
        return db_user



group = CRUDGroup(Group)