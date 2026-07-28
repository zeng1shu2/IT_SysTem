"""User management routes."""

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_admin, get_current_user, get_db
from app.models.user import User
from app.schemas.user import (
    UserCreate,
    UserListResponse,
    UserPasswordReset,
    UserResponse,
    UserUpdate,
)
from app.services.user_service import (
    assign_roles,
    create_user,
    delete_user,
    get_user_by_id,
    get_users,
    reset_password,
    update_user,
)

router = APIRouter()


def _user_to_response(user: User) -> UserResponse:
    """Convert User model to UserResponse with roles."""
    return UserResponse(
        id=user.id,
        username=user.username,
        real_name=user.real_name,
        email=user.email,
        phone=user.phone,
        department=user.department,
        is_active=user.is_active,
        is_admin=user.is_admin,
        last_login_at=user.last_login_at,
        last_login_ip=user.last_login_ip,
        created_at=user.created_at,
        updated_at=user.updated_at,
        roles=[r.code for r in user.roles],
    )


@router.get("", response_model=UserListResponse, summary="获取用户列表")
def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    keyword: str | None = Query(None),
    is_active: bool | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get paginated user list. Requires login."""
    users, total = get_users(db, skip=skip, limit=limit, keyword=keyword, is_active=is_active)
    return UserListResponse(total=total, items=[_user_to_response(u) for u in users])


@router.get("/{user_id}", response_model=UserResponse, summary="获取用户详情")
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a single user by ID."""
    user = get_user_by_id(db, user_id)
    return _user_to_response(user)


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED, summary="创建用户")
def create(
    body: UserCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    """Create a new user. Requires admin."""
    client_ip = request.client.host if request.client else "unknown"
    user = create_user(db, body, current_user.username, client_ip)
    return _user_to_response(user)


@router.put("/{user_id}", response_model=UserResponse, summary="更新用户")
def update(
    user_id: int,
    body: UserUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    """Update a user. Requires admin."""
    client_ip = request.client.host if request.client else "unknown"
    user = update_user(db, user_id, body, current_user.username, client_ip)
    return _user_to_response(user)


@router.delete("/{user_id}", summary="删除用户")
def delete(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    """Delete a user. Requires admin."""
    client_ip = request.client.host if request.client else "unknown"
    delete_user(db, user_id, current_user.username, client_ip)
    return {"message": "用户已删除"}


@router.post("/{user_id}/reset-password", summary="重置密码")
def reset_pwd(
    user_id: int,
    body: UserPasswordReset,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    """Reset a user's password. Requires admin."""
    client_ip = request.client.host if request.client else "unknown"
    reset_password(db, user_id, body.new_password, current_user.username, client_ip)
    return {"message": "密码已重置"}


@router.post("/{user_id}/roles", response_model=UserResponse, summary="分配角色")
def assign_user_roles(
    user_id: int,
    role_ids: list[int],
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    """Assign roles to a user. Requires admin."""
    client_ip = request.client.host if request.client else "unknown"
    user = assign_roles(db, user_id, role_ids, current_user.username, client_ip)
    return _user_to_response(user)
