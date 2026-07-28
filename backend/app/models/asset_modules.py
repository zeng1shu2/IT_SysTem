"""Asset sub-module models: PortConnection, IPPlan, InterconnectIP, ExternalBroadband, LicenseManagement."""

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, String, Text

from app.database import Base


class PortConnection(Base):
    """Port interconnection - links to an asset and stores port data."""

    __tablename__ = "port_connections"

    id = Column(Integer, primary_key=True, autoincrement=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False, comment="关联资产ID")
    asset_name = Column(String(100), nullable=True, comment="设备名称(冗余,便于展示)")
    port_count = Column(Integer, default=0, nullable=False, comment="端口总数")
    ports_data = Column(JSON, nullable=True, comment="物理端口数据: [{index, name, connected_device_id, connected_device, connected_interface, status, remark}]")
    logical_interfaces = Column(JSON, nullable=True, comment="逻辑接口数据: [{type: vlanif|eth-trunk, name, vlan_id, ip_address, mask, member_ports[], remark}]")
    remark = Column(Text, nullable=True, comment="备注")
    extra_data = Column(JSON, nullable=True, comment="自定义扩展字段")
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

    def __repr__(self):
        return f"<PortConnection(id={self.id}, asset_id={self.asset_id}, ports={self.port_count})>"


class IPPlan(Base):
    """IP address planning."""

    __tablename__ = "ip_plans"

    id = Column(Integer, primary_key=True, autoincrement=True)
    department = Column(String(100), nullable=True, comment="部门")
    group_name = Column(String(100), nullable=True, comment="小组")
    ip_range = Column(String(200), nullable=False, comment="IP段")
    vlan = Column(String(50), nullable=True, comment="VLAN")
    usage_status = Column(String(20), default="available", nullable=False, comment="使用状态: available/used/reserved")
    remark = Column(Text, nullable=True, comment="备注")
    extra_data = Column(JSON, nullable=True, comment="自定义扩展字段")
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

    def __repr__(self):
        return f"<IPPlan(id={self.id}, ip_range={self.ip_range})>"


class InterconnectIP(Base):
    """Interconnect IP - links source/dest devices and interfaces."""

    __tablename__ = "interconnect_ips"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ip_range = Column(String(200), nullable=False, comment="IP地址范围")
    source_device_id = Column(Integer, ForeignKey("assets.id"), nullable=True, comment="源设备ID")
    source_device_name = Column(String(100), nullable=True, comment="源设备名称(冗余)")
    source_interface = Column(String(200), nullable=True, comment="源接口")
    dest_device_id = Column(Integer, ForeignKey("assets.id"), nullable=True, comment="目的设备ID")
    dest_device_name = Column(String(100), nullable=True, comment="目的设备名称(冗余)")
    dest_interface = Column(String(200), nullable=True, comment="目的接口")
    remark = Column(Text, nullable=True, comment="备注")
    extra_data = Column(JSON, nullable=True, comment="自定义扩展字段")
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

    def __repr__(self):
        return f"<InterconnectIP(id={self.id}, ip_range={self.ip_range})>"


class ExternalBroadband(Base):
    """External broadband / WAN lines."""

    __tablename__ = "external_broadbands"

    id = Column(Integer, primary_key=True, autoincrement=True)
    operator = Column(String(50), nullable=True, comment="运营商")
    line_type = Column(String(50), nullable=True, comment="线路类型")
    ip_address = Column(String(45), nullable=True, comment="IP地址")
    mask = Column(String(45), nullable=True, comment="掩码")
    gateway = Column(String(45), nullable=True, comment="网关")
    dial_account = Column(String(100), nullable=True, comment="拨号账号/接入号")
    vlan = Column(String(50), nullable=True, comment="对应VLAN")
    bandwidth = Column(String(50), nullable=True, comment="线路带宽")
    ownership = Column(String(100), nullable=True, comment="线路归属")
    remark = Column(Text, nullable=True, comment="备注")
    extra_data = Column(JSON, nullable=True, comment="自定义扩展字段")
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

    def __repr__(self):
        return f"<ExternalBroadband(id={self.id}, operator={self.operator})>"


class LicenseManagement(Base):
    """License / authorization management."""

    __tablename__ = "license_managements"

    id = Column(Integer, primary_key=True, autoincrement=True)
    vendor = Column(String(100), nullable=True, comment="厂商")
    device_type = Column(String(50), nullable=True, comment="设备类型")
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=True, comment="关联资产ID")
    device_name = Column(String(100), nullable=True, comment="设备名称(关联资产统计)")
    license_key = Column(String(500), nullable=True, comment="授权码/序列号")
    activation_date = Column(DateTime, nullable=True, comment="激活日期")
    expiration_date = Column(DateTime, nullable=True, comment="到期日期")
    remark = Column(Text, nullable=True, comment="备注")
    extra_data = Column(JSON, nullable=True, comment="自定义扩展字段")
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

    def __repr__(self):
        return f"<LicenseManagement(id={self.id}, vendor={self.vendor})>"
