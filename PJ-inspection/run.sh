#!/bin/bash
# 代码评审工具启动脚本

echo "正在启动代码评审工具..."

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3，请先安装Python3"
    exit 1
fi

# 检查依赖是否安装
if ! python3 -c "import PyQt5" &> /dev/null; then
    echo "首次运行，正在安装依赖..."
    pip3 install -r requirements.txt
fi

# 运行程序
python3 main.py
