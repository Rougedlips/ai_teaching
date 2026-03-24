#!/bin/bash
# 启动代码评审工具

cd "$(dirname "$0")"

echo "🚀 正在启动代码评审工具..."
echo ""
echo "界面说明："
echo "  - 🏠 工作台: 默认显示的欢迎页面"
echo "  - 📄 代码评审: 点击后进入评审功能"
echo ""

python3 main.py

echo ""
echo "程序已退出"
