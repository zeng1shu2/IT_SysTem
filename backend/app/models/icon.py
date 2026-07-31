"""图标库 ORM 模型。

字段选项/设备类型/品牌等可在前端通过图标库页面统一上传图标，
保存到 frontend/public/icons/，数据库仅记录元数据。
"""
from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Index

from app.database import Base


class Icon(Base):
    """图标资源表。

    - name: 业务名称（用于检索/展示）
    - category: 分类，如 device / brand / operator / other
    - filename: 磁盘文件名（相对路径 icons/{yyyyMM}/{filename}）
    - path: Web URL 路径（前端可直接 <img :src>）
    - mime / size: 文件元信息
    - is_active: 软删除标志
    """
    __tablename__ = "icons"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(128), nullable=False, comment="图标名称")
    category = Column(String(32), nullable=False, default="other", comment="分类: device/brand/operator/other")
    filename = Column(String(255), nullable=False, comment="磁盘文件名(相对 icons/)")
    path = Column(String(512), nullable=False, comment="Web URL 路径")
    mime = Column(String(64), nullable=True, comment="MIME 类型")
    size = Column(Integer, nullable=True, comment="文件字节数")
    is_active = Column(Boolean, nullable=False, default=True, comment="启用")
    uploaded_by = Column(String(64), nullable=True, comment="上传者用户名")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, comment="上传时间")
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        comment="更新时间",
    )

    __table_args__ = (
        Index("ix_icons_category", "category"),
        Index("ix_icons_is_active", "is_active"),
    )