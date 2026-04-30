"""
损失函数和评估指标
"""
from typing import List, Optional, Tuple

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F


class FocalLoss(nn.Module):
    """Focal Loss - 专注于难分类样本"""
    
    def __init__(self, alpha: torch.Tensor = None, gamma: float = 2.0, smooth: float = 1e-6) -> None:
        """
        Args:
            alpha: 类别权重 [C]
            gamma: 聚焦参数，越大越关注难样本
            smooth: 平滑项
        """
        super(FocalLoss, self).__init__()
        self.gamma = gamma
        self.smooth = smooth
        if alpha is not None:
            self.register_buffer('alpha', alpha)
        else:
            self.alpha = None
    
    def forward(self, pred: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
        """
        Args:
            pred: 预测结果 [B, C, H, W]
            target: 真实标签 [B, H, W]
        """
        device = pred.device
        
        # 获取概率 - 使用 log_softmax 避免 MPS 问题
        log_pred_prob = F.log_softmax(pred, dim=1)  # [B, C, H, W]
        pred_prob = torch.exp(log_pred_prob)
        
        # 转为one-hot
        num_classes = pred.size(1)
        target_long = target.long()
        target_one_hot = F.one_hot(target_long, num_classes=num_classes)
        target_one_hot = target_one_hot.permute(0, 3, 1, 2).float()  # [B, C, H, W]
        
        # 获取正确类别的概率
        pt = (pred_prob * target_one_hot).sum(dim=1)  # [B, H, W]
        
        # 计算 focal weight
        focal_weight = (1 - pt) ** self.gamma
        
        # 计算 CrossEntropy - 使用 log_softmax 的结果
        ce_loss = F.nll_loss(log_pred_prob, target_long, reduction='none')  # [B, H, W]
        
        # 应用 focal weight
        focal_loss = focal_weight * ce_loss
        
        # 应用类别权重 - 确保alpha在正确的设备上
        if self.alpha is not None:
            # 将alpha移到正确的设备
            alpha_device = self.alpha.to(device)
            # 根据目标类别获取权重
            alpha_t = alpha_device[target_long]  # [B, H, W]
            focal_loss = alpha_t * focal_loss
        
        return focal_loss.mean()


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
        # 确保target是long类型
        target = target.long()
        
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


class BoundaryLoss(nn.Module):
    """边界损失函数
    
    用于增强分割边界的准确性
    """
    
    def __init__(self, theta0: float = 3.0, theta: float = 5.0) -> None:
        """
        Args:
            theta0: 边界宽度参数
            theta: 损失缩放参数
        """
        super(BoundaryLoss, self).__init__()
        self.theta0 = theta0
        self.theta = theta
    
    def forward(
        self,
        pred_boundary: torch.Tensor,
        target_boundary: torch.Tensor
    ) -> torch.Tensor:
        """
        Args:
            pred_boundary: 预测的边界图 [B, 1, H, W]
            target_boundary: 真实的边界图 [B, 1, H, W]
        
        Returns:
            boundary_loss: 边界损失
        """
        # 使用 BCE 损失计算边界误差
        bce_loss = F.binary_cross_entropy_with_logits(
            pred_boundary, 
            target_boundary.float(),
            reduction='mean'
        )
        
        return bce_loss


class CombinedLoss(nn.Module):
    """组合损失: CrossEntropy + Dice + Focal Loss
    
    注意: 在MPS设备上，CrossEntropyLoss有已知的bus error问题，
    因此需要在CPU上计算后再移回原设备
    """

    def __init__(
        self, 
        weight_ce: float = 1.0, 
        weight_dice: float = 1.0,
        weight_focal: float = 1.0,
        class_weights: Optional[torch.Tensor] = None,
        focal_gamma: float = 2.0
    ) -> None:
        """
        Args:
            weight_ce: CrossEntropy 损失权重
            weight_dice: Dice 损失权重
            weight_focal: Focal Loss 权重
            class_weights: 类别权重 [C]
            focal_gamma: Focal Loss gamma参数
        """
        super(CombinedLoss, self).__init__()
        self.weight_ce = weight_ce
        self.weight_dice = weight_dice
        self.weight_focal = weight_focal
        
        # 存储类别权重（不注册为buffer，避免设备问题）
        self.class_weights_tensor = class_weights
        
        # CrossEntropyLoss - 不在这里指定权重，在forward中处理
        self.ce_loss = nn.CrossEntropyLoss(weight=None)
        self.dice_loss = DiceLoss()
        self.focal_loss = FocalLoss(alpha=class_weights, gamma=focal_gamma)

    def forward(self, pred: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
        """
        Args:
            pred: 预测结果 [B, C, H, W]
            target: 真实标签 [B, H, W]
        """
        device = pred.device
        
        # 如果有类别权重，在forward中动态创建CE损失（确保权重在正确设备上）
        if self.class_weights_tensor is not None:
            weights = self.class_weights_tensor.to(device)
            ce_loss_fn = nn.CrossEntropyLoss(weight=weights)
            ce = ce_loss_fn(pred, target)
        else:
            ce = self.ce_loss(pred, target)
        
        dice = self.dice_loss(pred, target)
        focal = self.focal_loss(pred, target)
        
        return self.weight_ce * ce + self.weight_dice * dice + self.weight_focal * focal


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


def calculate_precision_recall(
    pred: torch.Tensor,
    target: torch.Tensor,
    num_classes: int,
    smooth: float = 1e-6
) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """
    计算每个类别的Precision, Recall和F1-Score
    
    Args:
        pred: 预测结果 [B, H, W]
        target: 真实标签 [B, H, W]
        num_classes: 类别数
        smooth: 平滑项
        
    Returns:
        precision_per_class: 每个类别的Precision
        recall_per_class: 每个类别的Recall
        f1_per_class: 每个类别的F1-Score
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
    
    # 计算TP, FP, FN
    # TP: 预测为正类且真实为正类
    # FP: 预测为正类但真实为负类
    # FN: 预测为负类但真实为正类
    tp = torch.sum(pred_one_hot * target_one_hot, dim=(2, 3))  # [B, C]
    fp = torch.sum(pred_one_hot * (1 - target_one_hot), dim=(2, 3))
    fn = torch.sum((1 - pred_one_hot) * target_one_hot, dim=(2, 3))
    
    # 计算Precision和Recall
    precision_per_class = (tp + smooth) / (tp + fp + smooth)  # [B, C]
    recall_per_class = (tp + smooth) / (tp + fn + smooth)     # [B, C]
    
    # 计算F1-Score
    f1_per_class = 2 * precision_per_class * recall_per_class / (precision_per_class + recall_per_class + smooth)
    
    # 取平均
    precision_mean = precision_per_class.mean(dim=0)  # [C]
    recall_mean = recall_per_class.mean(dim=0)        # [C]
    f1_mean = f1_per_class.mean(dim=0)                # [C]
    
    return precision_mean, recall_mean, f1_mean


def calculate_metrics(
    pred: torch.Tensor,
    target: torch.Tensor,
    num_classes: int,
    smooth: float = 1e-6
) -> dict:
    """
    计算所有评估指标
    
    Args:
        pred: 预测结果 [B, H, W]
        target: 真实标签 [B, H, W]
        num_classes: 类别数
        smooth: 平滑项
        
    Returns:
        包含所有指标的字典
    """
    # 计算IoU
    iou_per_class, mean_iou = calculate_iou(pred, target, num_classes, smooth)
    
    # 计算Precision, Recall, F1
    precision, recall, f1 = calculate_precision_recall(pred, target, num_classes, smooth)
    
    # 计算像素准确率
    pixel_acc = calculate_pixel_accuracy(pred, target)
    
    # 排除背景的平均值
    mean_precision = precision[1:].mean()
    mean_recall = recall[1:].mean()
    mean_f1 = f1[1:].mean()
    
    return {
        'iou_per_class': iou_per_class,
        'mean_iou': mean_iou,
        'precision_per_class': precision,
        'recall_per_class': recall,
        'f1_per_class': f1,
        'mean_precision': mean_precision,
        'mean_recall': mean_recall,
        'mean_f1': mean_f1,
        'pixel_accuracy': pixel_acc
    }


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
