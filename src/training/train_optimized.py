"""
优化训练脚本 - 用于达到80% IoU目标
集成注意力机制、优化损失函数、增强数据增强

使用示例:
# 使用CBAM注意力从头训练
python3 src/training/train_optimized.py --use_gpu True --attention cbam --epochs 100

# 使用完整注意力架构
python3 src/training/train_optimized.py --use_gpu True --attention full --epochs 120

# 基于预训练模型微调
python3 src/training/train_optimized.py --use_gpu True --attention cbam_aspp --resume outputs/checkpoints/best_model.pth
"""
import argparse
import logging
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
from src.models.unet_plusplus_enhanced import create_model
from src.utils.exceptions import ConfigError, DataLoadError, ModelLoadError
from src.utils.losses import CombinedLoss, DeepSupervisionLoss, calculate_iou, calculate_pixel_accuracy
from src.utils.logging_config import get_training_logger


class OptimizedTrainer:
    """优化训练器 - 集成注意力机制和优化策略"""

    def __init__(self, args: argparse.Namespace) -> None:
        """初始化优化训练器"""
        self.args = args
        self.logger = get_training_logger(args.output_dir + '/logs')
        self.logger.info("="*60)
        self.logger.info("初始化优化训练器 - 目标IoU 80%")
        self.logger.info("="*60)

        # 验证配置
        self._validate_config()

        # 设置设备
        self.device = self._setup_device()

        # 创建数据加载器
        self.logger.info("加载数据集...")
        print("\n" + "="*60)
        print("加载优化数据集...")
        print("="*60)
        try:
            self.train_loader = get_dataloader(
                data_dir=args.data_dir,
                masks_dir=args.masks_dir,
                split='train',
                batch_size=args.batch_size,
                img_size=tuple(args.img_size),
                num_workers=args.num_workers,
                subset_ratio=args.subset_ratio,
                random_seed=args.random_seed,
                balance_sampling=args.balance_sampling,
                car_only=getattr(args, 'car_only', False)
            )

            self.val_loader = get_dataloader(
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

        # 创建增强模型
        self.logger.info(f"创建U-Net++增强模型 (注意力类型: {args.attention})...")
        print(f"\n创建U-Net++增强模型...")
        print(f"  注意力类型: {args.attention}")
        print(f"  编码器: {args.encoder}")
        print(f"  预训练: {args.pretrained}")
        
        self.model = create_model(
            num_classes=args.num_classes,
            attention_type=args.attention,
            encoder_name=args.encoder,
            pretrained=args.pretrained,
            deep_supervision=args.deep_supervision
        )
        self.model = self.model.to(self.device)

        # 计算并打印模型参数量
        self._print_model_info()

        # 创建优化的损失函数
        self._create_optimized_loss()

        # 创建优化器
        self.optimizer = self._create_optimizer()

        # 学习率调度器
        self.scheduler = self._create_scheduler()

        # 创建TensorBoard日志
        log_dir = os.path.join(
            args.output_dir, 
            'logs', 
            f'optimized_{args.attention}_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
        )
        self.writer = SummaryWriter(log_dir)

        # 训练状态
        self.best_iou = 0.0
        self.start_epoch = 1
        self.best_epoch = 0

        # 加载预训练模型
        if args.resume:
            self._load_checkpoint(args.resume)

        # Early Stopping
        self.patience = args.early_stopping_patience
        self.patience_counter = 0
        
        # 学习率预热
        self.warmup_epochs = args.warmup_epochs
        self.base_lr = args.lr

        self._print_config()

    def _validate_config(self) -> None:
        """验证配置参数"""
        if self.args.batch_size <= 0:
            raise ConfigError("批次大小必须大于0")
        if self.args.epochs <= 0:
            raise ConfigError("训练轮数必须大于0")
        if not os.path.exists(self.args.data_dir):
            raise ConfigError("数据目录不存在", self.args.data_dir)

    def _setup_device(self) -> torch.device:
        """设置训练设备"""
        if self.args.use_gpu:
            if torch.backends.mps.is_available():
                device = torch.device('mps')
                print("✓ 使用MPS (M4芯片GPU) 训练")
                self.logger.info("使用MPS (M4芯片GPU) 训练")
            elif torch.cuda.is_available():
                device = torch.device('cuda')
                print(f"✓ 使用CUDA GPU训练: {torch.cuda.get_device_name(0)}")
                self.logger.info(f"使用CUDA GPU训练: {torch.cuda.get_device_name(0)}")
            else:
                device = torch.device('cpu')
                print("⚠ GPU不可用，使用CPU训练")
                self.logger.warning("GPU不可用，使用CPU训练")
        else:
            device = torch.device('cpu')
            print("使用CPU训练")
            self.logger.info("使用CPU训练")
        return device

    def _print_model_info(self) -> None:
        """打印模型信息"""
        total_params = sum(p.numel() for p in self.model.parameters())
        trainable_params = sum(p.numel() for p in self.model.parameters() if p.requires_grad)
        
        print(f"\n模型参数统计:")
        print(f"  总参数量: {total_params:,}")
        print(f"  可训练参数量: {trainable_params:,}")
        print(f"  模型大小: {total_params * 4 / 1024 / 1024:.2f} MB")
        self.logger.info(f"模型参数量: {total_params:,}")

    def _create_optimized_loss(self) -> None:
        """创建优化的损失函数"""
        # 激进的类别权重 - 极度关注前景类别
        # Background: 极低权重 (避免过预测背景)
        # Car: 极高权重 (目标类别,当前52%,目标80%)
        # Truck: 最高权重 (最难类别,当前36%)
        # Bus: 中等权重 (已达标85%)
        
        if self.args.use_aggressive_weights:
            class_weights = torch.tensor([0.01, 5.0, 8.0, 2.0], dtype=torch.float32)
            print(f"\n使用激进类别权重:")
            print(f"  Background: {class_weights[0]:.4f} (降低以减少背景过预测)")
            print(f"  Car:        {class_weights[1]:.4f} (提升以改善边界)")
            print(f"  Truck:      {class_weights[2]:.4f} (最高权重,改善小目标)")
            print(f"  Bus:        {class_weights[3]:.4f} (维持权重)")
        else:
            class_weights = torch.tensor([0.02, 3.0, 2.5, 4.0], dtype=torch.float32)
            print(f"\n使用标准类别权重:")
            print(f"  Background: {class_weights[0]:.4f}")
            print(f"  Car:        {class_weights[1]:.4f}")
            print(f"  Truck:      {class_weights[2]:.4f}")
            print(f"  Bus:        {class_weights[3]:.4f}")
        
        self.logger.info(f"类别权重: {class_weights.tolist()}")
        
        # 优化的组合损失
        base_loss = CombinedLoss(
            weight_ce=1.0,          # CrossEntropy权重
            weight_dice=4.0,        # 提高Dice权重,改善边界
            weight_focal=0.0,       # 暂时禁用Focal Loss针对MPS
            class_weights=class_weights,
            focal_gamma=2.5
        )
        
        if self.args.deep_supervision:
            self.criterion = DeepSupervisionLoss(base_loss)
            print("✓ 启用深度监督损失")
        else:
            self.criterion = base_loss

    def _create_optimizer(self) -> optim.Optimizer:
        """创建优化器"""
        # 使用AdamW优化器,更好的权重衰减
        optimizer = optim.AdamW(
            self.model.parameters(),
            lr=self.args.lr,
            weight_decay=self.args.weight_decay,
            betas=(0.9, 0.999)
        )
        print(f"\n优化器: AdamW")
        print(f"  初始学习率: {self.args.lr}")
        print(f"  权重衰减: {self.args.weight_decay}")
        return optimizer

    def _create_scheduler(self) -> optim.lr_scheduler._LRScheduler:
        """创建学习率调度器"""
        # 使用CosineAnnealingWarmRestarts,周期性重启
        scheduler = optim.lr_scheduler.CosineAnnealingWarmRestarts(
            self.optimizer,
            T_0=self.args.cosine_t0,      # 第一次重启周期
            T_mult=2,                       # 每次重启周期倍增
            eta_min=self.args.min_lr        # 最小学习率
        )
        print(f"\n学习率调度器: CosineAnnealingWarmRestarts")
        print(f"  T_0: {self.args.cosine_t0}")
        print(f"  T_mult: 2")
        print(f"  eta_min: {self.args.min_lr}")
        return scheduler

    def _load_checkpoint(self, checkpoint_path: str) -> None:
        """加载检查点"""
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
            print(f"  ✓ 模型IoU: {self.best_iou:.4f}")
            print(f"  ✓ 起始轮数: {self.start_epoch}")
            self.logger.info(f"模型加载成功 - IoU: {self.best_iou:.4f}, 起始轮数: {self.start_epoch}")
        except Exception as e:
            self.logger.error(f"模型加载失败: {e}")
            raise ModelLoadError("模型加载失败", str(e))

    def _print_config(self) -> None:
        """打印训练配置"""
        print(f"\n{'='*60}")
        print("训练配置")
        print('='*60)
        print(f"  批次大小: {self.args.batch_size}")
        print(f"  学习率: {self.args.lr}")
        print(f"  训练轮数: {self.args.epochs}")
        print(f"  图像尺寸: {self.args.img_size}")
        print(f"  类别数: {self.args.num_classes}")
        print(f"  深度监督: {self.args.deep_supervision}")
        print(f"  注意力类型: {self.args.attention}")
        print(f"  早停耐心: {self.args.early_stopping_patience}")
        print(f"  目标IoU: 80%")
        print('='*60)
        self.logger.info(f"训练配置: batch_size={self.args.batch_size}, lr={self.args.lr}, epochs={self.args.epochs}")

    def train_epoch(self, epoch: int) -> Tuple[float, float, float]:
        """训练一个epoch"""
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
            images = images.to(self.device)
            masks = masks.to(self.device)

            # 前向传播
            self.optimizer.zero_grad()
            outputs = self.model(images)

            # 计算损失
            if self.device.type == 'mps':
                outputs_cpu = outputs[-1].cpu() if isinstance(outputs, list) else outputs.cpu()
                loss = self.criterion(outputs_cpu, masks.cpu().long())
                loss = loss.to(self.device)
            else:
                loss = self.criterion(outputs, masks)

            # 反向传播
            loss.backward()
            
            # 梯度裁剪
            if self.args.grad_clip > 0:
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), self.args.grad_clip)
            
            self.optimizer.step()

            # 计算指标
            if isinstance(outputs, list):
                preds = torch.argmax(outputs[-1], dim=1)
            else:
                preds = torch.argmax(outputs, dim=1)
            
            preds_cpu = preds.cpu()
            masks_cpu = masks.cpu()
            _, mean_iou = calculate_iou(preds_cpu, masks_cpu, self.args.num_classes)
            acc = calculate_pixel_accuracy(preds_cpu, masks_cpu)

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
        self.writer.add_scalar('Train/LR', current_lr, epoch)

        self.logger.info(f"Train Epoch {epoch} - Loss: {avg_loss:.4f}, IoU: {avg_iou:.4f}, Acc: {avg_acc:.4f}")
        print(f"Train - Loss: {avg_loss:.4f}, IoU: {avg_iou:.4f}, Acc: {avg_acc:.4f}")

        return avg_loss, avg_iou, avg_acc

    def validate(self, epoch: int) -> Tuple[float, float, float]:
        """验证"""
        self.model.eval()

        epoch_loss = 0.0
        epoch_iou = 0.0
        epoch_acc = 0.0

        pbar = tqdm(self.val_loader, desc=f'Epoch {epoch}/{self.args.epochs} [Val]')

        with torch.no_grad():
            for batch_idx, (images, masks) in enumerate(pbar):
                images = images.to(self.device)
                masks = masks.to(self.device)

                # 前向传播
                outputs = self.model(images)

                # 计算损失
                if self.device.type == 'mps':
                    outputs_cpu = outputs[-1].cpu() if isinstance(outputs, list) else outputs.cpu()
                    loss = self.criterion(outputs_cpu, masks.cpu().long())
                else:
                    loss = self.criterion(outputs, masks)

                # 计算指标
                if isinstance(outputs, list):
                    preds = torch.argmax(outputs[-1], dim=1)
                else:
                    preds = torch.argmax(outputs, dim=1)
                
                preds_cpu = preds.cpu()
                masks_cpu = masks.cpu()
                _, mean_iou = calculate_iou(preds_cpu, masks_cpu, self.args.num_classes)
                acc = calculate_pixel_accuracy(preds_cpu, masks_cpu)

                epoch_loss += loss.item()
                epoch_iou += mean_iou.item()
                epoch_acc += acc

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

    def train(self) -> None:
        """完整训练流程"""
        self.logger.info("开始优化训练...")
        print(f"\n{'='*60}")
        print("开始训练 - 目标: IoU ≥ 80%")
        print(f"{'='*60}")
        print(f"Early Stopping: patience={self.patience}")

        for epoch in range(self.start_epoch, self.args.epochs + 1):
            print(f"\n{'='*60}")
            print(f"Epoch {epoch}/{self.args.epochs}")
            print(f"{'='*60}")

            # 训练
            train_loss, train_iou, train_acc = self.train_epoch(epoch)

            # 验证
            val_loss, val_iou, val_acc = self.validate(epoch)

            # 更新学习率
            self.scheduler.step()

            # 保存最佳模型
            if val_iou > self.best_iou:
                self.best_iou = val_iou
                self.best_epoch = epoch
                self._save_checkpoint(epoch, is_best=True)
                self.patience_counter = 0
                print(f"✓ 验证IoU提升! 最佳IoU: {self.best_iou:.4f}")
                print(f"  距离目标80%: {(0.80 - self.best_iou)*100:.2f}%")
            else:
                self.patience_counter += 1
                print(f"⚠ 验证IoU未提升. Early Stopping计数: {self.patience_counter}/{self.patience}")
                print(f"  当前最佳IoU: {self.best_iou:.4f} (Epoch {self.best_epoch})")
                self.logger.info(f"Early Stopping计数: {self.patience_counter}/{self.patience}")
                
                if self.patience_counter >= self.patience:
                    print(f"\n⚠ Early Stopping触发! 已连续{self.patience}轮未提升验证IoU")
                    self.logger.warning(f"Early Stopping触发! 已连续{self.patience}轮未提升验证IoU")
                    break

            # 定期保存检查点
            if epoch % self.args.save_interval == 0:
                self._save_checkpoint(epoch, is_best=False)

        self.logger.info(f"训练完成! 最佳IoU: {self.best_iou:.4f} (Epoch {self.best_epoch})")
        print(f"\n{'='*60}")
        print("训练完成!")
        print(f"{'='*60}")
        print(f"最佳IoU: {self.best_iou:.4f} ({self.best_iou*100:.2f}%)")
        print(f"最佳Epoch: {self.best_epoch}")
        
        if self.best_iou >= 0.80:
            print(f"✅ 恭喜! 已达到目标 IoU ≥ 80%")
        else:
            print(f"⚠️  未达到目标 80%, 差距: {(0.80 - self.best_iou)*100:.2f}%")
        
        print(f"{'='*60}")

        self.writer.close()

    def _save_checkpoint(self, epoch: int, is_best: bool) -> None:
        """保存检查点"""
        checkpoint = {
            'epoch': epoch,
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'best_iou': self.best_iou,
            'args': self.args
        }

        if is_best:
            model_name = f'{self.args.attention}_best_model.pth'
            checkpoint_path = os.path.join(self.args.output_dir, 'checkpoints', model_name)
            torch.save(checkpoint, checkpoint_path)
            self.logger.info(f"保存最佳模型 (IoU: {self.best_iou:.4f})")
            print(f"保存最佳模型 (IoU: {self.best_iou:.4f}) -> {model_name}")
        else:
            checkpoint_path = os.path.join(self.args.output_dir, 'checkpoints', f'{self.args.attention}_epoch_{epoch}.pth')
            torch.save(checkpoint, checkpoint_path)
            self.logger.info(f"保存检查点: {checkpoint_path}")
            print(f"保存检查点: {checkpoint_path}")


