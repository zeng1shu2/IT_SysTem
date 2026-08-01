"""Role management routes."""

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_admin, get_current_user, get_db
from app.models.user import User
from app.schemas.role import RoleCreate, RoleListResponse, RoleResponse, RoleUpdate
from app.services.role_service import (
    create_role,
    delete_role,
    get_role_by_id,
    get_role_permissions,
    get_roles,
    update_role,
)

router = APIRouter()


def _role_to_response(role, db: Session) -> RoleResponse:
    """Convert Role model to RoleResponse with permissions."""
    permissions = get_role_permissions(db, role.id)
    return RoleResponse(
        id=role.id,
        name=role.name,
        code=role.code,
        description=role.description,
        permissions=permissions,
        created_at=role.created_at,
        updated_at=role.updated_at,
    )


@router.get("", response_model=RoleListResponse, summary="获取角色列表")
def list_roles(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    keyword: str | None = Query(None),
    order: str = Query("asc", description="ID排序: asc(正序) / desc(倒序)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get paginated role list."""
    roles, total = get_roles(db, skip=skip, limit=limit, keyword=keyword, order=order)
    return RoleListResponse(total=total, items=[_role_to_response(r, db) for r in roles])


@router.get("/{role_id}", response_model=RoleResponse, summary="获取角色详情")
def get_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a single role by ID."""
    role = get_role_by_id(db, role_id)
    return _role_to_response(role, db)


@router.post("", response_model=RoleResponse, status_code=status.HTTP_201_CREATED, summary="创建角色")
def create(
    body: RoleCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    """Create a new role. Requires admin."""
    client_ip = request.client.host if request.client else "unknown"
    role = create_role(db, body, current_user.username, client_ip)
    return _role_to_response(role, db)


@router.put("/{role_id}", response_model=RoleResponse, summary="更新角色")
def update(
    role_id: int,
    body: RoleUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    """Update a role. Requires admin."""
    client_ip = request.client.host if request.client else "unknown"
    role = update_role(db, role_id, body, current_user.username, client_ip)
    return _role_to_response(role, db)


@router.delete("/{role_id}", summary="删除角色")
def delete(
    role_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    """Delete a role. Requires admin."""
    client_ip = request.client.host if request.client else "unknown"
    delete_role(db, role_id, current_user.username, client_ip)
    return {"message": "角色已删除"}
