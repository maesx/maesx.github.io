"""
增强版推理和可视化脚本 - 支持自定义颜色和多种可视化模式
"""
import argparse
import logging
import os
import random
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import cv2
import numpy as np
import torch
from torch import Tensor

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.models.unet_plusplus import UNetPlusPlus
from src.utils.exceptions import DataLoadError, InferenceError, ModelLoadError
from src.utils.logging_config import get_inference_logger


class EnhancedVehicleSegmenter:
    """增强版车辆分割推理器 - 支持多种颜色方案"""

    # 颜色方案类型定义
    ColorScheme = List[List[int]]

    def __init__(
        self,
        model_path: str,
        device: str = 'cpu',
        color_scheme: str = 'standard'
    ) -> None:
        """
        初始化推理器

        Args:
            model_path: 模型权重路径
            device: 运行设备
            color_scheme: 颜色方案
                - 'standard': 标准颜色 (红绿蓝)
                - 'bright': 鲜艳颜色
                - 'pastel': 柔和颜色
                - 'dark': 深色
                - 'contrast': 高对比度
                - 'traffic': 交通标志颜色

        Raises:
            ModelLoadError: 模型加载失败
        """
        self.logger: logging.Logger = get_inference_logger()
        self.logger.info("初始化增强版推理器...")

        self.device: torch.device = torch.device(device)

        # 加载模型
        if not os.path.exists(model_path):
            raise ModelLoadError("模型文件不存在", model_path)

        try:
            self.logger.info(f"加载模型: {model_path}")
            checkpoint = torch.load(model_path, map_location=self.device, weights_only=False)
            args = checkpoint.get('args', None)

            # 处理无 args 的旧版 checkpoint
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

            # 类别名称
            self.class_names: List[str] = ['Background', 'Car', 'Truck', 'Bus']
            self.class_names_cn: List[str] = ['背景', '轿车', '卡车', '公交车']

            # 颜色方案 (BGR格式)
            self.color_schemes: Dict[str, self.ColorScheme] = {
                # 标准颜色方案
                'standard': [
                    [0, 0, 0],        # 背景 - 黑色
                    [0, 0, 255],      # car - 红色
                    [0, 255, 0],      # truck - 绿色
                    [255, 0, 0]       # bus - 蓝色
                ],
                # 鲜艳颜色方案 - 更易区分
                'bright': [
                    [0, 0, 0],        # 背景 - 黑色
                    [0, 255, 255],    # car - 黄色
                    [255, 0, 255],    # truck - 紫红色
                    [255, 255, 0]     # bus - 青色
                ],
                # 柔和颜色方案
                'pastel': [
                    [30, 30, 30],     # 背景 - 深灰
                    [200, 150, 255],  # car - 淡紫色
                    [150, 255, 200],  # truck - 淡绿色
                    [255, 200, 150]   # bus - 淡橙色
                ],
                # 深色方案
                'dark': [
                    [0, 0, 0],        # 背景 - 黑色
                    [0, 0, 180],      # car - 深红
                    [0, 180, 0],      # truck - 深绿
                    [180, 0, 0]       # bus - 深蓝
                ],
                # 高对比度方案 - 适合演示
                'contrast': [
                    [50, 50, 50],     # 背景 - 深灰
                    [61, 255, 255],   # car - 亮黄
                    [255, 144, 30],   # truck - 橙色
                    [180, 105, 255]   # bus - 粉色
                ],
                # 交通标志颜色
                'traffic': [
                    [0, 0, 0],        # 背景 - 黑色
                    [0, 204, 255],    # car - 橙色 (警告色)
                    [210, 105, 30],   # truck - 巧克力色
                    [255, 255, 0]     # bus - 蓝色 (信息色)
                ]
            }

            # 选择颜色方案
            self.colors: self.ColorScheme = self.color_schemes.get(color_scheme, self.color_schemes['standard'])
            self.color_scheme_name: str = color_scheme

            self.logger.info(f"模型加载完成: {model_path}")
            self.logger.info(f"设备: {self.device}")
            self.logger.info(f"图像尺寸: {self.img_size}")
            self.logger.info(f"颜色方案: {color_scheme}")

            print(f"模型加载完成: {model_path}")
            print(f"设备: {self.device}")
            print(f"图像尺寸: {self.img_size}")
            print(f"颜色方案: {color_scheme}")
            print(f"\n类别颜色映射:")
            for i, (name, name_cn, color) in enumerate(zip(self.class_names, self.class_names_cn, self.colors)):
                print(f"  {i}. {name:12s} ({name_cn:6s}): RGB({color[2]}, {color[1]}, {color[0]})")

        except Exception as e:
            self.logger.error(f"模型加载失败: {e}")
            raise ModelLoadError("模型加载失败", str(e))

    def preprocess(self, image: np.ndarray) -> Tensor:
        """图像预处理"""
        # 转换颜色空间
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # 调整大小
        image = cv2.resize(image, tuple(self.img_size))

        # 标准化
        image = image.astype(np.float32) / 255.0
        mean = np.array([0.485, 0.456, 0.406])
        std = np.array([0.229, 0.224, 0.225])
        image = (image - mean) / std

        # 转换为张量 [H, W, C] -> [C, H, W]
        image = torch.from_numpy(image).permute(2, 0, 1).float()

        return image

    def predict(self, image: np.ndarray) -> np.ndarray:
        """
        预测分割结果

        Args:
            image: OpenCV图像

        Returns:
            pred_mask: 预测的分割掩码

        Raises:
            InferenceError: 推理过程失败
        """
        try:
            # 原始尺寸
            original_size: Tuple[int, int] = (image.shape[1], image.shape[0])

            # 预处理
            input_tensor = self.preprocess(image)
            input_tensor = input_tensor.unsqueeze(0).to(self.device)

            # 推理
            with torch.no_grad():
                output = self.model(input_tensor)

            # 获取预测结果
            if isinstance(output, list):
                output = output[-1]

            pred_mask = torch.argmax(output, dim=1)
            pred_mask = pred_mask.squeeze(0).cpu().numpy()

            # 调整回原始尺寸
            pred_mask = cv2.resize(pred_mask.astype(np.uint8), original_size,
                                    interpolation=cv2.INTER_NEAREST)

            return pred_mask

        except Exception as e:
            self.logger.error(f"推理失败: {e}")
            raise InferenceError("推理失败", str(e))

    def create_colored_mask(
        self,
        pred_mask: np.ndarray,
        image_size: Optional[Tuple[int, int]] = None
    ) -> np.ndarray:
        """
        创建彩色掩码

        Args:
            pred_mask: 预测掩码
            image_size: 输出图像尺寸 (height, width)

        Returns:
            color_mask: 彩色掩码
        """
        if image_size is None:
            color_mask = np.zeros((pred_mask.shape[0], pred_mask.shape[1], 3), dtype=np.uint8)
        else:
            color_mask = np.zeros((image_size[0], image_size[1], 3), dtype=np.uint8)

        for class_id, color in enumerate(self.colors):
            mask = pred_mask == class_id
            color_mask[mask] = color

        return color_mask

    def visualize(
        self,
        image: np.ndarray,
        pred_mask: np.ndarray,
        save_path: Optional[str] = None,
        alpha: float = 0.5,
        show_original: bool = True,
        show_overlay: bool = True,
        show_mask: bool = True,
        show_legend: bool = True,
        show_stats: bool = True
    ) -> Tuple[np.ndarray, Dict[str, Tuple[int, float]]]:
        """
        增强版可视化

        Args:
            image: 原始图像
            pred_mask: 预测掩码
            save_path: 保存路径
            alpha: 叠加透明度
            show_original: 是否显示原图
            show_overlay: 是否显示叠加图
            show_mask: 是否显示纯掩码
            show_legend: 是否显示图例
            show_stats: 是否显示统计信息

        Returns:
            result: 可视化结果图像
            stats: 各类别统计信息
        """
        # 创建彩色掩码
        color_mask = self.create_colored_mask(pred_mask)

        # 叠加到原图
        overlay = cv2.addWeighted(image, 1-alpha, color_mask, alpha, 0)

        # 统计各类别像素数
        unique, counts = np.unique(pred_mask, return_counts=True)
        total_pixels = pred_mask.size
        stats: Dict[str, Tuple[int, float]] = {
            self.class_names[u]: (c, c/total_pixels*100)
            for u, c in zip(unique, counts)
        }

        # 创建结果图像
        images_to_show: List[np.ndarray] = []
        titles: List[str] = []

        if show_original:
            images_to_show.append(image)
            titles.append('Original')

        if show_overlay:
            images_to_show.append(overlay)
            titles.append('Overlay')

        if show_mask:
            images_to_show.append(color_mask)
            titles.append('Segmentation')

        # 横向拼接
        result = np.hstack(images_to_show)

        # 添加图例
        if show_legend:
            legend_height = 40 + len(self.class_names) * 35
            legend_width = 250
            legend = np.ones((legend_height, legend_width, 3), dtype=np.uint8) * 240

            # 标题
            cv2.putText(legend, 'Class Legend', (10, 25),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

            # 各类别
            for i, (name, name_cn, color) in enumerate(zip(self.class_names,
                                                            self.class_names_cn,
                                                            self.colors)):
                y = 55 + i * 30
                # 颜色方块
                cv2.rectangle(legend, (10, y-12), (35, y+8), color, -1)
                cv2.rectangle(legend, (10, y-12), (35, y+8), (0, 0, 0), 1)
                # 类别名称
                cv2.putText(legend, f"{name}", (45, y+5),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 0), 1)

            # 添加统计信息
            if show_stats:
                stats_y = legend_height + 20
                stats_legend = np.ones((100, legend_width, 3), dtype=np.uint8) * 240
                cv2.putText(stats_legend, 'Statistics:', (10, 20),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

                y_offset = 40
                for class_name, (count, percentage) in stats.items():
                    if class_name != 'Background':
                        text = f"{class_name}: {percentage:.1f}%"
                        cv2.putText(stats_legend, text, (10, y_offset),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
                        y_offset += 20

                # 合并图例和统计
                legend = np.vstack([legend, stats_legend])

            # 将图例添加到结果右侧
            h, w = result.shape[:2]
            legend_resized = cv2.resize(legend, (legend_width, h))
            result = np.hstack([result, legend_resized])

        # 保存结果
        if save_path:
            cv2.imwrite(save_path, result)
            self.logger.info(f"结果已保存: {save_path}")

        return result, stats

    def batch_predict(
        self,
        images_dir: str,
        output_dir: str,
        **viz_kwargs: Any
    ) -> None:
        """
        批量预测

        Args:
            images_dir: 图像目录
            output_dir: 输出目录
            **viz_kwargs: 可视化参数

        Raises:
            DataLoadError: 图像目录不存在或读取失败
            InferenceError: 推理过程失败
        """
        images_path = Path(images_dir)
        if not images_path.exists():
            raise DataLoadError("图像目录不存在", images_dir)

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        image_files = list(images_path.glob('*.jpg')) + list(images_path.glob('*.png'))

        if not image_files:
            raise DataLoadError("图像目录中没有图像文件", images_dir)

        self.logger.info(f"开始批量预测: {len(image_files)} 张图像")
        print(f"开始批量预测: {len(image_files)} 张图像")

        for img_file in image_files:
            image = cv2.imread(str(img_file))
            if image is None:
                self.logger.warning(f"无法读取图像: {img_file}")
                continue

            pred_mask = self.predict(image)
            save_path = output_path / f"{img_file.stem}_result.jpg"
            self.visualize(image, pred_mask, str(save_path), **viz_kwargs)

        self.logger.info(f"批量预测完成,结果保存在: {output_path}")
        print(f"批量预测完成,结果保存在: {output_path}")


def main() -> None:
    """主函数"""
    parser = argparse.ArgumentParser(description='增强版道路车辆分割推理')

    parser.add_argument('--model_path', type=str, default='outputs/checkpoints/best_model.pth',
                        help='模型权重路径')
    parser.add_argument('--image_path', type=str, default=None,
                        help='单张图像路径')
    parser.add_argument('--images_dir', type=str, default=None,
                        help='图像目录(批量预测)')
    parser.add_argument('--output_dir', type=str, default='outputs/visualizations',
                        help='输出目录')
    parser.add_argument('--device', type=str, default='cpu',
                        choices=['cpu', 'cuda', 'mps'],
                        help='运行设备')
    parser.add_argument('--split', type=str, default='val',
                        choices=['train', 'val', 'test'],
                        help='要预测的数据集划分')
    parser.add_argument('--num_samples', type=int, default=20,
                        help='可视化样本数量')

    # 新增参数
    parser.add_argument('--color_scheme', type=str, default='standard',
                        choices=['standard', 'bright', 'pastel', 'dark', 'contrast', 'traffic'],
                        help='颜色方案')
    parser.add_argument('--alpha', type=float, default=0.5,
                        help='叠加透明度 (0.0-1.0)')

    args = parser.parse_args()

    # 自动检测设备
    if args.device == 'mps' or (args.device == 'cpu' and torch.backends.mps.is_available()):
        device = 'mps'
    elif args.device == 'cuda' or (args.device == 'cpu' and torch.cuda.is_available()):
        device = 'cuda'
    else:
        device = 'cpu'

    # 创建推理器
    segmenter = EnhancedVehicleSegmenter(args.model_path, device, args.color_scheme)

    if args.image_path:
        # 单张图像预测
        if not os.path.exists(args.image_path):
            raise DataLoadError("图像文件不存在", args.image_path)

        image = cv2.imread(args.image_path)
        if image is None:
            raise DataLoadError("无法读取图像文件", args.image_path)

        pred_mask = segmenter.predict(image)

        output_path = Path(args.output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        save_path = output_path / f"{Path(args.image_path).stem}_result.jpg"

        segmenter.visualize(image, pred_mask, str(save_path), alpha=args.alpha)
        print(f"结果已保存: {save_path}")

    elif args.images_dir:
        # 批量预测
        segmenter.batch_predict(args.images_dir, args.output_dir, alpha=args.alpha)

    else:
        # 默认预测验证集
        data_dir = f'road_vehicle_pedestrian_det_datasets/images/{args.split}'
        if os.path.exists(data_dir):
            print(f"\n开始对 {args.split} 数据集进行推理...")

            image_files = list(Path(data_dir).glob('*.jpg')) + list(Path(data_dir).glob('*.png'))

            random.seed(42)
            if len(image_files) > args.num_samples:
                sample_files = random.sample(image_files, args.num_samples)
            else:
                sample_files = image_files

            print(f"将可视化 {len(sample_files)} 个样本\n")

            output_path = Path(args.output_dir) / args.split
            output_path.mkdir(parents=True, exist_ok=True)

            for i, img_file in enumerate(sample_files, 1):
                print(f"处理 [{i}/{len(sample_files)}]: {img_file.name}")

                image = cv2.imread(str(img_file))
                if image is None:
                    print(f"  警告: 无法读取图像 {img_file.name}")
                    continue

                pred_mask = segmenter.predict(image)
                save_path = output_path / f"{img_file.stem}_result.jpg"
                result, stats = segmenter.visualize(image, pred_mask, str(save_path),
                                                    alpha=args.alpha)

            print(f"\n✓ 所有结果已保存到: {output_path}")
        else:
            print(f"数据集目录不存在: {data_dir}")


if __name__ == '__main__':
    main()