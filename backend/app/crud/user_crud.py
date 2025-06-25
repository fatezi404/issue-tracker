from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_hashed_password, verify_password
from app.crud.base_crud import CRUDBase
from app.models.user_model import User
from app.schemas.user_schema import UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    async def create_user(self, *, obj_in: UserCreate, db: AsyncSession) -> User:
        db_user = User(**obj_in.model_dump(exclude={'password'}))
        db_user.hashed_password = get_hashed_password(obj_in.password)
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user

    async def update_user(self, *, id: int, obj_in: UserUpdate, db: AsyncSession) -> User | None:
        existing_user = await self.get(id=id, db=db)
        if not existing_user:
            return None
        return await self.update(obj_current=existing_user, obj_in=obj_in, db=db)

    async def update_user_is_active(self, *, id: int, db: AsyncSession) -> User | None:
        existing_user = await self.get(id=id, db=db)
        if not existing_user:
            return None
        existing_user.is_active = not existing_user.is_active
        await db.commit()
        await db.refresh(existing_user)
        return existing_user

    async def authenticate(self, *, email: EmailStr, password: str, db: AsyncSession) -> User | None:
        existing_user = await self.get(email=str(email), db=db)
        if not existing_user:
            return None
        if not verify_password(plain_password=password, hashed_password=existing_user.hashed_password):
            return None
        return existing_user

    async def delete_user(self, *, id: int, db: AsyncSession) -> User | None:
        return await self.delete(id=id, db=db)


user = CRUDUser(User)
