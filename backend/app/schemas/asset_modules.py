"""Schemas for asset sub-modules."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


# ==================== Port Connection ====================

class PortConnectionBase(BaseModel):
    asset_id: int = Field(..., description="关联资产ID")
    asset_name: str | None = Field(None, max_length=100)
    port_count: int = Field(0, ge=0)
    ports_data: list[dict[str, Any]] | None = Field(None, description="物理端口数据列表")
    logical_interfaces: list[dict[str, Any]] | None = Field(None, description="逻辑接口数据列表")
    remark: str | None = None
    extra_data: dict[str, Any] | None = None


class PortConnectionCreate(PortConnectionBase):
    pass


class PortConnectionUpdate(BaseModel):
    asset_id: int | None = None
    asset_name: str | None = None
    port_count: int | None = None
    ports_data: list[dict[str, Any]] | None = None
    logical_interfaces: list[dict[str, Any]] | None = None
    remark: str | None = None
    extra_data: dict[str, Any] | None = None


class PortConnectionResponse(PortConnectionBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PortConnectionListResponse(BaseModel):
    total: int
    items: list[PortConnectionResponse]


# ==================== IP Plan ====================

class IPPlanBase(BaseModel):
    department: str | None = Field(None, max_length=100)
    group_name: str | None = Field(None, max_length=100)
    ip_range: str = Field(..., min_length=1, max_length=200)
    vlan: str | None = Field(None, max_length=50)
    usage_status: str = Field("available", description="available/used/reserved")
    remark: str | None = None
    extra_data: dict[str, Any] | None = None


class IPPlanCreate(IPPlanBase):
    pass


class IPPlanUpdate(BaseModel):
    department: str | None = None
    group_name: str | None = None
    ip_range: str | None = None
    vlan: str | None = None
    usage_status: str | None = None
    remark: str | None = None
    extra_data: dict[str, Any] | None = None


class IPPlanResponse(IPPlanBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class IPPlanListResponse(BaseModel):
    total: int
    items: list[IPPlanResponse]


# ==================== Interconnect IP ====================

class InterconnectIPBase(BaseModel):
    ip_range: str = Field(..., min_length=1, max_length=200)
    source_device_id: int | None = None
    source_device_name: str | None = Field(None, max_length=100)
    source_interface: str | None = Field(None, max_length=200)
    dest_device_id: int | None = None
    dest_device_name: str | None = Field(None, max_length=100)
    dest_interface: str | None = Field(None, max_length=200)
    remark: str | None = None
    extra_data: dict[str, Any] | None = None


class InterconnectIPCreate(InterconnectIPBase):
    pass


class InterconnectIPUpdate(BaseModel):
    ip_range: str | None = None
    source_device_id: int | None = None
    source_device_name: str | None = None
    source_interface: str | None = None
    dest_device_id: int | None = None
    dest_device_name: str | None = None
    dest_interface: str | None = None
    remark: str | None = None
    extra_data: dict[str, Any] | None = None


class InterconnectIPResponse(InterconnectIPBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class InterconnectIPListResponse(BaseModel):
    total: int
    items: list[InterconnectIPResponse]


# ==================== External Broadband ====================

class ExternalBroadbandBase(BaseModel):
    operator: str | None = Field(None, max_length=50)
    line_type: str | None = Field(None, max_length=50)
    ip_address: str | None = Field(None, max_length=45)
    mask: str | None = Field(None, max_length=45)
    gateway: str | None = Field(None, max_length=45)
    dial_account: str | None = Field(None, max_length=100)
    vlan: str | None = Field(None, max_length=50)
    bandwidth: str | None = Field(None, max_length=50)
    ownership: str | None = Field(None, max_length=100)
    remark: str | None = None
    extra_data: dict[str, Any] | None = None


class ExternalBroadbandCreate(ExternalBroadbandBase):
    pass


class ExternalBroadbandUpdate(BaseModel):
    operator: str | None = None
    line_type: str | None = None
    ip_address: str | None = None
    mask: str | None = None
    gateway: str | None = None
    dial_account: str | None = None
    vlan: str | None = None
    bandwidth: str | None = None
    ownership: str | None = None
    remark: str | None = None
    extra_data: dict[str, Any] | None = None


class ExternalBroadbandResponse(ExternalBroadbandBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ExternalBroadbandListResponse(BaseModel):
    total: int
    items: list[ExternalBroadbandResponse]


# ==================== License Management ====================

class LicenseManagementBase(BaseModel):
    vendor: str | None = Field(None, max_length=100)
    device_type: str | None = Field(None, max_length=50)
    asset_id: int | None = None
    device_name: str | None = Field(None, max_length=100)
    license_key: str | None = Field(None, max_length=500)
    activation_date: datetime | None = None
    expiration_date: datetime | None = None
    remark: str | None = None
    extra_data: dict[str, Any] | None = None


class LicenseManagementCreate(LicenseManagementBase):
    pass


class LicenseManagementUpdate(BaseModel):
    vendor: str | None = None
    device_type: str | None = None
    asset_id: int | None = None
    device_name: str | None = None
    license_key: str | None = None
    activation_date: datetime | None = None
    expiration_date: datetime | None = None
    remark: str | None = None
    extra_data: dict[str, Any] | None = None


class LicenseManagementResponse(LicenseManagementBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class LicenseManagementListResponse(BaseModel):
    total: int
    items: list[LicenseManagementResponse]
