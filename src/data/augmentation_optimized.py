"""
优化数据增强策略
减少过度增强,保留核心增强操作,提高训练稳定性
"""
import albumentations as A
from albumentations.pytorch import ToTensorV2
from typing import Tuple


def get_optimized_training_augmentation(img_size: Tuple[int, int] = (512, 512)) -> A.Compose:
    """
    优化的训练集数据增强
    
    改进点:
    1. 减少增强操作数量: 17种 -> 10种
    2. 降低增强强度: 避免过度失真
    3. 移除不稳定的增强: ElasticTransform, GridDistortion等
    4. 保持关键增强: 翻转、旋转、颜色调整
    
    Args:
        img_size: 图像尺寸
        
    Returns:
        数据增强管道
    """
    train_transform = A.Compose([
        # 1. 几何变换 (核心增强)
        A.Resize(img_size[0], img_size[1]),
        A.HorizontalFlip(p=0.5),           # 水平翻转
        A.VerticalFlip(p=0.2),              # 垂直翻转 (降低概率)
        A.RandomRotate90(p=0.3),            # 随机旋转90度
        A.ShiftScaleRotate(
            shift_limit=0.1,                # 平移限制10%
            scale_limit=0.1,                # 缩放限制10%
            rotate_limit=15,                # 旋转限制15度
            border_mode=0,                  # 边界填充
            p=0.5
        ),
        
        # 2. 颜色变换 (适度增强)
        A.RandomBrightnessContrast(
            brightness_limit=0.2,           # 亮度调整范围 ±20%
            contrast_limit=0.2,             # 对比度调整范围 ±20%
            p=0.4
        ),
        A.HueSaturationValue(
            hue_shift_limit=10,             # 色调调整 ±10
            sat_shift_limit=20,             # 饱和度调整 ±20
            val_shift_limit=10,             # 明度调整 ±10
            p=0.3
        ),
        
        # 3. 轻微噪声 (降低概率)
        A.GaussNoise(
            var_limit=(10.0, 30.0),         # 噪声方差范围
            p=0.2
        ),
        A.GaussianBlur(
            blur_limit=3,                   # 模糊核大小限制
            p=0.2
        ),
        
        # 4. 标准化和转换
        A.Normalize(
            mean=(0.485, 0.456, 0.406),    # ImageNet均值
            std=(0.229, 0.224, 0.225)      # ImageNet标准差
        ),
        ToTensorV2(),
    ])
    
    print("\n[数据增强] 优化配置:")
    print("  ✓ 保留核心几何变换 (翻转、旋转、缩放)")
    print("  ✓ 保留适度颜色增强 (亮度、对比度、色调)")
    print("  ✓ 保留轻微噪声增强 (高斯噪声、模糊)")
    print("  ✗ 移除过度形变增强 (弹性形变、网格畸变)")
    print("  ✗ 移除人造效果 (阴影、光斑、通道混洗)")
    print(f"  总计: {len([t for t in train_transform.transforms if hasattr(t, 'p')])} 种增强操作")
    
    return train_transform


def get_conservative_training_augmentation(img_size: Tuple[int, int] = (512, 512)) -> A.Compose:
    """
    保守的训练集数据增强 (更少增强,更稳定)
    
    适用于:
    - 训练初期验证收敛性
    - 验证数据增强是否影响训练
    - 小数据集训练
    
    Args:
        img_size: 图像尺寸
        
    Returns:
        数据增强管道
    """
    train_transform = A.Compose([
        A.Resize(img_size[0], img_size[1]),
        
        # 仅保留最基本的几何变换
        A.HorizontalFlip(p=0.5),
        A.RandomRotate90(p=0.3),
        
        # 仅保留最轻微的颜色调整
        A.RandomBrightnessContrast(
            brightness_limit=0.1,
            contrast_limit=0.1,
            p=0.3
        ),
        
        # 标准化
        A.Normalize(
            mean=(0.485, 0.456, 0.406),
            std=(0.229, 0.224, 0.225)
        ),
        ToTensorV2(),
    ])
    
    print("\n[数据增强] 保守配置:")
    print("  ✓ 仅保留基本几何变换")
    print("  ✓ 仅保留轻微颜色调整")
    print("  ✗ 移除所有复杂增强")
    print(f"  总计: {len([t for t in train_transform.transforms if hasattr(t, 'p')])} 种增强操作")
    
    return train_transform


