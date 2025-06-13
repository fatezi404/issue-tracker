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
    DATABASE_USER: str
    DATABASE_PASSWORD: str
    DATABASE_NAME: str
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = '.env'


settings = Settings()
