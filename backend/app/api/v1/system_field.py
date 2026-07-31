"""API routes for 字段管理 (SystemField): managed option lists + dynamic options."""

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_admin, get_current_user, get_db
from app.models.user import User
from app.schemas.system_field import (
    SystemFieldCreate,
    SystemFieldListResponse,
    SystemFieldResponse,
    SystemFieldUpdate,
)
from app.services.system_field import (
    build_options,
    delete_by_id,
    system_field_service,
)

router = APIRouter()


@router.get("/options/{code}", summary="获取字段选项(动态加载)")
def get_options(
    code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return consumer-ready options for a managed field.

    - Flat fields: [{"label","value","icon"?,"emoji"?,"sort"}]
    - device_type: two-level cascader tree [{"label","options":[...]}]
    """
    return build_options(db, code)


@router.get("", response_model=SystemFieldListResponse, summary="获取字段选项列表")
def list_items(
    field_code: str | None = Query(None, description="按字段编码过滤: organization/brand/device_type/..."),
    keyword: str | None = Query(None),
    order: str = Query("desc", description="ID排序: desc(倒序) / asc(正序)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List system-field rows, optionally filtered by field_code."""
    items, total = system_field_service.list(db, skip=0, limit=2000, keyword=keyword, order=order, field_code=field_code)
    return SystemFieldListResponse(total=total, items=[SystemFieldResponse.model_validate(i) for i in items])


@router.get("/{item_id}", response_model=SystemFieldResponse, summary="获取字段选项详情")
def get_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return SystemFieldResponse.model_validate(system_field_service.get_by_id(db, item_id))


@router.post("", response_model=SystemFieldResponse, status_code=status.HTTP_201_CREATED, summary="创建字段选项")
def create_item(
    body: SystemFieldCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    client_ip = request.client.host if request.client else "unknown"
    return SystemFieldResponse.model_validate(system_field_service.create(db, body, current_user.username, client_ip))


@router.put("/{item_id}", response_model=SystemFieldResponse, summary="更新字段选项")
def update_item(
    item_id: int,
    body: SystemFieldUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    client_ip = request.client.host if request.client else "unknown"
    return SystemFieldResponse.model_validate(system_field_service.update(db, item_id, body, current_user.username, client_ip))


@router.delete("/{item_id}", summary="删除字段选项")
def delete_item(
    item_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    client_ip = request.client.host if request.client else "unknown"
    delete_by_id(db, item_id, current_user.username, client_ip)
    return {"message": "删除成功"}
