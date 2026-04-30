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
from torch.utils.data import DataLoader, Dataset, WeightedRandomSampler
from tqdm import tqdm


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


class CarFocusedDataset(Dataset):
    """
    Car专用数据集 - 三分类模式
    将Truck和Bus合并为Others类别，专注Car检测
    
    类别映射:
    - 0: Background
    - 1: Car (主要目标)
    - 2: Others (Truck + Bus)
    """

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
            subset_ratio: 使用数据集的比例 (0.0-1.0)
            random_seed: 随机种子
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
            print(f"[Car专用模式] 加载 {split} 数据集: {len(self.image_files)} 张图像 (采样率{subset_ratio*100:.1f}%)")
        else:
            self.image_files = all_image_files
            print(f"[Car专用模式] 加载 {split} 数据集: {len(self.image_files)} 张图像")
        
        # 类别统计
        self._analyze_class_distribution()

    def _analyze_class_distribution(self):
        """分析数据集中的类别分布"""
        print(f"[Car专用模式] 类别映射: BG=0, Car=1, Others(Truck+Bus)=2")

    def simplify_classes(self, mask: np.ndarray) -> np.ndarray:
        """
        简化类别: 将Truck(2)和Bus(3)合并为Others(2)
        
        Args:
            mask: 原始掩码 (0=BG, 1=Car, 2=Truck, 3=Bus)
        
        Returns:
            简化后的掩码 (0=BG, 1=Car, 2=Others)
        """
        mask_simplified = mask.copy()
        # Truck (2) 和 Bus (3) 都映射为 Others (2)
        mask_simplified[mask == 3] = 2  # Bus -> Others
        # Truck已经是2，无需修改
        return mask_simplified

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
        
        # 简化类别映射
        mask = self.simplify_classes(mask)
        
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
    balance_sampling: bool = False,
    car_only: bool = False
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
        balance_sampling: 是否使用类别平衡采样
        car_only: 是否只使用包含Car的样本
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
    
    # 如果启用 car_only，过滤只包含 Car 的样本
    if car_only and split == 'train':
        print("过滤数据集: 只保留包含 Car 的样本...")
        import cv2
        from pathlib import Path
        
        filtered_files = []
        mask_path = Path(masks_dir) / split
        
        for img_file in tqdm(dataset.image_files, desc="过滤样本"):
            mask_file = mask_path / (img_file.stem + '.png')
            if mask_file.exists():
                mask = cv2.imread(str(mask_file), cv2.IMREAD_GRAYSCALE)
                # 检查是否包含 Car (类别 1)
                if (mask == 1).sum() > 100:  # 至少100个像素的 Car
                    filtered_files.append(img_file)
        
        print(f"过滤后样本数: {len(filtered_files)} / {len(dataset.image_files)}")
        dataset.image_files = filtered_files
    
    # 使用加权随机采样器进行类别平衡
    if balance_sampling and split == 'train':
        # 计算每个样本的权重（基于样本数量较少的类别）
        print("使用类别平衡采样...")
        sampler = create_balanced_sampler(dataset, masks_dir, split)
        shuffle = False  # 使用sampler时不能shuffle
    else:
        sampler = None
    
    dataloader = DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle if sampler is None else False,
        sampler=sampler,
        num_workers=num_workers,
        pin_memory=pin_memory if torch.cuda.is_available() else False,  # MPS/CPU不支持pin_memory
        persistent_workers=num_workers > 0 if num_workers > 0 else False,  # macOS MPS兼容性：num_workers=0时必须禁用
        drop_last=split == 'train'  # 训练时丢弃不完整的批次
    )
    
    return dataloader


def get_car_focused_dataloader(
    data_dir: str,
    masks_dir: str,
    split: str = 'train',
    batch_size: int = 8,
    img_size: Tuple[int, int] = (512, 512),
    num_workers: int = 4,
    pin_memory: bool = True,
    subset_ratio: float = 1.0,
    random_seed: int = 42,
    balance_sampling: bool = False
) -> DataLoader:
    """
    获取Car专用数据加载器 - 三分类模式
    
    类别映射:
    - 0: Background
    - 1: Car (主要目标)
    - 2: Others (Truck + Bus)
    
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
        balance_sampling: 是否使用类别平衡采样
    """
    images_dir = os.path.join(data_dir, 'images')
    
    if split == 'train':
        transform = get_training_augmentation(img_size)
        shuffle = True
    else:
        transform = get_validation_augmentation(img_size)
        shuffle = False
    
    dataset = CarFocusedDataset(
        images_dir=images_dir,
        masks_dir=masks_dir,
        split=split,
        transform=transform,
        img_size=img_size,
        subset_ratio=subset_ratio,
        random_seed=random_seed
    )
    
    # 使用加权随机采样器进行类别平衡
    if balance_sampling and split == 'train':
        print("使用类别平衡采样 (Car专用模式)...")
        sampler = create_car_focused_sampler(dataset, masks_dir, split)
        shuffle = False
    else:
        sampler = None
    
    dataloader = DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle if sampler is None else False,
        sampler=sampler,
        num_workers=num_workers,
        pin_memory=pin_memory if torch.cuda.is_available() else False,  # MPS/CPU不支持pin_memory
        persistent_workers=num_workers > 0 if num_workers > 0 else False,  # macOS MPS兼容性
        drop_last=split == 'train'
    )
    
    return dataloader


