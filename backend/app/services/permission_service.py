"""Permission service — auto-approval mode."""

from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.permission import PermissionRequest
from app.models.user import User
from app.services.audit_service import log_operation
from app.schemas.permission import PermissionRequestCreate


# Predefined permission catalog (can be extended)
PERMISSION_CATALOG = [
    {"code": "asset:read", "name": "查看资产", "description": "查看网络设备资产信息"},
    {"code": "asset:write", "name": "管理资产", "description": "增删改网络设备资产信息"},
    {"code": "user:read", "name": "查看用户", "description": "查看用户列表"},
    {"code": "user:write", "name": "管理用户", "description": "增删改用户信息"},
    {"code": "role:read", "name": "查看角色", "description": "查看角色列表"},
    {"code": "role:write", "name": "管理角色", "description": "增删改角色信息"},
    {"code": "audit:read", "name": "查看审计", "description": "查看审计日志"},
    {"code": "permission:apply", "name": "申请权限", "description": "提交权限申请"},
]

# Auto-approval rules: which permissions are auto-approved
AUTO_APPROVE_RULES = {
    "asset:read": "auto_read_rule",
    "user:read": "auto_read_rule",
    "role:read": "auto_read_rule",
    "audit:read": "auto_read_rule",
    "permission:apply": "auto_apply_rule",
}
# Write permissions require admin (auto-rejected for non-admin)
AUTO_REJECT_RULES = {
    "asset:write": "admin_only_rule",
    "user:write": "admin_only_rule",
    "role:write": "admin_only_rule",
}


def get_permission_catalog() -> list[dict]:
    """Get the predefined permission catalog."""
    return PERMISSION_CATALOG


def get_permission_requests(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    user_id: int | None = None,
    status_filter: str | None = None,
) -> tuple[list[PermissionRequest], int]:
    """Get paginated permission request list."""
    query = db.query(PermissionRequest)
    if user_id:
        query = query.filter(PermissionRequest.user_id == user_id)
    if status_filter:
        query = query.filter(PermissionRequest.status == status_filter)

    total = query.count()
    items = query.order_by(PermissionRequest.id.desc()).offset(skip).limit(limit).all()
    return items, total


def create_permission_request(
    db: Session,
    user: User,
    req: PermissionRequestCreate,
    client_ip: str,
) -> PermissionRequest:
    """Create a permission request with auto-approval logic."""
    # Validate permission code
    valid_codes = [p["code"] for p in PERMISSION_CATALOG]
    if req.permission_code not in valid_codes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"无效的权限编码，可选: {', '.join(valid_codes)}",
        )

    # Auto-approval logic
    perm_code = req.permission_code
    if perm_code in AUTO_REJECT_RULES and not user.is_admin:
        # Auto-reject write permissions for non-admins
        status_val = "rejected"
        auto_rule = AUTO_REJECT_RULES[perm_code]
        approved_at = datetime.now()
    elif perm_code in AUTO_APPROVE_RULES:
        # Auto-approve read permissions
        status_val = "approved"
        auto_rule = AUTO_APPROVE_RULES[perm_code]
        approved_at = datetime.now()
    else:
        # Default: auto-approve
        status_val = "approved"
        auto_rule = "default_auto_rule"
        approved_at = datetime.now()

    record = PermissionRequest(
        user_id=user.id,
        permission_code=perm_code,
        reason=req.reason,
        status=status_val,
        approved_at=approved_at,
        approved_by="system",
        auto_rule=auto_rule,
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    log_operation(
        db,
        operator=user.username,
        operator_id=user.id,
        operator_ip=client_ip,
        operation_type="approve",
        target_type="permission",
        target_id=record.id,
        result=True,
        detail={
            "permission_code": perm_code,
            "status": status_val,
            "auto_rule": auto_rule,
            "reason": req.reason,
        },
    )
    return record
