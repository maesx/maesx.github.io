"""
推理和可视化脚本
支持CPU和GPU推理
"""
import argparse
import logging
import os
import random
import sys
from pathlib import Path
from typing import List, Optional, Tuple

import cv2
import numpy as np
import torch
from torch import Tensor

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.models.unet_plusplus import UNetPlusPlus
from src.utils.exceptions import DataLoadError, InferenceError, ModelLoadError
from src.utils.logging_config import get_inference_logger


class VehicleSegmenter:
    """车辆分割推理器"""

    def __init__(self, model_path: str, device: str = 'cpu') -> None:
        """
        初始化推理器

        Args:
            model_path: 模型权重路径
            device: 运行设备

        Raises:
            ModelLoadError: 模型加载失败
        """
        self.logger: logging.Logger = get_inference_logger()
        self.logger.info("初始化推理器...")

        self.device: torch.device = torch.device(device)

        # 加载模型
        if not os.path.exists(model_path):
            raise ModelLoadError("模型文件不存在", model_path)

        try:
            self.logger.info(f"加载模型: {model_path}")
            checkpoint = torch.load(model_path, map_location=self.device, weights_only=True)
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

            # 类别颜色映射(背景、car、truck、bus)
            self.colors: List[List[int]] = [
                [0, 0, 0],        # 背景 - 黑色
                [255, 0, 0],      # car - 红色
                [0, 255, 0],      # truck - 绿色
                [0, 0, 255]       # bus - 蓝色
            ]

            self.class_names: List[str] = ['background', 'car', 'truck', 'bus']

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
        """
        图像预处理

        Args:
            image: OpenCV图像 (BGR格式)

        Returns:
            tensor: 预处理后的张量
        """
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
                # 使用最后一个输出
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

    def visualize(
        self,
        image: np.ndarray,
        pred_mask: np.ndarray,
        save_path: Optional[str] = None,
        alpha: float = 0.5,
        show: bool = False
    ) -> np.ndarray:
        """
        可视化分割结果

        Args:
            image: 原始图像
            pred_mask: 预测掩码
            save_path: 保存路径
            alpha: 叠加透明度
            show: 是否显示图像

        Returns:
            result: 可视化结果图像
        """
        # 创建彩色掩码
        color_mask = np.zeros_like(image)
        for class_id, color in enumerate(self.colors):
            mask = pred_mask == class_id
            color_mask[mask] = color

        # 叠加到原图
        overlay = cv2.addWeighted(image, 1-alpha, color_mask, alpha, 0)

        # 创建图例
        legend = np.ones((150, 200, 3), dtype=np.uint8) * 255
        for i, (name, color) in enumerate(zip(self.class_names, self.colors)):
            y = 30 + i * 30
            cv2.rectangle(legend, (10, y-10), (30, y+10), color, -1)
            cv2.putText(legend, name, (40, y+5), cv2.FONT_HERSHEY_SIMPLEX,
                       0.5, (0, 0, 0), 1)

        # 合并图像
        result = np.hstack([image, overlay, color_mask])

        # 添加图例
        legend_start = result.shape[1] - 220
        result[10:160, legend_start:legend_start+200] = legend

        if save_path:
            cv2.imwrite(save_path, result)
            self.logger.info(f"结果已保存: {save_path}")
            print(f"  结果已保存: {save_path}")

        if show:
            # 显示
            import matplotlib.pyplot as plt
            plt.figure(figsize=(15, 5))
            plt.imshow(cv2.cvtColor(result, cv2.COLOR_BGR2RGB))
            plt.axis('off')
            plt.title('道路车辆分割结果')
            plt.show()

        return result

    def batch_predict(self, images_dir: str, output_dir: str) -> None:
        """
        批量预测

        Args:
            images_dir: 图像目录
            output_dir: 输出目录

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
            # 读取图像
            image = cv2.imread(str(img_file))
            if image is None:
                self.logger.warning(f"无法读取图像: {img_file}")
                continue

            # 预测
            pred_mask = self.predict(image)

            # 保存结果
            save_path = output_path / f"{img_file.stem}_result.jpg"
            self.visualize(image, pred_mask, str(save_path))

        self.logger.info(f"批量预测完成,结果保存在: {output_path}")
        print(f"批量预测完成,结果保存在: {output_path}")


def main() -> None:
    """主函数"""
    parser = argparse.ArgumentParser(description='道路车辆分割推理')

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
                        help='要预测的数据集划分 (默认: val)')
    parser.add_argument('--num_samples', type=int, default=10,
                        help='可视化样本数量 (默认: 10)')

    args = parser.parse_args()

    # 自动检测设备
    if args.device == 'mps' or (args.device == 'cpu' and torch.backends.mps.is_available()):
        device = 'mps'
    elif args.device == 'cuda' or (args.device == 'cpu' and torch.cuda.is_available()):
        device = 'cuda'
    else:
        device = 'cpu'

    # 创建推理器
    segmenter = VehicleSegmenter(args.model_path, device)

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

        segmenter.visualize(image, pred_mask, str(save_path))

    elif args.images_dir:
        # 批量预测
        segmenter.batch_predict(args.images_dir, args.output_dir)

    else:
        # 默认预测验证集或测试集
        data_dir = f'road_vehicle_pedestrian_det_datasets/images/{args.split}'
        if os.path.exists(data_dir):
            print(f"\n开始对 {args.split} 数据集进行推理...")

            # 读取数据集
            image_files = list(Path(data_dir).glob('*.jpg')) + list(Path(data_dir).glob('*.png'))

            # 随机选择样本进行可视化
            random.seed(42)
            if len(image_files) > args.num_samples:
                sample_files = random.sample(image_files, args.num_samples)
            else:
                sample_files = image_files

            print(f"将可视化 {len(sample_files)} 个样本")

            # 创建输出目录
            output_path = Path(args.output_dir) / args.split
            output_path.mkdir(parents=True, exist_ok=True)

            # 批量预测和可视化
            for i, img_file in enumerate(sample_files, 1):
                print(f"\n处理 [{i}/{len(sample_files)}]: {img_file.name}")

                # 读取图像
                image = cv2.imread(str(img_file))
                if image is None:
                    print(f"  警告: 无法读取图像 {img_file.name}")
                    continue

                # 预测
                pred_mask = segmenter.predict(image)

                # 保存结果
                save_path = output_path / f"{img_file.stem}_result.jpg"
                segmenter.visualize(image, pred_mask, str(save_path))

            print(f"\n✓ 所有结果已保存到: {output_path}")
        else:
            print(f"数据集目录不存在: {data_dir}")
            print("请指定图像路径或图像目录")


if __name__ == '__main__':
    main()