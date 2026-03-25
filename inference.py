#!/usr/bin/env python3
"""
推理入口代理脚本
实际推理逻辑在 src/inference/inference.py
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.inference.inference import main

if __name__ == '__main__':
    main()