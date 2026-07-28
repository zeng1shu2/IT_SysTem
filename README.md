# IT 综合运维管理系统 (IT_SysTem_OS)

> 前后端分离架构的 IT 综合运维管理系统，采用 Vue 3 + FastAPI + MySQL/SQLite 技术栈。

## 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| 前端框架 | Vue 3 + Vite | SPA 单页应用 |
| UI 组件库 | Element Plus | Vue3 生态最成熟 |
| 状态管理 | Pinia | Vue3 官方推荐 |
| HTTP 请求 | Axios | 封装 JWT 拦截器 |
| 后端框架 | Python + FastAPI | 自带 Swagger 文档 |
| ORM | SQLAlchemy 2.0 + Alembic | 数据库迁移管理 |
| 认证 | JWT Token | Bearer Token 鉴权 |
| 密码加密 | bcrypt | 安全哈希 |
| 数据库 | MySQL 8.0 (生产) / SQLite (开发) | 灵活切换 |

## 快速开始

### 一、后端启动

```bash
cd backend

# 1. 创建虚拟环境
python -m venv venv

# 2. 激活虚拟环境
# Windows (Git Bash):
source venv/Scripts/activate
# Linux:
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，修改数据库等配置

# 5. 启动后端
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

启动后访问：
- API 首页: http://localhost:8000/
- Swagger 文档: http://localhost:8000/api/docs
- 默认管理员: admin / admin123

### 二、前端启动

```bash
cd frontend

# 1. 安装依赖
npm install

# 2. 配置环境变量（可选，默认代理到 127.0.0.1:8000）
cp .env.example .env

# 3. 启动开发服务器
npm run dev
```

启动后访问: http://localhost:5173

### 三、前后端联调

1. 后端运行在 `http://localhost:8000`
2. 前端开发服务器运行在 `http://localhost:5173`
3. 前端通过 Vite proxy 将 `/api` 请求代理到后端
4. 前端已配置 CORS，支持跨域开发

## 功能模块

| 模块 | 功能 |
|------|------|
| 资产管理 | 网络设备（交换机/路由器/防火墙等）的增删改查 |
| 权限管理 | 权限申请（自动分配模式）、申请记录查询 |
| 用户管理 | 用户增删改查、启用/禁用、密码重置 |
| 角色管理 | 角色增删改查、权限绑定 |
| 审计日志 | 全量操作日志记录与多维度筛选查询 |

## 项目结构

```
IT_SysTem_OS/
├── frontend/          # 前端 Vue3 + Element Plus
├── backend/           # 后端 FastAPI + SQLAlchemy
├── scripts/           # 部署脚本
├── docs/              # 项目文档
└── README.md
```

## 生产部署

### 1. 后端部署 (openEuler)

```bash
# 在服务器上执行
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 配置 .env（使用 MySQL）
cp .env.example .env
# 编辑 .env: DB_TYPE=mysql, DB_HOST=..., DB_PASSWORD=...

# 启动
bash ../scripts/start_backend.sh
```

### 2. 前端编译 + 部署

```bash
# 在 Windows 开发机执行
cd frontend
npm run build

# 将 dist/ 目录内容上传到服务器 Apache 目录
# 或在服务器上执行部署脚本
bash ../scripts/deploy_frontend.sh
```

### 3. Apache 配置

参考 `scripts/apache.conf.example`，配置反向代理。

## 开发说明

- 后端开发模式下使用 SQLite，无需安装 MySQL
- 生产环境切换为 MySQL：修改 `.env` 中 `DB_TYPE=mysql`
- 数据库迁移使用 Alembic：`alembic revision --autogenerate -m "desc"` → `alembic upgrade head`
- 后端代码规范使用 Ruff：`ruff check app/`
- 前端代码规范使用 ESLint + Prettier
