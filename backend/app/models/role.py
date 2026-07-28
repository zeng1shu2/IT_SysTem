"""Role model."""

from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text, Table, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base

# Role-Permission association table (permission strings, not a separate table)
role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column("permission", String(100), primary_key=True, comment="权限标识，如 asset:read, user:write"),
)


class Role(Base):
    """Role model."""

    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False, comment="角色名称")
    code = Column(String(50), unique=True, nullable=False, comment="角色编码")
    description = Column(Text, nullable=True, comment="角色描述")
    created_at = Column(DateTime, default=datetime.now, nullable=False, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False, comment="更新时间")

    # Relationships
    users = relationship("User", secondary="user_roles", back_populates="roles")

    def __repr__(self):
        return f"<Role(id={self.id}, name={self.name})>"
