#!/bin/bash
# 继续 best_model 训练脚本
# 目标: 将 IoU 从 73.88% 提升到 80%
# 配置: batch_size=8, epochs=20

echo "=========================================="
echo "训练目标: IoU 73.88% -> 80%"
echo "=========================================="
echo ""

# 显示当前模型信息
echo "📊 当前模型状态:"
python3 -c "
import torch
checkpoint = torch.load('outputs/checkpoints/best_model.pth', map_location='cpu', weights_only=False)
print(f'  - 当前 IoU: {checkpoint[\"best_iou\"]*100:.2f}%')
print(f'  - 训练轮数: Epoch {checkpoint[\"epoch\"]}')
"
echo ""

# 训练参数说明
echo "🎯 训练策略:"
echo "  - 批次大小: 8 (增大以提高训练稳定性)"
echo "  - 训练轮数: 20 (继续训练,从Epoch 16开始)"
echo "  - 学习率: 1e-4 (较低学习率进行微调)"
echo "  - 早停机制: patience=15 (给模型更多收敛机会)"
echo "  - 最小学习率: 1e-5 (防止学习率过低)"
echo "  - 学习率调整: factor=0.7 (IoU下降时温和降速)"
echo "  - 深度监督: 启用 (提升训练效果)"
echo "  - 梯度裁剪: 1.0 (防止梯度爆炸)"
echo ""

# 启动训练
echo "🚀 开始训练..."
echo ""

python3 src/training/train.py \
    --use_gpu \
    --batch_size 8 \
    --epochs 20 \
    --lr 1e-4 \
    --weight_decay 1e-5 \
    --grad_clip 1.0 \
    --data_dir road_vehicle_pedestrian_det_datasets \
    --masks_dir outputs/masks_car \
    --output_dir outputs \
    --num_classes 4 \
    --deep_supervision True \
    --encoder vgg19 \
    --pretrained True \
    --img_size 512 512 \
    --num_workers 4 \
    --save_interval 5 \
    --early_stopping_patience 15 \
    --min_lr 1e-5 \
    --lr_adjustment_factor 0.7 \
    --warmup_epochs 3 \
    --model_name best_model \
    --balance_sampling \
    --resume outputs/checkpoints/best_model.pth

echo ""
echo "=========================================="
echo "✓ 训练完成!"
echo "=========================================="

# 显示训练结果
echo ""
echo "📊 最终模型性能:"
python3 scripts/check_model_iou.py 2>/dev/null || python3 -c "
import torch
checkpoint = torch.load('outputs/checkpoints/best_model.pth', map_location='cpu', weights_only=False)
print(f'  - 最终 IoU: {checkpoint[\"best_iou\"]*100:.2f}%')
print(f'  - 训练轮数: Epoch {checkpoint[\"epoch\"]}')
if checkpoint['best_iou'] >= 0.80:
    print('  - 🎉 恭喜! 已达到目标 IoU ≥ 80%')
else:
    gap = 0.80 - checkpoint['best_iou']
    print(f'  - 📈 距离目标还差: {gap*100:.2f}%')
"
