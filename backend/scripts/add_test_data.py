"""Add test asset data for demo."""
import urllib.request
import json

# Login
login_data = json.dumps({"username": "admin", "password": "admin123"}).encode()
req = urllib.request.Request(
    "http://127.0.0.1:8000/api/v1/auth/login",
    data=login_data,
    headers={"Content-Type": "application/json"},
)
resp = urllib.request.urlopen(req)
token = json.loads(resp.read())["access_token"]
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

# Check existing
req = urllib.request.Request("http://127.0.0.1:8000/api/v1/assets?skip=0&limit=100", headers=headers)
resp = urllib.request.urlopen(req)
data = json.loads(resp.read())
print(f"Existing assets: {data['total']}")

if data["total"] >= 5:
    print("Already have enough test data, skipping.")
    exit()

test_assets = [
    {"device_name": "核心交换机-01", "device_type": "switch", "brand": "华为", "model": "S5700-28C-HI", "ip_address": "192.168.1.1", "mac_address": "00:1A:2B:3C:4D:5E", "serial_number": "SN202401001", "location": "机房A-机柜01-U05", "status": "in_use", "purchase_date": "2024-01-15", "warranty_expire": "2027-01-15", "remark": "核心网络交换机，承载全楼网络"},
    {"device_name": "边界防火墙-01", "device_type": "firewall", "brand": "山石", "model": "SG-6000-E2860", "ip_address": "10.0.0.1", "mac_address": "00:2B:3C:4D:5E:6F", "serial_number": "SN202401002", "location": "机房A-机柜02-U01", "status": "in_use", "purchase_date": "2024-02-20", "warranty_expire": "2027-02-20", "remark": "互联网边界防火墙"},
    {"device_name": "出口路由器-01", "device_type": "router", "brand": "思科", "model": "ISR4331", "ip_address": "10.0.0.254", "mac_address": "00:3C:4D:5E:6F:70", "serial_number": "SN202401003", "location": "机房A-机柜02-U10", "status": "in_use", "purchase_date": "2024-03-10", "warranty_expire": "2027-03-10", "remark": "互联网出口路由器"},
    {"device_name": "IDS入侵检测-01", "device_type": "security", "brand": "绿盟", "model": "NIDS-5000", "ip_address": "192.168.2.100", "mac_address": "00:4D:5E:6F:70:81", "serial_number": "SN202401004", "location": "机房B-机柜01-U03", "status": "idle", "purchase_date": "2024-04-05", "warranty_expire": "2026-04-05", "remark": "备用入侵检测设备"},
    {"device_name": "接入交换机-02", "device_type": "switch", "brand": "华三", "model": "S5120V3-28S-LI", "ip_address": "192.168.3.1", "mac_address": "00:5E:6F:70:81:92", "serial_number": "SN202401005", "location": "机房B-机柜03-U12", "status": "maintenance", "purchase_date": "2023-06-18", "warranty_expire": "2025-06-18", "remark": "楼层接入交换机，正在维护中"},
]

for asset in test_assets:
    req = urllib.request.Request(
        "http://127.0.0.1:8000/api/v1/assets",
        data=json.dumps(asset).encode(),
        headers=headers,
    )
    resp = urllib.request.urlopen(req)
    result = json.loads(resp.read())
    print(f"  Created: {result['device_name']} (id={result['id']})")

print(f"Total created: {len(test_assets)}")
