"""
训练脚本
支持CPU和GPU训练

python3 src/training/train.py --use_gpu True --subset_ratio 1.0 --epochs 30 --batch_size 8 --save_interval 5 --early_stopping_patience 10 --num_workers 0 --resume outputs/checkpoints/best_model.pth
"""
import argparse
import logging
import math
import os
import sys
from datetime import datetime
from typing import Tuple

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torch.utils.tensorboard import SummaryWriter
from tqdm import tqdm

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.data.dataset import get_dataloader
from src.models.unet_plusplus import UNetPlusPlus
from src.utils.exceptions import ConfigError, DataLoadError, ModelLoadError
from src.utils.losses import CombinedLoss, DeepSupervisionLoss, calculate_iou, calculate_pixel_accuracy
from src.utils.logging_config import get_training_logger


class Trainer:
    """训练器"""

    def __init__(self, args: argparse.Namespace) -> None:
        """
        初始化训练器

        Args:
            args: 命令行参数

        Raises:
            ConfigError: 配置参数无效
            DataLoadError: 数据加载失败
            ModelLoadError: 模型加载失败
        """
        self.args = args
        self.logger = get_training_logger(args.output_dir + '/logs')
        self.logger.info("初始化训练器...")

        # 验证配置参数
        self._validate_config()

        # 设置设备
        self.device: torch.device = self._setup_device()

        # 创建数据加载器
        self.logger.info("加载数据集...")
        print("\n加载数据集...")
        try:
            self.train_loader: DataLoader = get_dataloader(
                data_dir=args.data_dir,
                masks_dir=args.masks_dir,
                split='train',
                batch_size=args.batch_size,
                img_size=tuple(args.img_size),
                num_workers=args.num_workers,
                subset_ratio=args.subset_ratio,
                random_seed=args.random_seed
            )

            self.val_loader: DataLoader = get_dataloader(
                data_dir=args.data_dir,
                masks_dir=args.masks_dir,
                split='val',
                batch_size=args.batch_size,
                img_size=tuple(args.img_size),
                num_workers=args.num_workers,
                subset_ratio=args.subset_ratio,
                random_seed=args.random_seed
            )
        except Exception as e:
            self.logger.error(f"数据加载失败: {e}")
            raise DataLoadError("数据加载失败", str(e))

        # 创建模型
        self.logger.info("创建模型...")
        print("\n创建模型...")
        self.model: UNetPlusPlus = UNetPlusPlus(
            in_channels=3,
            num_classes=args.num_classes,
            deep_supervision=args.deep_supervision,
            encoder_name=args.encoder,
            pretrained=args.pretrained
        )
        self.model = self.model.to(self.device)

        # 创建损失函数，添加类别权重
        # 类别权重：根据数据集分布计算
        # Background: 98.35%, Road: 84.85%, Vehicle: 8.33%, Pedestrian: 37.64%
        # 权重计算: 1 / sqrt(frequency)，并对车辆类别额外加权
        class_weights = torch.tensor([0.0165, 0.1515, 12.0, 2.6596], dtype=torch.float32)
        self.logger.info(f"类别权重: Background={class_weights[0]:.4f}, Road={class_weights[1]:.4f}, Vehicle={class_weights[2]:.4f}, Pedestrian={class_weights[3]:.4f}")
        
        base_loss = CombinedLoss(weight_ce=1.0, weight_dice=1.0, class_weights=class_weights)
        if args.deep_supervision:
            self.criterion: nn.Module = DeepSupervisionLoss(base_loss)
        else:
            self.criterion = base_loss

        # 创建优化器
        self.optimizer: optim.Adam = optim.Adam(
            self.model.parameters(),
            lr=args.lr,
            weight_decay=args.weight_decay
        )

        # 学习率调度器
        self.scheduler: optim.lr_scheduler.ReduceLROnPlateau = optim.lr_scheduler.ReduceLROnPlateau(
            self.optimizer,
            mode='max',
            factor=0.5,
            patience=5
        )

        # 创建TensorBoard日志
        log_dir = os.path.join(args.output_dir, 'logs', datetime.now().strftime('%Y%m%d_%H%M%S'))
        self.writer: SummaryWriter = SummaryWriter(log_dir)

        # 最佳IoU
        self.best_iou: float = 0.0
        self.start_epoch: int = 1

        # 加载预训练模型
        if args.resume:
            self._load_checkpoint(args.resume)

        # 学习率预热设置
        self.warmup_epochs: int = args.warmup_epochs
        self.base_lr: float = args.lr
        
        # Early Stopping设置
        self.patience: int = args.early_stopping_patience
        self.patience_counter: int = 0
        
        # 智能学习率调整设置
        self.min_lr: float = args.min_lr  # 最小学习率
        self.prev_val_iou: float = 0.0  # 前一个epoch的验证IoU
        self.lr_adjustment_counter: int = 0  # 学习率调整计数器
        self.lr_adjustment_factor: float = args.lr_adjustment_factor  # 学习率调整因子

        self._print_config()

    def _validate_config(self) -> None:
        """验证配置参数

        Raises:
            ConfigError: 配置参数无效
        """
        if self.args.batch_size <= 0:
            raise ConfigError("批次大小必须大于0")
        if self.args.epochs <= 0:
            raise ConfigError("训练轮数必须大于0")
        if self.args.lr <= 0:
            raise ConfigError("学习率必须大于0")
        if not os.path.exists(self.args.data_dir):
            raise ConfigError("数据目录不存在", self.args.data_dir)

    def _setup_device(self) -> torch.device:
        """设置训练设备

        Returns:
            训练设备
        """
        if self.args.use_gpu:
            if torch.backends.mps.is_available():
                device = torch.device('mps')
                print("使用MPS (M4芯片GPU) 训练")
                self.logger.info("使用MPS (M4芯片GPU) 训练")
            elif torch.cuda.is_available():
                device = torch.device('cuda')
                print(f"使用CUDA GPU训练: {torch.cuda.get_device_name(0)}")
                self.logger.info(f"使用CUDA GPU训练: {torch.cuda.get_device_name(0)}")
            else:
                device = torch.device('cpu')
                print("GPU不可用，使用CPU训练")
                self.logger.warning("GPU不可用，使用CPU训练")
        else:
            device = torch.device('cpu')
            print("使用CPU训练")
            self.logger.info("使用CPU训练")
        return device

    def _load_checkpoint(self, checkpoint_path: str) -> None:
        """加载检查点

        Args:
            checkpoint_path: 检查点路径

        Raises:
            ModelLoadError: 模型加载失败
        """
        if not os.path.exists(checkpoint_path):
            raise ModelLoadError("模型文件不存在", checkpoint_path)

        try:
            print(f"\n加载预训练模型: {checkpoint_path}")
            self.logger.info(f"加载预训练模型: {checkpoint_path}")
            checkpoint = torch.load(checkpoint_path, map_location=self.device, weights_only=False)
            self.model.load_state_dict(checkpoint['model_state_dict'])
            if 'optimizer_state_dict' in checkpoint:
                self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
            if 'best_iou' in checkpoint:
                self.best_iou = checkpoint['best_iou']
            if 'epoch' in checkpoint:
                self.start_epoch = checkpoint['epoch'] + 1
            print(f"  - 模型IoU: {self.best_iou:.4f}")
            print(f"  - 起始轮数: {self.start_epoch}")
            self.logger.info(f"模型加载成功 - IoU: {self.best_iou:.4f}, 起始轮数: {self.start_epoch}")
        except Exception as e:
            self.logger.error(f"模型加载失败: {e}")
            raise ModelLoadError("模型加载失败", str(e))

    def _print_config(self) -> None:
        """打印训练配置"""
        print(f"\n训练配置:")
        print(f"  - 批次大小: {self.args.batch_size}")
        print(f"  - 学习率: {self.args.lr}")
        print(f"  - 训练轮数: {self.args.epochs}")
        print(f"  - 图像尺寸: {self.args.img_size}")
        print(f"  - 类别数: {self.args.num_classes}")
        print(f"  - 深度监督: {self.args.deep_supervision}")
        self.logger.info(f"训练配置: batch_size={self.args.batch_size}, lr={self.args.lr}, epochs={self.args.epochs}")

    def train_epoch(self, epoch: int) -> Tuple[float, float, float]:
        """
        训练一个epoch

        Args:
            epoch: 当前epoch

        Returns:
            平均损失、平均IoU、平均准确率
        """
        self.model.train()

        # 学习率预热
        if epoch <= self.warmup_epochs:
            warmup_lr = self.base_lr * (epoch / self.warmup_epochs)
            for param_group in self.optimizer.param_groups:
                param_group['lr'] = warmup_lr
            current_lr = warmup_lr
        else:
            current_lr = self.optimizer.param_groups[0]['lr']

        epoch_loss = 0.0
        epoch_iou = 0.0
        epoch_acc = 0.0

        pbar = tqdm(self.train_loader, desc=f'Epoch {epoch}/{self.args.epochs} [Train] [lr={current_lr:.6f}]')

        for batch_idx, (images, masks) in enumerate(pbar):
            # 移动到设备
            images = images.to(self.device)
            masks = masks.to(self.device)

            # 前向传播
            self.optimizer.zero_grad()
            outputs = self.model(images)

            # 计算损失
            loss = self.criterion(outputs, masks)

            # 反向传播
            loss.backward()
            self.optimizer.step()

            # 计算指标
            if isinstance(outputs, list):
                preds = torch.argmax(outputs[-1], dim=1)
            else:
                preds = torch.argmax(outputs, dim=1)

            _, mean_iou = calculate_iou(preds, masks, self.args.num_classes)
            acc = calculate_pixel_accuracy(preds, masks)

            # 累积指标
            epoch_loss += loss.item()
            epoch_iou += mean_iou.item()
            epoch_acc += acc

            # 更新进度条
            pbar.set_postfix({
                'loss': f'{loss.item():.4f}',
                'iou': f'{mean_iou.item():.4f}',
                'acc': f'{acc:.4f}'
            })

        # 计算平均指标
        num_batches = len(self.train_loader)
        avg_loss = epoch_loss / num_batches
        avg_iou = epoch_iou / num_batches
        avg_acc = epoch_acc / num_batches

        # 记录到TensorBoard
        self.writer.add_scalar('Train/Loss', avg_loss, epoch)
        self.writer.add_scalar('Train/IoU', avg_iou, epoch)
        self.writer.add_scalar('Train/Accuracy', avg_acc, epoch)

        self.logger.info(f"Train Epoch {epoch} - Loss: {avg_loss:.4f}, IoU: {avg_iou:.4f}, Acc: {avg_acc:.4f}")
        print(f"Train - Loss: {avg_loss:.4f}, IoU: {avg_iou:.4f}, Acc: {avg_acc:.4f}")

        return avg_loss, avg_iou, avg_acc

    def validate(self, epoch: int) -> Tuple[float, float, float]:
        """
        验证

        Args:
            epoch: 当前epoch

        Returns:
            平均损失、平均IoU、平均准确率
        """
        self.model.eval()

        epoch_loss = 0.0
        epoch_iou = 0.0
        epoch_acc = 0.0

        pbar = tqdm(self.val_loader, desc=f'Epoch {epoch}/{self.args.epochs} [Val]')

        with torch.no_grad():
            for batch_idx, (images, masks) in enumerate(pbar):
                # 移动到设备
                images = images.to(self.device)
                masks = masks.to(self.device)

                # 前向传播
                outputs = self.model(images)

                # 计算损失
                loss = self.criterion(outputs, masks)

                # 计算指标
                if isinstance(outputs, list):
                    preds = torch.argmax(outputs[-1], dim=1)
                else:
                    preds = torch.argmax(outputs, dim=1)

                _, mean_iou = calculate_iou(preds, masks, self.args.num_classes)
                acc = calculate_pixel_accuracy(preds, masks)

                # 累积指标
                epoch_loss += loss.item()
                epoch_iou += mean_iou.item()
                epoch_acc += acc

                # 更新进度条
                pbar.set_postfix({
                    'loss': f'{loss.item():.4f}',
                    'iou': f'{mean_iou.item():.4f}',
                    'acc': f'{acc:.4f}'
                })

        # 计算平均指标
        num_batches = len(self.val_loader)
        avg_loss = epoch_loss / num_batches
        avg_iou = epoch_iou / num_batches
        avg_acc = epoch_acc / num_batches

        # 记录到TensorBoard
        self.writer.add_scalar('Val/Loss', avg_loss, epoch)
        self.writer.add_scalar('Val/IoU', avg_iou, epoch)
        self.writer.add_scalar('Val/Accuracy', avg_acc, epoch)

        self.logger.info(f"Val Epoch {epoch} - Loss: {avg_loss:.4f}, IoU: {avg_iou:.4f}, Acc: {avg_acc:.4f}")
        print(f"Val   - Loss: {avg_loss:.4f}, IoU: {avg_iou:.4f}, Acc: {avg_acc:.4f}")

        return avg_loss, avg_iou, avg_acc

    def _adjust_learning_rate_on_iou_drop(self, val_iou: float) -> None:
        """
        当IoU下降时智能调整学习率
        
        Args:
            val_iou: 当前验证IoU
        """
        current_lr = self.optimizer.param_groups[0]['lr']
        
        # 如果当前IoU比之前低,且学习率还未达到最小值
        if val_iou < self.prev_val_iou and current_lr > self.min_lr:
            # 计算新的学习率
            new_lr = max(current_lr * self.lr_adjustment_factor, self.min_lr)
            
            # 如果新学习率与当前学习率不同
            if new_lr != current_lr:
                for param_group in self.optimizer.param_groups:
                    param_group['lr'] = new_lr
                
                self.lr_adjustment_counter += 1
                print(f"\n📉 检测到IoU下降 ({self.prev_val_iou:.4f} -> {val_iou:.4f})")
                print(f"   学习率调整: {current_lr:.6f} -> {new_lr:.6f}")
                print(f"   累计调整次数: {self.lr_adjustment_counter}")
                self.logger.info(f"IoU下降,学习率从{current_lr:.6f}调整到{new_lr:.6f}")
        
        # 更新前一个epoch的验证IoU
        self.prev_val_iou = val_iou

    def train(self) -> None:
        """
        完整训练流程

        训练模型并保存最佳模型和定期检查点
        支持Early Stopping机制
        """
        self.logger.info("开始训练...")
        print("\n开始训练...")
        print(f"Early Stopping: patience={self.patience}")

        for epoch in range(self.start_epoch, self.args.epochs + 1):
            print(f"\n{'='*60}")
            print(f"Epoch {epoch}/{self.args.epochs}")
            print(f"{'='*60}")

            # 训练
            train_loss, train_iou, train_acc = self.train_epoch(epoch)

            # 验证
            val_loss, val_iou, val_acc = self.validate(epoch)

            # 学习率调整
            self.scheduler.step(val_iou)

            # 保存最佳模型并检查Early Stopping
            if val_iou > self.best_iou:
                self.best_iou = val_iou
                self._save_checkpoint(epoch, is_best=True)
                self.patience_counter = 0  # 重置计数器
                print(f"✓ 验证IoU提升! 重置Early Stopping计数器")
            else:
                self.patience_counter += 1
                print(f"⚠ 验证IoU未提升. Early Stopping计数: {self.patience_counter}/{self.patience}")
                self.logger.info(f"Early Stopping计数: {self.patience_counter}/{self.patience}")
                
                if self.patience_counter >= self.patience:
                    print(f"\n⚠ Early Stopping触发! 已连续{self.patience}轮未提升验证IoU")
                    self.logger.warning(f"Early Stopping触发! 已连续{self.patience}轮未提升验证IoU")
                    break

            # 定期保存检查点
            if epoch % self.args.save_interval == 0:
                self._save_checkpoint(epoch, is_best=False)

        self.logger.info(f"训练完成! 最佳IoU: {self.best_iou:.4f}")
        print(f"\n训练完成!")
        print(f"最佳IoU: {self.best_iou:.4f}")

        self.writer.close()

    def _save_checkpoint(self, epoch: int, is_best: bool) -> None:
        """
        保存检查点

        Args:
            epoch: 当前epoch
            is_best: 是否为最佳模型
        """
        checkpoint = {
            'epoch': epoch,
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'best_iou': self.best_iou,
            'args': self.args
        }

        if is_best:
            checkpoint_path = os.path.join(self.args.output_dir, 'checkpoints', 'best_model.pth')
            torch.save(checkpoint, checkpoint_path)
            self.logger.info(f"保存最佳模型 (IoU: {self.best_iou:.4f})")
            print(f"保存最佳模型 (IoU: {self.best_iou:.4f})")
        else:
            checkpoint_path = os.path.join(self.args.output_dir, 'checkpoints', f'model_epoch_{epoch}.pth')
            torch.save(checkpoint, checkpoint_path)
            self.logger.info(f"保存检查点: {checkpoint_path}")
            print(f"保存检查点: {checkpoint_path}")


