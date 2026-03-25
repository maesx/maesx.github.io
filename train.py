#!/usr/bin/env python3
"""
训练入口代理脚本
实际训练逻辑在 src/training/train.py
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.training.train import main

if __name__ == '__main__':
    main()