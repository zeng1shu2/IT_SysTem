"""Form config schemas."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class FormConfigBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="表单名称")
    code: str = Field(..., min_length=1, max_length=50, description="表单编码")
    description: str | None = Field(None, max_length=500)
    form_schema: str = Field(..., description="表单字段JSON字符串")
    is_active: bool = True


class FormConfigCreate(FormConfigBase):
    pass


class FormConfigUpdate(BaseModel):
    name: str | None = None
    code: str | None = None
    description: str | None = None
    form_schema: str | None = None
    is_active: bool | None = None


class FormConfigResponse(FormConfigBase):
    id: int
    created_by: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class FormConfigListResponse(BaseModel):
    total: int
    items: list[FormConfigResponse]
