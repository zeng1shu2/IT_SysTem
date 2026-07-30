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
    IPAllocationCreate,
    IPAllocationListResponse,
    IPAllocationResponse,
    IPAllocationUpdate,
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
    ip_allocation_service,
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
        order: str = Query("desc", description="ID排序: desc(倒序) / asc(正序)"),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ):
        items, total = service.list(db, skip=skip, limit=limit, keyword=keyword, order=order)
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


# 反向互联链路批量查询（须在 port-connections 子路由注册之前定义，
# 否则会被子路由的 /{item_id} 命中）。
@router.get("/port-connections/reverse-links", summary="批量查询反向互联链路")
def get_reverse_links(
    device_id: int = Query(..., description="本端设备ID"),
    port_names: str = Query("", description="逗号分隔的本端端口名列表"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """给定本端设备及其端口名列表，返回每个端口在其它设备上被谁互联的信息
    （对方设备、接口、接口类型、网络类型、VLAN），用于打开对端设备时自动回填互联关系。
    例如 A 的 GE1 互联到 B 的 GE1，则打开 B 时 B 的 GE1 会自动关联回 A。"""
    names = [n.strip() for n in (port_names or "").split(",") if n.strip()]
    return port_connection_service.get_reverse_links(db, device_id, names)


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
                  ExternalBroadbandResponse, ExternalBroadbandListResponse, "external-broadbands", "IPS带宽"),
    prefix="/external-broadbands", tags=["IPS带宽"],
)
router.include_router(
    _build_router(license_service, LicenseManagementCreate, LicenseManagementUpdate,
                  LicenseManagementResponse, LicenseManagementListResponse, "licenses", "授权管理"),
    prefix="/licenses", tags=["授权管理"],
)

router.include_router(
    _build_router(ip_allocation_service, IPAllocationCreate, IPAllocationUpdate,
                  IPAllocationResponse, IPAllocationListResponse, "ip-allocations", "IP地址分配表"),
    prefix="/ip-allocations", tags=["IP地址分配表"],
)
