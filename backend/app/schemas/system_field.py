"""Schemas for the 字段管理 (SystemField) module."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class SystemFieldBase(BaseModel):
    field_code: str = Field(..., max_length=50, description="字段编码")
    field_name: str = Field(..., max_length=50, description="字段中文名")
    value: str = Field(..., max_length=100, description="选项值")
    label: str = Field(..., max_length=100, description="选项显示名")
    icon: str | None = Field(None, max_length=255)
    emoji: str | None = Field(None, max_length=20)
    sort: int = Field(0, ge=0)
    is_active: int = Field(1, description="是否启用 1/0")
    parent_value: str | None = Field(None, max_length=100, description="父级value(设备类型大类)")
    level: int = Field(0, ge=0, description="层级 0=顶层 1=子级")
    description: str | None = Field(None, max_length=255)


class SystemFieldCreate(SystemFieldBase):
    pass


class SystemFieldUpdate(BaseModel):
    field_code: str | None = None
    field_name: str | None = None
    value: str | None = None
    label: str | None = None
    icon: str | None = None
    emoji: str | None = None
    sort: int | None = None
    is_active: int | None = None
    parent_value: str | None = None
    level: int | None = None
    description: str | None = None


class SystemFieldResponse(SystemFieldBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SystemFieldListResponse(BaseModel):
    total: int
    items: list[SystemFieldResponse]
