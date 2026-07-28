"""Form config service."""

from sqlalchemy.orm import Session

from app.models.form_config import FormConfig
from app.schemas.form_config import FormConfigCreate, FormConfigUpdate


def get_form_configs(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    keyword: str | None = None,
) -> tuple[list[FormConfig], int]:
    """Get paginated form configs with optional keyword search."""
    query = db.query(FormConfig)
    if keyword:
        query = query.filter(
            (FormConfig.name.contains(keyword))
            | (FormConfig.code.contains(keyword))
        )
    total = query.count()
    items = query.order_by(FormConfig.updated_at.desc()).offset(skip).limit(limit).all()
    return items, total


def get_form_config_by_id(db: Session, config_id: int) -> FormConfig:
    """Get a form config by ID."""
    obj = db.query(FormConfig).filter(FormConfig.id == config_id).first()
    if not obj:
        raise ValueError(f"表单配置(id={config_id})不存在")
    return obj


def get_form_config_by_code(db: Session, code: str) -> FormConfig | None:
    """Get a form config by code."""
    return db.query(FormConfig).filter(FormConfig.code == code).first()


def create_form_config(
    db: Session, data: FormConfigCreate, creator: str
) -> FormConfig:
    """Create a new form config."""
    if get_form_config_by_code(db, data.code):
        raise ValueError(f"表单编码 '{data.code}' 已存在")
    obj = FormConfig(
        name=data.name,
        code=data.code,
        description=data.description,
        form_schema=data.form_schema,
        is_active=data.is_active,
        created_by=creator,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update_form_config(
    db: Session, config_id: int, data: FormConfigUpdate
) -> FormConfig:
    """Update a form config."""
    obj = get_form_config_by_id(db, config_id)
    update_data = data.model_dump(exclude_unset=True)
    # Check code uniqueness if changing
    if "code" in update_data and update_data["code"] != obj.code:
        if get_form_config_by_code(db, update_data["code"]):
            raise ValueError(f"表单编码 '{update_data['code']}' 已存在")
    for key, value in update_data.items():
        setattr(obj, key, value)
    db.commit()
    db.refresh(obj)
    return obj


def delete_form_config(db: Session, config_id: int) -> None:
    """Delete a form config."""
    obj = get_form_config_by_id(db, config_id)
    db.delete(obj)
    db.commit()
