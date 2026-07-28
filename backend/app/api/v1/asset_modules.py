"""API routes for asset sub-modules: PortConnection, IPPlan, InterconnectIP, ExternalBroadband, LicenseManagement."""

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_admin, get_current_user, get_db
from app.models.user import User
from app.schemas.asset_modules import (
    ExternalBroadbandCreate,
    ExternalBroadbandListResponse,
    ExternalBroadbandResponse,
    ExternalBroadbandUpdate,
    InterconnectIPCreate,
    InterconnectIPListResponse,
    InterconnectIPResponse,
    InterconnectIPUpdate,
    IPPlanCreate,
    IPPlanListResponse,
    IPPlanResponse,
    IPPlanUpdate,
    LicenseManagementCreate,
    LicenseManagementListResponse,
    LicenseManagementResponse,
    LicenseManagementUpdate,
    PortConnectionCreate,
    PortConnectionListResponse,
    PortConnectionResponse,
    PortConnectionUpdate,
)
from app.services.asset_modules import (
    external_broadband_service,
    interconnect_ip_service,
    ip_plan_service,
    license_service,
    port_connection_service,
)

router = APIRouter()


def _build_router(service, create_schema, update_schema, response_schema, list_response_schema, prefix, tag):
    """Build a sub-router for a generic CRUD module."""
    sub = APIRouter()

    @sub.get("", response_model=list_response_schema, summary=f"获取{tag}列表")
    def list_items(
        skip: int = Query(0, ge=0),
        limit: int = Query(20, ge=1, le=1000),
        keyword: str | None = Query(None),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ):
        items, total = service.list(db, skip=skip, limit=limit, keyword=keyword)
        return list_response_schema(total=total, items=[response_schema.model_validate(i) for i in items])

    @sub.get("/{item_id}", response_model=response_schema, summary=f"获取{tag}详情")
    def get_item(
        item_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ):
        return response_schema.model_validate(service.get_by_id(db, item_id))

    @sub.post("", response_model=response_schema, status_code=status.HTTP_201_CREATED, summary=f"创建{tag}")
    def create_item(
        body: create_schema,
        request: Request,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_admin),
    ):
        client_ip = request.client.host if request.client else "unknown"
        return response_schema.model_validate(service.create(db, body, current_user.username, client_ip))

    @sub.put("/{item_id}", response_model=response_schema, summary=f"更新{tag}")
    def update_item(
        item_id: int,
        body: update_schema,
        request: Request,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_admin),
    ):
        client_ip = request.client.host if request.client else "unknown"
        return response_schema.model_validate(service.update(db, item_id, body, current_user.username, client_ip))

    @sub.delete("/{item_id}", summary=f"删除{tag}")
    def delete_item(
        item_id: int,
        request: Request,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_admin),
    ):
        client_ip = request.client.host if request.client else "unknown"
        service.delete(db, item_id, current_user.username, client_ip)
        return {"message": "删除成功"}

    return sub


# Register sub-routers
router.include_router(
    _build_router(port_connection_service, PortConnectionCreate, PortConnectionUpdate,
                  PortConnectionResponse, PortConnectionListResponse, "port-connections", "端口互联"),
    prefix="/port-connections", tags=["端口互联"],
)


@router.get("/port-connections/by-asset/{asset_id}", response_model=PortConnectionResponse, summary="按资产ID获取端口互联")
def get_port_connection_by_asset(
    asset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """根据资产ID查询该设备的端口互联配置，用于其他页面级联选择接口。"""
    items, _ = port_connection_service.list(db, skip=0, limit=1, asset_id=asset_id)
    if not items:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"该设备暂无端口互联配置: asset_id={asset_id}")
    return PortConnectionResponse.model_validate(items[0])


router.include_router(
    _build_router(ip_plan_service, IPPlanCreate, IPPlanUpdate,
                  IPPlanResponse, IPPlanListResponse, "ip-plans", "IP地址规划"),
    prefix="/ip-plans", tags=["IP地址规划"],
)
router.include_router(
    _build_router(interconnect_ip_service, InterconnectIPCreate, InterconnectIPUpdate,
                  InterconnectIPResponse, InterconnectIPListResponse, "interconnect-ips", "互联IP"),
    prefix="/interconnect-ips", tags=["互联IP"],
)
router.include_router(
    _build_router(external_broadband_service, ExternalBroadbandCreate, ExternalBroadbandUpdate,
                  ExternalBroadbandResponse, ExternalBroadbandListResponse, "external-broadbands", "外线宽带"),
    prefix="/external-broadbands", tags=["外线宽带"],
)
router.include_router(
    _build_router(license_service, LicenseManagementCreate, LicenseManagementUpdate,
                  LicenseManagementResponse, LicenseManagementListResponse, "licenses", "授权管理"),
    prefix="/licenses", tags=["授权管理"],
)
