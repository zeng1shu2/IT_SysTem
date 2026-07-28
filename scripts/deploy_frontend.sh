#!/bin/bash
# ============================================================
# IT_SysTem_OS 前端编译 + 部署脚本
# 在 Windows 开发机编译，部署到 openEuler Apache 目录
# ============================================================

set -e

# 项目根目录
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
FRONTEND_DIR="$PROJECT_DIR/frontend"

# Apache 部署目录（openEuler 服务器上）
APACHE_DIR="${APACHE_DIR:-/var/www/it-system-os}"

echo "=========================================="
echo "  IT_SysTem_OS 前端编译 + 部署"
echo "=========================================="

cd "$FRONTEND_DIR"

# 检查 node_modules
if [ ! -d node_modules ]; then
    echo "[INFO] 安装依赖..."
    npm install
fi

# 编译前端
echo "[INFO] 编译前端..."
npm run build

# 检查编译产物
if [ ! -d dist ]; then
    echo "[ERROR] 编译失败，dist 目录不存在"
    exit 1
fi

echo "[INFO] 编译完成，dist 目录已生成"

# 部署到 Apache 目录（如果在服务器上执行）
if [ -d "$(dirname "$APACHE_DIR")" ]; then
    echo "[INFO] 部署到 Apache 目录: $APACHE_DIR"
    sudo mkdir -p "$APACHE_DIR"
    sudo rm -rf "$APACHE_DIR"/*
    sudo cp -r dist/* "$APACHE_DIR"/
    sudo systemctl reload httpd
    echo "[INFO] 部署完成，已重载 Apache"
else
    echo "[INFO] Apache 目录不存在: $APACHE_DIR"
    echo "[INFO] 请手动将 dist/ 目录内容复制到 Apache 部署目录"
    echo "[INFO] 或设置 APACHE_DIR 环境变量指定部署路径"
fi

echo ""
echo "=========================================="
echo "  部署完成！"
echo "=========================================="
