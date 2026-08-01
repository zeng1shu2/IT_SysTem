"""一次性数据填充脚本：为资产 inventory 中每台设备生成一条端口互联记录，
并自动填充其物理端口（与前端「新增」弹窗的 resolveAssetPorts 逻辑保持一致）。

用法：
    cd backend
    python seed_port_connections.py            # 执行填充（已存在的设备跳过）
    python seed_port_connections.py --dry-run  # 仅预览，不写库
    python seed_port_connections.py --rollback # 删除本脚本创建的填充记录（按 remark 标记）

说明：
    - 物理端口来源优先级：port_groups(+stack) > eth_count > ETH 族兜底 > port_count 兜底
    - 端口字段映射对齐前端 handleSubmit（port_type 存中文 typeLabel，状态默认 disconnected）
    - 逻辑接口默认留空；remark 写入 'AUTO_SEED' 便于回滚识别
"""

import argparse
import json
import os
import sqlite3
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "it_system_os.db")

# 与 frontend/src/utils/portNaming.js 的 PORT_TYPES 对齐
PORT_TYPES = {
    "ge_elec":  {"prefix": "GE",   "label": "千兆电口", "medium": "elec", "speed": "1g"},
    "ge_opt":   {"prefix": "GE",   "label": "千兆光口", "medium": "opt",  "speed": "1g"},
    "xge_opt":  {"prefix": "XGE",  "label": "万兆光口", "medium": "opt",  "speed": "10g"},
    "40g_opt":  {"prefix": "40XGE","label": "40G光口",  "medium": "opt",  "speed": "40g"},
    "100g_opt": {"prefix": "100XGE","label": "100G光口","medium": "opt",  "speed": "100g"},
}

ETH_FAMILY_DEVICE_TYPES = [
    "other", "hub", "internet_behavior", "bastion", "ips", "ids",
    "ddos", "vpn", "antivirus", "admission", "auth", "nms",
    "database", "ops_audit", "api_gateway",
]


def generate_ports(port_groups, stack_config):
    groups = port_groups if isinstance(port_groups, list) else []
    stack_enabled = bool(stack_config and stack_config.get("enabled"))
    stack_count = max(1, int(stack_config.get("count") or 1)) if stack_enabled else 0
    member_loops = stack_count if stack_enabled else 1
    ports = []
    for m in range(1, member_loops + 1):
        slot = m if stack_enabled else 0
        for g in groups:
            defn = PORT_TYPES.get(g.get("type"))
            if not defn:
                continue
            count = int(g.get("count") or 0)
            for i in range(1, count + 1):
                ports.append({
                    "name": f"{defn['prefix']}{slot}/0/{i}",
                    "type": g.get("type"),
                    "typeLabel": defn["label"],
                    "medium": defn["medium"],
                    "speed": defn["speed"],
                    "prefix": defn["prefix"],
                    "member": m if stack_enabled else None,
                    "index": i,
                    "net_type": "access",
                    "vlan_id": "",
                    "vlan_range": "",
                })
    return ports


def generate_eth_ports(eth_count=1):
    count = max(1, int(eth_count) or 1)
    ports = []
    for i in range(count):
        ports.append({
            "name": f"ETH-{i}",
            "type": "eth",
            "typeLabel": "ETH接口",
            "medium": "",
            "speed": "",
            "prefix": "ETH",
            "member": None,
            "index": i + 1,
            "net_type": "access",
            "vlan_id": "",
            "vlan_range": "",
        })
    return ports


