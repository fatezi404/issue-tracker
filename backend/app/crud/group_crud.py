from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.crud.base_crud import CRUDBase
from app.models.user_model import User
from app.models.group_model import Group, user_group
from app.schemas.group_schema import GroupCreate, GroupUpdate, GroupResponse, GroupWithUsers


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

    #async def add_user_to_group(
    #    self,
    #    *,
    #    id: int,
    #    user_list: GroupWithUsers,
    #    db: AsyncSession
    #):

group = CRUDGroup(Group)