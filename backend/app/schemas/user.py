"""User schemas."""

from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class UserBase(BaseModel):
    username: str = Field(..., min_length=2, max_length=50)
    real_name: str | None = Field(None, max_length=50)
    email: str | None = Field(None, max_length=100)
    phone: str | None = Field(None, max_length=20)
    department: str | None = Field(None, max_length=100)
    is_active: bool = True
    is_admin: bool = False


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=128)


class UserUpdate(BaseModel):
    real_name: str | None = None
    email: str | None = None
    phone: str | None = None
    department: str | None = None
    is_active: bool | None = None
    is_admin: bool | None = None


class UserPasswordReset(BaseModel):
    new_password: str = Field(..., min_length=6, max_length=128)


class UserResponse(UserBase):
    id: int
    last_login_at: datetime | None = None
    last_login_ip: str | None = None
    created_at: datetime
    updated_at: datetime
    roles: list[str] = []

    model_config = {"from_attributes": True}


class UserListResponse(BaseModel):
    total: int
    items: list[UserResponse]
