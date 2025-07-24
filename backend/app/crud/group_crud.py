from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload

from app.crud.base_crud import CRUDBase
from app.models.user_model import User
from app.models.group_model import Group, user_group
from app.schemas.group_schema import GroupCreate, GroupUpdate
from app.utils.exceptions import UserAlreadyInGroupError, GroupNotInDatabaseError, UserNotInGroupError, UserHaveNoRightsError


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
        current_user: User,
        db: AsyncSession
    ):
        # await self.delete(db=db, id=id)
        #group_creator = await db.execute(select(Group).where(Group.id == id))
        #group_obj = group_creator.scalar_one_or_none()
        #if not group_obj:
        #    return None
        group_obj = await self.get(db=db, id=id)
        if not group_obj:
            raise GroupNotInDatabaseError(group_id=id)
        if current_user.id != group_obj.creator_id:
            raise UserHaveNoRightsError(current_user.id, id)
        await db.execute(delete(user_group).where(user_group.c.group_id == id))
        await db.delete(group_obj)
        await db.commit()
        return group_obj


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
        current_user: User,
        db: AsyncSession
    ):
        group_obj = await self.get_all_users(db=db, id=group_id)
        if current_user.id != group_obj.creator_id:
            raise UserHaveNoRightsError(current_user.id, group_id)
        if not group_obj:
            raise GroupNotInDatabaseError(group_id=group_id)
        if current_user.id == user_id:
            raise ValueError(f'Wrong ID - {user_id}. You cannot delete yourself.')

        if user_id not in [user.id for user in group_obj.users]:
            raise UserNotInGroupError(user_id=user_id)
        await db.execute(
            delete(user_group)
            .where(user_group.c.user_id == user_id)
            .where(user_group.c.group_id == group_id))
        await db.commit()



group = CRUDGroup(Group)