"""Asset schemas."""

from datetime import datetime

from pydantic import BaseModel, Field


class AssetBase(BaseModel):
    device_type: str = Field(..., description="设备类型: switch/router/firewall/security/other")
    device_name: str = Field(..., min_length=1, max_length=100)
    brand: str | None = Field(None, max_length=50)
    model: str | None = Field(None, max_length=100)
    serial_number: str | None = Field(None, max_length=100)
    ip_address: str | None = Field(None, max_length=45)
    mac_address: str | None = Field(None, max_length=20)
    location: str | None = Field(None, max_length=200)
    status: str = Field("in_use", description="状态: in_use/idle/fault/maintenance/scrap")
    purchase_date: datetime | None = None
    warranty_expire: datetime | None = None
    remark: str | None = None


class AssetCreate(AssetBase):
    pass


class AssetUpdate(BaseModel):
    device_type: str | None = None
    device_name: str | None = None
    brand: str | None = None
    model: str | None = None
    serial_number: str | None = None
    ip_address: str | None = None
    mac_address: str | None = None
    location: str | None = None
    status: str | None = None
    purchase_date: datetime | None = None
    warranty_expire: datetime | None = None
    remark: str | None = None


class AssetResponse(AssetBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AssetListResponse(BaseModel):
    total: int
    items: list[AssetResponse]
