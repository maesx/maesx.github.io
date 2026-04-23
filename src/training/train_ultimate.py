"""
极致优化训练脚本 - 目标 IoU 80%
使用 ResNet-101 + FPN + 注意力 + 边界优化

这是最激进的训练配置,理论上限可达75-80% mIoU

使用示例:
# 完整训练 (推荐,预期75-80% IoU)
python3 src/training/train_ultimate.py --use_gpu True --epochs 120

# 快速验证 (预期65-70% IoU)
python3 src/training/train_ultimate.py --use_gpu True --epochs 50 --use_fpn False

# 轻量级训练 (预期60-65% IoU)
python3 src/training/train_ultimate.py --use_gpu True --epochs 80 --use_fpn False --attention cbam
"""
import argparse
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Tuple

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torch.utils.tensorboard import SummaryWriter
from tqdm import tqdm

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.data.dataset import get_dataloader
from src.models.unet_plusplus_ultimate import create_ultimate_model
from src.utils.losses import BoundaryLoss, DiceLoss


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BoundaryAwareLoss(nn.Module):
    """
    边界感知损失
    结合交叉熵 + Dice + 边界损失
    """
    def __init__(
        self,
        class_weights: torch.Tensor,
        dice_weight: float = 4.0,
        boundary_weight: float = 2.0
    ) -> None:
        super(BoundaryAwareLoss, self).__init__()
        self.ce_loss = nn.CrossEntropyLoss(weight=class_weights)
        self.dice_loss = DiceLoss()
        self.boundary_loss = BoundaryLoss()
        self.dice_weight = dice_weight
        self.boundary_weight = boundary_weight
    
    def forward(
        self,
        pred: torch.Tensor,
        target: torch.Tensor,
        boundary_pred: torch.Tensor = None,
        boundary_target: torch.Tensor = None
    ) -> Tuple[torch.Tensor, dict]:
        """
        Args:
            pred: 分割预测 [B, C, H, W]
            target: 分割真值 [B, H, W]
            boundary_pred: 边界预测 [B, 1, H, W]
            boundary_target: 边界真值 [B, 1, H, W]
        
        Returns:
            total_loss: 总损失
            loss_dict: 各项损失字典
        """
        # 分割损失
        ce_loss = self.ce_loss(pred, target)
        dice_loss = self.dice_loss(pred, target)
        
        total_loss = ce_loss + self.dice_weight * dice_loss
        loss_dict = {
            'ce_loss': ce_loss.item(),
            'dice_loss': dice_loss.item()
        }
        
        # 边界损失
        if boundary_pred is not None and boundary_target is not None:
            b_loss = self.boundary_loss(boundary_pred, boundary_target)
            total_loss += self.boundary_weight * b_loss
            loss_dict['boundary_loss'] = b_loss.item()
        
        loss_dict['total_loss'] = total_loss.item()
        return total_loss, loss_dict


def extract_boundary(mask: torch.Tensor) -> torch.Tensor:
    """
    从分割掩码提取边界
    
    Args:
        mask: 分割掩码 [B, H, W]
    
    Returns:
        boundary: 边界图 [B, 1, H, W]
    """
    # 使用Laplacian算子检测边界
    mask_float = mask.float().unsqueeze(1)  # [B, 1, H, W]
    
    # Sobel算子
    sobel_x = torch.tensor([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], 
                           dtype=torch.float32, device=mask.device).view(1, 1, 3, 3)
    sobel_y = torch.tensor([[-1, -2, -1], [0, 0, 0], [1, 2, 1]], 
                          dtype=torch.float32, device=mask.device).view(1, 1, 3, 3)
    
    edge_x = torch.abs(torch.nn.functional.conv2d(mask_float, sobel_x, padding=1))
    edge_y = torch.abs(torch.nn.functional.conv2d(mask_float, sobel_y, padding=1))
    
    boundary = (edge_x + edge_y).squeeze(1)  # [B, H, W]
    boundary = (boundary > 0.5).float()  # 二值化
    
    return boundary.unsqueeze(1)  # [B, 1, H, W]


def compute_iou(pred: torch.Tensor, target: torch.Tensor, num_classes: int = 4) -> Tuple[float, list]:
    """
    计算IoU指标
    
    Args:
        pred: 预测结果 [B, H, W]
        target: 真值 [B, H, W]
        num_classes: 类别数
    
    Returns:
        mIoU: 平均IoU (排除背景)
        class_ious: 各类别IoU列表
    """
    class_ious = []
    
    for cls in range(num_classes):
        pred_mask = (pred == cls)
        target_mask = (target == cls)
        
        intersection = (pred_mask & target_mask).sum().float()
        union = (pred_mask | target_mask).sum().float()
        
        if union > 0:
            iou = (intersection / union).item()
        else:
            iou = 0.0
        
        class_ious.append(iou)
    
    # 排除背景的mIoU
    mIoU = np.mean(class_ious[1:])
    
    return mIoU, class_ious


