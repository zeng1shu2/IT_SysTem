"""Seed all pages under the "IP管理" (IP Management) menu with demo data:
  - IP地址规划  -> ip_plans        (target: 50)
  - IP地址分配表 -> ip_allocations  (target: 50)
  - 互联IP      -> interconnect_ips (target: 50)

Replicates the field schema / options used by the UI "新增" dialogs:
  - frontend/src/views/ip/ip-plan/index.vue
  - frontend/src/views/ip/ip-allocation/index.vue
  - frontend/src/views/ip/interconnect-ip/index.vue

For 互联IP, source/dest device names are resolved from the assets table and
interface names are taken from port_connections (so they match the dropdowns in the UI).

Idempotent: existing rows are skipped
  (ip_plans by ip_range; ip_allocations by ip_address;
   interconnect_ips by (source_device_id, dest_device_id, ip_range)).
Supports --dry-run (preview) and --rollback (remove seeded rows only).

Seeded rows are tagged in extra_data {"_seed": "AUTO_SEED"} for precise rollback.
"""

import argparse
import json
import os
import sqlite3
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "it_system_os.db")
SEED_TAG = {"_seed": "AUTO_SEED"}


def now_iso():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# ---------------- IP地址规划 (ip_plans): 14 original + 36 generated = 50 ----------------
IP_PLAN_ROWS = [
    ("运维部", "网络组", "192.168.1.0/24", "VLAN 100", "available", "办公网段A"),
    ("运维部", "网络组", "192.168.2.0/24", "VLAN 101", "used", "办公网段B"),
    ("业务部", "应用组", "10.10.1.0/24", "VLAN 200", "used", "业务应用服务器区"),
    ("业务部", "应用组", "10.10.2.0/24", "VLAN 201", "reserved", "业务扩展预留"),
    ("财务部", "财务组", "10.20.0.0/24", "VLAN 300", "reserved", "财务专网预留"),
    ("分公司A", "网络组", "172.16.1.0/24", "VLAN 400", "available", "分公司A办公"),
    ("分公司B", "网络组", "172.16.2.0/24", "VLAN 401", "used", "分公司B办公"),
    ("灾备中心", "运维组", "10.30.0.0/24", "VLAN 500", "available", "灾备互联"),
    ("安防部", "监控组", "192.168.100.0/24", "VLAN 900", "used", "视频监控网"),
    ("无线组", "", "192.168.200.0/24", "VLAN 800", "available", "无线访客网"),
    ("运维部", "服务器组", "10.50.0.0/24", "VLAN 600", "used", "核心服务器区"),
    ("运维部", "管理组", "10.0.0.0/24", "VLAN 99", "reserved", "设备管理网预留"),
    ("安全部", "DMZ组", "192.168.50.0/24", "VLAN 50", "available", "对外DMZ区"),
    ("测试组", "", "10.99.0.0/24", "VLAN 999", "used", "临时测试网段"),
]


