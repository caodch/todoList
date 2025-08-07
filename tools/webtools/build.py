#!/usr/bin/env python3
"""
打包脚本，用于将Flask待办事项应用打包为可执行文件
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def install_pyinstaller():
    """安装PyInstaller"""
    try:
        import PyInstaller
        print("PyInstaller已安装")
    except ImportError:
        print("正在安装PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "PyInstaller"])

def create_spec_file():
    """创建spec文件以自定义打包配置"""
    spec_content = '''
# -*- mode: python ; coding: utf-8 -*-

import os
from kivy_deps import sdl2, glew

block_cipher = None

added_files = [
    ('templates', 'templates'),
    ('static', 'static'),
    ('requirements.txt', '.'),
]

a = Analysis(
    ['web.py'],
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='todo_app',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
'''
    
    with open('todo_app.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    print("已创建打包配置文件 todo_app.spec")

def prepare_build():
    """准备打包环境"""
    # 确保static/uploads目录存在
    os.makedirs('static/uploads', exist_ok=True)
    print("已创建 static/uploads 目录")

def build_executable():
    """构建可执行文件"""
    print("开始打包应用...")
    
    # 使用PyInstaller打包
    try:
        # 如果spec文件存在，使用spec文件打包
        if os.path.exists('todo_app.spec'):
            subprocess.check_call([
                sys.executable, '-m', 'PyInstaller', 'todo_app.spec'
            ])
        else:
            # 直接打包
            subprocess.check_call([
                sys.executable, '-m', 'PyInstaller',
                '--name=todo_app',
                '--onefile',
                '--add-data=templates;templates',
                '--add-data=static;static',
                '--add-data=requirements.txt;.',
                'web.py'
            ])
        print("应用打包完成！")
        print("可执行文件位于 dist/todo_app")
    except subprocess.CalledProcessError as e:
        print(f"打包过程中出现错误: {e}")
        sys.exit(1)

def main():
    """主函数"""
    print("开始准备打包待办事项应用...")
    
    # 安装PyInstaller
    install_pyinstaller()
    
    # 准备打包环境
    prepare_build()
    
    # 创建spec文件
    create_spec_file()
    
    # 构建可执行文件
    build_executable()
    
    print("打包完成！")
    print("运行方式:")
    print("  Windows: dist/todo_app.exe")
    print("  Linux/macOS: ./dist/todo_app")

if __name__ == '__main__':
    main()