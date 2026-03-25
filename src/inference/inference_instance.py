"""
实例分割可视化脚本 - 同类型车辆也能用不同颜色区分
功能：对每个独立的车辆实例进行编号和着色
"""
import argparse
import logging
import os
import random
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import cv2
import numpy as np
import torch
from scipy import ndimage
from torch import Tensor

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.models.unet_plusplus import UNetPlusPlus
from src.utils.exceptions import DataLoadError, InferenceError, ModelLoadError
from src.utils.logging_config import get_inference_logger


class InstanceSegmenter:
    """实例分割推理器 - 区分每个独立车辆实例"""

    def __init__(self, model_path: str, device: str = 'cpu') -> None:
        """
        初始化

        Args:
            model_path: 模型权重路径
            device: 运行设备

        Raises:
            ModelLoadError: 模型加载失败
        """
        self.logger: logging.Logger = get_inference_logger()
        self.logger.info("初始化实例分割推理器...")

        self.device: torch.device = torch.device(device)

        # 加载模型
        if not os.path.exists(model_path):
            raise ModelLoadError("模型文件不存在", model_path)

        try:
            self.logger.info(f"加载模型: {model_path}")
            checkpoint = torch.load(model_path, map_location=self.device, weights_only=False)
            args = checkpoint.get('args', None)

            # 如果没有args，使用默认配置
            if args is None:
                num_classes = 4
                encoder_name = 'vgg19'
                deep_supervision = True
                img_size = [512, 512]
            else:
                num_classes = args.num_classes
                encoder_name = args.encoder
                deep_supervision = args.deep_supervision
                img_size = args.img_size

            self.model: UNetPlusPlus = UNetPlusPlus(
                in_channels=3,
                num_classes=num_classes,
                deep_supervision=deep_supervision,
                encoder_name=encoder_name,
                pretrained=False
            )

            self.model.load_state_dict(checkpoint['model_state_dict'])
            self.model = self.model.to(self.device)
            self.model.eval()

            self.img_size: List[int] = img_size
            self.class_names: List[str] = ['Background', 'Car', 'Truck', 'Bus']
            self.class_names_cn: List[str] = ['背景', '轿车', '卡车', '公交车']

            self.logger.info(f"模型加载完成: {model_path}")
            self.logger.info(f"设备: {self.device}")
            self.logger.info(f"图像尺寸: {self.img_size}")

            print(f"模型加载完成: {model_path}")
            print(f"设备: {self.device}")
            print(f"图像尺寸: {self.img_size}")

        except Exception as e:
            self.logger.error(f"模型加载失败: {e}")
            raise ModelLoadError("模型加载失败", str(e))

    def preprocess(self, image: np.ndarray) -> Tensor:
        """图像预处理"""
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = cv2.resize(image, tuple(self.img_size))
        image = image.astype(np.float32) / 255.0
        mean = np.array([0.485, 0.456, 0.406])
        std = np.array([0.229, 0.224, 0.225])
        image = (image - mean) / std
        image = torch.from_numpy(image).permute(2, 0, 1).float()
        return image

    def predict_semantic(self, image: np.ndarray) -> np.ndarray:
        """
        语义分割预测

        Args:
            image: OpenCV图像

        Returns:
            pred_mask: 语义分割掩码

        Raises:
            InferenceError: 推理过程失败
        """
        try:
            original_size: Tuple[int, int] = (image.shape[1], image.shape[0])
            input_tensor = self.preprocess(image)
            input_tensor = input_tensor.unsqueeze(0).to(self.device)

            with torch.no_grad():
                output = self.model(input_tensor)

            if isinstance(output, list):
                output = output[-1]

            pred_mask = torch.argmax(output, dim=1)
            pred_mask = pred_mask.squeeze(0).cpu().numpy()
            pred_mask = cv2.resize(pred_mask.astype(np.uint8), original_size,
                                    interpolation=cv2.INTER_NEAREST)

            return pred_mask

        except Exception as e:
            self.logger.error(f"语义分割推理失败: {e}")
            raise InferenceError("语义分割推理失败", str(e))

    def separate_instances(
        self,
        semantic_mask: np.ndarray
    ) -> Tuple[np.ndarray, Dict[int, Tuple[int, int]]]:
        """
        将语义分割结果转换为实例分割

        Args:
            semantic_mask: 语义分割掩码 (H, W), 值为类别ID

        Returns:
            instance_mask: 实例分割掩码 (H, W), 值为实例ID
            instance_info: 字典 {实例ID: (类别ID, 面积)}
        """
        instance_mask = np.zeros_like(semantic_mask, dtype=np.int32)
        instance_info: Dict[int, Tuple[int, int]] = {}

        current_instance_id = 1

        # 对每个类别分别处理
        for class_id in range(1, 4):  # 1=Car, 2=Truck, 3=Bus
            # 提取当前类别的区域
            class_mask = (semantic_mask == class_id).astype(np.uint8)

            if class_mask.sum() == 0:
                continue

            # 使用连通区域分析分离实例
            labeled_array, num_features = ndimage.label(class_mask)

            # 对每个实例
            for instance_idx in range(1, num_features + 1):
                # 获取实例掩码
                instance_region = (labeled_array == instance_idx)
                area = instance_region.sum()

                # 过滤太小的区域（噪声）
                if area < 100:  # 最小面积阈值
                    continue

                # 分配实例ID
                instance_mask[instance_region] = current_instance_id
                instance_info[current_instance_id] = (class_id, int(area))
                current_instance_id += 1

        return instance_mask, instance_info

    def generate_instance_colors(
        self,
        num_instances: int,
        color_mode: str = 'random'
    ) -> Dict[int, List[int]]:
        """
        为每个实例生成颜色

        Args:
            num_instances: 实例数量
            color_mode: 颜色生成模式
                - 'random': 随机颜色
                - 'class_based': 基于类别但不同色调
                - 'distinct': 高对比度区分色

        Returns:
            colors: 实例颜色字典 {实例ID: [B, G, R]}
        """
        colors: Dict[int, List[int]] = {}

        if color_mode == 'random':
            # 纯随机颜色
            for i in range(1, num_instances + 1):
                colors[i] = [random.randint(50, 255) for _ in range(3)]

        elif color_mode == 'distinct':
            # 使用预设的高对比度色板
            distinct_colors: List[List[int]] = [
                [255, 0, 0],      # 红
                [0, 255, 0],      # 绿
                [0, 0, 255],      # 蓝
                [255, 255, 0],    # 黄
                [255, 0, 255],    # 紫
                [0, 255, 255],    # 青
                [255, 128, 0],    # 橙
                [128, 0, 255],    # 紫罗兰
                [0, 255, 128],    # 青绿
                [255, 0, 128],    # 玫红
                [128, 255, 0],    # 黄绿
                [0, 128, 255],    # 天蓝
                [255, 64, 64],    # 浅红
                [64, 255, 64],    # 浅绿
                [64, 64, 255],    # 浅蓝
                [255, 192, 0],    # 金黄
                [192, 0, 255],    # 紫色
                [0, 192, 255],    # 浅蓝
                [255, 0, 192],    # 粉红
                [0, 255, 192],    # 青色
            ]

            for i in range(1, num_instances + 1):
                colors[i] = distinct_colors[(i - 1) % len(distinct_colors)]

        elif color_mode == 'class_based':
            # 基于类别但每个实例色调略有不同
            pass  # 需要instance_info, 稍后实现

        return colors

    def visualize_instances(
        self,
        image: np.ndarray,
        semantic_mask: np.ndarray,
        instance_mask: np.ndarray,
        instance_info: Dict[int, Tuple[int, int]],
        save_path: Optional[str] = None,
        alpha: float = 0.5,
        show_labels: bool = True
    ) -> Tuple[np.ndarray, Dict[int, Tuple[int, int]]]:
        """
        可视化实例分割结果

        Args:
            image: 原始图像
            semantic_mask: 语义分割掩码
            instance_mask: 实例分割掩码
            instance_info: 实例信息字典
            save_path: 保存路径
            alpha: 叠加透明度
            show_labels: 是否显示实例标签

        Returns:
            result: 可视化结果图像
            instance_info: 实例信息字典
        """
        # 生成实例颜色
        num_instances = len(instance_info)
        instance_colors = self.generate_instance_colors(num_instances, color_mode='distinct')

        # 创建彩色掩码
        color_mask = np.zeros_like(image)
        for instance_id in instance_info.keys():
            mask = instance_mask == instance_id
            color_mask[mask] = instance_colors[instance_id]

        # 叠加
        overlay = cv2.addWeighted(image, 1-alpha, color_mask, alpha, 0)

        # 在每个实例上标注
        if show_labels and len(instance_info) > 0:
            for instance_id, (class_id, area) in instance_info.items():
                # 找到实例的中心位置
                mask = (instance_mask == instance_id).astype(np.uint8)
                moments = cv2.moments(mask)

                if moments['m00'] > 0:
                    cx = int(moments['m10'] / moments['m00'])
                    cy = int(moments['m01'] / moments['m00'])

                    # 绘制标签
                    class_name = self.class_names_cn[class_id]
                    label = f"#{instance_id} {class_name}"

                    # 绘制背景框
                    (text_width, text_height), baseline = cv2.getTextSize(
                        label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)

                    # 选择文字颜色（与背景对比）
                    color = instance_colors[instance_id]
                    brightness = sum(color) / 3
                    text_color = (0, 0, 0) if brightness > 127 else (255, 255, 255)

                    # 绘制矩形背景
                    cv2.rectangle(overlay,
                                (cx - text_width//2 - 5, cy - text_height//2 - 5),
                                (cx + text_width//2 + 5, cy + text_height//2 + 5),
                                color, -1)
                    cv2.rectangle(overlay,
                                (cx - text_width//2 - 5, cy - text_height//2 - 5),
                                (cx + text_width//2 + 5, cy + text_height//2 + 5),
                                (0, 0, 0), 1)

                    # 绘制文字
                    cv2.putText(overlay, label,
                              (cx - text_width//2, cy + text_height//4),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 1)

        # 创建语义分割掩码（用于对比）
        semantic_colors: List[List[int]] = [
            [0, 0, 0],        # Background
            [0, 0, 255],      # Car - 红
            [0, 255, 0],      # Truck - 绿
            [255, 0, 0]       # Bus - 蓝
        ]

        semantic_color_mask = np.zeros_like(image)
        for class_id, color in enumerate(semantic_colors):
            mask = semantic_mask == class_id
            semantic_color_mask[mask] = color

        # 创建图例
        legend_width = 350
        legend_height = 100 + len(instance_info) * 25
        legend = np.ones((legend_height, legend_width, 3), dtype=np.uint8) * 240

        # 标题
        cv2.putText(legend, 'Instance Segmentation Results', (10, 25),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

        # 统计信息
        cv2.putText(legend, f'Total Instances: {len(instance_info)}', (10, 55),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

        # 各类别实例数
        class_counts: Dict[int, int] = {}
        for class_id, _ in instance_info.values():
            class_counts[class_id] = class_counts.get(class_id, 0) + 1

        y_offset = 80
        for class_id, count in class_counts.items():
            text = f"{self.class_names_cn[class_id]}: {count} instances"
            cv2.putText(legend, text, (10, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 0), 1)
            y_offset += 20

        # 实例列表
        y_offset += 10
        cv2.putText(legend, 'Instance Details:', (10, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
        y_offset += 25

        for instance_id, (class_id, area) in sorted(instance_info.items()):
            color = instance_colors[instance_id]
            # 色块
            cv2.rectangle(legend, (10, y_offset-10), (30, y_offset+5), color, -1)
            # 实例信息
            text = f"#{instance_id} {self.class_names_cn[class_id]} ({area} px)"
            cv2.putText(legend, text, (40, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
            y_offset += 25

        # 合并结果
        # 左到右: 原图 | 实例分割 | 语义分割对比 | 图例
        result = np.hstack([image, overlay, semantic_color_mask])

        # 添加图例
        legend_resized = cv2.resize(legend, (legend_width, result.shape[0]))
        result = np.hstack([result, legend_resized])

        if save_path:
            cv2.imwrite(save_path, result)
            self.logger.info(f"结果已保存: {save_path}")

        return result, instance_info

    def process_image(
        self,
        image_path: str,
        output_dir: str,
        alpha: float = 0.5
    ) -> Dict[int, Tuple[int, int]]:
        """
        处理单张图像

        Args:
            image_path: 图像路径
            output_dir: 输出目录
            alpha: 叠加透明度

        Returns:
            instance_info: 实例信息字典

        Raises:
            DataLoadError: 图像加载失败
            InferenceError: 推理过程失败
        """
        if not os.path.exists(image_path):
            raise DataLoadError("图像文件不存在", image_path)

        image = cv2.imread(str(image_path))
        if image is None:
            raise DataLoadError("无法读取图像文件", image_path)

        # 语义分割
        semantic_mask = self.predict_semantic(image)

        # 实例分离
        instance_mask, instance_info = self.separate_instances(semantic_mask)

        # 可视化
        save_path = Path(output_dir) / f"{Path(image_path).stem}_instance.jpg"
        result, info = self.visualize_instances(image, semantic_mask, instance_mask,
                                                 instance_info, str(save_path), alpha)

        return info


def main() -> None:
    """主函数"""
    parser = argparse.ArgumentParser(description='实例分割推理 - 区分每个车辆实例')

    parser.add_argument('--model_path', type=str, default='outputs/checkpoints/best_model.pth',
                        help='模型权重路径')
    parser.add_argument('--split', type=str, default='val',
                        choices=['train', 'val', 'test'],
                        help='数据集划分')
    parser.add_argument('--num_samples', type=int, default=20,
                        help='处理样本数量')
    parser.add_argument('--device', type=str, default='mps',
                        choices=['cpu', 'cuda', 'mps'],
                        help='运行设备')
    parser.add_argument('--output_dir', type=str, default='outputs/visualizations/instance',
                        help='输出目录')
    parser.add_argument('--alpha', type=float, default=0.6,
                        help='叠加透明度 (0.0-1.0)')

    args = parser.parse_args()

    # 自动检测设备
    if args.device == 'mps' or (args.device == 'cpu' and torch.backends.mps.is_available()):
        device = 'mps'
    elif args.device == 'cuda' or (args.device == 'cpu' and torch.cuda.is_available()):
        device = 'cuda'
    else:
        device = 'cpu'

    # 创建实例分割器
    segmenter = InstanceSegmenter(args.model_path, device)

    # 处理数据集
    data_dir = f'road_vehicle_pedestrian_det_datasets/images/{args.split}'

    if os.path.exists(data_dir):
        print(f"\n开始对 {args.split} 数据集进行实例分割...")

        image_files = list(Path(data_dir).glob('*.jpg')) + list(Path(data_dir).glob('*.png'))

        # 随机选择样本
        random.seed(42)
        if len(image_files) > args.num_samples:
            sample_files = random.sample(image_files, args.num_samples)
        else:
            sample_files = image_files

        print(f"将处理 {len(sample_files)} 个样本\n")

        output_path = Path(args.output_dir) / args.split
        output_path.mkdir(parents=True, exist_ok=True)

        total_instances = 0

        for i, img_file in enumerate(sample_files, 1):
            print(f"处理 [{i}/{len(sample_files)}]: {img_file.name}")

            try:
                instance_info = segmenter.process_image(str(img_file), str(output_path), args.alpha)
                total_instances += len(instance_info)

                # 显示检测到的实例
                if instance_info:
                    print(f"  检测到 {len(instance_info)} 个车辆实例:")
                    for inst_id, (class_id, area) in instance_info.items():
                        print(f"    #{inst_id}: {segmenter.class_names_cn[class_id]} ({area} 像素)")
            except (DataLoadError, InferenceError) as e:
                print(f"  警告: 处理失败 - {e}")
                continue

        print(f"\n{'='*70}")
        print(f"✓ 所有结果已保存到: {output_path}")
        print(f"✓ 共处理 {len(sample_files)} 张图像，检测到 {total_instances} 个车辆实例")
        if len(sample_files) > 0:
            print(f"✓ 平均每张图像 {total_instances/len(sample_files):.1f} 个实例")
        print(f"{'='*70}")
    else:
        print(f"数据集目录不存在: {data_dir}")


if __name__ == '__main__':
    main()