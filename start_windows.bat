@echo off
REM Windows 启动脚本
REM 图像分割可视化平台

echo ============================================================
echo     图像分割可视化平台 - 服务启动器 (Windows)
echo ============================================================
echo.

REM 获取脚本所在目录
set SCRIPT_DIR=%~dp0

REM 清理旧进程
echo 清理旧进程...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq app.py*" 2>nul
taskkill /F /IM node.exe /FI "WINDOWTITLE eq vite*" 2>nul
timeout /t 2 /nobreak >nul

REM 创建输出目录
if not exist "%SCRIPT_DIR%outputs\uploads" mkdir "%SCRIPT_DIR%outputs\uploads"
if not exist "%SCRIPT_DIR%outputs\results" mkdir "%SCRIPT_DIR%outputs\results"
if not exist "%SCRIPT_DIR%outputs\checkpoints" mkdir "%SCRIPT_DIR%outputs\checkpoints"

REM 启动后端
echo 启动后端服务...
cd /d "%SCRIPT_DIR%src\web\backend"
start "Backend Server" python app.py
timeout /t 3 /nobreak >nul

REM 检查前端依赖
cd /d "%SCRIPT_DIR%src\web\frontend"
if not exist "node_modules" (
    echo 检测到未安装依赖，正在安装前端依赖...
    call npm install
    echo 前端依赖安装完成
)

REM 启动前端
echo 启动前端服务...
start "Frontend Server" cmd /c "npm run dev"
timeout /t 3 /nobreak >nul

echo.
echo ============================================================
echo 服务已启动！
echo ============================================================
echo.
echo 前端: http://localhost:3000
echo 后端: http://localhost:5002
echo.
echo 注意：两个新的命令行窗口已打开，请勿关闭
echo.
echo 按任意键退出此窗口...
pause >nul
