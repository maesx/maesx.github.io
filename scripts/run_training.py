#!/usr/bin/env python3
"""直接启动训练脚本"""
import subprocess
import sys

cmd = [
    sys.executable, "src/training/train.py",
    "--use_gpu",
    "--batch_size", "4",
    "--epochs", "30",
    "--lr", "1e-4",
    "--data_dir", "road_vehicle_pedestrian_det_datasets",
    "--masks_dir", "outputs/masks_car",
    "--output_dir", "outputs",
    "--num_classes", "4",
    "--deep_supervision", "True",
    "--encoder", "vgg19",
    "--pretrained", "True",
    "--save_interval", "10",
    "--early_stopping_patience", "20",
    "--min_lr", "1e-5",
    "--lr_adjustment_factor", "0.7",
    "--warmup_epochs", "3",
    "--model_name", "best_model",
    "--num_workers", "0",
    "--balance_sampling",
    "--resume", "outputs/checkpoints/best_model.pth"
]

print("=" * 60)
print("启动MPS优化训练")
print("=" * 60)
print(f"命令: {' '.join(cmd)}")
print("=" * 60)

subprocess.run(cmd)