def main() -> None:
    """主函数"""
    parser = argparse.ArgumentParser(description='U-Net++ 优化训练 - 目标IoU 80%')

    # 数据参数
    parser.add_argument('--data_dir', type=str, default='road_vehicle_pedestrian_det_datasets')
    parser.add_argument('--masks_dir', type=str, default='outputs/masks_car')
    parser.add_argument('--output_dir', type=str, default='outputs')

    # 模型参数
    parser.add_argument('--num_classes', type=int, default=4)
    parser.add_argument('--deep_supervision', type=bool, default=True)
    parser.add_argument('--encoder', type=str, default='vgg19', choices=['vgg19', 'vgg19_bn'])
    parser.add_argument('--pretrained', type=bool, default=True)
    parser.add_argument('--attention', type=str, default='cbam_aspp',
                        choices=['none', 'cbam', 'se', 'aspp', 'cbam_aspp', 'se_aspp', 'full'],
                        help='注意力类型: none(基线), cbam, se, aspp, cbam_aspp, se_aspp, full(完整)')
    
    # 训练参数 (优化后)
    parser.add_argument('--batch_size', type=int, default=8)
    parser.add_argument('--epochs', type=int, default=100)
    parser.add_argument('--lr', type=float, default=2e-4, help='提高学习率加速收敛')
    parser.add_argument('--weight_decay', type=float, default=1e-4, help='增加权重衰减防止过拟合')
    parser.add_argument('--grad_clip', type=float, default=1.0)
    parser.add_argument('--img_size', type=int, nargs=2, default=[512, 512])
    parser.add_argument('--num_workers', type=int, default=4)
    
    # 学习率调度参数
    parser.add_argument('--cosine_t0', type=int, default=10, help='Cosine Annealing第一次重启周期')
    parser.add_argument('--min_lr', type=float, default=1e-6, help='最小学习率')
    parser.add_argument('--warmup_epochs', type=int, default=5, help='学习率预热轮数')
    
    # Early Stopping
    parser.add_argument('--early_stopping_patience', type=int, default=15, help='提高耐心值')
    
    # 损失函数优化
    parser.add_argument('--use_aggressive_weights', action='store_true',
                        help='使用激进的类别权重,大幅提高前景权重')
    
    # 设备参数
    parser.add_argument('--use_gpu', action='store_true')
    
    # 其他参数
    parser.add_argument('--subset_ratio', type=float, default=1.0)
    parser.add_argument('--random_seed', type=int, default=42)
    parser.add_argument('--save_interval', type=int, default=10)
    parser.add_argument('--balance_sampling', action='store_true')
    parser.add_argument('--resume', type=str, default=None)
    parser.add_argument('--car_only', action='store_true')

    args = parser.parse_args()

    # 创建输出目录
    os.makedirs(os.path.join(args.output_dir, 'checkpoints'), exist_ok=True)

    # 开始训练
    trainer = OptimizedTrainer(args)
    trainer.train()


if __name__ == '__main__':
    main()
