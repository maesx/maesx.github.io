"""
损失函数和评估指标
"""
from typing import List, Optional, Tuple

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F


class DiceLoss(nn.Module):
    """Dice损失函数"""

    def __init__(self, smooth: float = 1.0) -> None:
        super(DiceLoss, self).__init__()
        self.smooth = smooth

    def forward(self, pred: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
        """
        Args:
            pred: 预测结果 [B, C, H, W]
            target: 真实标签 [B, H, W]
        """
        # 转为one-hot编码
        num_classes = pred.size(1)
        target_one_hot = F.one_hot(target, num_classes=num_classes)
        target_one_hot = target_one_hot.permute(0, 3, 1, 2).float()
        
        # softmax
        pred = F.softmax(pred, dim=1)
        
        # 计算dice系数
        intersection = torch.sum(pred * target_one_hot, dim=(2, 3))
        cardinality = torch.sum(pred + target_one_hot, dim=(2, 3))
        
        dice_score = (2.0 * intersection + self.smooth) / (cardinality + self.smooth)
        
        # 平均dice损失
        dice_loss = 1.0 - dice_score.mean()
        
        return dice_loss


class CombinedLoss(nn.Module):
    """组合损失: CrossEntropy + Dice"""

    def __init__(
        self, 
        weight_ce: float = 1.0, 
        weight_dice: float = 1.0
    ) -> None:
        """
        Args:
            weight_ce: CrossEntropy 损失权重
            weight_dice: Dice 损失权重
        """
        super(CombinedLoss, self).__init__()
        self.weight_ce = weight_ce
        self.weight_dice = weight_dice
        self.ce_loss = nn.CrossEntropyLoss()
        self.dice_loss = DiceLoss()

    def forward(self, pred: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
        """
        Args:
            pred: 预测结果 [B, C, H, W]
            target: 真实标签 [B, H, W]
        """
        ce = self.ce_loss(pred, target)
        dice = self.dice_loss(pred, target)
        
        return self.weight_ce * ce + self.weight_dice * dice


class DeepSupervisionLoss(nn.Module):
    """深度监督损失"""

    def __init__(self, base_loss: nn.Module) -> None:
        super(DeepSupervisionLoss, self).__init__()
        self.base_loss = base_loss
        # 不同层级的权重
        self.weights: List[float] = [0.5, 0.75, 1.0, 1.25]

    def forward(self, preds: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
        """
        Args:
            preds: 预测结果列表 [pred1, pred2, pred3, pred4]
            target: 真实标签 [B, H, W]
        """
        if not isinstance(preds, list):
            return self.base_loss(preds, target)
        
        total_loss = 0.0
        for i, pred in enumerate(preds):
            # 确保target是long类型
            target_long = target.long()
            
            # 调整target尺寸以匹配pred
            if pred.size(2) != target_long.size(1):
                target_resized = F.interpolate(
                    target_long.unsqueeze(1).float(), 
                    size=pred.size()[2:], 
                    mode='nearest'
                ).squeeze(1).long()
            else:
                target_resized = target_long
            
            loss = self.base_loss(pred, target_resized)
            total_loss += self.weights[i] * loss
        
        return total_loss / sum(self.weights)


def calculate_iou(
    pred: torch.Tensor,
    target: torch.Tensor,
    num_classes: int,
    smooth: float = 1e-6
) -> Tuple[torch.Tensor, torch.Tensor]:
    """
    计算IoU(Intersection over Union)
    
    Args:
        pred: 预测结果 [B, H, W]
        target: 真实标签 [B, H, W]
        num_classes: 类别数
        smooth: 平滑项
        
    Returns:
        iou_per_class: 每个类别的IoU
        mean_iou: 平均IoU
    """
    # 确保是long类型
    pred = pred.long()
    target = target.long()
    
    # 转为one-hot编码
    pred_one_hot = F.one_hot(pred, num_classes=num_classes)
    target_one_hot = F.one_hot(target, num_classes=num_classes)
    
    # 转换维度 [B, H, W, C] -> [B, C, H, W]
    pred_one_hot = pred_one_hot.permute(0, 3, 1, 2).float()
    target_one_hot = target_one_hot.permute(0, 3, 1, 2).float()
    
    # 计算交集和并集
    intersection = torch.sum(pred_one_hot * target_one_hot, dim=(2, 3))
    union = torch.sum(pred_one_hot + target_one_hot, dim=(2, 3)) - intersection
    
    # 计算IoU
    iou_per_class = (intersection + smooth) / (union + smooth)
    
    # 排除背景类的平均IoU
    iou_per_class_mean = iou_per_class.mean(dim=0)
    mean_iou = iou_per_class_mean[1:].mean()  # 排除背景
    
    return iou_per_class_mean, mean_iou


def calculate_pixel_accuracy(pred: torch.Tensor, target: torch.Tensor) -> float:
    """
    计算像素准确率
    
    Args:
        pred: 预测结果 [B, H, W]
        target: 真实标签 [B, H, W]
    """
    correct = (pred == target).sum().item()
    total = target.numel()
    
    return correct / total


if __name__ == '__main__':
    # 测试损失函数
    print("测试损失函数...")
    
    # 创建模拟数据
    pred = torch.randn(2, 4, 256, 256)  # [B, C, H, W]
    target = torch.randint(0, 4, (2, 256, 256))  # [B, H, W]
    
    # 测试组合损失
    criterion = CombinedLoss()
    loss = criterion(pred, target)
    print(f"组合损失: {loss.item():.4f}")
    
    # 测试深度监督损失
    preds = [torch.randn(2, 4, 256, 256) for _ in range(4)]
    ds_loss = DeepSupervisionLoss(CombinedLoss())
    loss = ds_loss(preds, target)
    print(f"深度监督损失: {loss.item():.4f}")
    
    # 测试IoU计算
    pred_argmax = torch.argmax(pred, dim=1)
    iou_per_class, mean_iou = calculate_iou(pred_argmax, target, num_classes=4)
    print(f"\n每个类别的IoU: {iou_per_class}")
    print(f"平均IoU(排除背景): {mean_iou:.4f}")
