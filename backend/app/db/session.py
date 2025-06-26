from collections.abc import AsyncGenerator
from redis.asyncio import Redis, from_url

from app.core.config import settings

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base


engine = create_async_engine(url=str(settings.DATABASE_URL))

Base = declarative_base()

Session = async_sessionmaker(bind=engine, expire_on_commit=False)


async def get_redis_db() -> Redis:
    redis = await from_url(
        url=str(settings.REDIS_URL),
        encoding='utf8',
        decode_responses=True
    )
    return redis

async def get_db() -> AsyncGenerator:
    async with Session() as db:
        yield db
