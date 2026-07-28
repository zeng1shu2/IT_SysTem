"""Auth routes: login, logout, token refresh, current user info."""

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse, UserInfo
from app.services.auth_service import login as do_login
from app.services.auth_service import logout as do_logout

router = APIRouter()


@router.post("/login", response_model=TokenResponse, summary="用户登录")
def login(request: Request, body: LoginRequest, db: Session = Depends(get_db)):
    """Login with username and password, returns JWT token."""
    client_ip = request.client.host if request.client else "unknown"
    result = do_login(db, body.username, body.password, client_ip)
    return result


@router.post("/logout", summary="用户登出")
def logout(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Logout the current user."""
    client_ip = request.client.host if request.client else "unknown"
    do_logout(db, current_user, client_ip)
    return {"message": "已成功登出"}


@router.get("/me", response_model=UserInfo, summary="获取当前用户信息")
def get_me(current_user: User = Depends(get_current_user)):
    """Get current authenticated user info."""
    return UserInfo(
        id=current_user.id,
        username=current_user.username,
        real_name=current_user.real_name,
        is_admin=current_user.is_admin,
        roles=[r.code for r in current_user.roles],
    )
