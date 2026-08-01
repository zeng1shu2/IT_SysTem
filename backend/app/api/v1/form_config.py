"""Form config management routes."""

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session
import json

from app.core.deps import get_current_admin, get_current_user, get_db
from app.models.user import User
from app.schemas.form_config import (
    FormConfigCreate,
    FormConfigListResponse,
    FormConfigResponse,
    FormConfigUpdate,
)
from app.services.form_config_service import (
    create_form_config,
    delete_form_config,
    get_form_config_by_code,
    get_form_config_by_id,
    get_form_configs,
    update_form_config,
)

router = APIRouter()


@router.get("", response_model=FormConfigListResponse, summary="获取表单配置列表")
def list_form_configs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    keyword: str | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get paginated form config list."""
    items, total = get_form_configs(db, skip=skip, limit=limit, keyword=keyword)
    return FormConfigListResponse(
        total=total,
        items=[FormConfigResponse.model_validate(i) for i in items],
    )


@router.get("/code/{code}", response_model=FormConfigResponse, summary="按编码获取表单配置")
def get_by_code(
    code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a form config by its unique code."""
    obj = get_form_config_by_code(db, code)
    if not obj:
        raise HTTPException(status_code=404, detail=f"表单编码 '{code}' 不存在")
    return FormConfigResponse.model_validate(obj)


@router.get("/{config_id}", response_model=FormConfigResponse, summary="获取表单配置详情")
def get_form_config(
    config_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a single form config by ID."""
    obj = get_form_config_by_id(db, config_id)
    return FormConfigResponse.model_validate(obj)


@router.post("", response_model=FormConfigResponse, status_code=status.HTTP_201_CREATED, summary="创建表单配置")
def create(
    body: FormConfigCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    """Create a new form config. Requires admin."""
    try:
        obj = create_form_config(db, body, current_user.username)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return FormConfigResponse.model_validate(obj)


@router.put("/{config_id}", response_model=FormConfigResponse, summary="更新表单配置")
def update(
    config_id: int,
    body: FormConfigUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    """Update a form config. Requires admin."""
    try:
        obj = update_form_config(db, config_id, body)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return FormConfigResponse.model_validate(obj)


@router.post("/{config_id}/reset-to-default", response_model=FormConfigResponse, summary="恢复为代码默认模板")
def reset_to_default(
    config_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    """管理员手动将表单配置恢复为 main.py 中定义的默认模板（覆盖用户自定义）。"""
    from app.main import DEFAULT_FORM_CONFIGS_BY_CODE
    obj = get_form_config_by_id(db, config_id)
    default = DEFAULT_FORM_CONFIGS_BY_CODE.get(obj.code)
    if not default:
        raise HTTPException(status_code=404, detail=f"未找到编码 '{obj.code}' 的代码默认模板")
    _name, _desc, schema_list = default
    obj.form_schema = json.dumps(schema_list, ensure_ascii=False)
    obj.name = _name
    db.commit()
    db.refresh(obj)
    return FormConfigResponse.model_validate(obj)


@router.delete("/{config_id}", summary="删除表单配置")
def delete(
    config_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    """Delete a form config. Requires admin."""
    try:
        delete_form_config(db, config_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"message": "表单配置已删除"}
