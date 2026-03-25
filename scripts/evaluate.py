"""
模型评估脚本
在测试集上计算IoU和准确率
"""
import argparse
import os
import sys
from pathlib import Path

import numpy as np
import torch
from torch.utils.data import DataLoader
from tqdm import tqdm

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data.dataset import RoadVehicleDataset, get_validation_augmentation
from src.models.unet_plusplus import UNetPlusPlus
from src.utils.losses import calculate_iou, calculate_pixel_accuracy


def evaluate_model(
    model_path: str,
    data_dir: str,
    masks_dir: str,
    split: str = 'test',
    batch_size: int = 8,
    num_classes: int = 4,
    device: str = 'cpu'
) -> dict:
    """
    评估模型
    
    Args:
        model_path: 模型路径
        data_dir: 数据目录
        masks_dir: 掩码目录
        split: 数据集划分
        batch_size: 批次大小
        num_classes: 类别数
        device: 设备
        
    Returns:
        评估结果字典
    """
    # 设置设备
    device = torch.device(device)
    print(f"使用设备: {device}")
    
    # 加载模型
    print(f"\n加载模型: {model_path}")
    checkpoint = torch.load(model_path, map_location=device, weights_only=False)
    args = checkpoint.get('args', None)
    
    # 处理无args的旧版checkpoint
    if args is None:
        encoder_name = 'vgg19'
        deep_supervision = True
        img_size = [512, 512]
    else:
        encoder_name = args.encoder
        deep_supervision = args.deep_supervision
        img_size = args.img_size
    
    model = UNetPlusPlus(
        in_channels=3,
        num_classes=num_classes,
        deep_supervision=deep_supervision,
        encoder_name=encoder_name,
        pretrained=False
    )
    model.load_state_dict(checkpoint['model_state_dict'])
    model = model.to(device)
    model.eval()
    
    print(f"  - 编码器: {encoder_name}")
    print(f"  - 深度监督: {deep_supervision}")
    print(f"  - 训练时的IoU: {checkpoint.get('best_iou', 'Unknown')}")
    
    # 加载测试数据集
    print(f"\n加载{split}数据集...")
    images_dir = os.path.join(data_dir, 'images')
    dataset = RoadVehicleDataset(
        images_dir=images_dir,
        masks_dir=masks_dir,
        split=split,
        img_size=tuple(img_size),
        transform=get_validation_augmentation(tuple(img_size))
    )
    
    dataloader = DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=4,
        pin_memory=True if device.type != 'cpu' else False
    )
    
    print(f"  - 样本数量: {len(dataset)}")
    
    # 评估
    print(f"\n开始评估...")
    total_iou = 0.0
    total_acc = 0.0
    class_ious = {i: [] for i in range(num_classes)}
    
    with torch.no_grad():
        for images, masks in tqdm(dataloader, desc="评估中"):
            images = images.to(device)
            masks = masks.to(device)
            
            # 预测
            outputs = model(images)
            if isinstance(outputs, list):
                outputs = outputs[-1]
            
            preds = torch.argmax(outputs, dim=1)
            
            # 计算指标
            batch_iou, mean_iou = calculate_iou(preds, masks, num_classes)
            acc = calculate_pixel_accuracy(preds, masks)
            
            total_iou += mean_iou.item()
            total_acc += acc
            
            # 记录每个类别的IoU
            for cls_id in range(num_classes):
                cls_iou = batch_iou[cls_id].item()
                if cls_iou > 0:  # 忽略不存在的类别
                    class_ious[cls_id].append(cls_iou)
    
    # 计算平均指标
    num_batches = len(dataloader)
    avg_iou = total_iou / num_batches
    avg_acc = total_acc / num_batches
    
    # 计算每个类别的平均IoU
    class_mean_ious = {}
    class_names = ['background', 'car', 'truck', 'bus']
    for cls_id in range(num_classes):
        if class_ious[cls_id]:
            class_mean_ious[class_names[cls_id]] = np.mean(class_ious[cls_id])
        else:
            class_mean_ious[class_names[cls_id]] = 0.0
    
    results = {
        'mean_iou': avg_iou,
        'pixel_accuracy': avg_acc,
        'class_ious': class_mean_ious,
        'num_samples': len(dataset)
    }
    
    return results


def main():
    parser = argparse.ArgumentParser(description='模型评估脚本')
    parser.add_argument('--model_path', type=str, default='outputs/checkpoints/best_model.pth',
                        help='模型权重路径')
    parser.add_argument('--data_dir', type=str, default='road_vehicle_pedestrian_det_datasets',
                        help='数据集根目录')
    parser.add_argument('--masks_dir', type=str, default='outputs/masks',
                        help='掩码目录')
    parser.add_argument('--split', type=str, default='test',
                        choices=['train', 'val', 'test'],
                        help='评估的数据集划分')
    parser.add_argument('--batch_size', type=int, default=8,
                        help='批次大小')
    parser.add_argument('--num_classes', type=int, default=4,
                        help='类别数')
    parser.add_argument('--device', type=str, default='cpu',
                        help='评估设备')
    
    args = parser.parse_args()
    
    # 自动检测设备
    if args.device == 'cpu':
        if torch.backends.mps.is_available():
            args.device = 'mps'
        elif torch.cuda.is_available():
            args.device = 'cuda'
    
    print("="*60)
    print("模型评估")
    print("="*60)
    
    results = evaluate_model(
        model_path=args.model_path,
        data_dir=args.data_dir,
        masks_dir=args.masks_dir,
        split=args.split,
        batch_size=args.batch_size,
        num_classes=args.num_classes,
        device=args.device
    )
    
    # 打印结果
    print("\n" + "="*60)
    print("评估结果")
    print("="*60)
    print(f"数据集: {args.split}")
    print(f"样本数: {results['num_samples']}")
    print(f"\n整体性能:")
    print(f"  - 平均IoU (mIoU): {results['mean_iou']:.4f} ({results['mean_iou']*100:.2f}%)")
    print(f"  - 像素准确率: {results['pixel_accuracy']:.4f} ({results['pixel_accuracy']*100:.2f}%)")
    
    print(f"\n各类别IoU:")
    for class_name, iou in results['class_ious'].items():
        print(f"  - {class_name:12s}: {iou:.4f} ({iou*100:.2f}%)")
    
    print("\n" + "="*60)


if __name__ == '__main__':
    main()
