"""Service for the 字段管理 (SystemField) module."""

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.system_field import SystemField
from app.services.asset_modules import GenericCRUDService
from app.services.audit_service import log_operation

# Generic CRUD service for the system_fields table.
system_field_service = GenericCRUDService(
    SystemField,
    search_fields=["field_name", "label", "value"],
    target_type="system_field",
)


def list_by_code(db: Session, code: str, include_inactive: bool = True):
    """Return all rows for a given field_code, ordered by level then sort.

    Used by the management page (shows inactive rows too so they can be re-enabled).
    """
    query = db.query(SystemField).filter(SystemField.field_code == code)
    if not include_inactive:
        query = query.filter(SystemField.is_active == 1)
    rows = query.order_by(SystemField.level.asc(), SystemField.sort.asc()).all()
    return rows


def build_options(db: Session, code: str):
    """Build consumer-ready options for `code`.

    - Flat fields (organization, location, brand, security_zones, protocol, operator):
      return a list of active options:
        [{"label", "value", "icon"?, "emoji"?, "sort"}]
    - device_type (two-level tree): return the cascader shape:
        [{"label": "网络设备类", "options": [{"label", "value", "icon"?, "emoji"?}, ...]}, ...]
      Only active categories/subtypes are included.
    """
    rows = (
        db.query(SystemField)
        .filter(SystemField.field_code == code, SystemField.is_active == 1)
        .order_by(SystemField.level.asc(), SystemField.sort.asc())
        .all()
    )

    if code == "device_type":
        cats = [r for r in rows if r.level == 0]
        subs = [r for r in rows if r.level == 1]
        tree = []
        for c in cats:
            children = [
                {
                    "label": s.label,
                    "value": s.value,
                    **({"icon": s.icon} if s.icon else {}),
                    **({"emoji": s.emoji} if s.emoji else {}),
                }
                for s in subs
                if s.parent_value == c.value
            ]
            tree.append({"label": c.label, "options": children})
        return tree

    return [
        {
            "label": r.label,
            "value": r.value,
            **({"icon": r.icon} if r.icon else {}),
            **({"emoji": r.emoji} if r.emoji else {}),
            "sort": r.sort,
        }
        for r in rows
    ]


def delete_by_id(db: Session, item_id: int, operator: str, operator_ip: str):
    item = db.query(SystemField).filter(SystemField.id == item_id).first()
    if not item:
        from fastapi import HTTPException, status

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"字段选项不存在: id={item_id}")
    db.delete(item)
    db.commit()
    log_operation(
        db, operator=operator, operator_ip=operator_ip, operation_type="delete",
        target_type="system_field", target_id=item_id, result=True,
        detail={"field_code": item.field_code, "value": item.value},
    )
