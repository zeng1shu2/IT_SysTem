"""一键初始化数据库并灌入全部演示数据（供新成员本地快速上手）。

执行顺序（后者依赖前者）：
  1. seed_devices.py         -> 资产库存（含 33 台 demo 设备，撑满端口互联/授权到 50 条）
  2. seed_port_connections.py-> 端口互联（每台设备一套物理端口）
  3. seed_ips_license.py     -> IPS 带宽 + 授权管理
  4. seed_ip_management.py   -> IP 规划 / IP 分配 / 互联 IP

说明：
  - 首次运行会先确保全部表已创建（等价于启动一次后端）；
  - 所有脚本均幂等：已存在的记录会自动跳过，可反复运行；
  - 如需清空本次演示数据：依次对各脚本加 --rollback 参数，或运行 seed_devices.py --rollback。
"""

import os
import sys
import subprocess

# 让脚本在 backend 目录下可被直接执行（python seed_all.py）
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

# 1) 确保全部表已创建（包含 asset_modules 等不一定被 __init__ 导入的模型）
from app.database import engine, Base  # noqa: E402
import app.models  # noqa: E402 基础模型
import app.models.asset_modules  # noqa: E402 端口/IPS/授权/IP 等表
import app.models.icon  # noqa: E402
import app.models.system_field  # noqa: E402

print("==> 确保数据库表结构已创建 ...")
Base.metadata.create_all(bind=engine)
print("==> 表结构就绪。\n")

# 2) 按依赖顺序执行各 seed 脚本
SEEDS = [
    "seed_devices.py",
    "seed_port_connections.py",
    "seed_ips_license.py",
    "seed_ip_management.py",
]

for script in SEEDS:
    path = os.path.join(BASE_DIR, script)
    if not os.path.exists(path):
        print(f"[跳过] 未找到 {script}")
        continue
    print(f"\n===== 运行 {script} =====")
    # 子脚本写库，沿用当前进程的 SQLite 连接环境；在需要权限的沙箱中需放行
    result = subprocess.run([sys.executable, path], cwd=BASE_DIR)
    if result.returncode != 0:
        print(f"[错误] {script} 执行失败（返回码 {result.returncode}），已中止。")
        sys.exit(result.returncode)

print("\n✅ 全部演示数据已就绪。启动后端 / 前端即可查看（前端无需重新构建）。")
