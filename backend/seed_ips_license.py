"""Seed IPS带宽(external_broadbands) and 授权管理(license_managements) with demo data.

Replicates what the UI "新增" dialog would create per record, so the data matches
the column schema / options defined in:
  - frontend/src/views/asset/external-broadband/index.vue
  - frontend/src/views/asset/license/index.vue

Target: 50 rows each.

Idempotent: existing rows are skipped
  (external_broadband by operator+line_type+ip_address; license by asset_id).
Supports --dry-run (preview) and --rollback (remove seeded rows only).

Seeded rows are tagged in extra_data {"_seed": "AUTO_SEED"} so --rollback can remove
exactly these without touching manually-added records.
"""

import argparse
import hashlib
import json
import os
import random
import sqlite3
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "it_system_os.db")
SEED_TAG = {"_seed": "AUTO_SEED"}


# ---- mirror of LicenseManagement.compute_status (backend/app/models/asset_modules.py) ----
def compute_status(activation_date=None, expiration_date=None, now=None):
    if expiration_date is None:
        return "正常"
    if now is None:
        now = datetime.now()
    if isinstance(expiration_date, str):
        expiration_date = datetime.fromisoformat(expiration_date)
    if isinstance(now, str):
        now = datetime.fromisoformat(now)
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


# ---- brand mapping by device_type (mirrors vendor bar options / device categories) ----
SECURITY_DEEP = {"firewall", "internet_behavior", "vpn", "antivirus"}  # 深信服
SOFTWARE_TYPES = {"admission", "auth", "nms", "database", "ops_audit", "api_gateway"}


def brand_for(device_type):
    if device_type in SECURITY_DEEP:
        return "深信服"
    if device_type in {"ids", "ips", "ddos", "bastion"}:
        return "绿盟"
    if device_type in SOFTWARE_TYPES:
        return "信锐"
    if device_type in {"switch", "router"}:
        return "华为"
    return "H3C"  # hub / other


def gen_key(brand):
    prefix = {"华为": "HW", "H3C": "H3C", "深信服": "SF", "绿盟": "NS", "信锐": "XR"}[brand]
    block = lambda: "".join(random.choices("0123456789ABCDEF", k=4))
    return f"{prefix}-{block()}-{block()}-{block()}-{block()}"


def now_iso():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# ---- IPS带宽 (external_broadbands): 12 original + 38 generated = 50 ----
EXTERNAL_ROWS = [
    ("电信", "专线", "正常", "202.96.128.86", "255.255.255.252", "202.96.128.85",
     "kd0293847@telecom", "100", "500M", "总部数据中心", "主用互联网出口"),
    ("联通", "专线", "正常", "58.246.80.10", "255.255.255.252", "58.246.80.9",
     "", "101", "500M", "总部数据中心", "备用互联网出口"),
    ("移动", "宽带", "正常", "120.80.40.2", "255.255.255.248", "120.80.40.1",
     "yd88291002", "102", "200M", "分公司A", "分公司A办公上网"),
    ("广电", "光纤", "空闲", "113.66.10.20", "255.255.255.252", "113.66.10.19",
     "", "103", "100M", "分公司B", "待启用"),
    ("电信", "宽带", "故障", "61.135.169.121", "255.255.255.252", "61.135.169.122",
     "dx55120933", "104", "100M", "分公司B", "线路故障待维修"),
    ("联通", "专线", "停用", "125.35.6.8", "255.255.255.252", "125.35.6.7",
     "", "105", "300M", "总部数据中心", "已停用(合同到期)"),
    ("移动", "专线", "正常", "183.232.20.30", "255.255.255.252", "183.232.20.29",
     "", "106", "1G", "灾备中心", "灾备专线"),
    ("电信", "光纤", "正常", "202.101.33.50", "255.255.255.252", "202.101.33.49",
     "", "107", "1G", "灾备中心", "灾备互联"),
    ("广电", "宽带", "空闲", "211.91.88.6", "255.255.255.248", "211.91.88.1",
     "gd77001234", "108", "200M", "分公司C", "分公司C备用"),
    ("联通", "宽带", "正常", "60.10.20.40", "255.255.255.248", "60.10.20.33",
     "lt66009876", "109", "100M", "分公司C", "分公司C办公"),
    ("移动", "光纤", "正常", "111.30.130.8", "255.255.255.252", "111.30.130.7",
     "", "110", "500M", "总部数据中心", "视频会议专线"),
    ("电信", "专线", "正常", "219.143.12.18", "255.255.255.252", "219.143.12.17",
     "", "111", "200M", "总部数据中心", "厂商远程维护专线"),
]


