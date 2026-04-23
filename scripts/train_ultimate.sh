#!/bin/bash
# 极致优化训练脚本 - 目标 IoU 80%
# 使用 ResNet-101 + FPN + 注意力 + 边界优化

echo "=========================================="
echo "U-Net++ 极致优化版 - 目标 IoU 80%"
echo "=========================================="
echo ""

# 设置Python路径
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# 显示警告
echo "⚠️  重要提示:"
echo "   此版本使用 ResNet-101 编码器,参数量较大(~60M)"
echo "   预计训练时间: 24-36小时 (M4芯片)"
echo "   预期 mIoU: 75-80%"
echo ""
read -p "确认开始训练? (y/n): " confirm

if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
    echo "已取消训练"
    exit 0
fi

# 选择配置
echo ""
echo "选择训练配置:"
echo "  1. 快速验证模式 (无FPN, CBAM注意力, 50轮, 预期60-65% IoU, 12-15小时)"
echo "  2. 标准激进模式 (FPN+CBAM+ASPP, 100轮, 预期70-75% IoU, 20-24小时)"
echo "  3. 极致优化模式 (完整架构+边界优化, 120轮, 预期75-80% IoU, 24-36小时)"
echo ""
read -p "请选择 (1-3): " mode

case $mode in
    1)
        echo ""
        echo "快速验证模式 - 无FPN, 预期60-65% IoU"
        USE_FPN="False"
        ATTENTION="cbam"
        EPOCHS=50
        BATCH_SIZE=16
        USE_BOUNDARY="False"
        ;;
    2)
        echo ""
        echo "标准激进模式 - FPN+CBAM+ASPP, 预期70-75% IoU"
        USE_FPN="True"
        ATTENTION="cbam_aspp"
        EPOCHS=100
        BATCH_SIZE=6
        USE_BOUNDARY="False"
        ;;
    3)
        echo ""
        echo "极致优化模式 - 完整架构, 预期75-80% IoU"
        USE_FPN="True"
        ATTENTION="full"
        EPOCHS=120
        BATCH_SIZE=6
        USE_BOUNDARY="True"
        ;;
    *)
        echo "无效选择,使用标准激进模式"
        USE_FPN="True"
        ATTENTION="cbam_aspp"
        EPOCHS=100
        BATCH_SIZE=6
        USE_BOUNDARY="False"
        ;;
esac

echo ""
echo "训练配置:"
echo "  编码器: ResNet-101 (ImageNet预训练)"
echo "  FPN: $USE_FPN"
echo "  注意力类型: $ATTENTION"
echo "  边界优化: $USE_BOUNDARY"
echo "  深度可分离卷积: True"
echo "  训练轮数: $EPOCHS"
echo "  批次大小: $BATCH_SIZE"
echo "  超激进类别权重: Truck=10.0"
echo ""

# 询问是否继续训练
read -p "是否从头开始训练? (y/n): " from_scratch

if [ "$from_scratch" = "n" ] || [ "$from_scratch" = "N" ]; then
    echo ""
    read -p "请输入预训练模型路径: " resume_path
    
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
python3 src/training/train_ultimate.py \
    --use_gpu True \
    --use_fpn $USE_FPN \
    --attention $ATTENTION \
    --use_boundary_refinement $USE_BOUNDARY \
    --use_separable_conv True \
    --use_aggressive_weights True \
    --epochs $EPOCHS \
    --batch_size $BATCH_SIZE \
    --lr 1e-4 \
    --weight_decay 1e-4 \
    --early_stopping_patience 20 \
    --save_interval 10 \
    --num_workers 4 \
    $RESUME_ARG

echo ""
echo "=========================================="
echo "训练完成!"
echo "=========================================="
echo ""
echo "查看训练日志:"
echo "  tensorboard --logdir outputs/logs"
echo ""
