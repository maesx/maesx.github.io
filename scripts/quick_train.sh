#!/bin/bash
# 快速训练启动脚本 - 针对1-2小时快速训练优化

# 切换到项目根目录
cd "$(dirname "$0")/.."

echo "========================================"
echo "道路车辆分割系统 - 快速训练模式"
echo "========================================"
echo ""

# 显示训练选项
echo "请选择训练模式:"
echo ""
echo "1) 超快速验证 (~1小时)"
echo "   - 数据: 720张图像 (9%数据集)"
echo "   - Epochs: 10"
echo "   - 用途: 验证代码流程"
echo ""
echo "2) 快速训练 (~2小时) ⭐推荐"
echo "   - 数据: 900张图像 (11.25%数据集)"
echo "   - Epochs: 20"
echo "   - 用途: 得到初步训练结果"
echo ""
echo "3) 标准快速 (~3小时)"
echo "   - 数据: 1600张图像 (20%数据集)"
echo "   - Epochs: 30"
echo "   - 用途: 较完整的验证"
echo ""
echo "4) 完整训练 (~60小时)"
echo "   - 数据: 全部8000张图像"
echo "   - Epochs: 50"
echo "   - 用途: 获得最佳性能"
echo ""

read -p "请输入选项 (1-4): " choice

case $choice in
    1)
        echo ""
        echo "启动超快速验证..."
        python3 train.py \
            --batch_size 8 \
            --epochs 10 \
            --use_gpu True \
            --subset_ratio 0.09 \
            --save_interval 5 \
            --num_workers 0
        ;;
    2)
        echo ""
        echo "启动快速训练..."
        python3 train.py \
            --batch_size 8 \
            --epochs 20 \
            --use_gpu True \
            --subset_ratio 0.1125 \
            --save_interval 5 \
            --num_workers 0
        ;;
    3)
        echo ""
        echo "启动标准快速训练..."
        python3 train.py \
            --batch_size 8 \
            --epochs 30 \
            --use_gpu True \
            --subset_ratio 0.2 \
            --save_interval 10 \
            --num_workers 0
        ;;
    4)
        echo ""
        echo "启动完整训练..."
        python3 train.py \
            --batch_size 8 \
            --epochs 50 \
            --use_gpu True \
            --subset_ratio 1.0 \
            --save_interval 10 \
            --num_workers 0
        ;;
    *)
        echo "无效选项，退出"
        exit 1
        ;;
esac

echo ""
echo "========================================"
echo "训练完成!"
echo "========================================"
echo ""
echo "下一步:"
echo "1. 查看训练日志: tensorboard --logdir outputs/logs"
echo "2. 模型推理: python3 inference.py --model_path outputs/checkpoints/best_model.pth"
