"""API v1 package."""

from fastapi import APIRouter

from app.api.v1 import asset, asset_modules, audit, auth, form_config, permission, role, system_field, user

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["认证管理"])
api_router.include_router(user.router, prefix="/users", tags=["用户管理"])
api_router.include_router(role.router, prefix="/roles", tags=["角色管理"])
api_router.include_router(asset.router, prefix="/assets", tags=["资产管理"])
api_router.include_router(asset_modules.router, tags=["资产子模块"])
api_router.include_router(permission.router, prefix="/permissions", tags=["权限管理"])
api_router.include_router(audit.router, prefix="/audit", tags=["审计日志"])
api_router.include_router(form_config.router, prefix="/form-configs", tags=["表单设计"])
api_router.include_router(system_field.router, prefix="/system-fields", tags=["字段管理"])
