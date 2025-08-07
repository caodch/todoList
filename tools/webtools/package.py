#!/usr/bin/env python3
"""
简单的打包脚本，用于创建可执行的待办事项应用
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_dependencies():
    """检查必要依赖"""
    print("检查必要依赖...")
    
    # 检查Python版本
    if sys.version_info < (3, 6):
        print("需要Python 3.6或更高版本")
        return False
    
    # 检查pip
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "--version"], 
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        print("未找到pip，请先安装pip")
        return False
    
    return True

def install_pyinstaller():
    """安装PyInstaller"""
    try:
        import PyInstaller
        print("PyInstaller已安装")
    except ImportError:
        print("正在安装PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "PyInstaller"])
        print("PyInstaller安装完成")

def prepare_build_env():
    """准备打包环境"""
    print("准备打包环境...")
    
    # 确保必要的目录存在
    dirs_to_create = ['static/uploads', 'dist', 'build']
    for dir_path in dirs_to_create:
        os.makedirs(dir_path, exist_ok=True)
        print(f"创建目录: {dir_path}")

def create_executable():
    """创建可执行文件"""
    print("开始打包应用...")
    
    # PyInstaller命令
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=todo_app",
        "--onefile",
        "--add-data=templates" + os.pathsep + "templates",
        "--add-data=static" + os.pathsep + "static",
        "web.py"
    ]
    
    try:
        subprocess.check_call(cmd)
        print("打包完成！")
        print(f"可执行文件位置: {os.path.join(os.getcwd(), 'dist', 'todo_app.exe')}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"打包失败: {e}")
        return False

def create_run_script():
    """创建运行脚本"""
    # 创建Windows批处理文件
    bat_content = """@echo off
cd /d %~dp0
echo 正在启动待办事项应用...
echo 请在浏览器中访问 http://localhost:5002

REM 启动应用
start "待办事项应用" /D "%~dp0" todo_app.exe

REM 等待几秒钟让应用启动
timeout /t 3 /nobreak >nul

REM 自动打开浏览器
start http://localhost:5002

echo 应用已启动，浏览器窗口已打开
echo 如果浏览器未自动打开，请手动访问 http://localhost:5002
echo.

:confirm_stop
echo 是否停止应用？
echo 输入 Y/y 继续后台运行
echo 输入 N/n 立即停止应用
set /p choice=请选择 (Y/y/N/n): 

if /i "%choice%"=="Y" (
    echo 应用将继续在后台运行
    echo 如需手动停止，请使用任务管理器结束todo_app.exe进程
    timeout /t 2 /nobreak >nul
    exit /b
)

if /i "%choice%"=="N" (
    echo 正在停止应用...
    taskkill /f /im todo_app.exe 2>nul
    echo 应用已停止
    timeout /t 2 /nobreak >nul
    exit /b
)

echo 请输入 Y/y 继续运行 或 N/n 停止应用
goto confirm_stop
"""
    
    with open(os.path.join('dist', 'run.bat'), 'w', encoding='utf-8') as f:
        f.write(bat_content)
    
    # 创建Unix shell脚本
    sh_content = """#!/bin/bash
cd "$(dirname "$0")"
echo "正在启动待办事项应用..."
echo "请在浏览器中访问 http://localhost:5002"
echo "按 Ctrl+C 停止应用"

# 定义清理函数
cleanup() {
    echo ""
    echo "检测到退出信号，是否停止应用？"
    echo "输入 Y/y 继续后台运行"
    echo "输入 N/n 立即停止应用"
    
    while true; do
        read -p "请选择 (Y/y/N/n): " choice
        case $choice in
            [Yy]* ) 
                echo "应用将继续在后台运行"
                echo "如需手动停止，请使用任务管理器或执行 'kill $APP_PID'"
                exit 0
                ;;
            [Nn]* ) 
                echo "正在停止应用..."
                if [ ! -z "$APP_PID" ]; then
                    kill $APP_PID 2>/dev/null
                fi
                echo "应用已停止"
                exit 0
                ;;
            * ) 
                echo "请输入 Y/y 继续运行 或 N/n 停止应用"
                ;;
        esac
    done
}

# 注册清理函数，处理Ctrl+C
trap cleanup INT TERM

# 启动应用并在后台运行
./todo_app &
APP_PID=$!

# 等待几秒钟让应用启动
sleep 3

# 根据操作系统自动打开浏览器
if command -v xdg-open > /dev/null; then
    # Linux
    xdg-open http://localhost:5002
elif command -v open > /dev/null; then
    # macOS
    open http://localhost:5002
elif command -v start > /dev/null; then
    # Windows (WSL)
    start http://localhost:5002
else
    echo "无法自动打开浏览器，请手动访问 http://localhost:5002"
fi

echo "应用已启动，浏览器窗口已打开"
echo "如果浏览器未自动打开，请手动访问 http://localhost:5002"
echo "按 Ctrl+C 停止应用"

# 等待应用进程结束
wait $APP_PID
"""
    
    with open(os.path.join('dist', 'run.sh'), 'w', encoding='utf-8') as f:
        f.write(sh_content)
    
    # 给shell脚本添加执行权限
    try:
        os.chmod(os.path.join('dist', 'run.sh'), 0o755)
    except:
        pass  # 在Windows上可能会失败，忽略错误

def copy_static_files():
    """复制静态文件到dist目录"""
    print("复制静态文件到dist目录...")
    
    # 确保dist/static/uploads目录存在
    dist_static_path = os.path.join('dist', 'static', 'uploads')
    os.makedirs(dist_static_path, exist_ok=True)
    print(f"确保目录存在: {dist_static_path}")

def main():
    """主函数"""
    print("=== 待办事项应用打包工具 ===")
    
    # 检查依赖
    if not check_dependencies():
        sys.exit(1)
    
    # 安装PyInstaller
    install_pyinstaller()
    
    # 准备环境
    prepare_build_env()
    
    # 创建可执行文件
    if create_executable():
        # 复制静态文件
        copy_static_files()
        
        # 创建运行脚本
        create_run_script()
        print("\n打包成功完成！")
        print("使用方法:")
        print("  Windows: 运行 dist\\run.bat")
        print("  macOS/Linux: 运行 dist/run.sh")
        print("  或直接运行 dist/todo_app")
        print("\n应用将在 http://localhost:5002 上运行")
    else:
        print("打包失败")
        sys.exit(1)

if __name__ == '__main__':
    main()