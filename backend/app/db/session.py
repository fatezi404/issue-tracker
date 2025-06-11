from collections.abc import AsyncGenerator

from app.core.config import settings

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base


engine = create_async_engine(url=str(settings.DATABASE_URL))

Base = declarative_base()

Session = async_sessionmaker(bind=engine, expire_on_commit=False)


async def get_db() -> AsyncGenerator:
    async with Session() as db:
        yield db
