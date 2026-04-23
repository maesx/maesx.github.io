#!/bin/bash
# 训练优化脚本 - 解决连续Epoch无提升问题
# 生成时间: 2026-04-23
# 问题: 验证IoU连续6个epoch停滞在0.47-0.53区间

set -e  # 遇到错误立即退出

echo "===================================================================="
echo "训练优化脚本"
echo "===================================================================="
echo ""
echo "问题诊断:"
echo "  - 验证IoU停滞在0.47-0.53区间"
echo "  - Early Stopping计数: 6/10"
echo "  - 学习率一直固定在1e-4"
echo "  - 训练损失波动明显"
echo ""
echo "优化方案:"
echo "  1. 降低学习率: 1e-4 -> 5e-5 (更稳定)"
echo "  2. 添加学习率预热: 3个epoch (避免初始震荡)"
echo "  3. 增加Early Stopping patience: 10 -> 20 (避免过早停止)"
echo "  4. 增强正则化: weight_decay 1e-5 -> 1e-4, grad_clip 1.0 -> 0.5"
echo "  5. 从当前最佳模型恢复训练"
echo ""
echo "===================================================================="
echo ""

# 配置参数
DATA_DIR="road_vehicle_pedestrian_det_datasets"
MASKS_DIR="outputs/masks_car"
OUTPUT_DIR="outputs"
MODEL_NAME="optimized_v1_$(date +%Y%m%d_%H%M%S)"
RESUME_MODEL="outputs/checkpoints/best_model.pth"

# 检查数据目录
if [ ! -d "$DATA_DIR" ]; then
    echo "❌ 错误: 数据目录不存在: $DATA_DIR"
    exit 1
fi

if [ ! -d "$MASKS_DIR" ]; then
    echo "❌ 错误: 掩码目录不存在: $MASKS_DIR"
    exit 1
fi

# 检查恢复模型
if [ ! -f "$RESUME_MODEL" ]; then
    echo "⚠️  警告: 恢复模型不存在: $RESUME_MODEL"
    echo "   将从头开始训练..."
    RESUME_ARG=""
else
    echo "✅ 找到恢复模型: $RESUME_MODEL"
    RESUME_ARG="--resume $RESUME_MODEL"
fi

# 创建输出目录
mkdir -p "$OUTPUT_DIR/checkpoints"
mkdir -p "$OUTPUT_DIR/logs"

# 备份当前最佳模型
if [ -f "$OUTPUT_DIR/checkpoints/best_model.pth" ]; then
    BACKUP_NAME="best_model_backup_$(date +%Y%m%d_%H%M%S).pth"
    echo "📦 备份当前最佳模型: $BACKUP_NAME"
    cp "$OUTPUT_DIR/checkpoints/best_model.pth" "$OUTPUT_DIR/checkpoints/$BACKUP_NAME"
fi

echo ""
echo "🚀 开始训练..."
echo ""
echo "训练参数:"
echo "  - 学习率: 5e-5"
echo "  - 批次大小: 8"
echo "  - 训练轮数: 100"
echo "  - 学习率预热: 3 epochs"
echo "  - Early Stopping patience: 20"
echo "  - 权重衰减: 1e-4"
echo "  - 梯度裁剪: 0.5"
echo "  - 模型名称: $MODEL_NAME"
echo ""

# 启动训练
python3 src/training/train.py \
    --use_gpu True \
    --epochs 100 \
    --batch_size 8 \
    --lr 5e-5 \
    --warmup_epochs 3 \
    --early_stopping_patience 20 \
    --weight_decay 1e-4 \
    --grad_clip 0.5 \
    --data_dir "$DATA_DIR" \
    --masks_dir "$MASKS_DIR" \
    --output_dir "$OUTPUT_DIR" \
    --model_name "$MODEL_NAME" \
    --num_classes 4 \
    --deep_supervision True \
    --save_interval 5 \
    $RESUME_ARG

echo ""
echo "===================================================================="
echo "✅ 训练完成!"
echo "===================================================================="
echo ""
echo "模型保存位置: $OUTPUT_DIR/checkpoints/${MODEL_NAME}.pth"
echo ""
echo "下一步:"
echo "  1. 查看训练日志: tail -100 $OUTPUT_DIR/logs/training_*.log"
echo "  2. 启动TensorBoard: tensorboard --logdir $OUTPUT_DIR/logs --port 6006"
echo "  3. 对比模型性能: python3 scripts/compare_models.py"
echo ""
