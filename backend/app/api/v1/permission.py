"""Permission management routes."""

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.permission import (
    PermissionOption,
    PermissionRequestCreate,
    PermissionRequestListResponse,
    PermissionRequestResponse,
)
from app.services.permission_service import (
    create_permission_request,
    get_permission_catalog,
    get_permission_requests,
)

router = APIRouter()


@router.get("/catalog", response_model=list[PermissionOption], summary="获取权限目录")
def catalog(
    current_user: User = Depends(get_current_user),
):
    """Get the predefined permission catalog."""
    return [PermissionOption(**p) for p in get_permission_catalog()]


@router.get("", response_model=PermissionRequestListResponse, summary="获取权限申请列表")
def list_requests(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    user_id: int | None = Query(None),
    status: str | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get paginated permission request list."""
    items, total = get_permission_requests(db, skip=skip, limit=limit, user_id=user_id, status_filter=status)

    result_items = []
    for item in items:
        result_items.append(
            PermissionRequestResponse(
                id=item.id,
                user_id=item.user_id,
                username=item.user.username if item.user else None,
                permission_code=item.permission_code,
                reason=item.reason,
                status=item.status,
                approved_at=item.approved_at,
                approved_by=item.approved_by,
                auto_rule=item.auto_rule,
                created_at=item.created_at,
                updated_at=item.updated_at,
            )
        )
    return PermissionRequestListResponse(total=total, items=result_items)


@router.post("/apply", response_model=PermissionRequestResponse, status_code=status.HTTP_201_CREATED, summary="申请权限")
def apply(
    body: PermissionRequestCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Submit a permission request (auto-approved/rejected based on rules)."""
    client_ip = request.client.host if request.client else "unknown"
    record = create_permission_request(db, current_user, body, client_ip)
    return PermissionRequestResponse(
        id=record.id,
        user_id=record.user_id,
        username=current_user.username,
        permission_code=record.permission_code,
        reason=record.reason,
        status=record.status,
        approved_at=record.approved_at,
        approved_by=record.approved_by,
        auto_rule=record.auto_rule,
        created_at=record.created_at,
        updated_at=record.updated_at,
    )
