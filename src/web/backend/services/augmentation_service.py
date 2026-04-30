"""
数据增强服务
提供图像增强功能,用于Web界面
"""
import random
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import albumentations as A
from io import BytesIO
import base64


class AugmentationService:
    """数据增强服务类"""
    
    def __init__(self):
        """初始化增强服务"""
        self.augmentation_methods = {
            'horizontal_flip': '水平翻转',
            'vertical_flip': '垂直翻转',
            'rotation': '随机旋转',
            'brightness': '亮度调整',
            'contrast': '对比度调整',
            'gaussian_blur': '高斯模糊',
            'gaussian_noise': '高斯噪声',
            'hue_saturation': '色调饱和度',
            'random_crop': '随机裁剪',
            'elastic_transform': '弹性形变',
            'grid_distortion': '网格畸变',
        }
    
    def augment_image(self, image: np.ndarray, methods: list, num_variations: int = 3) -> list:
        """
        对图像应用增强效果
        
        Args:
            image: numpy数组格式的图像 (H, W, C)
            methods: 增强方法列表
            num_variations: 生成变体数量
            
        Returns:
            增强后的图片列表 [{'image': base64_str, 'augmentation_type': str}, ...]
        """
        results = []
        
        for _ in range(num_variations):
            # 随机选择增强方法
            selected_methods = random.sample(methods, min(len(methods), random.randint(2, 4)))
            
            # 应用增强
            augmented = self._apply_augmentations(image, selected_methods)
            
            # 转换为base64
            base64_str = self._numpy_to_base64(augmented)
            
            # 生成增强类型描述
            method_names = [self.augmentation_methods.get(m, m) for m in selected_methods]
            augmentation_type = ' + '.join(method_names)
            
            results.append({
                'image': base64_str,
                'augmentation_type': augmentation_type,
                'methods': selected_methods
            })
        
        return results
    
    def _apply_augmentations(self, image: np.ndarray, methods: list) -> np.ndarray:
        """
        应用增强方法
        
        Args:
            image: numpy数组格式的图像
            methods: 增强方法列表
            
        Returns:
            增强后的图像
        """
        augmented = image.copy()
        
        # 转换为PIL Image用于某些增强
        pil_image = Image.fromarray(augmented)
        
        for method in methods:
            try:
                if method == 'horizontal_flip':
                    # 水平翻转
                    if random.random() > 0.5:
                        augmented = np.fliplr(augmented).copy()
                
                elif method == 'vertical_flip':
                    # 垂直翻转
                    if random.random() > 0.5:
                        augmented = np.flipud(augmented).copy()
                
                elif method == 'rotation':
                    # 随机旋转
                    angle = random.uniform(-30, 30)
                    pil_image = Image.fromarray(augmented)
                    pil_image = pil_image.rotate(angle, resample=Image.BILINEAR, expand=False)
                    augmented = np.array(pil_image)
                
                elif method == 'brightness':
                    # 亮度调整
                    factor = random.uniform(0.7, 1.3)
                    pil_image = Image.fromarray(augmented)
                    enhancer = ImageEnhance.Brightness(pil_image)
                    pil_image = enhancer.enhance(factor)
                    augmented = np.array(pil_image)
                
                elif method == 'contrast':
                    # 对比度调整
                    factor = random.uniform(0.7, 1.3)
                    pil_image = Image.fromarray(augmented)
                    enhancer = ImageEnhance.Contrast(pil_image)
                    pil_image = enhancer.enhance(factor)
                    augmented = np.array(pil_image)
                
                elif method == 'gaussian_blur':
                    # 高斯模糊
                    pil_image = Image.fromarray(augmented)
                    pil_image = pil_image.filter(ImageFilter.GaussianBlur(radius=random.uniform(0.5, 2.0)))
                    augmented = np.array(pil_image)
                
                elif method == 'gaussian_noise':
                    # 高斯噪声
                    noise = np.random.normal(0, random.uniform(10, 30), augmented.shape)
                    augmented = np.clip(augmented + noise, 0, 255).astype(np.uint8)
                
                elif method == 'hue_saturation':
                    # 色调饱和度调整
                    pil_image = Image.fromarray(augmented)
                    # 色调
                    hue_factor = random.uniform(-15, 15)
                    # 饱和度
                    sat_factor = random.uniform(0.8, 1.2)
                    
                    enhancer = ImageEnhance.Color(pil_image)
                    pil_image = enhancer.enhance(sat_factor)
                    augmented = np.array(pil_image)
                
                elif method == 'random_crop':
                    # 随机裁剪(resize back to original size)
                    h, w = augmented.shape[:2]
                    crop_h, crop_w = int(h * random.uniform(0.8, 0.95)), int(w * random.uniform(0.8, 0.95))
                    top = random.randint(0, h - crop_h)
                    left = random.randint(0, w - crop_w)
                    cropped = augmented[top:top+crop_h, left:left+crop_w]
                    pil_image = Image.fromarray(cropped)
                    pil_image = pil_image.resize((w, h), Image.BILINEAR)
                    augmented = np.array(pil_image)
                
                elif method == 'elastic_transform':
                    # 弹性形变(简化版)
                    try:
                        transform = A.ElasticTransform(p=1.0, alpha=120, sigma=120 * 0.05, alpha_affine=120 * 0.03)
                        augmented = transform(image=augmented)['image']
                    except:
                        pass  # 如果失败则跳过
                
                elif method == 'grid_distortion':
                    # 网格畸变
                    try:
                        transform = A.GridDistortion(num_steps=5, distort_limit=0.3, p=1.0)
                        augmented = transform(image=augmented)['image']
                    except:
                        pass  # 如果失败则跳过
                        
            except Exception as e:
                print(f"[Augmentation] 方法 {method} 失败: {e}")
                continue
        
        return augmented
    
    def _numpy_to_base64(self, image: np.ndarray) -> str:
        """
        将numpy数组转换为base64字符串
        
        Args:
            image: numpy数组格式的图像
            
        Returns:
            base64编码的字符串(data URL格式)
        """
        pil_image = Image.fromarray(image.astype('uint8'))
        buffer = BytesIO()
        pil_image.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        return f"data:image/png;base64,{img_str}"
    
    def get_available_methods(self) -> dict:
        """
        获取所有可用的增强方法
        
        Returns:
            增强方法字典 {method_key: method_name}
        """
        return self.augmentation_methods


# 全局单例
_augmentation_service = None


def get_augmentation_service() -> AugmentationService:
    """
    获取数据增强服务单例
    
    Returns:
        AugmentationService实例
    """
    global _augmentation_service
    if _augmentation_service is None:
        _augmentation_service = AugmentationService()
    return _augmentation_service
