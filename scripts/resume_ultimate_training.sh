#!/bin/bash
# 终极优化模型继续训练脚本 (ResNet-101 + FPN + 注意力)
# 修复了检查点路径问题

echo "========================================"
echo "终极优化模型 - 继续训练"
echo "========================================"
echo "模型架构: ResNet-101 + FPN + CBAM-ASPP + 边界优化"
echo "目标IoU: 75-80%"
echo "========================================"
echo ""

# 查找最新的检查点
LATEST_CHECKPOINT=$(find outputs/checkpoints -name "best_model.pth" -type f -printf '%T@ %p\n' | sort -rn | head -1 | cut -d' ' -f2-)

if [ -z "$LATEST_CHECKPOINT" ]; then
    echo "⚠️  未找到检查点,将从头开始训练"
    RESUME_PARAM=""
else
    echo "✓ 找到检查点: $LATEST_CHECKPOINT"
    RESUME_PARAM="--resume $LATEST_CHECKPOINT"
fi

echo ""
echo "开始训练..."
echo ""

# 使用正确的检查点路径
python3 src/training/train_ultimate.py \
  --use_gpu True \
  --batch_size 6 \
  --epochs 120 \
  --lr 0.0001 \
  --attention cbam_aspp \
  --use_fpn True \
  --use_boundary_refinement True \
  --use_separable_conv True \
  --use_aggressive_weights True \
  --num_workers 0 \
  --early_stopping_patience 15 \
  --save_interval 10 \
  --save_dir outputs/checkpoints \
  $RESUME_PARAM

echo ""
echo "训练完成!"
