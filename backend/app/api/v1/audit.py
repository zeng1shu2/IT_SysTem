"""Audit log routes."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_current_admin, get_db
from app.models.audit_log import AuditLog
from app.models.user import User
from app.schemas.audit import AuditLogListResponse, AuditLogResponse

router = APIRouter()


@router.get("", response_model=AuditLogListResponse, summary="查询审计日志")
def list_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    operator: str | None = Query(None),
    operation_type: str | None = Query(None),
    target_type: str | None = Query(None),
    result: bool | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    """Query audit logs with filters. Requires admin."""
    query = db.query(AuditLog)

    if operator:
        query = query.filter(AuditLog.operator.ilike(f"%{operator}%"))
    if operation_type:
        query = query.filter(AuditLog.operation_type == operation_type)
    if target_type:
        query = query.filter(AuditLog.target_type == target_type)
    if result is not None:
        query = query.filter(AuditLog.result == result)

    total = query.count()
    # 默认按操作时间倒序展示（最新操作在前），不开放正倒序切换
    logs = query.order_by(AuditLog.operation_time.desc()).offset(skip).limit(limit).all()

    return AuditLogListResponse(
        total=total,
        items=[AuditLogResponse.model_validate(log) for log in logs],
    )
