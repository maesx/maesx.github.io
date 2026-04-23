#!/bin/bash
# 快速训练脚本 - 使用小数据集快速验证优化方案
# 生成时间: 2026-04-23
# 用途: 快速验证优化方案是否有效

set -e

echo "===================================================================="
echo "快速验证训练模式"
echo "===================================================================="
echo ""
echo "⚡ 快速训练参数:"
echo "  - 使用10%数据集"
echo "  - 训练20个epoch"
echo "  - 快速验证优化方案是否有效"
echo "  - 预计训练时间: 15-30分钟"
echo ""
echo "===================================================================="
echo ""

# 配置参数
DATA_DIR="road_vehicle_pedestrian_det_datasets"
MASKS_DIR="outputs/masks_car"
OUTPUT_DIR="outputs"
MODEL_NAME="quick_test_$(date +%Y%m%d_%H%M%S)"
RESUME_MODEL="outputs/checkpoints/best_model.pth"

# 检查恢复模型
RESUME_ARG=""
if [ -f "$RESUME_MODEL" ]; then
    echo "✅ 从最佳模型恢复: $RESUME_MODEL"
    RESUME_ARG="--resume $RESUME_MODEL"
fi

echo ""
echo "训练参数:"
echo "  - 数据集比例: 10%"
echo "  - 批次大小: 8"
echo "  - 训练轮数: 20"
echo "  - 学习率: 5e-5"
echo "  - Early Stopping patience: 10"
echo ""

# 启动快速训练
python3 src/training/train.py \
    --use_gpu True \
    --epochs 20 \
    --batch_size 8 \
    --lr 5e-5 \
    --warmup_epochs 2 \
    --early_stopping_patience 10 \
    --weight_decay 1e-4 \
    --grad_clip 0.5 \
    --data_dir "$DATA_DIR" \
    --masks_dir "$MASKS_DIR" \
    --output_dir "$OUTPUT_DIR" \
    --model_name "$MODEL_NAME" \
    --num_classes 4 \
    --deep_supervision True \
    --subset_ratio 0.1 \
    --save_interval 5 \
    $RESUME_ARG

echo ""
echo "===================================================================="
echo "✅ 快速训练完成!"
echo "===================================================================="
echo ""
echo "快速验证结果:"
echo "  1. 检查验证IoU是否提升"
echo "  2. 检查训练损失是否更稳定"
echo "  3. 如果验证IoU上升,说明优化方案有效"
echo ""
echo "如果验证成功,运行完整训练:"
echo "  bash scripts/train_optimized.sh"
echo ""
