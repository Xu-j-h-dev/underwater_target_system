#!/bin/bash
# 水下目标识别系统 - Linux/Mac 快速启动脚本
# 
# 功能：
# 1. 检查 Python 环境
# 2. 检查依赖安装
# 3. 启动应用程序

echo "========================================"
echo "  水下目标识别系统 启动脚本"
echo "========================================"
echo ""

# 检查 Python
echo "[1/4] 检查 Python 环境..."
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未找到 Python3，请先安装 Python 3.8+"
    exit 1
fi
python3 --version
echo ""

# 检查 MySQL
echo "[2/4] 检查数据库配置..."
echo "请确保 MySQL 已启动，并已在 config.py 中配置正确的连接信息"
echo ""

# 检查依赖
echo "[3/4] 检查依赖包..."
if ! python3 -c "import ultralytics" 2>/dev/null; then
    echo "[警告] 依赖包未完全安装"
    read -p "是否现在安装依赖？(y/n) " install_deps
    if [ "$install_deps" = "y" ] || [ "$install_deps" = "Y" ]; then
        echo "正在安装依赖..."
        pip3 install -r requirements.txt
    fi
fi
echo ""

# 启动应用
echo "[4/4] 启动应用程序..."
echo ""
echo "========================================"
python3 main.py

if [ $? -ne 0 ]; then
    echo ""
    echo "[错误] 应用程序启动失败"
    echo "请检查错误信息并确保："
    echo "1. 已安装所有依赖：pip3 install -r requirements.txt"
    echo "2. MySQL 数据库已启动"
    echo "3. config.py 中的数据库配置正确"
fi
