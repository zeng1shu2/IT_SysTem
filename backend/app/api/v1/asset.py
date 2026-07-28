"""Asset (network device) management routes."""

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_admin, get_current_user, get_db
from app.models.user import User
from app.schemas.asset import AssetCreate, AssetListResponse, AssetResponse, AssetUpdate
from app.services.asset_service import (
    create_asset,
    delete_asset,
    get_asset_by_id,
    get_assets,
    update_asset,
)

router = APIRouter()


@router.get("", response_model=AssetListResponse, summary="获取资产列表")
def list_assets(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=1000),
    keyword: str | None = Query(None),
    device_type: str | None = Query(None, description="设备类型: switch/router/firewall/security/other"),
    status: str | None = Query(None, description="状态: in_use/idle/fault/maintenance/scrap"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get paginated asset list with optional filters."""
    assets, total = get_assets(db, skip=skip, limit=limit, keyword=keyword, device_type=device_type, status=status)
    return AssetListResponse(total=total, items=[AssetResponse.model_validate(a) for a in assets])


@router.get("/{asset_id}", response_model=AssetResponse, summary="获取资产详情")
def get_asset(
    asset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a single asset by ID."""
    asset = get_asset_by_id(db, asset_id)
    return AssetResponse.model_validate(asset)


@router.post("", response_model=AssetResponse, status_code=status.HTTP_201_CREATED, summary="创建资产")
def create(
    body: AssetCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    """Create a new asset. Requires admin."""
    client_ip = request.client.host if request.client else "unknown"
    asset = create_asset(db, body, current_user.username, client_ip)
    return AssetResponse.model_validate(asset)


@router.put("/{asset_id}", response_model=AssetResponse, summary="更新资产")
def update(
    asset_id: int,
    body: AssetUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    """Update an asset. Requires admin."""
    client_ip = request.client.host if request.client else "unknown"
    asset = update_asset(db, asset_id, body, current_user.username, client_ip)
    return AssetResponse.model_validate(asset)


@router.delete("/{asset_id}", summary="删除资产")
def delete(
    asset_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    """Delete an asset. Requires admin."""
    client_ip = request.client.host if request.client else "unknown"
    delete_asset(db, asset_id, current_user.username, client_ip)
    return {"message": "设备已删除"}