def create_car_focused_sampler(dataset, masks_dir: str, split: str):
    """
    创建Car专用模式的类别平衡采样器
    
    为包含Others(Truck+Bus)的图像分配更高权重，确保模型也学习到Others类别
    """
    from torch.utils.data import WeightedRandomSampler
    import cv2
    from pathlib import Path
    
    print("计算样本权重 (三分类模式)...")
    
    mask_path = Path(masks_dir) / split
    weights = []
    
    # 统计各类别图像数量
    has_car_count = 0
    has_others_count = 0
    only_bg_count = 0
    
    for img_file in tqdm(dataset.image_files, desc="分析样本"):
        mask_file = mask_path / (img_file.stem + '.png')
        
        if not mask_file.exists():
            weights.append(1.0)
            only_bg_count += 1
            continue
        
        mask = cv2.imread(str(mask_file), cv2.IMREAD_GRAYSCALE)
        
        # 检查原始掩码中的类别（简化前）
        has_car = (mask == 1).sum() > 100
        has_truck = (mask == 2).sum() > 50
        has_bus = (mask == 3).sum() > 50
        has_others = has_truck or has_bus
        
        # 统计
        if has_others:
            has_others_count += 1
        elif has_car:
            has_car_count += 1
        else:
            only_bg_count += 1
        
        # 权重策略：Car专用模式
        weight = 1.0
        if has_car:
            weight += 2.0  # Car样本基础权重
        if has_others:
            weight += 5.0  # Others样本高权重，确保学习
        
        weights.append(weight)
    
    weights = torch.tensor(weights, dtype=torch.float)
    
    print(f"\n样本统计:")
    print(f"  - 包含Car的图像: {has_car_count}")
    print(f"  - 包含Others的图像: {has_others_count}")
    print(f"  - 仅背景的图像: {only_bg_count}")
    print(f"\n样本权重统计:")
    print(f"  - 最小权重: {weights.min():.2f}")
    print(f"  - 最大权重: {weights.max():.2f}")
    print(f"  - 平均权重: {weights.mean():.2f}")
    
    # 创建WeightedRandomSampler
    sampler = WeightedRandomSampler(
        weights=weights,
        num_samples=len(dataset),
        replacement=True
    )
    
    return sampler


def create_balanced_sampler(dataset, masks_dir: str, split: str):
    """
    创建类别平衡采样器
    
    为包含稀有类别（Vehicle和Pedestrian）的图像分配更高的权重
    """
    from torch.utils.data import WeightedRandomSampler
    import cv2
    from pathlib import Path
    
    print("计算样本权重...")
    
    mask_path = Path(masks_dir) / split
    weights = []
    
    for img_file in tqdm(dataset.image_files, desc="分析样本"):
        mask_file = mask_path / (img_file.stem + '.png')
        
        if not mask_file.exists():
            weights.append(1.0)
            continue
        
        mask = cv2.imread(str(mask_file), cv2.IMREAD_GRAYSCALE)
        
        # 计算权重：包含Vehicle或Pedestrian的图像权重更高
        has_vehicle = (mask == 2).sum() > 0
        has_pedestrian = (mask == 3).sum() > 0
        has_road = (mask == 1).sum() > 0
        
        # 权重策略
        weight = 1.0
        if has_vehicle:
            weight += 5.0  # Vehicle最重要
        if has_pedestrian:
            weight += 3.0  # Pedestrian次之
        if has_road:
            weight += 1.0  # Road也有一定权重
        
        weights.append(weight)
    
    weights = torch.tensor(weights, dtype=torch.float)
    
    print(f"样本权重统计:")
    print(f"  - 最小权重: {weights.min():.2f}")
    print(f"  - 最大权重: {weights.max():.2f}")
    print(f"  - 平均权重: {weights.mean():.2f}")
    
    # 创建WeightedRandomSampler
    sampler = WeightedRandomSampler(
        weights=weights,
        num_samples=len(dataset),
        replacement=True
    )
    
    return sampler


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
