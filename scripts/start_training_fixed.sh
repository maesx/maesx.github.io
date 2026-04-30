#!/bin/bash
# 修复版训练脚本 - 降低batch_size避免MPS内存问题

cd /Users/sux/IdeaProjects/maesx.github.io

echo "=========================================="
echo "开始训练 - 目标 IoU 80%"
echo "配置: batch_size=4 (避免MPS内存问题)"
echo "=========================================="

# 创建日志目录
mkdir -p outputs/logs

# 训练命令 - 降低batch_size从8到4
python3 src/training/train.py \
    --use_gpu \
    --batch_size 4 \
    --epochs 35 \
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

echo "=========================================="
echo "训练完成"
echo "=========================================="
