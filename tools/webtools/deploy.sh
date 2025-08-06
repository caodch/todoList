#!/bin/bash

# Flask 应用部署脚本
echo "开始部署任务管理系统..."

# 检查是否安装了 Python
if ! command -v python3 &> /dev/null
then
    echo "未找到 Python3，请先安装 Python3"
    exit 1
fi

# 检查是否安装了 pip
if ! command -v pip3 &> /dev/null
then
    echo "未找到 pip3，请先安装 pip3"
    exit 1
fi

# 安装依赖
echo "安装 Python 依赖..."
pip3 install -r requirements.txt

# 创建上传目录
echo "创建上传目录..."
mkdir -p static/uploads

# 设置环境变量
export FLASK_APP=web.py
export FLASK_ENV=production

# 启动应用
echo "启动应用..."
python3 web.py

echo "部署完成！应用已在 0.0.0.0:5002 上运行"