def get_aggressive_training_augmentation(img_size: Tuple[int, int] = (512, 512)) -> A.Compose:
    """
    激进的训练集数据增强 (更多增强,更强正则化)
    
    适用于:
    - 训练后期提升泛化能力
    - 大数据集训练
    - 模型过拟合时
    
    Args:
        img_size: 图像尺寸
        
    Returns:
        数据增强管道
    """
    train_transform = A.Compose([
        # 1. 几何变换 (增强版)
        A.SmallestMaxSize(max_size=int(img_size[0] * 1.2)),
        A.RandomCrop(height=img_size[0], width=img_size[1]),
        A.HorizontalFlip(p=0.5),
        A.VerticalFlip(p=0.3),
        A.RandomRotate90(p=0.5),
        A.ShiftScaleRotate(
            shift_limit=0.15,
            scale_limit=0.15,
            rotate_limit=30,
            border_mode=0,
            p=0.6
        ),
        
        # 2. 颜色变换 (增强版)
        A.RandomBrightnessContrast(
            brightness_limit=0.3,
            contrast_limit=0.3,
            p=0.5
        ),
        A.HueSaturationValue(
            hue_shift_limit=15,
            sat_shift_limit=25,
            val_shift_limit=15,
            p=0.4
        ),
        A.RGBShift(
            r_shift_limit=15,
            g_shift_limit=15,
            b_shift_limit=15,
            p=0.3
        ),
        
        # 3. 噪声和模糊
        A.GaussNoise(var_limit=(15.0, 40.0), p=0.3),
        A.GaussianBlur(blur_limit=5, p=0.3),
        A.MotionBlur(blur_limit=5, p=0.2),
        
        # 4. 天气效果 (新增)
        A.RandomRain(
            slant_lower=-10,
            slant_upper=10,
            drop_length=20,
            drop_width=1,
            drop_color=(200, 200, 200),
            blur_value=5,
            brightness_coefficient=0.7,
            p=0.1
        ),
        A.RandomFog(
            fog_coef_lower=0.1,
            fog_coef_upper=0.3,
            alpha_coef=0.1,
            p=0.1
        ),
        
        # 5. 标准化
        A.Normalize(
            mean=(0.485, 0.456, 0.406),
            std=(0.229, 0.224, 0.225)
        ),
        ToTensorV2(),
    ])
    
    print("\n[数据增强] 激进配置:")
    print("  ✓ 增强几何变换强度")
    print("  ✓ 增加颜色变换种类")
    print("  ✓ 添加天气效果 (雨、雾)")
    print("  ✓ 增强噪声和模糊")
    print(f"  总计: {len([t for t in train_transform.transforms if hasattr(t, 'p')])} 种增强操作")
    
    return train_transform


# 使用指南
"""
在 src/data/dataset.py 中使用优化后的数据增强:

# 原代码:
def get_training_augmentation(img_size: Tuple[int, int] = (512, 512)) -> A.Compose:
    train_transform = A.Compose([
        # ... 17种增强操作 ...
    ])
    return train_transform

# 修改为:
from src.data.augmentation_optimized import get_optimized_training_augmentation

def get_training_augmentation(img_size: Tuple[int, int] = (512, 512)) -> A.Compose:
    # 使用优化后的数据增强
    return get_optimized_training_augmentation(img_size)
    
# 或者根据训练阶段选择增强强度:
def get_training_augmentation(img_size: Tuple[int, int] = (512, 512), mode='optimized') -> A.Compose:
    if mode == 'conservative':
        from src.data.augmentation_optimized import get_conservative_training_augmentation
        return get_conservative_training_augmentation(img_size)
    elif mode == 'aggressive':
        from src.data.augmentation_optimized import get_aggressive_training_augmentation
        return get_aggressive_training_augmentation(img_size)
    else:  # optimized
        from src.data.augmentation_optimized import get_optimized_training_augmentation
        return get_optimized_training_augmentation(img_size)
"""
