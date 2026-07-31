"""System-managed option fields (字段管理).

Centralizes option lists that were previously hardcoded in form-config seeds,
so administrators can add new options (e.g. a new device type) directly from
the 字段管理 page without touching code.

A single table stores both flat option lists (organization, location, brand,
security_zones, protocol, operator) and the two-level device-type tree
(network/security/software categories -> subtypes).  For the device-type tree,
`level=0` rows are categories (parent_value is NULL) and `level=1` rows are
subtypes whose `parent_value` points at the category's `value`.
"""

from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text, UniqueConstraint

from app.database import Base


class SystemField(Base):
    """Managed option for a logical field (组织/位置/品牌/设备类型/...)."""

    __tablename__ = "system_fields"

    __table_args__ = (
        UniqueConstraint("field_code", "value", name="uq_system_field_code_value"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    field_code = Column(String(50), nullable=False, index=True, comment="字段编码: organization/location/brand/device_type/security_zones/protocol/operator")
    field_name = Column(String(50), nullable=False, comment="字段中文名: 组织/位置/品牌/设备类型")
    value = Column(String(100), nullable=False, comment="选项值(存储值, 如 switch)")
    label = Column(String(100), nullable=False, comment="选项显示名(如 交换机)")
    icon = Column(String(255), nullable=True, comment="图标路径(可选)")
    emoji = Column(String(20), nullable=True, comment="emoji 图标(可选)")
    sort = Column(Integer, default=0, nullable=False, comment="排序(同级升序)")
    is_active = Column(Integer, default=1, nullable=False, comment="是否启用 1=启用 0=停用")
    parent_value = Column(String(100), nullable=True, comment="父级value(设备类型大类); 顶层为 NULL")
    level = Column(Integer, default=0, nullable=False, comment="层级 0=顶层/大类 1=子级/小类")
    description = Column(String(255), nullable=True, comment="备注")
    created_at = Column(DateTime, default=datetime.now, nullable=False, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False, comment="更新时间")

    def __repr__(self):
        return f"<SystemField(id={self.id}, code={self.field_code}, value={self.value})>"
