"""Asset (network device) model."""

from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text, Enum
from sqlalchemy.orm import relationship

from app.database import Base


class Asset(Base):
    """Network device asset model."""

    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    device_type = Column(
        String(20),
        nullable=False,
        comment="设备类型: switch/router/firewall/security/other",
    )
    device_name = Column(String(100), nullable=False, comment="设备名称")
    brand = Column(String(50), nullable=True, comment="品牌")
    model = Column(String(100), nullable=True, comment="型号")
    serial_number = Column(String(100), nullable=True, comment="序列号")
    ip_address = Column(String(45), nullable=True, comment="管理IP地址")
    mac_address = Column(String(20), nullable=True, comment="MAC地址")
    location = Column(String(200), nullable=True, comment="存放位置")
    status = Column(String(20), default="in_use", nullable=False, comment="状态: in_use/idle/fault/maintenance/scrap")
    purchase_date = Column(DateTime, nullable=True, comment="采购日期")
    warranty_expire = Column(DateTime, nullable=True, comment="保修到期")
    remark = Column(Text, nullable=True, comment="备注")
    created_at = Column(DateTime, default=datetime.now, nullable=False, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False, comment="更新时间")

    def __repr__(self):
        return f"<Asset(id={self.id}, name={self.device_name})>"
