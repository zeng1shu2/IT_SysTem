"""Auth schemas."""

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=50, description="用户名")
    password: str = Field(..., min_length=1, max_length=128, description="密码")


class TokenResponse(BaseModel):
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token类型")
    user: "UserInfo" = Field(..., description="用户信息")


class UserInfo(BaseModel):
    id: int
    username: str
    real_name: str | None = None
    is_admin: bool
    roles: list[str] = []

    model_config = {"from_attributes": True}


TokenResponse.model_rebuild()
