from typing import List, Optional
from pydantic import BaseModel, ConfigDict, field_validator
from datetime import datetime

from app.schemas.user_schema import UserResponse


class OrmBaseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class GroupCreate(OrmBaseModel):
    title: str
    users: Optional[List[int]] = []

    @field_validator('title')
    def title_validator(cls, v: str) -> str:
        if len(v) > 256:
            raise ValueError('Title must have less than 256 characters.')
        if len(v) < 3:
            raise ValueError('Title must have at least 3 characters.')
        return v


class GroupUpdate(GroupCreate):
    pass


class GroupResponse(OrmBaseModel):
    id: int
    title: str
    created_at: datetime


class GroupWithUsers(GroupResponse):
    users: List[UserResponse]