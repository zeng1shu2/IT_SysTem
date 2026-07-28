"""Permission request model."""

from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class PermissionRequest(Base):
    """Permission request record (auto-approval mode)."""

    __tablename__ = "permission_requests"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, comment="申请用户ID")
    permission_code = Column(String(100), nullable=False, comment="申请的权限编码")
    reason = Column(Text, nullable=True, comment="申请理由")
    status = Column(String(20), default="approved", nullable=False, comment="状态: approved/rejected (一期自动批准)")
    approved_at = Column(DateTime, nullable=True, comment="审批时间")
    approved_by = Column(String(50), default="system", nullable=False, comment="审批人: system(自动)")
    auto_rule = Column(String(200), nullable=True, comment="匹配的自动分配规则")
    created_at = Column(DateTime, default=datetime.now, nullable=False, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False, comment="更新时间")

    # Relationships
    user = relationship("User", backref="permission_requests")

    def __repr__(self):
        return f"<PermissionRequest(id={self.id}, user_id={self.user_id}, permission={self.permission_code})>"
