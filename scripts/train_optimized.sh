#!/bin/bash
# 优化训练脚本 - 目标IoU 80%
# 使用注意: 该脚本会从头训练模型,预计耗时12-24小时

# 切换到项目根目录
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

echo "=========================================="
echo "U-Net++ 优化训练 - 目标 IoU 80%"
echo "=========================================="
echo ""

# 设置Python路径
export PYTHONPATH="${PYTHONPATH}:${PROJECT_ROOT}"

# 选择训练模式
read -p "选择训练模式 (1: 快速验证 2: 标准训练 3: 激进训练 4: 完整注意力): " mode

case $mode in
    1)
        echo "快速验证模式 - CBAM注意力, 30轮训练"
        ATTENTION="cbam"
        EPOCHS=30
        BATCH_SIZE=8
        AGGRESSIVE=""
        ;;
    2)
        echo "标准训练模式 - CBAM+ASPP组合, 80轮训练"
        ATTENTION="cbam_aspp"
        EPOCHS=80
        BATCH_SIZE=8
        AGGRESSIVE=""
        ;;
    3)
        echo "激进训练模式 - CBAM+ASPP + 激进权重, 100轮训练"
        ATTENTION="cbam_aspp"
        EPOCHS=100
        BATCH_SIZE=8
        AGGRESSIVE="--use_aggressive_weights"
        ;;
    4)
        echo "完整注意力模式 - SE+ASPP+CBAM全注意力, 120轮训练"
        ATTENTION="full"
        EPOCHS=120
        BATCH_SIZE=6
        AGGRESSIVE="--use_aggressive_weights"
        ;;
    *)
        echo "无效选择,使用默认标准训练模式"
        ATTENTION="cbam_aspp"
        EPOCHS=80
        BATCH_SIZE=8
        AGGRESSIVE=""
        ;;
esac

echo ""
echo "训练配置:"
echo "  注意力类型: $ATTENTION"
echo "  训练轮数: $EPOCHS"
echo "  批次大小: $BATCH_SIZE"
echo "  激进权重: $([ -n \"$AGGRESSIVE\" ] && echo '是' || echo '否')"
echo ""

# 询问是否继续训练
read -p "是否从头开始训练? (y/n): " from_scratch

if [ "$from_scratch" = "n" ] || [ "$from_scratch" = "N" ]; then
    echo ""
    read -p "请输入预训练模型路径 (例如 outputs/checkpoints/cbam_aspp_best_model.pth): " resume_path
    
    if [ -f "$resume_path" ]; then
        RESUME_ARG="--resume $resume_path"
        echo "✓ 将从 $resume_path 继续训练"
    else
        echo "⚠ 文件不存在,将从头开始训练"
        RESUME_ARG=""
    fi
else
    RESUME_ARG=""
    echo "✓ 将从头开始训练"
fi

echo ""
echo "开始训练..."
echo "=========================================="
echo ""

# 启动训练
python3 src/training/train_optimized.py \
    --use_gpu True \
    --attention $ATTENTION \
    --epochs $EPOCHS \
    --batch_size $BATCH_SIZE \
    --lr 2e-4 \
    --weight_decay 1e-4 \
    --cosine_t0 10 \
    --min_lr 1e-6 \
    --warmup_epochs 5 \
    --early_stopping_patience 15 \
    --save_interval 10 \
    --num_workers 4 \
    $AGGRESSIVE \
    $RESUME_ARG

echo ""
echo "=========================================="
echo "训练完成!"
echo "=========================================="
