@echo off
echo 开始部署任务管理系统...

REM 检查是否安装了 Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 未找到 Python，请先安装 Python
    pause
    exit /b 1
)

REM 安装依赖
echo 安装 Python 依赖...
pip install -r requirements.txt

REM 创建上传目录
echo 创建上传目录...
mkdir static\uploads 2>nul

REM 设置环境变量
set FLASK_APP=web.py
set FLASK_ENV=production

REM 启动应用
echo 启动应用...
python web.py

echo 部署完成！应用已在 0.0.0.0:5002 上运行
pause