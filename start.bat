@echo off
REM 水下目标识别系统 - Windows 快速启动脚本
REM 
REM 功能：
REM 1. 检查 Python 环境
REM 2. 检查依赖安装
REM 3. 启动应用程序

echo ========================================
echo   水下目标识别系统 启动脚本
echo ========================================
echo.

REM 检查 Python
echo [1/4] 检查 Python 环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.8+
    pause
    exit /b 1
)
python --version
echo.

REM 检查 MySQL 连接（可选）
echo [2/4] 检查数据库配置...
echo 请确保 MySQL 已启动，并已在 config.py 中配置正确的连接信息
echo.

REM 检查依赖
echo [3/4] 检查依赖包...
pip show ultralytics >nul 2>&1
if errorlevel 1 (
    echo [警告] 依赖包未完全安装
    echo 是否现在安装依赖？(Y/N)
    set /p install_deps=
    if /i "%install_deps%"=="Y" (
        echo 正在安装依赖...
        pip install -r requirements.txt
    )
)
echo.

REM 启动应用
echo [4/4] 启动应用程序...
echo.
echo ========================================
python main.py

if errorlevel 1 (
    echo.
    echo [错误] 应用程序启动失败
    echo 请检查错误信息并确保：
    echo 1. 已安装所有依赖：pip install -r requirements.txt
    echo 2. MySQL 数据库已启动
    echo 3. config.py 中的数据库配置正确
    pause
)
