"""Add 33 demo devices to the inventory so the port-connection / license modules can reach 50 rows.

These devices are needed because port_connections is 1-record-per-asset (17 real devices existed,
so it capped at 17). Adding 33 demo devices lets port_connections + license_managements hit 50.

Idempotent: device_name already present -> skipped. New devices are tagged in
extra_data {"_seed_device": "AUTO_SEED"} and carry port config (port_groups / eth_count) so the
port-connection seeder can populate their physical ports.

Usage:
  cd backend
  python seed_devices.py            # add 33 demo devices (skips existing)
  python seed_devices.py --dry-run  # preview
  python seed_devices.py --rollback # remove these devices + their dependent AUTO_SEED rows
"""

import argparse
import json
import os
import sqlite3
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "it_system_os.db")
SEED_TAG = {"_seed_device": "AUTO_SEED"}

# (device_name, device_type, port_config)
# port_config: {"port_groups":[{type,count},...]} for switches/routers, else {"eth_count": N}
DEVICES = [
    ("YF3F-ACC-SW", "switch", {"port_groups": [{"type": "ge_opt", "count": 24}, {"type": "xge_opt", "count": 4}]}),
    ("YF4F-ACC-SW", "switch", {"port_groups": [{"type": "ge_elec", "count": 48}]}),
    ("YD-BR-ACC-SW01", "switch", {"port_groups": [{"type": "ge_elec", "count": 24}, {"type": "ge_opt", "count": 4}]}),
    ("YD-BR-ACC-SW02", "switch", {"port_groups": [{"type": "ge_elec", "count": 24}, {"type": "ge_opt", "count": 4}]}),
    ("BR-CORE-RT01", "router", {"eth_count": 4}),
    ("BR-CORE-RT02", "router", {"eth_count": 4}),
    ("BR-FW-01", "firewall", {"eth_count": 8}),
    ("BR-FW-02", "firewall", {"eth_count": 8}),
    ("BR-IPS-01", "ips", {"eth_count": 4}),
    ("BR-IDS-01", "ids", {"eth_count": 2}),
    ("BR-DDoS-01", "ddos", {"eth_count": 2}),
    ("BR-VPN-01", "vpn", {"eth_count": 4}),
    ("BR-BASTION-01", "bastion", {"eth_count": 2}),
    ("SEC-IPS-02", "ips", {"eth_count": 4}),
    ("SEC-IDS-02", "ids", {"eth_count": 2}),
    ("SYS-AD-01", "admission", {"eth_count": 2}),
    ("SYS-AUTH-01", "auth", {"eth_count": 2}),
    ("SYS-NMS-01", "nms", {"eth_count": 2}),
    ("SYS-DB-01", "database", {"eth_count": 2}),
    ("SYS-AUDIT-01", "ops_audit", {"eth_count": 2}),
    ("SYS-API-01", "api_gateway", {"eth_count": 2}),
    ("HUB-BR-01", "hub", {"eth_count": 4}),
    ("HUB-BR-02", "hub", {"eth_count": 4}),
    ("OTHER-PRINT-01", "other", {"eth_count": 1}),
    ("OTHER-CAM-01", "other", {"eth_count": 1}),
    ("AV-EDR-01", "antivirus", {"eth_count": 2}),
    ("IB-BEHAVIOR-01", "internet_behavior", {"eth_count": 2}),
    ("WL-AC-01", "nms", {"eth_count": 2}),
    ("WL-AC-02", "nms", {"eth_count": 2}),
    ("STOR-NAS-01", "database", {"eth_count": 2}),
    ("STOR-SAN-01", "database", {"eth_count": 2}),
    ("LB-01", "api_gateway", {"eth_count": 4}),
    ("CLOUD-GW-01", "router", {"eth_count": 4}),
]


def now_iso():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def fetch_existing_names(con):
    cur = con.cursor()
    cur.execute("SELECT device_name FROM assets")
    return {r[0] for r in cur.fetchall()}


def insert_row(con, name, dtype, port_config):
    extra = dict(port_config)
    extra.update(SEED_TAG)
    ts = now_iso()
    con.execute(
        "INSERT INTO assets (device_type, device_name, status, created_at, updated_at, extra_data) "
        "VALUES (?,?,?,?,?,?)",
        (dtype, name, "in_use", ts, ts, json.dumps(extra, ensure_ascii=False)),
    )


def rollback(con):
    cur = con.cursor()
    cur.execute("SELECT id FROM assets WHERE extra_data LIKE ?", ("%" + "_seed_device" + "%",))
    ids = [r[0] for r in cur.fetchall()]
    if not ids:
        print("[rollback] no seed devices found")
        return 0
    ph = ",".join("?" * len(ids))
    cur.execute(f"DELETE FROM interconnect_ips WHERE source_device_id IN ({ph}) OR dest_device_id IN ({ph})", ids * 2)
    cur.execute(f"DELETE FROM license_managements WHERE asset_id IN ({ph})", ids)
    cur.execute(f"DELETE FROM port_connections WHERE asset_id IN ({ph})", ids)
    cur.execute(f"DELETE FROM assets WHERE id IN ({ph})", ids)
    con.commit()
    return len(ids)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--rollback", action="store_true")
    args = ap.parse_args()

    con = sqlite3.connect(DB_PATH)
    try:
        if args.rollback:
            n = rollback(con)
            print(f"[rollback] removed {n} seed devices + their dependent AUTO_SEED rows")
            return

        existing = fetch_existing_names(con)
        to_add = [(n, d, p) for (n, d, p) in DEVICES if n not in existing]

        if args.dry_run:
            print(f"[dry-run] devices to add: {len(to_add)} (existing inventory: {len(existing)})")
            for n, d, p in to_add:
                print(f"  + {n} [{d}] ports={p}")
            return

        for n, d, p in to_add:
            insert_row(con, n, d, p)
        con.commit()
        print(f"[done] added {len(to_add)} demo devices (tagged {json.dumps(SEED_TAG, ensure_ascii=False)}); "
              f"re-run seed_port_connections.py + seed_ips_license.py to populate their ports/licenses")
    finally:
        con.close()


if __name__ == "__main__":
    main()