def gen_plan_extra(n=36):
    depts = ["运维部", "业务部", "财务部", "分公司D", "分公司E", "分公司F",
             "灾备分中心", "研发部", "安全部", "新办公区"]
    groups = ["网络组", "应用组", "财务组", "运维组", "监控组",
              "服务器组", "管理组", "DMZ组", "测试组", "无线组"]
    stats = ["available", "used", "reserved"]
    rows = []
    for k in range(n):
        d = depts[k % len(depts)]
        g = groups[(k // 2) % len(groups)]
        ip = f"10.{100 + k // 16}.{(k % 16) * 16}.0/24"
        vlan = f"VLAN {1000 + k}"
        s = stats[k % 3]
        rows.append((d, g, ip, vlan, s, f"扩展网段{k + 1}"))
    return rows


def build_ip_plans():
    ts = now_iso()
    return [
        {
            "department": d, "group_name": g or None, "ip_range": r, "vlan": v,
            "usage_status": s, "remark": rem or None,
            "extra_data": json.dumps(SEED_TAG, ensure_ascii=False),
            "created_at": ts, "updated_at": ts,
        }
        for (d, g, r, v, s, rem) in IP_PLAN_ROWS + gen_plan_extra()
    ]


# ---------------- IP地址分配表 (ip_allocations): 15 original + 35 generated = 50 ----------------
IP_ALLOC_ROWS = [
    ("运维部", "张三", "192.168.1.10/24", "2025-03-01", None, "李四", "服务器管理IP"),
    ("运维部", "李四", "192.168.1.11/24", "2025-03-01", None, "李四", "网络设备管理IP"),
    ("业务部", "王五", "10.10.1.20/24", "2025-04-10", None, "赵六", "应用服务器1"),
    ("业务部", "赵六", "10.10.1.21/24", "2025-04-10", None, "赵六", "应用服务器2"),
    ("财务部", "钱七", "10.20.1.5/24", "2025-05-15", None, "孙八", "财务终端"),
    ("财务部", "孙八", "10.20.1.6/24", "2025-05-15", None, "孙八", "财务专机"),
    ("分公司A", "周九", "172.16.1.30/24", "2025-06-01", None, "周九", "分公司A终端"),
    ("分公司B", "吴十", "172.16.2.40/24", "2025-06-10", None, "吴十", "分公司B终端"),
    ("灾备中心", "郑一", "10.30.0.10/24", "2025-07-01", None, "郑一", "灾备服务器"),
    ("安防部", "王二", "192.168.100.5/24", "2025-03-20", None, "王二", "监控摄像头NVR"),
    ("无线组", "冯三", "192.168.200.50/24", "2025-08-01", None, "冯三", "无线AP管理"),
    ("运维部", "陈四", "10.50.0.10/24", "2025-02-15", None, "陈四", "数据库服务器"),
    ("运维部", "褚五", "10.0.0.5/24", "2025-01-10", None, "褚五", "核心交换机管理"),
    ("安全部", "卫六", "192.168.50.8/24", "2025-09-01", None, "卫六", "对外WEB服务器"),
    ("测试组", "蒋七", "10.99.0.15/24", "2025-10-01", "2026-01-15", "蒋七", "临时测试(已回收)"),
]


def gen_alloc_extra(n=35):
    depts = ["运维部", "业务部", "财务部", "分公司D", "分公司E", "研发部", "安全部", "新办公区"]
    users = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸", "子", "丑"]
    regs = ["张三", "李四", "王五", "赵六"]
    rows = []
    for k in range(n):
        d = depts[k % len(depts)]
        u = users[k % len(users)]
        ip = f"10.{200 + k // 16}.{(k % 16) * 16 + 5}/24"
        reg = regs[k % len(regs)]
        rows.append((d, u, ip, "2025-03-01", None, reg, f"扩展分配{k + 1}"))
    return rows


def build_ip_allocations():
    ts = now_iso()
    return [
        {
            "department": d, "user_name": u, "ip_address": ip,
            "apply_date": a, "recycle_date": rc, "remark": rem or None,
            "registrar": reg or None,
            "extra_data": json.dumps(SEED_TAG, ensure_ascii=False),
            "created_at": ts, "updated_at": ts,
        }
        for (d, u, ip, a, rc, reg, rem) in IP_ALLOC_ROWS + gen_alloc_extra()
    ]


# ---------------- 互联IP (interconnect_ips): 10 original + 40 generated = 50 ----------------
# (src_id, src_iface, dst_id, dst_iface, ip_range, remark)
INTERCONNECT_ROWS = [
    (1, "XGE1/0/1", 2, "GE0/0/1", "10.0.0.0/30", "核心-接入交换机互联"),
    (1, "XGE1/0/2", 3, "GE1/0/1", "10.0.0.4/30", "跨楼层接入互联"),
    (1, "XGE1/0/3", 4, "GE0/0/1", "10.0.0.8/30", "核心-演示交换机互联"),
    (1, "XGE1/0/4", 5, "GE0/0/1", "10.0.0.12/30", "核心-出口路由器互联"),
    (5, "GE0/0/2", 8, "GE0/0/1", "10.0.1.0/30", "出口路由器-防火墙互联"),
    (8, "GE0/0/2", 9, "ETH-0", "10.0.2.0/30", "防火墙Trust区互联"),
    (8, "GE0/0/3", 10, "ETH-0", "10.0.3.0/30", "防火墙Untrust区互联"),
    (9, "ETH-1", 11, "ETH-0", "10.0.4.0/30", "Trust-DMZ区互联"),
    (11, "ETH-1", 12, "ETH-0", "10.0.5.0/30", "DMZ-自定义区互联"),
    (6, "GE0/0/1", 7, "ETH-0", "10.0.6.0/30", "集线器-其他设备互联"),
]


def build_interconnect(asset_names):
    rows = []
    for (sid, sif, did, dif, ipr, rem) in INTERCONNECT_ROWS:
        sname = asset_names.get(sid)
        dname = asset_names.get(did)
        if not sname or not dname:
            continue
        rows.append({
            "ip_range": ipr,
            "source_device_id": sid, "source_device_name": sname, "source_interface": sif,
            "dest_device_id": did, "dest_device_name": dname, "dest_interface": dif,
            "remark": rem or None,
            "extra_data": json.dumps(SEED_TAG, ensure_ascii=False),
            "created_at": now_iso(), "updated_at": now_iso(),
        })
    return rows


def build_interconnect_extra(asset_names, port_map, n=40):
    rows = []
    ids = list(asset_names.keys())
    orig_pairs = {tuple(sorted((r[0], r[2]))) for r in INTERCONNECT_ROWS}
    used_pairs = set(orig_pairs)
    i = 0
    while len(rows) < n and i < 8000:
        a = ids[i % len(ids)]
        b = ids[(i * 7 + 5) % len(ids)]
        i += 1
        if a == b:
            continue
        pk = tuple(sorted((a, b)))
        if pk in used_pairs:
            continue
        pa = port_map.get(a)
        pb = port_map.get(b)
        if not pa or not pb:
            continue
        used_pairs.add(pk)
        sif = pa[i % len(pa)]
        dif = pb[(i * 3) % len(pb)]
        ipr = f"10.0.{10 + (len(rows) // 4)}.{(len(rows) % 4) * 4}/30"
        rows.append({
            "ip_range": ipr,
            "source_device_id": a, "source_device_name": asset_names[a], "source_interface": sif,
            "dest_device_id": b, "dest_device_name": asset_names[b], "dest_interface": dif,
            "remark": f"{asset_names[a]}与{asset_names[b]}互联(扩展)",
            "extra_data": json.dumps(SEED_TAG, ensure_ascii=False),
            "created_at": now_iso(), "updated_at": now_iso(),
        })
    return rows


# ---------------- helpers ----------------
def fetch_asset_names(con):
    cur = con.cursor()
    cur.execute("SELECT id, device_name FROM assets")
    return {r[0]: r[1] for r in cur.fetchall()}


def fetch_port_map(con):
    cur = con.cursor()
    cur.execute("SELECT asset_id, ports_data FROM port_connections")
    port_map = {}
    for aid, pd in cur.fetchall():
        try:
            ports = json.loads(pd) if pd else []
            port_map[aid] = [p.get("name") for p in ports if isinstance(p, dict) and p.get("name")]
        except Exception:
            port_map[aid] = []
    return port_map


def exists(con, table, where_cols, row):
    cur = con.cursor()
    where = " AND ".join(f"{c}=?" for c in where_cols)
    cur.execute(f"SELECT 1 FROM {table} WHERE {where}", [row[c] for c in where_cols])
    return cur.fetchone() is not None


def insert_row(con, table, row):
    cols = list(row.keys())
    placeholders = ", ".join("?" for _ in cols)
    con.execute(f"INSERT INTO {table} ({', '.join(cols)}) VALUES ({placeholders})",
                [row[c] for c in cols])


def rollback(con):
    cur = con.cursor()
    removed = 0
    for table in ("ip_plans", "ip_allocations", "interconnect_ips"):
        cur.execute(f"SELECT id, extra_data FROM {table}")
        ids = []
        for rid, ed in cur.fetchall():
            try:
                tagged = ed and json.loads(ed).get("_seed") == "AUTO_SEED"
            except Exception:
                tagged = False
            if tagged:
                ids.append(rid)
        if ids:
            con.execute(f"DELETE FROM {table} WHERE id IN ({','.join('?' for _ in ids)})", ids)
            removed += len(ids)
    con.commit()
    return removed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--rollback", action="store_true")
    args = ap.parse_args()

    con = sqlite3.connect(DB_PATH)
    try:
        if args.rollback:
            print(f"[rollback] removed {rollback(con)} seeded IP-management rows")
            return

        asset_names = fetch_asset_names(con)
        port_map = fetch_port_map(con)
        plan_rows = [r for r in build_ip_plans() if not exists(con, "ip_plans", ["ip_range"], r)]
        alloc_rows = [r for r in build_ip_allocations() if not exists(con, "ip_allocations", ["ip_address"], r)]
        ic_rows = (build_interconnect(asset_names) + build_interconnect_extra(asset_names, port_map))
        ic_rows = [r for r in ic_rows
                   if not exists(con, "interconnect_ips", ["source_device_id", "dest_device_id", "ip_range"], r)]

        print(f"[preview] ip_plans: {len(plan_rows)} | ip_allocations: {len(alloc_rows)} | interconnect_ips: {len(ic_rows)}")

        if args.dry_run:
            for r in plan_rows:
                print(f"  PLAN  {r['department']}/{r['group_name']} {r['ip_range']} {r['vlan']} {r['usage_status']}")
            for r in alloc_rows:
                print(f"  ALLOC {r['department']}/{r['user_name']} {r['ip_address']} 登记:{r['registrar']}")
            for r in ic_rows:
                print(f"  IC    {r['source_device_name']}({r['source_interface']}) <-> {r['dest_device_name']}({r['dest_interface']}) {r['ip_range']}")
            return

        for r in plan_rows:
            insert_row(con, "ip_plans", r)
        for r in alloc_rows:
            insert_row(con, "ip_allocations", r)
        for r in ic_rows:
            insert_row(con, "interconnect_ips", r)
        con.commit()
        print(f"[done] inserted {len(plan_rows)} ip_plan + {len(alloc_rows)} ip_allocation + {len(ic_rows)} interconnect_ip "
              f"(tagged {json.dumps(SEED_TAG, ensure_ascii=False)})")
    finally:
        con.close()


if __name__ == "__main__":
    main()
