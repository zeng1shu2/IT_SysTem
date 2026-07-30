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
    status = Column(String(20), nullable=True, comment="状态:正常/空闲/故障/停用")
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
    brand = Column(String(100), nullable=True, comment="品牌")
    device_type = Column(String(50), nullable=True, comment="设备类型")
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=True, comment="关联资产ID")
    device_name = Column(String(100), nullable=True, comment="设备名称(关联资产统计)")
    license_key = Column(String(500), nullable=True, comment="授权码/序列号")
    activation_date = Column(DateTime, nullable=True, comment="激活日期")
    expiration_date = Column(DateTime, nullable=True, comment="到期日期")
    status = Column(String(20), nullable=True, comment="状态: 正常/临期2月/临期1月/临期15天/过期")
    remark = Column(Text, nullable=True, comment="备注")
    extra_data = Column(JSON, nullable=True, comment="自定义扩展字段")
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

    def __repr__(self):
        return f"<LicenseManagement(id={self.id}, brand={self.brand})>"

    @staticmethod
    def compute_status(activation_date=None, expiration_date=None, now=None):
        """根据激活与到期时间自动计算授权状态。

        状态枚举：正常 / 临期2月 / 临期1月 / 临期15天 / 过期
        - 无到期日期：正常
        - 已过期（now > 到期）：过期
        - 距到期 <= 15 天：临期15天
        - 距到期 <= 30 天：临期1月
        - 距到期 <= 60 天：临期2月
        - 其余：正常
        """
        if expiration_date is None:
            return "正常"
        from datetime import datetime as _dt
        if now is None:
            now = _dt.now()
        if isinstance(expiration_date, str):
            expiration_date = _dt.fromisoformat(expiration_date)
        if isinstance(now, str):
            now = _dt.fromisoformat(now)
        delta_days = (expiration_date - now).days
        if delta_days < 0:
            return "过期"
        if delta_days <= 15:
            return "临期15天"
        if delta_days <= 30:
            return "临期1月"
        if delta_days <= 60:
            return "临期2月"
        return "正常"


class IPAllocation(Base):
    """IP address allocation table - assigned IP with owner/department/dates."""

    __tablename__ = "ip_allocations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    department = Column(String(100), nullable=True, comment="部门")
    user_name = Column(String(100), nullable=True, comment="使用人")
    ip_address = Column(String(200), nullable=False, comment="IP地址/掩码")
    apply_date = Column(DateTime, nullable=True, comment="申请日期")
    recycle_date = Column(DateTime, nullable=True, comment="回收日期")
    remark = Column(Text, nullable=True, comment="备注")
    registrar = Column(String(100), nullable=True, comment="登记人")
    extra_data = Column(JSON, nullable=True, comment="自定义扩展字段")
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

    def __repr__(self):
        return f"<IPAllocation(id={self.id}, ip_address={self.ip_address})>"
