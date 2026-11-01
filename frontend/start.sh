#!/bin/bash

echo "================================"
echo "后台管理系统前端启动脚本"
echo "================================"
echo

echo "正在检查 Node.js..."
if ! command -v node &> /dev/null; then
    echo "错误: 未找到 Node.js，请先安装 Node.js 18+"
    exit 1
fi

echo "Node.js 版本:"
node --version

echo
echo "正在检查依赖..."
if [ ! -d "node_modules" ]; then
    echo "未找到依赖，正在安装..."
    npm install
    if [ $? -ne 0 ]; then
        echo "依赖安装失败，请检查网络连接"
        exit 1
    fi
else
    echo "依赖已存在"
fi

echo
echo "启动开发服务器..."
echo "项目将在 http://localhost:3000 启动"
echo "默认登录账号: admin / admin123"
echo "请确保后端服务运行在 http://localhost:5000"
echo
echo "按 Ctrl+C 停止服务器"
echo

npm run dev
