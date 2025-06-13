from pydantic import BaseModel, ConfigDict

from app.schemas.user_schema import UserResponse


class OrmBaseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

class Token(OrmBaseModel):
    access_token: str
    token_type: str
    refresh_token: str
    user: UserResponse

class TokenResponse(OrmBaseModel):
    access_token: str
    token_type: str

class RefreshToken(OrmBaseModel):
    refresh_token: str
