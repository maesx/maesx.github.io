"""
数据加载和数据增强模块
"""
import os
import random
from pathlib import Path
from typing import List, Optional, Tuple

import albumentations as A
import cv2
import numpy as np
import torch
from albumentations.pytorch import ToTensorV2
from torch.utils.data import DataLoader, Dataset


class RoadVehicleDataset(Dataset):
    """道路车辆分割数据集"""

    def __init__(
        self,
        images_dir: str,
        masks_dir: str,
        split: str = 'train',
        transform: Optional[A.Compose] = None,
        img_size: Tuple[int, int] = (512, 512),
        subset_ratio: float = 1.0,
        random_seed: int = 42
    ) -> None:
        """
        初始化数据集

        Args:
            images_dir: 图像目录
            masks_dir: 掩码目录
            split: 数据集划分(train/val/test)
            transform: 数据增强变换
            img_size: 图像尺寸
            subset_ratio: 使用数据集的比例 (0.0-1.0), 1.0表示使用全部数据
            random_seed: 随机种子,用于可重复的数据子集选择
        """
        self.images_dir = Path(images_dir) / split
        self.masks_dir = Path(masks_dir) / split
        self.transform = transform
        self.img_size = img_size
        
        # 获取所有图像文件
        all_image_files = list(self.images_dir.glob('*.jpg')) + list(self.images_dir.glob('*.png'))
        
        # 应用子集比例
        if subset_ratio < 1.0:
            random.seed(random_seed)
            subset_size = int(len(all_image_files) * subset_ratio)
            self.image_files: List[Path] = random.sample(all_image_files, subset_size)
            print(f"加载 {split} 数据集: {len(self.image_files)} 张图像 (从{len(all_image_files)}张中随机选择{subset_ratio*100:.1f}%)")
        else:
            self.image_files = all_image_files
            print(f"加载 {split} 数据集: {len(self.image_files)} 张图像")

    def __len__(self) -> int:
        return len(self.image_files)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        # 读取图像
        img_path = self.image_files[idx]
        image = cv2.imread(str(img_path))
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # 读取掩码
        mask_path = self.masks_dir / (img_path.stem + '.png')
        mask = cv2.imread(str(mask_path), cv2.IMREAD_GRAYSCALE)
        
        # 应用数据增强
        if self.transform:
            augmented = self.transform(image=image, mask=mask)
            image = augmented['image']
            mask = augmented['mask']
        else:
            # 默认变换: resize + normalize
            image = cv2.resize(image, self.img_size)
            mask = cv2.resize(mask, self.img_size, interpolation=cv2.INTER_NEAREST)
            image = torch.from_numpy(image).permute(2, 0, 1).float() / 255.0
            mask = torch.from_numpy(mask).long()
        
        return image, mask


def get_training_augmentation(img_size: Tuple[int, int] = (512, 512)) -> A.Compose:
    """
    训练集数据增强（增强版）
    包括:翻转、旋转、缩放、亮度对比度调整、弹性形变、颜色抖动等
    """
    train_transform = A.Compose([
        # 调整大小到稍大的尺寸,以便后续裁剪
        A.SmallestMaxSize(max_size=int(img_size[0] * 1.3)),
        
        # 随机裁剪到目标尺寸
        A.RandomCrop(height=img_size[0], width=img_size[1]),
        
        # 水平翻转 (提高概率)
        A.HorizontalFlip(p=0.5),
        
        # 垂直翻转 (提高概率)
        A.VerticalFlip(p=0.3),
        
        # 随机旋转90度
        A.RandomRotate90(p=0.5),
        
        # 亮度和对比度调整 (增强范围)
        A.RandomBrightnessContrast(brightness_limit=0.3, contrast_limit=0.3, p=0.6),
        
        # 色调、饱和度、亮度调整 (新增)
        A.HueSaturationValue(hue_shift_limit=20, sat_shift_limit=30, val_shift_limit=20, p=0.5),
        
        # RGB偏移 (新增)
        A.RGBShift(r_shift_limit=20, g_shift_limit=20, b_shift_limit=20, p=0.3),
        
        # 通道混洗 (新增)
        A.ChannelShuffle(p=0.2),
        
        # 高斯模糊 (提高概率)
        A.GaussianBlur(blur_limit=7, p=0.4),
        
        # 高斯噪声 (提高概率)
        A.GaussNoise(p=0.4),
        
        # 弹性形变 (提高概率)
        A.ElasticTransform(p=0.4),
        
        # 网格畸变 (提高概率)
        A.GridDistortion(num_steps=5, distort_limit=0.3, p=0.4),
        
        # 随机阴影 (新增)
        A.RandomShadow(shadow_roi=(0, 0, 1, 1), shadow_dimension=5, p=0.3),
        
        # 随机太阳光斑 (新增)
        A.RandomSunFlare(flare_roi=(0, 0, 1, 0.5), src_radius=100, p=0.2),
        
        # 粗糙失真 (新增)
        A.CoarseDropout(p=0.3),
        
        # ISO噪声 (新增)
        A.ISONoise(color_shift=(0.01, 0.05), intensity=(0.1, 0.5), p=0.2),
        
        # 标准化
        A.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)),
        
        # 转换为Tensor
        ToTensorV2(),
    ])
    
    return train_transform


def get_validation_augmentation(img_size: Tuple[int, int] = (512, 512)) -> A.Compose:
    """
    验证/测试集数据增强
    仅包含resize和normalize
    """
    val_transform = A.Compose([
        A.Resize(img_size[0], img_size[1]),
        A.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)),
        ToTensorV2(),
    ])
    
    return val_transform


def get_dataloader(
    data_dir: str,
    masks_dir: str,
    split: str = 'train',
    batch_size: int = 8,
    img_size: Tuple[int, int] = (512, 512),
    num_workers: int = 4,
    pin_memory: bool = True,
    subset_ratio: float = 1.0,
    random_seed: int = 42
) -> DataLoader:
    """
    获取数据加载器
    
    Args:
        data_dir: 数据目录
        masks_dir: 掩码目录
        split: 数据集划分
        batch_size: 批次大小
        img_size: 图像尺寸
        num_workers: 工作进程数
        pin_memory: 是否锁页内存
        subset_ratio: 使用数据集的比例 (0.0-1.0)
        random_seed: 随机种子
        
    Returns:
        DataLoader
    """
    images_dir = os.path.join(data_dir, 'images')
    
    if split == 'train':
        transform = get_training_augmentation(img_size)
        shuffle = True
    else:
        transform = get_validation_augmentation(img_size)
        shuffle = False
    
    dataset = RoadVehicleDataset(
        images_dir=images_dir,
        masks_dir=masks_dir,
        split=split,
        transform=transform,
        img_size=img_size,
        subset_ratio=subset_ratio,
        random_seed=random_seed
    )
    
    dataloader = DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=num_workers,
        pin_memory=pin_memory
    )
    
    return dataloader


if __name__ == '__main__':
    # 测试数据加载器
    print("测试数据加载器...")
    
    train_loader = get_dataloader(
        data_dir='road_vehicle_pedestrian_det_datasets',
        masks_dir='outputs/masks',
        split='train',
        batch_size=4,
        img_size=(512, 512),
        num_workers=0
    )
    
    # 获取一个批次
    images, masks = next(iter(train_loader))
    print(f"图像批次形状: {images.shape}")
    print(f"掩码批次形状: {masks.shape}")
    print(f"掩码唯一值: {torch.unique(masks)}")
