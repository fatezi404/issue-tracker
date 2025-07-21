from pydantic import BaseModel, ConfigDict, field_validator
from datetime import datetime


class OrmBaseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class TaskCreate(OrmBaseModel):
    title: str
    description: str | None = None
    status: str
    priority: str
    assignee_id: int | None = None
    group_id: int

    @field_validator('title')
    def title_validator(cls, v: str) -> str:
        if len(v) > 256:
            raise ValueError('Title must have less than 256 characters.')
        if len(v) < 3:
            raise ValueError('Title must have at least 3 characters.')
        return v

    @field_validator('description')
    def description_validator(cls, v: str) -> str:
        if len(v) > 500:
            raise ValueError('Description must have less than 500 characters.')
        return v


class TaskUpdate(OrmBaseModel):
    title: str | None = None
    description: str | None = None
    status: str | None = None
    priority: str | None = None
    is_done: bool | None = None

    @field_validator('title')
    def title_validator(cls, v: str) -> str:
        if len(v) > 256:
            raise ValueError('Title must have less than 256 characters.')
        if len(v) < 3:
            raise ValueError('Title must have at least 3 characters.')
        return v

    @field_validator('description')
    def description_validator(cls, v: str) -> str:
        if len(v) > 500:
            raise ValueError('Description must have less than 500 characters.')
        return v


class TaskResponse(OrmBaseModel):
    id: int
    created_at: datetime
    title: str
    reporter_id: int
    group_id: int
