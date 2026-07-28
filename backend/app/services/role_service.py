"""Role management service."""

from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.role import Role, role_permissions
from app.services.audit_service import log_operation
from app.schemas.role import RoleCreate, RoleUpdate


def get_roles(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    keyword: str | None = None,
) -> tuple[list[Role], int]:
    """Get paginated role list."""
    query = db.query(Role)
    if keyword:
        query = query.filter(
            or_(
                Role.name.ilike(f"%{keyword}%"),
                Role.code.ilike(f"%{keyword}%"),
            )
        )
    total = query.count()
    roles = query.order_by(Role.id.desc()).offset(skip).limit(limit).all()
    return roles, total


def get_role_by_id(db: Session, role_id: int) -> Role:
    """Get a role by ID."""
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="角色不存在")
    return role


def get_role_permissions(db: Session, role_id: int) -> list[str]:
    """Get permission codes for a role."""
    rows = db.execute(
        role_permissions.select().where(role_permissions.c.role_id == role_id)
    ).fetchall()
    return [row.permission for row in rows]


def create_role(db: Session, role_create: RoleCreate, operator: str, operator_ip: str) -> Role:
    """Create a new role."""
    existing = db.query(Role).filter(Role.code == role_create.code).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="角色编码已存在")

    role = Role(
        name=role_create.name,
        code=role_create.code,
        description=role_create.description,
    )
    db.add(role)
    db.commit()
    db.refresh(role)

    # Insert permissions
    if role_create.permissions:
        for perm in role_create.permissions:
            db.execute(role_permissions.insert().values(role_id=role.id, permission=perm))
        db.commit()

    log_operation(
        db,
        operator=operator,
        operator_ip=operator_ip,
        operation_type="create",
        target_type="role",
        target_id=role.id,
        result=True,
        detail={"name": role.name, "code": role.code, "permissions": role_create.permissions},
    )
    return role


def update_role(db: Session, role_id: int, role_update: RoleUpdate, operator: str, operator_ip: str) -> Role:
    """Update a role."""
    role = get_role_by_id(db, role_id)
    update_data = role_update.model_dump(exclude_unset=True)

    permissions = update_data.pop("permissions", None)

    for field, value in update_data.items():
        setattr(role, field, value)

    # Update permissions if provided
    if permissions is not None:
        db.execute(role_permissions.delete().where(role_permissions.c.role_id == role_id))
        for perm in permissions:
            db.execute(role_permissions.insert().values(role_id=role_id, permission=perm))

    db.commit()
    db.refresh(role)

    log_operation(
        db,
        operator=operator,
        operator_ip=operator_ip,
        operation_type="update",
        target_type="role",
        target_id=role.id,
        result=True,
        detail={"updated_fields": list(update_data.keys()), "permissions_updated": permissions is not None},
    )
    return role


def delete_role(db: Session, role_id: int, operator: str, operator_ip: str) -> None:
    """Delete a role."""
    role = get_role_by_id(db, role_id)
    role_name = role.name
    db.execute(role_permissions.delete().where(role_permissions.c.role_id == role_id))
    db.delete(role)
    db.commit()

    log_operation(
        db,
        operator=operator,
        operator_ip=operator_ip,
        operation_type="delete",
        target_type="role",
        target_id=role_id,
        result=True,
        detail={"name": role_name},
    )
