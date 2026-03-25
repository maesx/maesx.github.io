#!/usr/bin/env python3
"""
完整的模型测试和验证脚本
"""
import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import torch
import numpy as np
from tqdm import tqdm
import cv2
from pathlib import Path

from src.models.unet_plusplus import UNetPlusPlus
from src.data.dataset import get_dataloader
from src.utils.losses import calculate_iou, calculate_pixel_accuracy

def test_model(model_path, split='test', device='mps'):
    """
    测试模型性能
    
    Args:
        model_path: 模型路径
        split: 数据集划分 (train/val/test)
        device: 设备
    """
    print("=" * 70)
    print("模型测试和验证")
    print("=" * 70)
    print()
    
    # 设置设备
    device = torch.device(device if torch.backends.mps.is_available() else 'cpu')
    print(f"使用设备: {device}")
    
    # 加载模型
    print(f"\n加载模型: {model_path}")
    checkpoint = torch.load(model_path, map_location=device, weights_only=False)
    args = checkpoint.get('args', None)
    
    if args:
        num_classes = args.num_classes
        encoder_name = args.encoder
        deep_supervision = args.deep_supervision
    else:
        num_classes = 4
        encoder_name = 'vgg19'
        deep_supervision = True
    
    model = UNetPlusPlus(
        in_channels=3,
        num_classes=num_classes,
        deep_supervision=deep_supervision,
        encoder_name=encoder_name,
        pretrained=False
    ).to(device)
    
    model.load_state_dict(checkpoint['model_state_dict'])
    model.eval()
    
    print(f"  - 训练轮数: {checkpoint.get('epoch', 'N/A')}")
    print(f"  - 最佳IoU: {checkpoint.get('best_iou', 0):.4f}")
    
    # 创建数据加载器
    print(f"\n加载{split}数据集...")
    data_loader = get_dataloader(
        data_dir='road_vehicle_pedestrian_det_datasets',
        masks_dir='outputs/masks',
        split=split,
        batch_size=8,
        img_size=(512, 512),
        num_workers=0,
        pin_memory=False
    )
    
    print(f"数据集大小: {len(data_loader.dataset)} 张图像")
    
    # 测试
    print(f"\n开始测试...")
    
    all_ious = []
    all_accs = []
    class_ious = {i: [] for i in range(num_classes)}
    class_names = ['Background', 'Car', 'Truck', 'Bus']
    
    with torch.no_grad():
        for images, masks in tqdm(data_loader, desc=f'测试{split}集'):
            images = images.to(device)
            masks = masks.to(device)
            
            # 推理
            outputs = model(images)
            if isinstance(outputs, list):
                outputs = outputs[-1]
            
            preds = torch.argmax(outputs, dim=1)
            
            # 计算指标
            for pred, mask in zip(preds, masks):
                class_iou, mean_iou = calculate_iou(pred.unsqueeze(0), 
                                                     mask.unsqueeze(0), 
                                                     num_classes)
                acc = calculate_pixel_accuracy(pred, mask)
                
                all_ious.append(mean_iou.item())
                all_accs.append(acc)
                
                # 各类别IoU
                for cls in range(num_classes):
                    class_ious[cls].append(class_iou[cls].item())
    
    # 统计结果
    mean_iou = np.mean(all_ious)
    mean_acc = np.mean(all_accs)
    std_iou = np.std(all_ious)
    
    print()
    print("=" * 70)
    print("测试结果")
    print("=" * 70)
    print()
    
    print(f"📊 整体性能:")
    print(f"  平均IoU:  {mean_iou:.4f} ± {std_iou:.4f} ({mean_iou*100:.2f}%)")
    print(f"  平均准确率: {mean_acc:.4f} ({mean_acc*100:.2f}%)")
    print()
    
    print(f"📈 各类别IoU:")
    for cls, name in enumerate(class_names):
        cls_iou = np.mean(class_ious[cls])
        cls_std = np.std(class_ious[cls])
        bar = '█' * int(cls_iou * 20)
        print(f"  {name:12s}: {cls_iou:.4f} ± {cls_std:.4f} {bar}")
    
    print()
    print(f"🎯 目标达成情况:")
    if mean_iou >= 0.80:
        print(f"  ✅ 已达到目标 IoU ≥ 80%")
        print(f"  ✅ 当前IoU: {mean_iou*100:.2f}%")
    else:
        print(f"  ⚠️  未达到目标 IoU ≥ 80%")
        print(f"  📊 当前IoU: {mean_iou*100:.2f}%")
        print(f"  📊 差距: {(0.80 - mean_iou)*100:.2f}%")
    
    print()
    
    # 与训练最佳对比
    best_train_iou = checkpoint.get('best_iou', 0)
    print(f"📉 性能对比:")
    print(f"  训练最佳IoU: {best_train_iou:.4f} ({best_train_iou*100:.2f}%)")
    print(f"  {split}集IoU:    {mean_iou:.4f} ({mean_iou*100:.2f}%)")
    
    diff = mean_iou - best_train_iou
    if diff >= 0:
        print(f"  提升: +{diff:.4f} (+{diff*100:.2f}%)")
    else:
        print(f"  差距: {diff:.4f} ({diff*100:.2f}%)")
    
    print()
    print("=" * 70)
    
    return mean_iou, class_ious


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='模型测试和验证')
    parser.add_argument('--model_path', type=str, 
                       default='outputs/checkpoints/best_model.pth',
                       help='模型路径')
    parser.add_argument('--split', type=str, default='test',
                       choices=['train', 'val', 'test'],
                       help='测试的数据集划分')
    parser.add_argument('--device', type=str, default='mps',
                       help='设备')
    
    args = parser.parse_args()
    
    test_model(args.model_path, args.split, args.device)
