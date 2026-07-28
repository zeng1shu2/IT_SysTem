"""Asset schemas."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator


class AssetBase(BaseModel):
    device_type: str = Field(..., description="设备类型: switch/router/firewall/security/other")
    device_name: str = Field(..., min_length=1, max_length=100)
    brand: str | None = Field(None, max_length=50)
    model: str | None = Field(None, max_length=100)
    serial_number: str | None = Field(None, max_length=100)
    it_asset_code: str | None = Field(None, max_length=100, description="IT资产编码")
    financial_asset_code: str | None = Field(None, max_length=100, description="财务资产编码")
    ip_address: str | None = Field(None, max_length=45)
    mac_address: str | None = Field(None, max_length=20)
    location: str | None = Field(None, max_length=200)
    status: str = Field("in_use", description="状态: in_use/idle/fault/maintenance/scrap")
    purchase_date: datetime | None = None
    warranty_expire: datetime | None = None
    remark: str | None = None
    extra_data: dict[str, Any] | None = Field(None, description="自定义扩展字段(来自表单设计器)")

    @field_validator("device_type", mode="before")
    @classmethod
    def normalize_device_type(cls, v):
        """Convert None/empty to 'other' to prevent 422 when frontend sends null."""
        if v is None or v == "":
            return "other"
        return v

    @field_validator("status", mode="before")
    @classmethod
    def normalize_status(cls, v):
        """Convert None/empty to 'in_use' to prevent 422 when frontend sends null."""
        if v is None or v == "":
            return "in_use"
        return v

    @field_validator("ip_address", "it_asset_code", "financial_asset_code", mode="before")
    @classmethod
    def normalize_empty_to_none(cls, v):
        """Treat empty strings as null so uniqueness constraints ignore unset values."""
        if v == "":
            return None
        return v


class AssetCreate(AssetBase):
    pass


class AssetUpdate(BaseModel):
    device_type: str | None = None
    device_name: str | None = None
    brand: str | None = None
    model: str | None = None
    serial_number: str | None = None
    it_asset_code: str | None = None
    financial_asset_code: str | None = None
    ip_address: str | None = None
    mac_address: str | None = None
    location: str | None = None
    status: str | None = None
    purchase_date: datetime | None = None
    warranty_expire: datetime | None = None
    remark: str | None = None
    extra_data: dict[str, Any] | None = None


class AssetResponse(AssetBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AssetListResponse(BaseModel):
    total: int
    items: list[AssetResponse]
