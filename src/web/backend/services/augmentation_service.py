"""
图像增强服务
支持基础增强和高级增强方式
"""
import random
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
from typing import List, Dict, Tuple, Any
import io
import base64


class AugmentationService:
    """图像增强服务"""
    
    def __init__(self):
        self.augmentation_methods = {
            # 基础增强
            'rotate': self._rotate,
            'flip': self._flip,
            'scale': self._scale,
            'crop': self._crop,
            # 高级增强
            'color': self._color_adjust,
            'noise': self._add_noise,
            'blur': self._blur,
            'brightness': self._brightness_contrast
        }
    
    def augment_image(
        self, 
        image: np.ndarray, 
        methods: List[str], 
        num_variations: int = 3
    ) -> List[Dict[str, Any]]:
        """
        对图像应用随机增强，生成多个变体
        
        Args:
            image: 输入图像 (numpy数组，RGB格式)
            methods: 要应用的增强方法列表
            num_variations: 生成变体数量（默认3个）
            
        Returns:
            增强后的图像列表，每个元素包含图像和增强类型
        """
        # 英文到中文的映射
        method_chinese_names = {
            'rotate': '旋转',
            'flip': '翻转',
            'scale': '缩放',
            'crop': '裁剪',
            'color': '颜色调整',
            'noise': '噪声',
            'blur': '模糊',
            'brightness': '亮度对比度'
        }
        
        variations = []
        
        for i in range(num_variations):
            # 随机选择增强方法组合
            num_methods = random.randint(1, min(3, len(methods)))
            selected_methods = random.sample(methods, num_methods)
            
            # 应用增强
            augmented = image.copy()
            applied_methods_info = []
            
            for method_name in selected_methods:
                if method_name in self.augmentation_methods:
                    augmented, param_info = self.augmentation_methods[method_name](augmented)
                    # 添加中文名称和参数信息
                    chinese_name = method_chinese_names.get(method_name, method_name)
                    if param_info:
                        applied_methods_info.append(f"{chinese_name}({param_info})")
                    else:
                        applied_methods_info.append(chinese_name)
            
            # 转换为base64
            if isinstance(augmented, np.ndarray):
                augmented_pil = Image.fromarray(augmented.astype('uint8'))
            else:
                augmented_pil = augmented
            
            buffered = io.BytesIO()
            augmented_pil.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            variations.append({
                'image': f"data:image/png;base64,{img_str}",
                'augmentation_type': ' + '.join(applied_methods_info)
            })
        
        return variations
    
    # ========== 基础增强方法 ==========
    
    def _rotate(self, image: np.ndarray) -> Tuple[np.ndarray, str]:
        """随机旋转"""
        angle = random.uniform(-30, 30)
        pil_img = Image.fromarray(image)
        rotated = pil_img.rotate(angle, expand=True, fillcolor=(128, 128, 128))
        return np.array(rotated), f"{angle:.1f}°"
    
    def _flip(self, image: np.ndarray) -> Tuple[np.ndarray, str]:
        """随机翻转"""
        flip_type = random.choice(['horizontal', 'vertical'])
        pil_img = Image.fromarray(image)
        
        if flip_type == 'horizontal':
            flipped = ImageOps.mirror(pil_img)
            return np.array(flipped), "水平"
        else:
            flipped = ImageOps.flip(pil_img)
            return np.array(flipped), "垂直"
    
    def _scale(self, image: np.ndarray) -> Tuple[np.ndarray, str]:
        """随机缩放"""
        scale_factor = random.uniform(0.7, 1.3)
        pil_img = Image.fromarray(image)
        
        new_width = int(pil_img.width * scale_factor)
        new_height = int(pil_img.height * scale_factor)
        
        scaled = pil_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # 裁剪或填充到原始大小
        orig_width, orig_height = pil_img.size
        result = Image.new('RGB', (orig_width, orig_height), (128, 128, 128))
        
        # 计算粘贴位置（居中）
        paste_x = (orig_width - new_width) // 2
        paste_y = (orig_height - new_height) // 2
        
        if scale_factor >= 1:
            # 缩放后更大，需要裁剪中心
            crop_x = (new_width - orig_width) // 2
            crop_y = (new_height - orig_height) // 2
            result = scaled.crop((crop_x, crop_y, crop_x + orig_width, crop_y + orig_height))
        else:
            # 缩放后更小，需要填充
            result.paste(scaled, (paste_x, paste_y))
        
        return np.array(result), f"{scale_factor:.2f}x"
    
    def _crop(self, image: np.ndarray) -> Tuple[np.ndarray, str]:
        """随机裁剪"""
        pil_img = Image.fromarray(image)
        width, height = pil_img.size
        
        # 随机裁剪比例
        crop_ratio = random.uniform(0.6, 0.9)
        new_width = int(width * crop_ratio)
        new_height = int(height * crop_ratio)
        
        # 随机裁剪位置
        left = random.randint(0, width - new_width)
        top = random.randint(0, height - new_height)
        right = left + new_width
        bottom = top + new_height
        
        cropped = pil_img.crop((left, top, right, bottom))
        
        # 调整回原始大小
        resized = cropped.resize((width, height), Image.Resampling.LANCZOS)
        
        return np.array(resized), f"{crop_ratio:.0%}"
    
    # ========== 高级增强方法 ==========
    
    def _color_adjust(self, image: np.ndarray) -> Tuple[np.ndarray, str]:
        """颜色调整"""
        pil_img = Image.fromarray(image)
        
        # 随机调整色调、饱和度
        enhancer = ImageEnhance.Color(pil_img)
        factor = random.uniform(0.5, 1.5)
        adjusted = enhancer.enhance(factor)
        
        return np.array(adjusted), f"饱和度{factor:.2f}"
    
    def _add_noise(self, image: np.ndarray) -> Tuple[np.ndarray, str]:
        """添加噪声"""
        noise_type = random.choice(['gaussian', 'salt_pepper'])
        
        if noise_type == 'gaussian':
            # 高斯噪声
            mean = 0
            sigma = random.uniform(10, 30)
            noise = np.random.normal(mean, sigma, image.shape)
            noisy = np.clip(image + noise, 0, 255).astype(np.uint8)
            return noisy, f"高斯σ={sigma:.1f}"
        else:
            # 椒盐噪声
            prob = random.uniform(0.01, 0.05)
            noisy = image.copy()
            
            # 盐噪声（白点）
            salt_mask = np.random.random(image.shape[:2]) < prob / 2
            noisy[salt_mask] = 255
            
            # 椒噪声（黑点）
            pepper_mask = np.random.random(image.shape[:2]) < prob / 2
            noisy[pepper_mask] = 0
            
            return noisy, f"椒盐{prob:.1%}"
    
    def _blur(self, image: np.ndarray) -> Tuple[np.ndarray, str]:
        """模糊效果（高斯模糊）"""
        pil_img = Image.fromarray(image)
        
        # 高斯模糊
        radius = random.uniform(1, 3)
        blurred = pil_img.filter(ImageFilter.GaussianBlur(radius=radius))
        
        return np.array(blurred), f"半径{radius:.1f}"
    
    def _brightness_contrast(self, image: np.ndarray) -> Tuple[np.ndarray, str]:
        """亮度和对比度调整"""
        pil_img = Image.fromarray(image)
        
        # 随机调整亮度
        brightness_enhancer = ImageEnhance.Brightness(pil_img)
        brightness_factor = random.uniform(0.6, 1.4)
        brightened = brightness_enhancer.enhance(brightness_factor)
        
        # 随机调整对比度
        contrast_enhancer = ImageEnhance.Contrast(brightened)
        contrast_factor = random.uniform(0.6, 1.4)
        adjusted = contrast_enhancer.enhance(contrast_factor)
        
        return np.array(adjusted), f"亮度{brightness_factor:.1f} 对比度{contrast_factor:.1f}"


# 单例模式
_augmentation_service = None


def get_augmentation_service() -> AugmentationService:
    """获取增强服务实例"""
    global _augmentation_service
    if _augmentation_service is None:
        _augmentation_service = AugmentationService()
    return _augmentation_service
