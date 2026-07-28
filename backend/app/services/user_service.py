"""User management service."""

from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.models.user import User
from app.models.role import Role
from app.services.audit_service import log_operation
from app.schemas.user import UserCreate, UserUpdate


def get_users(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    keyword: str | None = None,
    is_active: bool | None = None,
) -> tuple[list[User], int]:
    """Get paginated user list with optional filters."""
    query = db.query(User)
    if keyword:
        query = query.filter(
            or_(
                User.username.ilike(f"%{keyword}%"),
                User.real_name.ilike(f"%{keyword}%"),
                User.email.ilike(f"%{keyword}%"),
            )
        )
    if is_active is not None:
        query = query.filter(User.is_active == is_active)

    total = query.count()
    users = query.order_by(User.id.desc()).offset(skip).limit(limit).all()
    return users, total


def get_user_by_id(db: Session, user_id: int) -> User:
    """Get a user by ID."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    return user


def get_user_by_username(db: Session, username: str) -> User | None:
    """Get a user by username."""
    return db.query(User).filter(User.username == username).first()


def create_user(db: Session, user_create: UserCreate, operator: str, operator_ip: str) -> User:
    """Create a new user."""
    if get_user_by_username(db, user_create.username):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户名已存在")

    user = User(
        username=user_create.username,
        password_hash=get_password_hash(user_create.password),
        real_name=user_create.real_name,
        email=user_create.email,
        phone=user_create.phone,
        department=user_create.department,
        is_active=user_create.is_active,
        is_admin=user_create.is_admin,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    log_operation(
        db,
        operator=operator,
        operator_ip=operator_ip,
        operation_type="create",
        target_type="user",
        target_id=user.id,
        result=True,
        detail={"username": user.username, "real_name": user.real_name},
    )
    return user


def update_user(db: Session, user_id: int, user_update: UserUpdate, operator: str, operator_ip: str) -> User:
    """Update a user."""
    user = get_user_by_id(db, user_id)
    old_values = {}
    update_data = user_update.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        old_values[field] = getattr(user, field)
        setattr(user, field, value)

    db.commit()
    db.refresh(user)

    log_operation(
        db,
        operator=operator,
        operator_ip=operator_ip,
        operation_type="update",
        target_type="user",
        target_id=user.id,
        result=True,
        detail={"old": old_values, "new": update_data},
    )
    return user


def delete_user(db: Session, user_id: int, operator: str, operator_ip: str) -> None:
    """Delete a user."""
    user = get_user_by_id(db, user_id)
    username = user.username
    db.delete(user)
    db.commit()

    log_operation(
        db,
        operator=operator,
        operator_ip=operator_ip,
        operation_type="delete",
        target_type="user",
        target_id=user_id,
        result=True,
        detail={"username": username},
    )


def reset_password(db: Session, user_id: int, new_password: str, operator: str, operator_ip: str) -> None:
    """Reset a user's password."""
    user = get_user_by_id(db, user_id)
    user.password_hash = get_password_hash(new_password)
    db.commit()

    log_operation(
        db,
        operator=operator,
        operator_ip=operator_ip,
        operation_type="update",
        target_type="user",
        target_id=user.id,
        result=True,
        detail={"action": "password_reset"},
    )


def assign_roles(db: Session, user_id: int, role_ids: list[int], operator: str, operator_ip: str) -> User:
    """Assign roles to a user."""
    user = get_user_by_id(db, user_id)
    roles = db.query(Role).filter(Role.id.in_(role_ids)).all() if role_ids else []
    user.roles = roles
    db.commit()
    db.refresh(user)

    log_operation(
        db,
        operator=operator,
        operator_ip=operator_ip,
        operation_type="update",
        target_type="user",
        target_id=user.id,
        result=True,
        detail={"action": "assign_roles", "role_ids": role_ids},
    )
    return user
