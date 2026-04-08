#!/bin/bash

# 图像分割可视化平台启动脚本

echo "=========================================="
echo "  图像分割可视化平台"
echo "=========================================="
echo ""

# 检查Python依赖
echo "检查Python依赖..."
python3 -c "import flask" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  Flask未安装，正在安装..."
    pip3 install Flask Flask-RESTful Flask-CORS --user
fi

# 检查前端依赖
echo "检查前端依赖..."
if [ ! -d "node_modules" ]; then
    echo "⚠️  前端依赖未安装"
    echo "请运行: cd src/web/frontend && npm install"
fi

echo ""
echo "启动方式："
echo ""
echo "1. 启动后端服务："
echo "   cd src/web/backend"
echo "   python3 app.py"
echo ""
echo "2. 启动前端服务（新终端窗口）："
echo "   cd src/web/frontend"
echo "   npm run dev"
echo ""
echo "3. 访问应用："
echo "   http://localhost:3000"
echo ""
echo "=========================================="