def train_one_epoch(
    model: nn.Module,
    dataloader: DataLoader,
    criterion: nn.Module,
    optimizer: optim.Optimizer,
    device: torch.device,
    epoch: int,
    use_boundary: bool = True
) -> dict:
    """
    训练一个epoch
    """
    model.train()
    
    total_loss = 0
    total_iou = 0
    class_ious_sum = [0.0] * 4
    num_batches = 0
    
    pbar = tqdm(dataloader, desc=f"Epoch {epoch}")
    
    for images, masks in pbar:
        images = images.to(device)
        masks = masks.to(device).long()  # 确保masks是Long类型
        
        optimizer.zero_grad()
        
        # 前向传播
        outputs = model(images)
        
        # 处理输出
        if isinstance(outputs, tuple):
            if len(outputs) == 3:
                # 主输出 + 辅助输出 + 边界
                main_output, aux_outputs, boundary_pred = outputs
                loss_terms = criterion(
                    main_output, masks,
                    boundary_pred, extract_boundary(masks)
                )
                total_batch_loss = loss_terms[0] + 0.4 * sum(
                    criterion(aux, masks)[0] for aux in aux_outputs
                )
            elif len(outputs) == 2:
                # 主输出 + 辅助输出 (或边界)
                if use_boundary:
                    main_output, boundary_pred = outputs
                    total_batch_loss = criterion(
                        main_output, masks,
                        boundary_pred, extract_boundary(masks)
                    )[0]
                else:
                    main_output, aux_outputs = outputs
                    total_batch_loss = criterion(main_output, masks)[0] + 0.4 * sum(
                        criterion(aux, masks)[0] for aux in aux_outputs
                    )
            else:
                main_output = outputs
                total_batch_loss = criterion(main_output, masks)[0]
        else:
            main_output = outputs
            total_batch_loss = criterion(main_output, masks)[0]
        
        # 反向传播
        total_batch_loss.backward()
        optimizer.step()
        
        # 计算指标
        pred = main_output.argmax(dim=1)
        mIoU, class_ious = compute_iou(pred, masks, num_classes=4)
        
        total_loss += total_batch_loss.item()
        total_iou += mIoU
        for i, ci in enumerate(class_ious):
            class_ious_sum[i] += ci
        num_batches += 1
        
        # 更新进度条
        pbar.set_postfix({
            'loss': total_batch_loss.item(),
            'mIoU': mIoU
        })
    
    # 计算平均值
    metrics = {
        'loss': total_loss / num_batches,
        'mIoU': total_iou / num_batches,
        'class_ious': [ci / num_batches for ci in class_ious_sum]
    }
    
    return metrics


def validate(
    model: nn.Module,
    dataloader: DataLoader,
    criterion: nn.Module,
    device: torch.device,
    use_boundary: bool = True
) -> dict:
    """
    验证模型
    """
    model.eval()
    
    total_loss = 0
    total_iou = 0
    class_ious_sum = [0.0] * 4
    num_batches = 0
    
    with torch.no_grad():
        for images, masks in tqdm(dataloader, desc="Validating"):
            images = images.to(device)
            masks = masks.to(device).long()  # 确保masks是Long类型
            
            # 前向传播
            outputs = model(images)
            
            # 处理输出
            if isinstance(outputs, tuple):
                if len(outputs) == 3:
                    main_output, aux_outputs, boundary_pred = outputs
                    total_batch_loss, _ = criterion(
                        main_output, masks,
                        boundary_pred, extract_boundary(masks)
                    )
                elif len(outputs) == 2:
                    if use_boundary:
                        main_output, boundary_pred = outputs
                        total_batch_loss, _ = criterion(
                            main_output, masks,
                            boundary_pred, extract_boundary(masks)
                        )
                    else:
                        main_output, aux_outputs = outputs
                        total_batch_loss, _ = criterion(main_output, masks)
                else:
                    main_output = outputs
                    total_batch_loss, _ = criterion(main_output, masks)
            else:
                main_output = outputs
                total_batch_loss, _ = criterion(main_output, masks)
            
            # 计算指标
            pred = main_output.argmax(dim=1)
            mIoU, class_ious = compute_iou(pred, masks, num_classes=4)
            
            total_loss += total_batch_loss.item()
            total_iou += mIoU
            for i, ci in enumerate(class_ious):
                class_ious_sum[i] += ci
            num_batches += 1
    
    metrics = {
        'loss': total_loss / num_batches,
        'mIoU': total_iou / num_batches,
        'class_ious': [ci / num_batches for ci in class_ious_sum]
    }
    
    return metrics


