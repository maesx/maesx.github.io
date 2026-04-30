#!/bin/bash
# MPS完全兼容训练脚本
# 解决segmentation fault问题

cd /Users/sux/IdeaProjects/maesx.github.io

echo "============================================================"
echo "MPS兼容训练 - 目标 IoU 80%"
echo "============================================================"
echo "关键修复:"
echo "  ✅ num_workers=0 (避免多进程问题)"
echo "  ✅ pin_memory=False (MPS不支持)"
echo "  ✅ batch_size=4 (降低内存压力)"
echo "  ✅ 禁用Focal Loss (避免MPS兼容性问题)"
echo "  ✅ 简化数据增强 (避免复杂操作)"
echo "============================================================"
echo ""

# 创建日志目录
mkdir -p outputs/logs

# MPS兼容训练
python3 src/training/train.py \
    --use_gpu \
    --batch_size 4 \
    --epochs 30 \
    --lr 5e-5 \
    --data_dir road_vehicle_pedestrian_det_datasets \
    --masks_dir outputs/masks_car \
    --output_dir outputs \
    --num_classes 4 \
    --deep_supervision False \
    --encoder vgg19 \
    --pretrained True \
    --save_interval 10 \
    --early_stopping_patience 20 \
    --min_lr 1e-5 \
    --lr_adjustment_factor 0.7 \
    --warmup_epochs 3 \
    --model_name best_model \
    --num_workers 0 \
    --resume outputs/checkpoints/best_model.pth 2>&1 | tee outputs/logs/training_mps_safe_$(date +%Y%m%d_%H%M%S).log

echo ""
echo "============================================================"
echo "训练完成或中断"
echo "============================================================"
