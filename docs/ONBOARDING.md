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

### 5.1 分支模型（主开发者集成制）
本项目采用「主开发者集成」模式：**A 为主开发、B 为副开发**。

- `master`：**稳定/发版分支，受保护**，禁止直接 push，必须走 PR。当 A 在 develop 完成并做最终优化后，提 `develop → master` 的 PR 合入，即为官方正式版。
- `develop`（= dev-A，A 的分支）：**主开发 + 集成分支**。A 的日常开发在此进行，并负责接收 B 的合并（A 即审核人）。
- `dev-B`（B 的分支）：**副开发者 B 的长期分支**，从 `develop` 拉出。B 在此开发，功能完成即 PR 合回 `develop`。

- 流程：B `git checkout -b dev-B origin/develop` → 开发 → 提 PR（dev-B → develop）→ A 评审合并 → 稳定后 A 提 PR（develop → master）。
- 关键习惯（避免冲突）：
  1. B **每完成一个小功能就合并到 develop**，不要憋到最后一次性大合并——两根长期分支时间越久越分叉，冲突会累积成山；
  2. B 定期 `git rebase develop` 把 dev-B 跟 develop 同步，避免落后太多。
- 功能分支命名（如需更细拆分）：`feature/<模块>-<页面>`，例如 `feature/asset-stack-config`，从 `develop` 拉取。

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

### 5.5 PR 模板与合并检查清单（dev-B → develop）

B 完成功能后，在 GitHub 提 **dev-B → develop** 的 PR。下面是可复用的清单与模板。

**B 提 PR 前自查：**
- [ ] 已从 `develop` 拉取最新并 `git rebase develop`，无落后主干的冲突
- [ ] 本地后端能启动、前端 `npm run build` 无报错
- [ ] 若动了共享文件（`columnWidths.js` / `router/index.js` / `vendors.js` / `form_config` / `package.json` / `requirements.txt`），已在 PR 描述里说明
- [ ] 若新增/改了表结构或演示数据，已同步更新对应 `seed_*.py`（保证 `seed_all.py` 仍可一键复跑）
- [ ] 自测功能正常，控制台无遗留报错

**PR 描述模板（直接粘贴到 PR 正文）：**
```
## 改动说明
<一句话说清做了什么>

## 关联模块 / 路由 / 表
<页面或接口>

## 共享文件改动
<有/无；有的话列出来并说明原因>

## 自测结果
<怎么测的、结果如何>
```

**A（审核人）合并前检查：**
- [ ] 代码 review 通过，风格符合 5.3 UI 约定
- [ ] 本地/CI 构建无报错
- [ ] 确认没有把 `*.db`、`.env`、密钥带进提交（gitignore 已挡，double check）
- [ ] 合并方式：优先 **Squash merge**（把 B 的多个 WIP 提交压成一个干净提交）；保持 `develop` 历史线性
- [ ] 合并后 `develop` 仍能 `seed_all.py` + 正常启动

---

## 6. 常见问题

- **页面表格是空的？** 多半是没跑 `seed_all.py`。该脚本也会建表，先跑一次。
- **改了列宽不生效？** 确认是否改在 `columnWidths.js`，并浏览器硬刷新（Ctrl+Shift+R）。
- **换行符满屏差异？** 项目已加 `.gitattributes`（`* text=auto`）；新克隆不会再有此问题。
- **后端启动报缺少模块？** 确认已 `pip install -r requirements.txt` 且激活了 venv。

---

## 7. master 保护分支设置（GitHub 网页操作）

`master` 是官方发版分支，必须设为受保护、禁止直接 push，强制走 PR。由仓库管理员（A）在 GitHub 网页完成：

1. 打开仓库页面 `https://github.com/zeng1shu2/IT_SysTem`，点右上角 **Settings**。
2. 左侧 **Branches**（在 "Code and automation" 分组下），点 **Add branch protection rule**。
3. **Branch name pattern** 填 `master`，回车。
4. 在规则里勾选（按需）：
   - ☑ Require a pull request before merging（核心：禁止直推）
   - ☑ Require approvals → 填 `1`（至少 1 人审核；目前即 A 自己审 B 的 develop→master PR）
   - ☑ Dismiss stale pull request approvals when new commits are pushed（新提交后旧审核失效，可选）
   - ☑ Require status checks to pass before merging（若以后接了 CI，选对应 check；暂未接可不勾）
   - ☑ Do not allow bypassing the above settings（防止管理员本人绕过）
   - ☑ Require linear history（保持线性历史，可选）
   - ❌ **不要**勾 "Allow force pushes" / "Allow deletions"（保持默认不勾）
5. 点 **Create / Save protection rule**。

**建议顺手做：**
- 给 `develop` 也加一条保护规则（pattern 填 `develop`，勾 Require PR + 禁止直推），这样 B 也不能直接推 `develop`，所有合入都走 PR 由 A 审核。
- 给第二人（B）加协作权限：仓库 **Settings → Collaborators → Add people**，输入 B 的 GitHub 用户名，选 **Write** 角色，B 即可提 PR。
- （可选）在仓库 `.github/PULL_REQUEST_TEMPLATE.md` 放一份 PR 模板，提 PR 时自动带出上面的「PR 描述模板」结构。