def resolve_asset_ports(asset):
    """对齐 frontend resolveAssetPorts：typed port_groups > eth_count > ETH 族 > port_count 兜底。"""
    extra = asset.get("extra_data") or {}
    pg = extra.get("port_groups")
    if isinstance(pg, list) and len(pg) > 0:
        gen = generate_ports(pg, extra.get("stack_config"))
        if gen:
            return gen
    ec = extra.get("eth_count")
    if ec and int(ec) >= 1:
        return generate_eth_ports(ec)
    if asset.get("device_type") in ETH_FAMILY_DEVICE_TYPES:
        return generate_eth_ports(1)
    fb = int(extra.get("port_count") or 0)
    if fb > 0:
        return [{
            "name": f"端口{i + 1}", "type": "", "typeLabel": "", "medium": "",
            "speed": "", "prefix": "", "member": None, "index": i + 1,
            "net_type": "access", "vlan_id": "", "vlan_range": "",
        } for i in range(fb)]
    return []


def to_ports_data(resolved):
    """对齐前端 handleSubmit 的 ports_data 字段映射（port_type 存中文 typeLabel）。"""
    out = []
    for i, p in enumerate(resolved):
        out.append({
            "index": i + 1,
            "name": p.get("name") or f"端口{i + 1}",
            "port_type": p.get("typeLabel") or "",
            "medium": p.get("medium") or "",
            "speed": p.get("speed") or "",
            "member": p.get("member") or None,
            "net_type": p.get("net_type") or "access",
            "vlan_id": p.get("vlan_id") or "",
            "vlan_range": p.get("vlan_range") or "",
            "connected_device_id": None,
            "connected_device": "",
            "connected_interface": "",
            "remote_net_type": "access",
            "remote_vlan_id": "",
            "remote_vlan_range": "",
            "status": "disconnected",
            "remark": "",
        })
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="仅预览不写库")
    ap.add_argument("--rollback", action="store_true", help="删除 AUTO_SEED 填充记录")
    args = ap.parse_args()

    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    if args.rollback:
        cur.execute("DELETE FROM port_connections WHERE remark = 'AUTO_SEED'")
        n = cur.rowcount
        con.commit()
        print(f"[rollback] 已删除 {n} 条 AUTO_SEED 填充记录")
        con.close()
        return

    cur.execute("SELECT id, device_name, device_type, extra_data FROM assets ORDER BY id")
    assets = cur.fetchall()
    cur.execute("SELECT asset_id FROM port_connections")
    existing = {r[0] for r in cur.fetchall()}

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    created, skipped = [], []

    for a in assets:
        aid = a["id"]
        if aid in existing:
            skipped.append(aid)
            continue
        extra = json.loads(a["extra_data"]) if a["extra_data"] else {}
        asset_dict = {"device_type": a["device_type"], "extra_data": extra}
        resolved = resolve_asset_ports(asset_dict)
        ports_data = to_ports_data(resolved)
        payload = (
            aid,
            a["device_name"],
            len(ports_data),
            json.dumps(ports_data, ensure_ascii=False),
            json.dumps([], ensure_ascii=False),
            "AUTO_SEED",
            json.dumps({}, ensure_ascii=False),
            now,
            now,
        )
        if args.dry_run:
            created.append((aid, a["device_name"], len(ports_data)))
            continue
        cur.execute(
            "INSERT INTO port_connections "
            "(asset_id, asset_name, port_count, ports_data, logical_interfaces, remark, extra_data, created_at, updated_at) "
            "VALUES (?,?,?,?,?,?,?,?,?)",
            payload,
        )
        created.append((aid, a["device_name"], len(ports_data)))

    con.commit()
    con.close()

    if args.dry_run:
        print("[dry-run] 以下设备将被填充（不写库）：")
    else:
        print("[done] 已填充以下设备的端口互联记录：")
    port_total = 0
    for aid, name, pc in created:
        print(f"  asset_id={aid:<3} {name:<28} 物理端口数={pc}")
        port_total += pc
    print(f"新增记录: {len(created)} 条，跳过已存在: {len(skipped)} 条，合计物理端口: {port_total}")
    if not args.dry_run and skipped:
        print(f"（已跳过 asset_id: {skipped}）")


if __name__ == "__main__":
    main()
