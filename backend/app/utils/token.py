from redis.asyncio import Redis
from app.models.user_model import User
from datetime import timedelta
from app.core.config import TokenType


async def add_tokens_to_redis(
    redis_client: Redis,
    user: User,
    token: str,
    token_type: TokenType,
    expire_time: int | None = None
):
    token_key = f'user:{user.id}:{token_type}'
    await redis_client.sadd(token_key, token)
    if expire_time:
        await redis_client.expire(token_key, timedelta(minutes=expire_time))


async def get_valid_tokens(
    redis_client: Redis,
    user_id: int,
    token_type: TokenType
):
    token_key = f'user:{user_id}:{token_type}'
    valid_token = await redis_client.smembers(token_key)
    return valid_token


async def delete_tokens(
    redis_client: Redis,
    user_id: int,
    token_type: TokenType
):
    token_key = f'user:{user_id}:{token_type}'
    valid_token = await redis_client.smembers(token_key)
    if valid_token is not None:
        await redis_client.delete(token_key)