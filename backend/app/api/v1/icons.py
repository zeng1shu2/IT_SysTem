"""API routes for 图标库 (Icon).

提供：上传（multipart）、列表（按 category 过滤）、删除。
权限：写入需管理员；读取任意已登录用户。
文件落盘到 frontend/public/icons/{yyyyMM}/{uuid}.{ext}，由 FastAPI 挂载的 StaticFiles 提供。
"""
from __future__ import annotations

import os
import uuid
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.deps import get_current_admin, get_current_user, get_db
from app.models.icon import Icon
from app.models.user import User

router = APIRouter()

# 图标文件物理目录：frontend/public/icons/
# 与 FastAPI 静态挂载点一致（见 main.py 的 mount('/icons', ...)）。
PUBLIC_DIR = Path(__file__).resolve().parents[4] / "frontend" / "public" / "icons"
PUBLIC_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_MIME = {"image/png", "image/jpeg", "image/jpg", "image/svg+xml", "image/webp", "image/gif"}
ALLOWED_EXT = {".png", ".jpg", ".jpeg", ".svg", ".webp", ".gif"}
MAX_SIZE_BYTES = 2 * 1024 * 1024  # 2MB


def _safe_ext(filename: str) -> str:
    ext = os.path.splitext(filename or "")[1].lower()
    if ext not in ALLOWED_EXT:
        raise HTTPException(status_code=400, detail=f"不支持的文件类型: {ext or '(无)'}")
    return ext


def _read_public_dir() -> Path:
    """Resolve icons directory (supports tests overriding env var)."""
    override = os.environ.get("ICONS_DIR")
    if override:
        p = Path(override)
        p.mkdir(parents=True, exist_ok=True)
        return p
    return PUBLIC_DIR


@router.post("/upload", summary="上传图标（管理员）")
async def upload_icon(
    file: UploadFile = File(..., description="PNG/JPG/SVG/WebP/GIF，最大 2MB"),
    name: str = Form(..., description="图标名称"),
    category: str = Form("other", description="分类"),
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    if file.content_type not in ALLOWED_MIME:
        raise HTTPException(status_code=400, detail=f"不支持的 MIME 类型: {file.content_type}")

    ext = _safe_ext(file.filename or "")
    contents = await file.read()
    if len(contents) > MAX_SIZE_BYTES:
        raise HTTPException(status_code=413, detail=f"文件超过 {MAX_SIZE_BYTES // 1024 // 1024}MB 限制")
    if len(contents) == 0:
        raise HTTPException(status_code=400, detail="空文件")

    subdir = datetime.utcnow().strftime("%Y%m")
    target_dir = _read_public_dir() / subdir
    target_dir.mkdir(parents=True, exist_ok=True)

    # 禁止同名上传：已存在同名（且启用）图标则拒绝，避免重复图标难以区分
    # 注意：fname（uuid 文件名）在下方才生成，此处不能引用；name 为空时回退到上传文件名
    name_key = name.strip() or (file.filename or "未命名图标")
    existing = db.query(Icon).filter(Icon.name == name_key, Icon.is_active.is_(True)).first()
    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"已存在同名图标「{existing.name}」，请改名或先删除旧图标后再上传",
        )

    fname = f"{uuid.uuid4().hex}{ext}"
    target = target_dir / fname
    target.write_bytes(contents)

    web_path = f"/icons/{subdir}/{fname}"
    icon = Icon(
        name=name.strip() or fname,
        category=(category or "other").strip().lower(),
        filename=f"{subdir}/{fname}",
        path=web_path,
        mime=file.content_type,
        size=len(contents),
        is_active=True,
        uploaded_by=current_user.username,
    )
    db.add(icon)
    db.commit()
    db.refresh(icon)

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "id": icon.id,
            "name": icon.name,
            "category": icon.category,
            "path": icon.path,
            "mime": icon.mime,
            "size": icon.size,
            "uploaded_by": icon.uploaded_by,
            "created_at": icon.created_at.isoformat() if icon.created_at else None,
        },
    )


@router.get("", summary="图标库列表")
def list_icons(
    category: str | None = Query(None, description="按分类过滤"),
    keyword: str | None = Query(None, description="名称模糊匹配"),
    include_inactive: bool = Query(False, description="是否包含已禁用"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    q = db.query(Icon)
    if not include_inactive:
        q = q.filter(Icon.is_active.is_(True))
    if category:
        q = q.filter(Icon.category == category)
    if keyword:
        like = f"%{keyword}%"
        q = q.filter(Icon.name.like(like))
    rows = q.order_by(Icon.created_at.desc()).all()
    return {
        "total": len(rows),
        "items": [
            {
                "id": r.id,
                "name": r.name,
                "category": r.category,
                "path": r.path,
                "mime": r.mime,
                "size": r.size,
                "is_active": r.is_active,
                "uploaded_by": r.uploaded_by,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in rows
        ],
    }


@router.delete("/{icon_id}", summary="删除图标（管理员，软删除）")
def delete_icon(
    icon_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    icon = db.query(Icon).filter(Icon.id == icon_id).first()
    if not icon:
        raise HTTPException(status_code=404, detail="图标不存在")

    # 软删除：仅标记 is_active=False，磁盘文件保留（便于恢复/审计）
    icon.is_active = False
    icon.updated_at = datetime.utcnow()
    db.commit()

    return {"id": icon.id, "is_active": False, "message": "已禁用"}


@router.delete("/{icon_id}/permanent", summary="永久删除图标（管理员，删库+删文件）")
def permanent_delete_icon(
    icon_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """物理删除：删除数据库记录 + 磁盘文件，不可逆。"""
    icon = db.query(Icon).filter(Icon.id == icon_id).first()
    if not icon:
        raise HTTPException(status_code=404, detail="图标不存在")

    # 删除磁盘文件（文件缺失不阻断数据库记录删除）
    try:
        target = _read_public_dir() / icon.filename
        if target.exists():
            target.unlink()
    except OSError:
        pass

    db.delete(icon)
    db.commit()
    return {"id": icon_id, "message": "已永久删除"}