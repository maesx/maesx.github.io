#!/bin/bash
# CPU训练脚本 - 解决MPS兼容性问题

cd /Users/sux/IdeaProjects/maesx.github.io

echo "=========================================="
echo "开始训练 - 目标 IoU 80%"
echo "使用CPU训练 (避免MPS bus error)"
echo "=========================================="

# 创建日志目录
mkdir -p outputs/logs

# CPU训练命令
python3 src/training/train.py \
    --batch_size 8 \
    --epochs 20 \
    --lr 1e-4 \
    --data_dir road_vehicle_pedestrian_det_datasets \
    --masks_dir outputs/masks_car \
    --output_dir outputs \
    --num_classes 4 \
    --deep_supervision True \
    --encoder vgg19 \
    --pretrained True \
    --save_interval 5 \
    --early_stopping_patience 15 \
    --min_lr 1e-5 \
    --lr_adjustment_factor 0.7 \
    --warmup_epochs 3 \
    --model_name best_model \
    --num_workers 4 \
    --balance_sampling \
    --resume outputs/checkpoints/best_model.pth

echo "=========================================="
echo "训练完成"
echo "=========================================="
