"""Audit log service — central logging for all operations."""

import json
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


def log_operation(
    db: Session,
    *,
    operator: str | None = None,
    operator_id: int | None = None,
    operator_ip: str | None = None,
    operation_type: str = "query",
    target_type: str | None = None,
    target_id: str | None = None,
    result: bool = True,
    detail: dict[str, Any] | None = None,
) -> AuditLog:
    """Create an audit log entry. Commits immediately."""
    entry = AuditLog(
        operator=operator,
        operator_id=operator_id,
        operator_ip=operator_ip,
        operation_time=datetime.now(),
        operation_type=operation_type,
        target_type=target_type,
        target_id=str(target_id) if target_id is not None else None,
        result=result,
        detail=json.dumps(detail, ensure_ascii=False, default=str) if detail else None,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry
