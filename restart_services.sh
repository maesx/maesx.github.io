#!/bin/bash

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# 清理旧进程
pkill -9 -f "python.*app.py" 2>/dev/null
pkill -9 -f "node.*vite" 2>/dev/null
sleep 2

# 启动后端
cd "$SCRIPT_DIR"
nohup python3 src/web/backend/app.py > /tmp/backend.log 2>&1 &
echo "后端启动中..."

# 等待后端启动
sleep 3

# 启动前端
cd "$SCRIPT_DIR/src/web/frontend"
nohup npm run dev > /tmp/frontend.log 2>&1 &
echo "前端启动中..."

sleep 3

# 检查服务
echo "检查后端..."
curl -s http://localhost:5002/api/health && echo " ✅" || echo " ❌"

echo "检查前端..."
curl -s http://localhost:3000 > /dev/null && echo " ✅" || echo " ❌"

echo ""
echo "服务已启动！"
echo "前端: http://localhost:3000"
echo "后端: http://localhost:5002"
echo ""
echo "日志位置:"
echo "  后端: /tmp/backend.log"
echo "  前端: /tmp/frontend.log"
