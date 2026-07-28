"""Permission schemas."""

from datetime import datetime

from pydantic import BaseModel, Field


class PermissionRequestCreate(BaseModel):
    permission_code: str = Field(..., min_length=1, max_length=100, description="申请的权限编码")
    reason: str | None = Field(None, max_length=500, description="申请理由")


class PermissionRequestResponse(BaseModel):
    id: int
    user_id: int
    username: str | None = None
    permission_code: str
    reason: str | None = None
    status: str
    approved_at: datetime | None = None
    approved_by: str
    auto_rule: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PermissionRequestListResponse(BaseModel):
    total: int
    items: list[PermissionRequestResponse]


class PermissionOption(BaseModel):
    """Available permission for selection."""
    code: str
    name: str
    description: str
