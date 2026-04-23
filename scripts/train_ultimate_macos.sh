#!/bin/bash
# 终极优化模型训练 - macOS优化配置
# ResNet-101 + FPN + 注意力机制 + 边界优化

echo "========================================"
echo "终极优化模型训练 (macOS优化版)"
echo "========================================"
echo "模型架构: ResNet-101 + FPN + CBAM-ASPP"
echo "优化配置:"
echo "  - 批次大小: 4 (降低内存占用)"
echo "  - 工作进程: 0 (避免macOS多进程问题)"
echo "  - 目标IoU: 75-80%"
echo "========================================"
echo ""

# 检查是否有之前的检查点
if [ -f "outputs/checkpoints/ultimate_best_model.pth" ]; then
    echo "✓ 找到检查点: outputs/checkpoints/ultimate_best_model.pth"
    echo "将从断点继续训练..."
    RESUME_PARAM="--resume outputs/checkpoints/ultimate_best_model.pth"
else
    echo "未找到检查点,从头开始训练"
    RESUME_PARAM=""
fi

echo ""
echo "开始训练..."
echo ""

# macOS优化配置
python3 src/training/train_ultimate.py \
  --use_gpu True \
  --batch_size 4 \
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
  --img_size 512 512 \
  $RESUME_PARAM

echo ""
echo "========================================"
echo "训练完成!"
echo "========================================"
