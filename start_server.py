#!/usr/bin/env python3
"""
启动前后端服务脚本
支持跨平台：Windows, macOS, Linux
"""
import subprocess
import sys
import os
import time
import signal
import platform
from threading import Thread

# 进程列表
processes = []

def get_python_command():
    """获取 Python 命令"""
    if platform.system() == 'Windows':
        return 'python'
    else:
        return 'python3'

def run_backend():
    """启动后端服务"""
    print("🚀 启动后端服务...")
    backend_path = os.path.join(os.path.dirname(__file__), 'src', 'web', 'backend', 'app.py')
    python_cmd = get_python_command()
    
    # Windows 需要特殊处理
    if platform.system() == 'Windows':
        process = subprocess.Popen(
            [python_cmd, backend_path],
            creationflags=subprocess.CREATE_NEW_CONSOLE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=1,
            universal_newlines=True
        )
    else:
        process = subprocess.Popen(
            [python_cmd, backend_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=1,
            universal_newlines=True
        )
    
    processes.append(process)
    
    try:
        for line in iter(process.stdout.readline, ''):
            print(f"[后端] {line.rstrip()}")
    except:
        pass
    
def run_frontend():
    """启动前端服务"""
    print("🎨 启动前端服务...")
    frontend_dir = os.path.join(os.path.dirname(__file__), 'src', 'web', 'frontend')
    
    # 检查 node_modules 是否存在
    node_modules = os.path.join(frontend_dir, 'node_modules')
    if not os.path.exists(node_modules):
        print("📦 检测到未安装依赖，正在安装前端依赖...")
        
        # Windows 使用 npm.cmd
        npm_cmd = 'npm.cmd' if platform.system() == 'Windows' else 'npm'
        
        npm_install = subprocess.Popen(
            [npm_cmd, 'install'],
            cwd=frontend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            shell=True if platform.system() == 'Windows' else False
        )
        for line in iter(npm_install.stdout.readline, ''):
            print(f"[npm install] {line.rstrip()}")
        npm_install.wait()
        print("✅ 前端依赖安装完成")
    
    # 启动开发服务器
    npm_cmd = 'npm.cmd' if platform.system() == 'Windows' else 'npm'
    
    # Windows 需要特殊处理
    if platform.system() == 'Windows':
        process = subprocess.Popen(
            [npm_cmd, 'run', 'dev'],
            cwd=frontend_dir,
            creationflags=subprocess.CREATE_NEW_CONSOLE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=1,
            universal_newlines=True,
            shell=True
        )
    else:
        process = subprocess.Popen(
            [npm_cmd, 'run', 'dev'],
            cwd=frontend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=1,
            universal_newlines=True
        )
    
    processes.append(process)
    
    try:
        for line in iter(process.stdout.readline, ''):
            print(f"[前端] {line.rstrip()}")
    except:
        pass

def signal_handler(sig, frame):
    """处理 Ctrl+C 信号"""
    print("\n\n正在停止所有服务...")
    for p in processes:
        p.terminate()
        try:
            p.wait(timeout=3)
        except subprocess.TimeoutExpired:
            p.kill()
    print("✅ 所有服务已停止")
    sys.exit(0)

if __name__ == '__main__':
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("\n" + "="*60)
    print("    图像分割可视化平台 - 服务启动器")
    print("="*60 + "\n")
    
    # 创建线程
    backend_thread = Thread(target=run_backend, daemon=True)
    frontend_thread = Thread(target=run_frontend, daemon=True)
    
    # 启动线程
    backend_thread.start()
    time.sleep(2)  # 等待后端先启动
    frontend_thread.start()
    
    # 等待所有线程
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        signal_handler(None, None)
