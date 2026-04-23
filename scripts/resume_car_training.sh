#!/bin/bash
# Car模型继续训练脚本
# 从epoch 7继续,模型文件: car-best_model.pth

echo "========================================"
echo "Car分割模型 - 继续训练"
echo "========================================"
echo "模型检查点: outputs/checkpoints/car-best_model.pth"
echo "当前Epoch: 7/20"
echo "最佳IoU: 0.5612 (56.12%)"
echo "Mask目录: outputs/masks_car"
echo "========================================"
echo ""

# 继续训练命令
python3 src/training/train.py \
  --use_gpu \
  --data_dir road_vehicle_pedestrian_det_datasets \
  --masks_dir outputs/masks_car \
  --output_dir outputs \
  --num_classes 4 \
  --batch_size 8 \
  --epochs 20 \
  --lr 0.0001 \
  --weight_decay 1e-5 \
  --grad_clip 1.0 \
  --img_size 512 512 \
  --num_workers 0 \
  --save_interval 5 \
  --early_stopping_patience 10 \
  --warmup_epochs 2 \
  --min_lr 3e-5 \
  --lr_adjustment_factor 0.6 \
  --deep_supervision True \
  --encoder vgg19 \
  --pretrained True \
  --model_name car-best_model \
  --resume outputs/checkpoints/car-best_model.pth

echo ""
echo "训练完成!"
