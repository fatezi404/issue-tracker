from enum import Enum
from pydantic import PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class TokenType(str, Enum):
    access = 'access_token'
    refresh = 'refresh_token'


class Settings(BaseSettings):
    DATABASE_URL: PostgresDsn
    DATABASE_PORT: str
    DATABASE_USER: str
    DATABASE_PASSWORD: str
    DATABASE_NAME: str
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 420228
    REDIS_URL: RedisDsn

    model_config = SettingsConfigDict(
        env_file= ".env", env_file_encoding='utf-8'
    )

settings = Settings()
