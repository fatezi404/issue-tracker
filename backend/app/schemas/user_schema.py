from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.core.config import UserRole


def validate_password(v: str) -> str:
    if (
        v is None
        or len(v) < 8
        or not any(c.isupper() for c in v)
        or not any(c.islower() for c in v)
        or not any(c.isdigit() for c in v)
    ):
        raise ValueError('Password must have at least 8 digits, both upper and lowercase characters, one digit.')
    return v


class OrmBaseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class UserBase(OrmBaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str

    @field_validator('password')
    def password_validator(cls, v: str) -> str:
        return validate_password(v)


class UserUpdate(OrmBaseModel):
    email: EmailStr | None = None
    password: str | None = None
    is_active: bool | None = None
    role: UserRole | None = None

    @field_validator('password')
    def password_validator(cls, v: str) -> str:
        return validate_password(v)


class UserResponse(UserBase):
    id: int
    created_at: datetime
    is_active: bool = Field(default=True)
    role: UserRole
