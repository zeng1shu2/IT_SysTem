"""Audit log schemas."""

from datetime import datetime

from pydantic import BaseModel


class AuditLogResponse(BaseModel):
    id: int
    operator: str | None = None
    operator_id: int | None = None
    operator_ip: str | None = None
    operation_time: datetime
    operation_type: str
    target_type: str | None = None
    target_id: str | None = None
    result: bool
    detail: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class AuditLogListResponse(BaseModel):
    total: int
    items: list[AuditLogResponse]
