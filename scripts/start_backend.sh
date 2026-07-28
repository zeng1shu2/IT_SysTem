#!/bin/bash
# ============================================================
# IT_SysTem_OS 后端启动脚本
# 用于 openEuler 服务器部署
# ============================================================

set -e

# 项目根目录（脚本所在目录的上一级）
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
BACKEND_DIR="$PROJECT_DIR/backend"

echo "=========================================="
echo "  IT_SysTem_OS 后端启动"
echo "=========================================="

# 检查 Python 虚拟环境
if [ ! -d "$BACKEND_DIR/venv" ]; then
    echo "[ERROR] Python 虚拟环境不存在，请先执行:"
    echo "  cd $BACKEND_DIR"
    echo "  python3 -m venv venv"
    echo "  source venv/bin/activate"
    echo "  pip install -r requirements.txt"
    exit 1
fi

# 激活虚拟环境
cd "$BACKEND_DIR"
source venv/bin/activate

# 检查 .env 文件
if [ ! -f .env ]; then
    echo "[WARN] .env 文件不存在，使用默认配置"
    echo "[WARN] 生产环境请复制 .env.example 为 .env 并修改配置"
fi

# 启动参数
HOST="${BACKEND_HOST:-0.0.0.0}"
PORT="${BACKEND_PORT:-8000}"
WORKERS="${BACKEND_WORKERS:-4}"

echo "[INFO] 启动 FastAPI 服务..."
echo "[INFO] Host: $HOST"
echo "[INFO] Port: $PORT"
echo "[INFO] Workers: $WORKERS"
echo "[INFO] API文档: http://$HOST:$PORT/api/docs"
echo ""

# 启动 Uvicorn
exec uvicorn app.main:app \
    --host "$HOST" \
    --port "$PORT" \
    --workers "$WORKERS"
