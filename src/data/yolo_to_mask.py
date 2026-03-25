"""
YOLO标注转换为语义分割掩码
将YOLO格式的边界框标注转换为像素级的语义分割掩码
"""
import argparse
import logging
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import cv2
import numpy as np
from tqdm import tqdm

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.utils.exceptions import ConfigError, DataLoadError


def get_logger() -> logging.Logger:
    """获取日志记录器"""
    logger = logging.getLogger('yolo_to_mask')
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


class YOLOToMaskConverter:
    """YOLO标注转换器"""

    def __init__(
        self,
        classes_file: str,
        target_classes: Optional[List[str]] = None
    ) -> None:
        """
        初始化转换器

        Args:
            classes_file: 类别文件路径
            target_classes: 目标分割类别列表

        Raises:
            ConfigError: 类别文件不存在或格式错误
        """
        self.logger = get_logger()
        self.logger.info("初始化YOLO到掩码转换器...")

        if target_classes is None:
            target_classes = ['car', 'truck', 'bus']

        if not os.path.exists(classes_file):
            raise ConfigError("类别文件不存在", classes_file)

        try:
            with open(classes_file, 'r', encoding='utf-8') as f:
                all_classes = [line.strip() for line in f.readlines() if line.strip()]
        except Exception as e:
            raise ConfigError("读取类别文件失败", str(e))

        self.all_classes: List[str] = all_classes
        self.target_classes: List[str] = target_classes

        # 创建类别映射(只包含目标类别)
        self.class_to_label: Dict[str, int] = {}
        self.label_to_class: Dict[int, str] = {}

        # 背景为0
        self.class_to_label['background'] = 0
        self.label_to_class[0] = 'background'

        # 目标类别从1开始编号
        for idx, cls in enumerate(target_classes, start=1):
            if cls in all_classes:
                self.class_to_label[cls] = idx
                self.label_to_class[idx] = cls

        self.logger.info(f"类别映射: {self.class_to_label}")
        print(f"类别映射: {self.class_to_label}")

    def convert_yolo_to_mask(
        self,
        label_path: str,
        img_shape: Tuple[int, int, int]
    ) -> np.ndarray:
        """
        将单个YOLO标注文件转换为分割掩码

        Args:
            label_path: YOLO标注文件路径
            img_shape: 图像形状 (height, width, channels)

        Returns:
            mask: 分割掩码 (H, W)
        """
        height, width = img_shape[:2]
        mask = np.zeros((height, width), dtype=np.uint8)

        if not os.path.exists(label_path):
            return mask

        try:
            with open(label_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception as e:
            self.logger.warning(f"无法读取标注文件 {label_path}: {e}")
            return mask

        for line in lines:
            parts = line.strip().split()
            if len(parts) != 5:
                continue

            try:
                class_id = int(parts[0])
                x_center = float(parts[1]) * width
                y_center = float(parts[2]) * height
                bbox_width = float(parts[3]) * width
                bbox_height = float(parts[4]) * height
            except ValueError:
                continue

            # 获取类别名称
            if class_id >= len(self.all_classes):
                continue

            class_name = self.all_classes[class_id]

            # 只处理目标类别
            if class_name not in self.target_classes:
                continue

            label = self.class_to_label[class_name]

            # 计算边界框坐标
            x1 = int(max(0, x_center - bbox_width / 2))
            y1 = int(max(0, y_center - bbox_height / 2))
            x2 = int(min(width, x_center + bbox_width / 2))
            y2 = int(min(height, y_center + bbox_height / 2))

            # 在掩码中填充边界框区域(同一类别可能有重叠,保留后标注的)
            mask[y1:y2, x1:x2] = label

        return mask

    def convert_dataset(
        self,
        images_dir: str,
        labels_dir: str,
        output_dir: str,
        split: str = 'train'
    ) -> int:
        """
        转换整个数据集

        Args:
            images_dir: 图像目录
            labels_dir: 标签目录
            output_dir: 输出目录
            split: 数据集划分(train/val/test)

        Returns:
            converted_count: 成功转换的图像数量

        Raises:
            DataLoadError: 数据目录不存在
        """
        images_path = Path(images_dir) / split
        labels_path = Path(labels_dir) / split
        output_path = Path(output_dir) / split

        if not images_path.exists():
            raise DataLoadError("图像目录不存在", str(images_path))

        output_path.mkdir(parents=True, exist_ok=True)

        image_files = list(images_path.glob('*.jpg')) + list(images_path.glob('*.png'))

        self.logger.info(f"正在转换 {split} 数据集,共 {len(image_files)} 张图像...")
        print(f"正在转换 {split} 数据集,共 {len(image_files)} 张图像...")

        converted_count = 0

        for img_file in tqdm(image_files, desc=f"Converting {split}"):
            # 读取图像
            img = cv2.imread(str(img_file))
            if img is None:
                self.logger.warning(f"无法读取图像: {img_file}")
                continue

            # 对应的标注文件
            label_file = labels_path / (img_file.stem + '.txt')

            # 转换为掩码
            mask = self.convert_yolo_to_mask(str(label_file), img.shape)

            # 保存掩码
            mask_file = output_path / (img_file.stem + '.png')
            cv2.imwrite(str(mask_file), mask)
            converted_count += 1

        self.logger.info(f"{split} 数据集转换完成,掩码保存在: {output_path}")
        print(f"{split} 数据集转换完成,掩码保存在: {output_path}")

        return converted_count


def main() -> None:
    """主函数"""
    parser = argparse.ArgumentParser(description='YOLO标注转换为语义分割掩码')
    parser.add_argument('--data_dir', type=str, default='road_vehicle_pedestrian_det_datasets',
                        help='数据集根目录')
    parser.add_argument('--output_dir', type=str, default='outputs/masks',
                        help='掩码输出目录')
    parser.add_argument('--classes', nargs='+', default=['car', 'truck', 'bus'],
                        help='要分割的类别')

    args = parser.parse_args()

    # 创建转换器
    converter = YOLOToMaskConverter(
        classes_file=os.path.join(args.data_dir, 'classes.txt'),
        target_classes=args.classes
    )

    # 转换所有数据集
    total_converted = 0
    for split in ['train', 'val', 'test']:
        try:
            count = converter.convert_dataset(
                images_dir=os.path.join(args.data_dir, 'images'),
                labels_dir=os.path.join(args.data_dir, 'labels'),
                output_dir=args.output_dir,
                split=split
            )
            total_converted += count
        except DataLoadError as e:
            print(f"跳过 {split} 数据集: {e}")
            continue

    print(f"\n所有数据集转换完成! 共转换 {total_converted} 张图像")


if __name__ == '__main__':
    main()