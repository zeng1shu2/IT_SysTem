"""Asset (network device) management service."""

from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.asset import Asset
from app.services.audit_service import log_operation
from app.schemas.asset import AssetCreate, AssetUpdate


# Field labels for Chinese error messages
UNIQUE_FIELD_LABELS = {
    "device_name": "设备名称",
    "ip_address": "管理IP",
    "it_asset_code": "IT资产编码",
    "financial_asset_code": "财务资产编码",
}


def _check_unique_constraints(
    db: Session,
    data: dict,
    exclude_asset_id: int | None = None,
) -> None:
    """Raise 409 if any unique field value is already used by another asset."""
    for field, label in UNIQUE_FIELD_LABELS.items():
        value = data.get(field)
        if value is None:
            continue
        query = db.query(Asset).filter(getattr(Asset, field) == value)
        if exclude_asset_id is not None:
            query = query.filter(Asset.id != exclude_asset_id)
        if query.first() is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"{label}「{value}」已存在，请更换",
            )


def get_assets(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    keyword: str | None = None,
    device_type: str | None = None,
    status: str | None = None,
) -> tuple[list[Asset], int]:
    """Get paginated asset list with optional filters."""
    query = db.query(Asset)
    if keyword:
        query = query.filter(
            or_(
                Asset.device_name.ilike(f"%{keyword}%"),
                Asset.ip_address.ilike(f"%{keyword}%"),
                Asset.serial_number.ilike(f"%{keyword}%"),
                Asset.brand.ilike(f"%{keyword}%"),
            )
        )
    if device_type:
        query = query.filter(Asset.device_type == device_type)
    if status:
        query = query.filter(Asset.status == status)

    total = query.count()
    assets = query.order_by(Asset.id.desc()).offset(skip).limit(limit).all()
    return assets, total


def get_asset_by_id(db: Session, asset_id: int) -> Asset:
    """Get an asset by ID."""
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="设备不存在")
    return asset


def create_asset(db: Session, asset_create: AssetCreate, operator: str, operator_ip: str) -> Asset:
    """Create a new asset."""
    _check_unique_constraints(db, asset_create.model_dump())
    asset = Asset(**asset_create.model_dump())
    db.add(asset)
    db.commit()
    db.refresh(asset)

    log_operation(
        db,
        operator=operator,
        operator_ip=operator_ip,
        operation_type="create",
        target_type="asset",
        target_id=asset.id,
        result=True,
        detail=asset_create.model_dump(),
    )
    return asset


def update_asset(db: Session, asset_id: int, asset_update: AssetUpdate, operator: str, operator_ip: str) -> Asset:
    """Update an asset."""
    asset = get_asset_by_id(db, asset_id)
    old_values = {}
    update_data = asset_update.model_dump(exclude_unset=True)

    _check_unique_constraints(db, update_data, exclude_asset_id=asset_id)

    for field, value in update_data.items():
        old_values[field] = getattr(asset, field)
        setattr(asset, field, value)

    db.commit()
    db.refresh(asset)

    log_operation(
        db,
        operator=operator,
        operator_ip=operator_ip,
        operation_type="update",
        target_type="asset",
        target_id=asset.id,
        result=True,
        detail={"old": old_values, "new": update_data},
    )
    return asset


def delete_asset(db: Session, asset_id: int, operator: str, operator_ip: str) -> None:
    """Delete an asset."""
    asset = get_asset_by_id(db, asset_id)
    device_name = asset.device_name
    db.delete(asset)
    db.commit()

    log_operation(
        db,
        operator=operator,
        operator_ip=operator_ip,
        operation_type="delete",
        target_type="asset",
        target_id=asset_id,
        result=True,
        detail={"device_name": device_name},
    )
