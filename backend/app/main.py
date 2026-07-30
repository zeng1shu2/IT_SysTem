"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import api_router
from app.core.config import settings
from app.database import Base, engine

# Import all models so tables are created
import app.models.user  # noqa: F401
import app.models.role  # noqa: F401
import app.models.asset  # noqa: F401
import app.models.asset_modules  # noqa: F401
import app.models.form_config  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown."""
    # Create tables (for development; use Alembic in production)
    Base.metadata.create_all(bind=engine)

    # Seed initial data
    from app.database import SessionLocal
    from app.models.user import User
    from app.models.role import Role
    from app.core.security import get_password_hash

    db = SessionLocal()
    try:
        # Check if admin user exists
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            admin = User(
                username="admin",
                password_hash=get_password_hash("admin123"),
                real_name="系统管理员",
                is_active=True,
                is_admin=True,
            )
            db.add(admin)
            db.commit()
            print("[Startup] Created default admin user: admin / admin123")

        # Create default roles if none exist
        if db.query(Role).count() == 0:
            roles = [
                Role(name="管理员", code="admin", description="系统管理员，拥有全部权限"),
                Role(name="运维人员", code="operator", description="运维人员，可查看和管理资产"),
                Role(name="普通用户", code="user", description="普通用户，仅可查看"),
            ]
            for role in roles:
                db.add(role)
            db.commit()
            print("[Startup] Created default roles")

        # Seed form configs
        from app.models.form_config import FormConfig
        import json

        def _seed_form_config(db, code, name, description, schema_list):
            """Upsert form config: delete old and create new if schema changed."""
            existing = db.query(FormConfig).filter(FormConfig.code == code).first()
            new_schema = json.dumps(schema_list, ensure_ascii=False)
            if existing:
                # Update existing config with new schema
                existing.form_schema = new_schema
                existing.name = name
                db.commit()
                return False  # updated
            form_cfg = FormConfig(
                code=code, name=name, description=description,
                form_schema=new_schema, is_active=True, created_by="system",
            )
            db.add(form_cfg)
            db.commit()
            return True  # created

        # --- Asset form (设备类型两级联动 + 全类型端口配置 + 安全域/路由协议多选) ---
        _seed_form_config(db, "asset_form", "资产统计表单", "资产统计页面的动态表单配置", [
            {"type": "divider", "label": "基础信息", "span": 24},
            {"type": "input", "label": "设备名称", "prop": "device_name", "required": True, "span": 12, "placeholder": "如：核心交换机-01"},
            {"type": "select-cascade", "label": "设备类型", "prop": "device_type", "required": True, "span": 12, "defaultValue": "switch", "cascaderOptions": [
                {"label": "网络设备类", "options": [
                    {"label": "交换机", "value": "switch"}, {"label": "路由器", "value": "router"},
                    {"label": "集线器", "value": "hub"}, {"label": "其他设备", "value": "other"},
                ]},
                {"label": "安全设备类", "options": [
                    {"label": "防火墙", "value": "firewall"}, {"label": "上网行为管理", "value": "internet_behavior"},
                    {"label": "堡垒机", "value": "bastion"}, {"label": "IPS", "value": "ips"},
                    {"label": "IDS", "value": "ids"}, {"label": "DDoS", "value": "ddos"},
                    {"label": "VPN", "value": "vpn"}, {"label": "杀毒软件", "value": "antivirus"},
                ]},
                {"label": "其他软件类", "options": [
                    {"label": "准入系统", "value": "admission"}, {"label": "认证系统", "value": "auth"},
                    {"label": "网管系统", "value": "nms"}, {"label": "数据库系统", "value": "database"},
                    {"label": "运维审计系统", "value": "ops_audit"}, {"label": "API网关系统", "value": "api_gateway"},
                ]},
            ]},
            # 品牌：与授权管理 license_form.brand 保持一致（select-icon 单选：华为/深信服/绿盟/H3C/信锐）
            {"type": "select-icon", "label": "品牌", "prop": "brand", "span": 12, "options": [
                {"label": "华为", "value": "华为", "icon": "/brand-icons/huawei.png"},
                {"label": "深信服", "value": "深信服", "icon": "/brand-icons/sangfor.png"},
                {"label": "绿盟", "value": "绿盟", "icon": "/brand-icons/nsfocus.png"},
                {"label": "H3C", "value": "H3C", "icon": "/brand-icons/h3c.png"},
                {"label": "信锐", "value": "信锐", "emoji": "📡"},
            ]},
            {"type": "input", "label": "型号", "prop": "model", "span": 12, "placeholder": "如：S5700-28C-HI"},
            {"type": "divider", "label": "资产编码", "span": 24},
            {"type": "input", "label": "IT资产编码", "prop": "it_asset_code", "span": 12, "placeholder": "如：IT-2024-0001"},
            {"type": "input", "label": "财务资产编码", "prop": "financial_asset_code", "span": 12, "placeholder": "如：FA-2024-0001"},
            {"type": "divider", "label": "网络信息", "span": 24},
            {"type": "input", "label": "管理IP", "prop": "ip_address", "span": 12, "placeholder": "如：192.168.1.1"},
            {"type": "input", "label": "MAC地址", "prop": "mac_address", "span": 12, "placeholder": "如：00:1A:2B:3C:4D:5E"},
            {"type": "divider", "label": "设备特性（动态）", "span": 24},
            # 网络设备类（交换机/路由器/集线器）：与交换机一致增加端口配置 + 堆叠 + 管理VLAN
            {"type": "portGroups", "label": "端口配置（按类型）", "prop": "port_groups", "span": 24, "visibleWhen": {"prop": "device_type", "in": ["switch", "router", "hub"]}},
            {"type": "stackConfig", "label": "堆叠配置", "prop": "stack_config", "span": 24, "visibleWhen": {"prop": "device_type", "in": ["switch", "router", "hub"]}},
            {"type": "input", "label": "管理VLAN", "prop": "vlan_range", "span": 12, "placeholder": "如：1-100, 200", "visibleWhen": {"prop": "device_type", "in": ["switch", "router", "hub"]}},
            # 防火墙：与交换机一致增加端口配置 + 堆叠 + 管理VLAN
            {"type": "portGroups", "label": "端口配置（按类型）", "prop": "port_groups", "span": 24, "visibleWhen": {"prop": "device_type", "equals": "firewall"}},
            {"type": "stackConfig", "label": "堆叠配置", "prop": "stack_config", "span": 24, "visibleWhen": {"prop": "device_type", "equals": "firewall"}},
            {"type": "input", "label": "管理VLAN", "prop": "vlan_range", "span": 12, "placeholder": "如：1-100, 200", "visibleWhen": {"prop": "device_type", "equals": "firewall"}},
            # 路由器：路由协议改为可多选
            {"type": "select", "label": "路由协议", "prop": "protocol", "span": 12, "defaultValue": [], "multiple": True, "options": [
                {"label": "OSPF", "value": "ospf"}, {"label": "BGP", "value": "bgp"},
                {"label": "RIP", "value": "rip"}, {"label": "静态路由", "value": "static"},
                {"label": "ISIS", "value": "isis"},
            ], "visibleWhen": {"prop": "device_type", "equals": "router"}},
            {"type": "number", "label": "WAN口数", "prop": "wan_count", "span": 12, "min": 0, "max": 16, "visibleWhen": {"prop": "device_type", "equals": "router"}},
            # 防火墙：安全域改为可多选
            {"type": "select", "label": "安全域", "prop": "security_zones", "span": 12, "multiple": True, "options": [
                {"label": "Trust（信任）", "value": "trust"}, {"label": "Untrust（不信任）", "value": "untrust"},
                {"label": "DMZ（隔离区）", "value": "dmz"}, {"label": "自定义", "value": "custom"},
            ], "visibleWhen": {"prop": "device_type", "equals": "firewall"}},
            {"type": "number", "label": "策略数", "prop": "policy_count", "span": 12, "defaultValue": 0, "min": 0, "max": 9999, "visibleWhen": {"prop": "device_type", "equals": "firewall"}},
            # 其他设备/系统类：默认仅 ETH-0 接口（eth_count）
            {"type": "input", "label": "ETH接口数", "prop": "eth_count", "span": 12, "defaultValue": 1, "min": 1, "max": 64,
             "placeholder": "默认 1（即 ETH-0），新增则为 ETH-1…",
             "visibleWhen": {"prop": "device_type", "in": ["other", "hub", "internet_behavior", "bastion", "ips", "ids", "ddos", "vpn", "antivirus", "admission", "auth", "nms", "database", "ops_audit", "api_gateway"]}},
            # 安全设备类（非防火墙）子类型 + 防护级别
            {"type": "select", "label": "安全子类", "prop": "sub_type", "span": 12, "options": [
                {"label": "IDS（入侵检测）", "value": "ids"}, {"label": "IPS（入侵防御）", "value": "ips"},
                {"label": "WAF（Web应用防火墙）", "value": "waf"}, {"label": "上网行为管理", "value": "behavior"},
            ], "visibleWhen": {"prop": "device_type", "in": ["internet_behavior", "bastion", "ips", "ids", "ddos", "vpn", "antivirus"]}},
            {"type": "rate", "label": "防护级别", "prop": "protection_level", "span": 12, "defaultValue": 3, "max": 5, "visibleWhen": {"prop": "device_type", "in": ["internet_behavior", "bastion", "ips", "ids", "ddos", "vpn", "antivirus"]}},
            # 其他设备描述
            {"type": "textarea", "label": "设备描述", "prop": "description", "span": 24, "rows": 2, "placeholder": "请描述设备用途...", "visibleWhen": {"prop": "device_type", "in": ["other", "hub"]}},
            {"type": "divider", "label": "位置与状态", "span": 24},
            {"type": "input", "label": "序列号", "prop": "serial_number", "span": 12, "placeholder": "设备序列号"},
            {"type": "select", "label": "状态", "prop": "status", "required": True, "span": 12, "defaultValue": "in_use", "options": [
                {"label": "使用中", "value": "in_use"}, {"label": "空闲", "value": "idle"},
                {"label": "故障", "value": "fault"}, {"label": "维护中", "value": "maintenance"},
                {"label": "已报废", "value": "scrap"},
            ]},
            {"type": "input", "label": "存放位置", "prop": "location", "span": 24, "placeholder": "如：机房A-机柜03-U12"},
            {"type": "date", "label": "采购日期", "prop": "purchase_date", "span": 12},
            {"type": "date", "label": "保修到期", "prop": "warranty_expire", "span": 12},
            {"type": "textarea", "label": "备注", "prop": "remark", "span": 24, "rows": 2},
        ])

        # --- IP Plan form ---
        _seed_form_config(db, "ip_plan_form", "IP地址规划表单", "IP地址规划页面的动态表单配置", [
            {"type": "divider", "label": "基本信息", "span": 24},
            {"type": "input", "label": "部门", "prop": "department", "span": 12, "placeholder": "如：运维部"},
            {"type": "input", "label": "小组", "prop": "group_name", "span": 12, "placeholder": "如：网络组"},
            {"type": "input", "label": "IP段", "prop": "ip_range", "required": True, "span": 12, "placeholder": "如：192.168.1.0/24"},
            {"type": "input", "label": "VLAN", "prop": "vlan", "span": 12, "placeholder": "如：VLAN 100"},
            {"type": "select", "label": "使用状态", "prop": "usage_status", "span": 12, "defaultValue": "available", "options": [
                {"label": "可用", "value": "available"}, {"label": "已使用", "value": "used"},
                {"label": "已保留", "value": "reserved"},
            ]},
            {"type": "textarea", "label": "备注", "prop": "remark", "span": 24, "rows": 2},
        ])

        # --- Interconnect IP form ---
        _seed_form_config(db, "interconnect_ip_form", "互联IP表单", "互联IP页面的动态表单配置", [
            {"type": "divider", "label": "IP信息", "span": 24},
            {"type": "input", "label": "IP地址范围", "prop": "ip_range", "required": True, "span": 24, "placeholder": "如：10.0.0.1-10.0.0.10"},
            {"type": "divider", "label": "源端", "span": 24},
            {"type": "input", "label": "源设备", "prop": "source_device_name", "span": 12, "placeholder": "选择或输入源设备名称"},
            {"type": "input", "label": "源接口", "prop": "source_interface", "span": 12, "placeholder": "如：GigabitEthernet0/0/1"},
            {"type": "divider", "label": "目的端", "span": 24},
            {"type": "input", "label": "目的设备", "prop": "dest_device_name", "span": 12, "placeholder": "选择或输入目的设备名称"},
            {"type": "input", "label": "目的接口", "prop": "dest_interface", "span": 12, "placeholder": "如：GigabitEthernet0/0/2"},
            {"type": "textarea", "label": "备注", "prop": "remark", "span": 24, "rows": 2},
        ])

        # --- External Broadband form ---
        _seed_form_config(db, "external_broadband_form", "IPS带宽表单", "IPS带宽页面的动态表单配置", [
            {"type": "divider", "label": "线路信息", "span": 24},
            {"type": "select-icon", "label": "运营商", "prop": "operator", "span": 12, "options": [
                {"label": "中国电信", "value": "电信", "icon": "/brand-icons/telecom.png"},
                {"label": "中国联通", "value": "联通", "icon": "/brand-icons/unicom.png"},
                {"label": "中国移动", "value": "移动", "icon": "/brand-icons/mobile.png"},
                {"label": "中国广电", "value": "广电", "icon": "/brand-icons/broadcast.png"},
                {"label": "其他", "value": "其他", "emoji": "🌐"},
            ]},
            {"type": "select", "label": "线路类型", "prop": "line_type", "span": 12, "options": [
                {"label": "专线", "value": "专线"}, {"label": "宽带", "value": "宽带"},
                {"label": "光纤", "value": "光纤"}, {"label": "其他", "value": "其他"},
            ]},
            {"type": "select", "label": "状态", "prop": "status", "span": 12, "defaultValue": "正常", "options": [
                {"label": "正常", "value": "正常"}, {"label": "空闲", "value": "空闲"},
                {"label": "故障", "value": "故障"}, {"label": "停用", "value": "停用"},
            ]},
            {"type": "input", "label": "IP", "prop": "ip_address", "span": 12, "placeholder": "如：202.96.128.86"},
            {"type": "input", "label": "掩码", "prop": "mask", "span": 12, "placeholder": "如：255.255.255.252"},
            {"type": "input", "label": "网关", "prop": "gateway", "span": 12, "placeholder": "如：202.96.128.85"},
            {"type": "input", "label": "拨号账号/接入号", "prop": "dial_account", "span": 12, "placeholder": "拨号账号或接入号"},
            {"type": "input", "label": "对应VLAN", "prop": "vlan", "span": 12, "placeholder": "如：VLAN 100"},
            {"type": "input", "label": "线路带宽", "prop": "bandwidth", "span": 12, "placeholder": "如：100M"},
            {"type": "input", "label": "线路归属", "prop": "ownership", "span": 12, "placeholder": "如：总部/分公司A"},
            {"type": "textarea", "label": "备注", "prop": "remark", "span": 24, "rows": 2},
        ])

        # --- License Management form ---
        _seed_form_config(db, "license_form", "授权管理表单", "授权管理页面的动态表单配置", [
            {"type": "divider", "label": "授权信息", "span": 24},
            {"type": "select-icon", "label": "品牌", "prop": "brand", "span": 12, "options": [
                {"label": "华为", "value": "华为", "icon": "/brand-icons/huawei.png"},
                {"label": "深信服", "value": "深信服", "icon": "/brand-icons/sangfor.png"},
                {"label": "绿盟", "value": "绿盟", "icon": "/brand-icons/nsfocus.png"},
                {"label": "H3C", "value": "H3C", "icon": "/brand-icons/h3c.png"},
                {"label": "信锐", "value": "信锐", "emoji": "📡"},
            ]},
            {"type": "select-cascade", "label": "设备类型", "prop": "device_type", "span": 12, "cascaderOptions": [
                {"label": "网络设备类", "options": [
                    {"label": "交换机", "value": "switch"}, {"label": "路由器", "value": "router"},
                    {"label": "集线器", "value": "hub"}, {"label": "其他设备", "value": "other"},
                ]},
                {"label": "安全设备类", "options": [
                    {"label": "防火墙", "value": "firewall"}, {"label": "上网行为管理", "value": "internet_behavior"},
                    {"label": "堡垒机", "value": "bastion"}, {"label": "IPS", "value": "ips"},
                    {"label": "IDS", "value": "ids"}, {"label": "DDoS", "value": "ddos"},
                    {"label": "VPN", "value": "vpn"}, {"label": "杀毒软件", "value": "antivirus"},
                ]},
                {"label": "其他软件类", "options": [
                    {"label": "准入系统", "value": "admission"}, {"label": "认证系统", "value": "auth"},
                    {"label": "网管系统", "value": "nms"}, {"label": "数据库系统", "value": "database"},
                    {"label": "运维审计系统", "value": "ops_audit"}, {"label": "API网关系统", "value": "api_gateway"},
                ]},
            ]},
            {"type": "select-remote-filtered", "label": "设备名称", "prop": "device_name", "span": 12,
             "placeholder": "先选上方设备类型，再选设备", "remoteUrl": "/assets",
             "remoteLabelKey": "device_name", "remoteValueKey": "device_name",
             "filterProp": "device_type", "filterExtraKeys": ["device_type"]},
            {"type": "input", "label": "授权码", "prop": "license_key", "span": 12, "placeholder": "授权码/序列号"},
            {"type": "date", "label": "激活日期", "prop": "activation_date", "span": 12},
            {"type": "date", "label": "到期日期", "prop": "expiration_date", "span": 12},
            {"type": "select", "label": "状态", "prop": "status", "span": 12, "disabled": True, "options": [
                {"label": "正常", "value": "正常"}, {"label": "临期2月", "value": "临期2月"},
                {"label": "临期1月", "value": "临期1月"}, {"label": "临期15天", "value": "临期15天"},
                {"label": "过期", "value": "过期"},
            ]},
            {"type": "textarea", "label": "备注", "prop": "remark", "span": 24, "rows": 2},
        ])

        # --- IP Allocation form (IP地址分配表) ---
        _seed_form_config(db, "ip_allocation_form", "IP地址分配表表单", "IP地址分配表页面的动态表单配置", [
            {"type": "divider", "label": "基本信息", "span": 24},
            {"type": "input", "label": "部门", "prop": "department", "span": 12, "placeholder": "如：运维部"},
            {"type": "input", "label": "使用人", "prop": "user_name", "span": 12, "placeholder": "如：张三"},
            {"type": "input", "label": "IP地址/掩码", "prop": "ip_address", "required": True, "span": 12, "placeholder": "如：192.168.1.10/24"},
            {"type": "input", "label": "登记人", "prop": "registrar", "span": 12, "placeholder": "如：李四"},
            {"type": "date", "label": "申请日期", "prop": "apply_date", "span": 12},
            {"type": "date", "label": "回收日期", "prop": "recycle_date", "span": 12},
            {"type": "textarea", "label": "备注", "prop": "remark", "span": 24, "rows": 2},
        ])

        print("[Startup] Form configs seeded/updated")
    finally:
        db.close()

    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="IT 综合运维管理系统 API",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/", tags=["健康检查"])
def root():
    """Root endpoint."""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/api/docs",
    }


@app.get("/api/health", tags=["健康检查"])
def health():
    """Health check endpoint."""
    return {"status": "ok"}
