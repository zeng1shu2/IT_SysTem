# 上手指南（ONBOARDING）

面向新加入本项目的开发者。按本指南操作即可在本地跑起完整项目与演示数据。

---

## 1. 环境要求

| 工具 | 版本 | 说明 |
|---|---|---|
| Python | 3.11+ | 后端运行时（项目内置 venv 隔离） |
| Node.js | 18+ | 前端运行时 |
| 包管理 | pip / npm | 后端用 pip，前端用 npm（已锁定 `package-lock.json`） |

> 数据库使用 SQLite（`backend/it_system_os.db`），**已被 `.gitignore` 忽略，不入库**。
> 每人本地各有一份，通过下面的 seed 脚本获得完全一致的演示数据。

---

## 2. 克隆与安装

```bash
git clone <远程仓库地址>
cd IT_SysTem_OS
```

### 2.1 后端

```bash
cd backend
python -m venv venv            # 创建隔离环境
source venv/Scripts/activate   # Windows；macOS/Linux 用 source venv/bin/activate
pip install -r requirements.txt

# 复制并填写配置
cp .env.example .env           # 按实际情况修改（默认 SQLite 即可）
```

### 2.2 前端

```bash
cd frontend
npm ci                         # 用 lockfile 保证依赖版本一致（不要用 npm install 随意升级）
```

---

## 3. 初始化数据库与演示数据（一键）

在项目 `backend/` 目录下执行：

```bash
cd backend
python seed_all.py
```

`seed_all.py` 会：
1. 先确保全部表已创建（等价于启动一次后端，包含端口/IPS/授权/IP 等模块表）；
2. 按依赖顺序灌入演示数据：
   - `seed_devices.py`          → 资产库存（含 33 台 demo 设备）
   - `seed_port_connections.py` → 端口互联（每台设备一套物理端口）
   - `seed_ips_license.py`      → IPS 带宽 + 授权管理
   - `seed_ip_management.py`    → IP 规划 / IP 分配 / 互联 IP

> 每个脚本**幂等**：已存在的数据会自动跳过，可反复运行。
> 如需清空本次演示数据：依次对脚本加 `--rollback`，或运行 `python seed_devices.py --rollback`（会连带清理依赖它的子表）。

---

## 4. 启动

```bash
# 终端 1：后端（默认 http://127.0.0.1:8000）
cd backend && source venv/Scripts/activate
uvicorn app.main:app --reload

# 终端 2：前端（默认 http://127.0.0.1:5173）
cd frontend
npm run dev
```

打开前端地址即可看到各模块已填充演示数据。

---

## 5. 协作规范（重要，避免冲突）

### 5.1 分支模型
- `master`：**稳定/发版分支，受保护**，禁止直接 push，必须走 PR/MR。
- `develop`：**日常集成分支**，两人都从它拉功能分支、合回它。
- 功能分支命名：`feature/<模块>-<页面>`，例如 `feature/asset-stack-config`。
- 流程：从 `develop` 拉分支 → 开发 → 提 PR 到 `develop` → 评审合并 → 稳定后 `develop` 合 `master`。

### 5.2 共享文件（改动需知会对方，避免冲突）
- `frontend/src/constants/columnWidths.js`：**列宽唯一来源**，任何列表列宽调整都改这里。
- `frontend/src/components/IdColumn.vue`：ID/序号列统一组件。
- `frontend/src/router/index.js`：新页面都在此注册路由，约定**按模块分段/前缀**。
- `frontend/src/constants/vendors.js`：品牌/设备类型元数据。
- `frontend/src/api/form_config.js` + 后端 `form_config`：动态表单配置。
- `package.json` / `requirements.txt`：加依赖时务必沟通，避免锁文件冲突。

### 5.3 UI 约定（保持风格统一）
- 列表页优先使用 `CrudTablePage` 组件，列宽统一走 `colWidth(key)`。
- 设备/资产相关页面复用 `resolveAssetPorts` 等工具函数。
- 新增品牌图标放到 `frontend/public/icons/`。

### 5.4 数据同步
- 数据库每人本地一份，**不共享**（gitignore）。需要一致演示数据时，各自运行 `seed_all.py`。
- 如需共享真实业务数据，再单独导出 `*.db` 或引入迁移工具（Alembic）。

---

## 6. 常见问题

- **页面表格是空的？** 多半是没跑 `seed_all.py`。该脚本也会建表，先跑一次。
- **改了列宽不生效？** 确认是否改在 `columnWidths.js`，并浏览器硬刷新（Ctrl+Shift+R）。
- **换行符满屏差异？** 项目已加 `.gitattributes`（`* text=auto`）；新克隆不会再有此问题。
- **后端启动报缺少模块？** 确认已 `pip install -r requirements.txt` 且激活了 venv。
