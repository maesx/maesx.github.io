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

#python3 src/training/train.py --use_gpu True --subset_ratio 0.6 --epochs 30 --save_interval 5 --early_stopping_patience 8 --num_workers 0 --resume outputs/checkpoints/best_model.pth