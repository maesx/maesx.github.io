"""
数据加载和数据增强模块
"""
import os
import random
from collections import OrderedDict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import albumentations as A
import cv2
import numpy as np
import torch
from albumentations.pytorch import ToTensorV2
from torch.utils.data import DataLoader, Dataset


class LRUCache:
    """LRU (Least Recently Used) 缓存实现
    
    用于缓存预处理后的图像和掩码，减少重复计算开销。
    当缓存达到上限时，自动淘汰最久未使用的数据。
    """
    
    def __init__(self, max_size: int = 1000):
        """
        Args:
            max_size: 缓存最大容量
        """
        self.max_size = max_size
        self.cache: OrderedDict = OrderedDict()
    
    def get(self, key: str) -> Optional[Tuple[np.ndarray, np.ndarray]]:
        """获取缓存数据，同时更新访问顺序"""
        if key in self.cache:
            # 移到末尾（最近使用）
            self.cache.move_to_end(key)
            return self.cache[key]
        return None
    
    def put(self, key: str, value: Tuple[np.ndarray, np.ndarray]) -> None:
        """添加数据到缓存"""
        if key in self.cache:
            # 已存在，更新并移到末尾
            self.cache.move_to_end(key)
            self.cache[key] = value
        else:
            # 新数据
            if len(self.cache) >= self.max_size:
                # 淘汰最久未使用的（第一个）
                self.cache.popitem(last=False)
            self.cache[key] = value
    
    def __len__(self) -> int:
        return len(self.cache)
    
    def clear(self) -> None:
        """清空缓存"""
        self.cache.clear()


class RoadVehicleDataset(Dataset):
    """道路车辆分割数据集，支持 LRU 缓存"""

    def __init__(
        self,
        images_dir: str,
        masks_dir: str,
        split: str = 'train',
        transform: Optional[A.Compose] = None,
        img_size: Tuple[int, int] = (512, 512),
        subset_ratio: float = 1.0,
        random_seed: int = 42,
        use_cache: bool = True,
        cache_size: int = 1000
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
            use_cache: 是否使用缓存
            cache_size: 缓存最大容量
        """
        self.images_dir = Path(images_dir) / split
        self.masks_dir = Path(masks_dir) / split
        self.transform = transform
        self.img_size = img_size
        self.use_cache = use_cache
        
        # 初始化缓存
        if self.use_cache:
            self.cache = LRUCache(max_size=cache_size)
            print(f"数据缓存已启用，缓存大小: {cache_size}")
        
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
        img_path = self.image_files[idx]
        cache_key = str(img_path)
        
        # 尝试从缓存获取
        if self.use_cache:
            cached = self.cache.get(cache_key)
            if cached is not None:
                image, mask = cached
                # 应用变换（变换通常包含随机增强，所以需要重新应用）
                if self.transform:
                    augmented = self.transform(image=image, mask=mask)
                    image = augmented['image']
                    mask = augmented['mask']
                else:
                    image = torch.from_numpy(image).permute(2, 0, 1).float() / 255.0
                    mask = torch.from_numpy(mask).long()
                return image, mask
        
        # 读取图像
        image = cv2.imread(str(img_path))
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # 读取掩码
        mask_path = self.masks_dir / (img_path.stem + '.png')
        mask = cv2.imread(str(mask_path), cv2.IMREAD_GRAYSCALE)
        
        # 缓存原始数据（后续变换前的数据）
        if self.use_cache:
            self.cache.put(cache_key, (image.copy(), mask.copy()))
        
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
    random_seed: int = 42,
    use_cache: bool = True,
    cache_size: int = 1000,
    prefetch_factor: int = 2,
    persistent_workers: bool = True
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
        use_cache: 是否使用缓存
        cache_size: 缓存最大容量
        prefetch_factor: 预取因子，每个worker预取的批次数
        persistent_workers: 是否保持worker进程活跃
        
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
        random_seed=random_seed,
        use_cache=use_cache,
        cache_size=cache_size
    )
    
    # DataLoader 参数优化
    dataloader_kwargs = {
        'dataset': dataset,
        'batch_size': batch_size,
        'shuffle': shuffle,
        'num_workers': num_workers,
        'pin_memory': pin_memory
    }
    
    # 仅在 num_workers > 0 时添加 prefetch_factor 和 persistent_workers
    if num_workers > 0:
        dataloader_kwargs['prefetch_factor'] = prefetch_factor
        dataloader_kwargs['persistent_workers'] = persistent_workers
    
    dataloader = DataLoader(**dataloader_kwargs)
    
    return dataloader


def calculate_class_weights(
    masks_dir: str,
    num_classes: int = 4,
    split: str = 'train'
) -> torch.Tensor:
    """
    根据数据集计算类别权重
    
    使用 inverse frequency 方法：权重 = 总样本数 / (类别数 * 该类别样本数)
    
    Args:
        masks_dir: 掩码目录
        num_classes: 类别数
        split: 数据集划分
    
    Returns:
        类别权重张量 [num_classes]
    """
    masks_path = Path(masks_dir) / split
    
    if not masks_path.exists():
        raise FileNotFoundError(f"掩码目录不存在: {masks_path}")
    
    # 统计每个类别的像素数
    class_pixel_counts = np.zeros(num_classes, dtype=np.int64)
    total_pixels = 0
    
    mask_files = list(masks_path.glob('*.png'))
    print(f"正在计算类别权重，扫描 {len(mask_files)} 张掩码...")
    
    for mask_file in mask_files:
        mask = cv2.imread(str(mask_file), cv2.IMREAD_GRAYSCALE)
        if mask is None:
            continue
            
        total_pixels += mask.size
        
        # 统计每个类别的像素数
        for class_id in range(num_classes):
            class_pixel_counts[class_id] += np.sum(mask == class_id)
    
    # 避免除零
    class_pixel_counts = np.maximum(class_pixel_counts, 1)
    
    # 计算权重 (inverse frequency)
    # 权重 = 总像素数 / (类别数 * 该类别像素数)
    weights = total_pixels / (num_classes * class_pixel_counts)
    
    # 归一化权重
    weights = weights / weights.sum() * num_classes
    
    print(f"\n类别像素分布:")
    for i in range(num_classes):
        percentage = class_pixel_counts[i] / total_pixels * 100
        print(f"  类别 {i}: {class_pixel_counts[i]:,} 像素 ({percentage:.2f}%), 权重: {weights[i]:.4f}")
    
    return torch.tensor(weights, dtype=torch.float32)


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
