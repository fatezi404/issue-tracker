from enum import Enum
from dotenv import load_dotenv
from pydantic import PostgresDsn
from pydantic_settings import BaseSettings

load_dotenv()


class UserRole(str, Enum):
    user = 'user'
    moderator = 'moderator'
    admin = 'admin'


class Settings(BaseSettings):
    DATABASE_URL: PostgresDsn
    DATABASE_PORT: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    SECRET_KEY: str

    class Config:
        env_file = '.env'


settings = Settings()
