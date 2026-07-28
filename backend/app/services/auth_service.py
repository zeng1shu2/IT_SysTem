"""Authentication service."""

from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.user import User
from app.services.audit_service import log_operation


def authenticate_user(db: Session, username: str, password: str) -> User:
    """Authenticate a user by username and password."""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )
    if not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用，请联系管理员",
        )
    return user


def login(db: Session, username: str, password: str, client_ip: str) -> dict:
    """Login a user and return token + user info."""
    user = authenticate_user(db, username, password)

    # Update login info
    user.last_login_at = datetime.now()
    user.last_login_ip = client_ip
    db.commit()

    # Generate token
    token = create_access_token(
        subject=user.id,
        extra_data={"username": user.username, "is_admin": user.is_admin},
    )

    # Audit log
    log_operation(
        db,
        operator=user.username,
        operator_id=user.id,
        operator_ip=client_ip,
        operation_type="login",
        target_type="system",
        result=True,
        detail={"username": username},
    )

    roles = [r.code for r in user.roles]

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "real_name": user.real_name,
            "is_admin": user.is_admin,
            "roles": roles,
        },
    }


def logout(db: Session, user: User, client_ip: str) -> None:
    """Logout a user — just log it."""
    log_operation(
        db,
        operator=user.username,
        operator_id=user.id,
        operator_ip=client_ip,
        operation_type="logout",
        target_type="system",
        result=True,
    )