def main() -> None:
    """主函数"""
    parser = argparse.ArgumentParser(description='U-Net++ 道路车辆分割训练')

    # 数据参数
    parser.add_argument('--data_dir', type=str, default='road_vehicle_pedestrian_det_datasets',
                        help='数据集根目录')
    parser.add_argument('--masks_dir', type=str, default='outputs/masks',
                        help='掩码目录')
    parser.add_argument('--output_dir', type=str, default='outputs',
                        help='输出目录')

    # 模型参数
    parser.add_argument('--num_classes', type=int, default=4,
                        help='分割类别数(包括背景)')
    parser.add_argument('--deep_supervision', type=bool, default=True,
                        help='是否使用深度监督')
    parser.add_argument('--encoder', type=str, default='vgg19',
                        choices=['vgg19', 'vgg19_bn'],
                        help='编码器类型')
    parser.add_argument('--pretrained', type=bool, default=True,
                        help='是否使用预训练权重')

    # 训练参数
    parser.add_argument('--batch_size', type=int, default=8,
                        help='批次大小')
    parser.add_argument('--epochs', type=int, default=50,
                        help='训练轮数')
    parser.add_argument('--lr', type=float, default=1e-4,
                        help='学习率')
    parser.add_argument('--weight_decay', type=float, default=1e-5,
                        help='权重衰减')
    parser.add_argument('--img_size', type=int, nargs=2, default=[512, 512],
                        help='输入图像尺寸')
    parser.add_argument('--num_workers', type=int, default=4,
                        help='数据加载工作进程数')

    # 设备参数
    parser.add_argument('--use_gpu', type=bool, default=False,
                        help='是否使用GPU训练 (默认: False, 使用CPU，如果为True会优先使用MPS，然后CUDA)')

    # 数据子集参数
    parser.add_argument('--subset_ratio', type=float, default=1.0,
                        help='使用数据集的比例 (0.0-1.0)，例如0.1表示使用10%%的数据 (默认: 1.0全部数据)')
    parser.add_argument('--random_seed', type=int, default=42,
                        help='数据子集随机种子，用于可重复的数据选择 (默认: 42)')

    # 其他参数
    parser.add_argument('--save_interval', type=int, default=10,
                        help='保存检查点的间隔')

    # 模型加载参数
    parser.add_argument('--resume', type=str, default=None,
                        help='恢复训练的模型路径 (例如: outputs/checkpoints/best_model.pth)')

    # 学习率预热参数
    parser.add_argument('--warmup_epochs', type=int, default=0,
                        help='学习率预热的epoch数 (默认: 0, 不使用预热)')

    # Early Stopping参数
    parser.add_argument('--early_stopping_patience', type=int, default=10,
                        help='Early Stopping的耐心值,连续多少轮验证IoU未提升则停止训练 (默认: 10)')
    
    # 智能学习率调整参数
    parser.add_argument('--min_lr', type=float, default=3e-5,
                        help='最小学习率,防止学习率过低导致过拟合 (默认: 3e-5)')
    parser.add_argument('--lr_adjustment_factor', type=float, default=0.6,
                        help='学习率调整因子,当IoU下降时学习率乘以该因子 (默认: 0.6)')

    args = parser.parse_args()

    # 创建输出目录
    os.makedirs(os.path.join(args.output_dir, 'checkpoints'), exist_ok=True)

    # 开始训练
    trainer = Trainer(args)
    trainer.train()


if __name__ == '__main__':
    main()