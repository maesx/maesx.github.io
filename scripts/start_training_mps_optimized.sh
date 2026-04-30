#!/bin/bash
# MPS优化训练脚本 - 解决bus error问题
# 关键配置: num_workers=0, pin_memory=False, batch_size=4

cd /Users/sux/IdeaProjects/maesx.github.io

echo "=========================================="
echo "开始训练 - 目标 IoU 80%"
echo "使用MPS训练 (优化配置)"
echo "=========================================="
echo ""
echo "🔧 解决MPS问题的配置:"
echo "  - num_workers=0 (单进程,避免多进程问题)"
echo "  - batch_size=4 (降低内存使用)"
echo "  - 自动禁用pin_memory"
echo ""

# 创建日志目录
mkdir -p outputs/logs

# MPS优化训练命令
python3 src/training/train.py \
    --use_gpu \
    --batch_size 4 \
    --epochs 30 \
    --lr 1e-4 \
    --data_dir road_vehicle_pedestrian_det_datasets \
    --masks_dir outputs/masks_car \
    --output_dir outputs \
    --num_classes 4 \
    --deep_supervision True \
    --encoder vgg19 \
    --pretrained True \
    --save_interval 10 \
    --early_stopping_patience 20 \
    --min_lr 1e-5 \
    --lr_adjustment_factor 0.7 \
    --warmup_epochs 3 \
    --model_name best_model \
    --num_workers 0 \
    --balance_sampling \
    --resume outputs/checkpoints/best_model.pth

echo ""
echo "=========================================="
echo "训练完成"
echo "=========================================="