def gen_external_extra(n=38):
    rows = []
    owners = ["分公司D", "分公司E", "分公司F", "灾备分中心", "新办公区",
              "总部B栋", "研发中心", "数据中心2", "边缘节点", "海外节点"]
    op = ["电信", "联通", "移动", "广电"]
    lt = ["专线", "宽带", "光纤"]
    st = ["正常", "空闲", "故障", "停用"]
    bw = ["100M", "200M", "500M", "1G"]
    for k in range(n):
        o = op[k % 4]
        l = lt[(k // 4) % 3]
        s = st[(k // 12) % 4]
        b = bw[(k // 2) % 4]
        seg = 30 + (k // 4)
        host = 2 + (k % 4) * 2
        ip = f"10.{seg}.0.{host}"
        mask = "255.255.255.252"
        gw = f"10.{seg}.0.{host - 1}"
        owner = owners[k % len(owners)]
        vlan = str(2000 + k)
        remark = f"{owner}{l}线路"
        rows.append((o, l, s, ip, mask, gw, "", vlan, b, owner, remark))
    return rows


def build_external_rows():
    ts = now_iso()
    rows = []
    for (operator, line_type, status, ip, mask, gw, dial, vlan, bw, owner, remark) in EXTERNAL_ROWS + gen_external_extra():
        rows.append({
            "operator": operator,
            "line_type": line_type,
            "status": status,
            "ip_address": ip,
            "mask": mask,
            "gateway": gw,
            "dial_account": dial or None,
            "vlan": vlan,
            "bandwidth": bw,
            "ownership": owner,
            "remark": remark,
            "extra_data": json.dumps(SEED_TAG, ensure_ascii=False),
            "created_at": ts,
            "updated_at": ts,
        })
    return rows


# ---- 授权管理 (license_managements): one per asset, deterministic dates -> status mix ----
def dates_for(aid):
    h = int(hashlib.md5(str(aid).encode()).hexdigest(), 16)
    now = datetime.now()
    offset = (h % 600) - 200          # expiration: -200 .. +399 days from now
    exp = now + timedelta(days=offset)
    act = now - timedelta(days=400 + (h % 300))
    return act.strftime("%Y-%m-%d"), exp.strftime("%Y-%m-%d")


def build_license_rows(assets):
    ts = now_iso()
    rows = []
    for (aid, name, dtype) in assets:
        act, exp = dates_for(aid)
        brand = brand_for(dtype)
        status = compute_status(activation_date=act, expiration_date=exp)
        rows.append({
            "brand": brand,
            "device_type": dtype,
            "asset_id": aid,
            "device_name": name,
            "license_key": gen_key(brand),
            "activation_date": act,
            "expiration_date": exp,
            "status": status,
            "remark": f"{name} {brand}授权(自动填充)",
            "extra_data": json.dumps(SEED_TAG, ensure_ascii=False),
            "created_at": ts,
            "updated_at": ts,
        })
    return rows


def fetch_assets(con):
    cur = con.cursor()
    cur.execute("SELECT id, device_name, device_type FROM assets ORDER BY id")
    return [(r[0], r[1], r[2]) for r in cur.fetchall()]


def exists_external(con, row):
    cur = con.cursor()
    cur.execute(
        "SELECT 1 FROM external_broadbands WHERE operator=? AND line_type=? AND ip_address=?",
        (row["operator"], row["line_type"], row["ip_address"]),
    )
    return cur.fetchone() is not None


def exists_license(con, row):
    cur = con.cursor()
    cur.execute("SELECT 1 FROM license_managements WHERE asset_id=?", (row["asset_id"],))
    return cur.fetchone() is not None


def insert_row(con, table, row):
    cols = list(row.keys())
    placeholders = ", ".join("?" for _ in cols)
    sql = f"INSERT INTO {table} ({', '.join(cols)}) VALUES ({placeholders})"
    con.execute(sql, [row[c] for c in cols])


def rollback(con):
    cur = con.cursor()
    removed = 0
    for table in ("external_broadbands", "license_managements"):
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
            q = f"DELETE FROM {table} WHERE id IN ({','.join('?' for _ in ids)})"
            cur.execute(q, ids)
            removed += len(ids)
    con.commit()
    return removed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="preview only, no writes")
    ap.add_argument("--rollback", action="store_true", help="remove seeded rows only")
    args = ap.parse_args()

    con = sqlite3.connect(DB_PATH)
    try:
        if args.rollback:
            n = rollback(con)
            print(f"[rollback] removed {n} seeded rows from external_broadbands + license_managements")
            return

        assets = fetch_assets(con)
        ext_rows = build_external_rows()
        lic_rows = build_license_rows(assets)

        # idempotency filter
        ext_rows = [r for r in ext_rows if not exists_external(con, r)]
        lic_rows = [r for r in lic_rows if not exists_license(con, r)]

        print(f"[preview] external_broadbands to insert: {len(ext_rows)} (total assets: {len(assets)})")
        print(f"[preview] license_managements to insert: {len(lic_rows)} (total assets: {len(assets)})")

        if args.dry_run:
            for r in ext_rows:
                print(f"  EXT  {r['operator']}/{r['line_type']}/{r['status']} {r['ip_address']} {r['bandwidth']} -> {r['ownership']}")
            for r in lic_rows:
                print(f"  LIC  {r['brand']}/{r['device_type']} {r['device_name']} {r['status']} key={r['license_key']}")
            return

        for r in ext_rows:
            insert_row(con, "external_broadbands", r)
        for r in lic_rows:
            insert_row(con, "license_managements", r)
        con.commit()
        print(f"[done] inserted {len(ext_rows)} external_broadband + {len(lic_rows)} license rows "
              f"(tagged {json.dumps(SEED_TAG, ensure_ascii=False)} in extra_data)")
    finally:
        con.close()


if __name__ == "__main__":
    main()
