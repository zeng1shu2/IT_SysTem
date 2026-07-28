"""Form configuration model for dynamic form designer."""

from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text, Boolean

from app.database import Base


class FormConfig(Base):
    """Dynamic form configuration created by the form designer."""

    __tablename__ = "form_configs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, comment="表单名称")
    code = Column(String(50), nullable=False, unique=True, comment="表单编码（唯一标识）")
    description = Column(String(500), nullable=True, comment="表单描述")
    form_schema = Column(Text, nullable=False, comment="表单字段JSON配置")
    is_active = Column(Boolean, default=True, nullable=False, comment="是否启用")
    created_by = Column(String(50), nullable=True, comment="创建人")
    created_at = Column(DateTime, default=datetime.now, nullable=False, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False, comment="更新时间")

    def __repr__(self):
        return f"<FormConfig(id={self.id}, name={self.name}, code={self.code})>"
