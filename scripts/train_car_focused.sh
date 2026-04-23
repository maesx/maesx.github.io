#!/bin/bash
# Car专用训练脚本 - 提升Car类别IoU
# 生成时间: 2026-04-23
# 目标: 专注提升Car类别的分割性能

set -e

echo "===================================================================="
echo "Car专用训练模式"
echo "===================================================================="
echo ""
echo "训练策略:"
echo "  1. 只使用包含Car的样本进行训练"
echo "  2. 使用类别平衡采样器"
echo "  3. 提高学习率和训练轮数"
echo "  4. 更强的数据增强"
echo ""
echo "===================================================================="
echo ""

# 配置参数
DATA_DIR="road_vehicle_pedestrian_det_datasets"
MASKS_DIR="outputs/masks_car"
OUTPUT_DIR="outputs"
MODEL_NAME="car_focused_$(date +%Y%m%d_%H%M%S)"

# 检查数据目录
if [ ! -d "$DATA_DIR" ]; then
    echo "❌ 错误: 数据目录不存在: $DATA_DIR"
    exit 1
fi

# 创建输出目录
mkdir -p "$OUTPUT_DIR/checkpoints"
mkdir -p "$OUTPUT_DIR/logs"

echo "🚗 Car专用训练模式"
echo ""
echo "训练参数:"
echo "  - 学习率: 1e-4"
echo "  - 批次大小: 8"
echo "  - 训练轮数: 150"
echo "  - 学习率预热: 5 epochs"
echo "  - Early Stopping patience: 25"
echo "  - Car专用样本过滤: 启用"
echo "  - 类别平衡采样: 启用"
echo "  - 模型名称: $MODEL_NAME"
echo ""

# 启动训练
python3 src/training/train.py \
    --use_gpu True \
    --epochs 150 \
    --batch_size 8 \
    --lr 1e-4 \
    --warmup_epochs 5 \
    --early_stopping_patience 25 \
    --weight_decay 1e-4 \
    --grad_clip 1.0 \
    --data_dir "$DATA_DIR" \
    --masks_dir "$MASKS_DIR" \
    --output_dir "$OUTPUT_DIR" \
    --model_name "$MODEL_NAME" \
    --num_classes 4 \
    --deep_supervision True \
    --car_only \
    --balance_sampling \
    --save_interval 5

echo ""
echo "===================================================================="
echo "✅ Car专用训练完成!"
echo "===================================================================="
echo ""
echo "模型保存位置: $OUTPUT_DIR/checkpoints/${MODEL_NAME}.pth"
echo ""
echo "评估Car类别性能:"
echo "  python3 scripts/evaluate_model.py --model $OUTPUT_DIR/checkpoints/${MODEL_NAME}.pth --class_id 1"
echo ""