def main():
    parser = argparse.ArgumentParser(description="U-Net++ 极致训练")
    
    # 数据参数
    parser.add_argument('--train_img_dir', type=str, 
                       default='road_vehicle_pedestrian_det_datasets/images/train')
    parser.add_argument('--train_mask_dir', type=str,
                       default='outputs/masks_car/train')
    parser.add_argument('--val_img_dir', type=str,
                       default='road_vehicle_pedestrian_det_datasets/images/val')
    parser.add_argument('--val_mask_dir', type=str,
                       default='outputs/masks_car/val')
    parser.add_argument('--batch_size', type=int, default=6)
    parser.add_argument('--num_workers', type=int, default=4)
    parser.add_argument('--img_size', type=tuple, default=(512, 512))
    
    # 模型参数
    parser.add_argument('--num_classes', type=int, default=4)
    parser.add_argument('--attention', type=str, default='cbam_aspp',
                       choices=['none', 'cbam', 'se', 'aspp', 'cbam_aspp', 'se_aspp', 'full'])
    parser.add_argument('--use_fpn', type=bool, default=True)
    parser.add_argument('--use_boundary_refinement', type=bool, default=True)
    parser.add_argument('--use_separable_conv', type=bool, default=True)
    parser.add_argument('--use_aggressive_weights', type=bool, default=True)
    
    # 训练参数
    parser.add_argument('--epochs', type=int, default=120)
    parser.add_argument('--lr', type=float, default=1e-4)  # ResNet-101使用更小学习率
    parser.add_argument('--weight_decay', type=float, default=1e-4)
    parser.add_argument('--use_gpu', type=bool, default=True)
    parser.add_argument('--early_stopping_patience', type=int, default=20)
    
    # 保存参数
    parser.add_argument('--save_dir', type=str, default='outputs/checkpoints')
    parser.add_argument('--save_interval', type=int, default=10)
    parser.add_argument('--log_dir', type=str, default='outputs/logs')
    
    # 恢复训练
    parser.add_argument('--resume', type=str, default=None)
    
    args = parser.parse_args()
    
    # 检查数据集路径是否存在
    data_dir = Path('road_vehicle_pedestrian_det_datasets')
    masks_dir = Path('outputs/masks_car')
    
    logger.info("检查数据集路径...")
    logger.info(f"当前工作目录: {os.getcwd()}")
    logger.info(f"数据集目录: {data_dir.absolute()}")
    logger.info(f"掩码目录: {masks_dir.absolute()}")
    
    # 检查训练集
    train_img_dir = data_dir / 'images' / 'train'
    train_mask_dir = masks_dir / 'train'
    
    if not train_img_dir.exists():
        logger.error(f"❌ 训练图像目录不存在: {train_img_dir.absolute()}")
        logger.error("请确保:")
        logger.error("  1. 在项目根目录运行脚本")
        logger.error("  2. 数据集已正确解压")
        logger.error("  3. 目录结构正确:")
        logger.error("     road_vehicle_pedestrian_det_datasets/images/train/")
        logger.error("     outputs/masks_car/train/")
        return
    
    if not train_mask_dir.exists():
        logger.error(f"❌ 训练掩码目录不存在: {train_mask_dir.absolute()}")
        logger.error("请确保:")
        logger.error("  1. 在项目根目录运行脚本")
        logger.error("  2. 掩码文件已正确生成")
        logger.error("  3. 目录结构正确:")
        logger.error("     outputs/masks_car/train/")
        return
    
    # 检查文件数量
    train_images = list(train_img_dir.glob('*.jpg')) + list(train_img_dir.glob('*.png'))
    train_masks = list(train_mask_dir.glob('*.png'))
    
    logger.info(f"✓ 找到训练图像: {len(train_images)} 张")
    logger.info(f"✓ 找到训练掩码: {len(train_masks)} 张")
    
    if len(train_images) == 0:
        logger.error("❌ 训练图像目录为空!")
        return
    
    if len(train_masks) == 0:
        logger.error("❌ 训练掩码目录为空!")
        return
    
    # 检查验证集
    val_img_dir = data_dir / 'images' / 'val'
    val_mask_dir = masks_dir / 'val'
    
    if not val_img_dir.exists():
        logger.warning(f"⚠️  验证图像目录不存在: {val_img_dir.absolute()}")
    else:
        val_images = list(val_img_dir.glob('*.jpg')) + list(val_img_dir.glob('*.png'))
        logger.info(f"✓ 找到验证图像: {len(val_images)} 张")
    
    if not val_mask_dir.exists():
        logger.warning(f"⚠️  验证掩码目录不存在: {val_mask_dir.absolute()}")
    elif val_mask_dir.exists():
        val_masks = list(val_mask_dir.glob('*.png'))
        logger.info(f"✓ 找到验证掩码: {len(val_masks)} 张")
    
    logger.info("✓ 数据集路径检查通过!")
    logger.info("")
    
    # 设置设备
    if args.use_gpu and torch.backends.mps.is_available():
        device = torch.device('mps')
        logger.info("使用 MPS (Apple Silicon GPU)")
    elif args.use_gpu and torch.cuda.is_available():
        device = torch.device('cuda')
        logger.info("使用 CUDA GPU")
    else:
        device = torch.device('cpu')
        logger.info("使用 CPU")
    
    # 创建保存目录
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # 如果是恢复训练,使用原有目录;否则创建新目录
    if args.resume and os.path.exists(args.resume):
        # 从恢复路径推断保存目录
        resume_dir = os.path.dirname(args.resume)
        if 'ultimate_' in resume_dir:
            save_dir = resume_dir
            logger.info(f"继续使用保存目录: {save_dir}")
        else:
            save_dir = os.path.join(args.save_dir, f'ultimate_{timestamp}')
            os.makedirs(save_dir, exist_ok=True)
    else:
        save_dir = os.path.join(args.save_dir, f'ultimate_{timestamp}')
        os.makedirs(save_dir, exist_ok=True)
    
    os.makedirs(args.log_dir, exist_ok=True)
    
    # 日志文件
    log_file = os.path.join(args.log_dir, f'ultimate_training_{timestamp}.log')
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    
    # TensorBoard
    writer = SummaryWriter(os.path.join(args.log_dir, f'ultimate_{timestamp}'))
    
    # 创建数据集
    logger.info("创建数据集...")
    
    # 使用 get_dataloader 函数创建数据加载器
    train_loader = get_dataloader(
        data_dir='road_vehicle_pedestrian_det_datasets',
        masks_dir='outputs/masks_car',
        split='train',
        batch_size=args.batch_size,
        img_size=args.img_size,
        num_workers=args.num_workers,
        pin_memory=True if args.num_workers > 0 else False  # macOS MPS兼容性
    )
    
    val_loader = get_dataloader(
        data_dir='road_vehicle_pedestrian_det_datasets',
        masks_dir='outputs/masks_car',
        split='val',
        batch_size=args.batch_size,
        img_size=args.img_size,
        num_workers=args.num_workers,
        pin_memory=True if args.num_workers > 0 else False  # macOS MPS兼容性
    )
    
    logger.info(f"训练集: {len(train_loader.dataset)} 张图像")
    logger.info(f"验证集: {len(val_loader.dataset)} 张图像")
    
    # 创建模型
    logger.info("创建模型...")
    logger.info(f"配置:")
    logger.info(f"  - 编码器: ResNet-101 (ImageNet预训练)")
    logger.info(f"  - 注意力: {args.attention}")
    logger.info(f"  - FPN: {args.use_fpn}")
    logger.info(f"  - 边界优化: {args.use_boundary_refinement}")
    logger.info(f"  - 深度可分离卷积: {args.use_separable_conv}")
    
    model = create_ultimate_model(
        num_classes=args.num_classes,
        pretrained=True,
        use_fpn=args.use_fpn,
        attention_type=args.attention,
        use_boundary_refinement=args.use_boundary_refinement,
        use_separable_conv=args.use_separable_conv
    )
    model = model.to(device)
    
    # 统计参数
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    logger.info(f"模型参数: {total_params:,} (可训练: {trainable_params:,})")
    logger.info(f"模型大小: {total_params * 4 / 1024 / 1024:.2f} MB")
    
    # 类别权重 (超激进配置)
    if args.use_aggressive_weights:
        # Car: 5.0, Truck: 10.0 (最高权重,重点改善小目标), Bus: 3.0
        class_weights = torch.tensor([0.01, 5.0, 10.0, 3.0], device=device)
        logger.info("使用超激进类别权重: BG=0.01, Car=5.0, Truck=10.0, Bus=3.0")
    else:
        # 标准激进权重
        class_weights = torch.tensor([0.02, 4.0, 6.0, 2.5], device=device)
        logger.info("使用标准激进权重: BG=0.02, Car=4.0, Truck=6.0, Bus=2.5")
    
    # 损失函数
    criterion = BoundaryAwareLoss(
        class_weights=class_weights,
        dice_weight=5.0,  # 提高Dice权重
        boundary_weight=3.0  # 提高边界损失权重
    )
    
    # 优化器
    optimizer = optim.AdamW(
        model.parameters(),
        lr=args.lr,
        weight_decay=args.weight_decay
    )
    
    # 学习率调度器 (使用ReduceLROnPlateau,更稳健)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode='max', factor=0.5, patience=5,
        verbose=True, min_lr=1e-7
    )
    
    # 恢复训练
    start_epoch = 0
    best_iou = 0.0
    
    if args.resume:
        if os.path.isfile(args.resume):
            logger.info(f"从 {args.resume} 恢复训练...")
            checkpoint = torch.load(args.resume, map_location=device, weights_only=False)
            model.load_state_dict(checkpoint['model_state_dict'])
            optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
            start_epoch = checkpoint['epoch'] + 1
            best_iou = checkpoint.get('best_iou', 0.0)
            logger.info(f"从 Epoch {start_epoch} 继续, 最佳IoU: {best_iou:.4f}")
        else:
            logger.warning(f"未找到模型文件 {args.resume},从头开始训练")
    
    # 早停
    patience_counter = 0
    
    # 训练循环
    logger.info("="*80)
    logger.info("开始训练")
    logger.info("="*80)
    
    for epoch in range(start_epoch, args.epochs):
        logger.info(f"\nEpoch {epoch+1}/{args.epochs}")
        logger.info("-" * 80)
        
        # 训练
        train_metrics = train_one_epoch(
            model, train_loader, criterion, optimizer, device,
            epoch+1, args.use_boundary_refinement
        )
        
        # 验证
        val_metrics = validate(
            model, val_loader, criterion, device,
            args.use_boundary_refinement
        )
        
        # 学习率调度
        scheduler.step(val_metrics['mIoU'])
        current_lr = optimizer.param_groups[0]['lr']
        
        # 日志记录
        logger.info(f"Train - Loss: {train_metrics['loss']:.4f}, mIoU: {train_metrics['mIoU']:.4f}")
        logger.info(f"Val   - Loss: {val_metrics['loss']:.4f}, mIoU: {val_metrics['mIoU']:.4f}")
        logger.info(f"Class IoUs: BG={val_metrics['class_ious'][0]:.4f}, "
                   f"Car={val_metrics['class_ious'][1]:.4f}, "
                   f"Truck={val_metrics['class_ious'][2]:.4f}, "
                   f"Bus={val_metrics['class_ious'][3]:.4f}")
        logger.info(f"学习率: {current_lr:.2e}")
        
        # TensorBoard记录
        writer.add_scalar('Loss/train', train_metrics['loss'], epoch)
        writer.add_scalar('Loss/val', val_metrics['loss'], epoch)
        writer.add_scalar('mIoU/train', train_metrics['mIoU'], epoch)
        writer.add_scalar('mIoU/val', val_metrics['mIoU'], epoch)
        writer.add_scalar('Learning_Rate', current_lr, epoch)
        
        for i, cls_name in enumerate(['Background', 'Car', 'Truck', 'Bus']):
            writer.add_scalar(f'IoU/{cls_name}', val_metrics['class_ious'][i], epoch)
        
        # 保存最佳模型
        if val_metrics['mIoU'] > best_iou:
            best_iou = val_metrics['mIoU']
            patience_counter = 0
            
            best_model_path = os.path.join(save_dir, 'best_model.pth')
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'best_iou': best_iou,
                'val_metrics': val_metrics
            }, best_model_path)
            
            logger.info(f"✓ 保存最佳模型, mIoU: {best_iou:.4f}")
        else:
            patience_counter += 1
        
        # 定期保存
        if (epoch + 1) % args.save_interval == 0:
            checkpoint_path = os.path.join(save_dir, f'epoch_{epoch+1}.pth')
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'best_iou': best_iou,
                'val_metrics': val_metrics
            }, checkpoint_path)
            logger.info(f"保存检查点: {checkpoint_path}")
        
        # 早停检查
        if patience_counter >= args.early_stopping_patience:
            logger.info(f"早停触发! {args.early_stopping_patience} 轮未提升")
            break
    
    # 训练结束
    logger.info("="*80)
    logger.info("训练完成!")
    logger.info(f"最佳验证 IoU: {best_iou:.4f}")
    logger.info(f"最佳模型保存在: {os.path.join(save_dir, 'best_model.pth')}")
    logger.info("="*80)
    
    writer.close()


if __name__ == '__main__':
    main()
