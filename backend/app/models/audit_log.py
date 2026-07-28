"""Audit log model."""

from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text, Boolean

from app.database import Base


class AuditLog(Base):
    """Audit log for all key operations."""

    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    operator = Column(String(50), nullable=True, comment="操作人用户名")
    operator_id = Column(Integer, nullable=True, comment="操作人ID")
    operator_ip = Column(String(45), nullable=True, comment="操作IP地址")
    operation_time = Column(DateTime, default=datetime.now, nullable=False, index=True, comment="操作时间")
    operation_type = Column(String(30), nullable=False, comment="操作类型: login/logout/create/update/delete/approve/query")
    target_type = Column(String(30), nullable=True, comment="操作对象类型: user/role/asset/permission/system")
    target_id = Column(String(50), nullable=True, comment="操作对象ID")
    result = Column(Boolean, nullable=False, comment="操作结果: True=成功, False=失败")
    detail = Column(Text, nullable=True, comment="变更详情，JSON格式")
    created_at = Column(DateTime, default=datetime.now, nullable=False, comment="记录创建时间")

    def __repr__(self):
        return f"<AuditLog(id={self.id}, operator={self.operator}, type={self.operation_type})>"
