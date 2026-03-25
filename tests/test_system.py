"""
快速测试脚本: 验证数据加载和模型是否正常工作
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import torch
from src.data.dataset import get_dataloader
from src.models.unet_plusplus import UNetPlusPlus
from src.utils.losses import CombinedLoss, DeepSupervisionLoss, calculate_iou

print("="*60)
print("道路车辆分割系统 - 快速测试")
print("="*60)

# 测试数据加载
print("\n[1/4] 测试数据加载...")
try:
    train_loader = get_dataloader(
        data_dir='road_vehicle_pedestrian_det_datasets',
        masks_dir='outputs/masks',
        split='train',
        batch_size=2,
        img_size=(512, 512),
        num_workers=0
    )
    
    images, masks = next(iter(train_loader))
    print(f"✓ 数据加载成功!")
    print(f"  图像批次形状: {images.shape}")
    print(f"  掩码批次形状: {masks.shape}")
    print(f"  掩码唯一值: {torch.unique(masks).tolist()}")
except Exception as e:
    print(f"✗ 数据加载失败: {e}")
    sys.exit(1)

# 测试模型
print("\n[2/4] 测试模型构建...")
try:
    model = UNetPlusPlus(
        in_channels=3,
        num_classes=4,
        deep_supervision=True,
        encoder_name='vgg19',
        pretrained=True
    )
    
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    
    print(f"✓ 模型构建成功!")
    print(f"  总参数量: {total_params:,}")
    print(f"  可训练参数量: {trainable_params:,}")
except Exception as e:
    print(f"✗ 模型构建失败: {e}")
    sys.exit(1)

# 测试前向传播
print("\n[3/4] 测试前向传播...")
try:
    model.eval()
    with torch.no_grad():
        outputs = model(images)
    
    if isinstance(outputs, list):
        print(f"✓ 前向传播成功! (深度监督模式)")
        for i, out in enumerate(outputs):
            print(f"  输出层 {i+1} 形状: {out.shape}")
    else:
        print(f"✓ 前向传播成功!")
        print(f"  输出形状: {outputs.shape}")
except Exception as e:
    print(f"✗ 前向传播失败: {e}")
    sys.exit(1)

# 测试损失计算
print("\n[4/4] 测试损失和指标计算...")
try:
    base_loss = CombinedLoss()
    criterion = DeepSupervisionLoss(base_loss)
    
    loss = criterion(outputs, masks)
    print(f"✓ 损失计算成功!")
    print(f"  损失值: {loss.item():.4f}")
    
    # 计算IoU
    if isinstance(outputs, list):
        preds = torch.argmax(outputs[-1], dim=1)
    else:
        preds = torch.argmax(outputs, dim=1)
    
    iou_per_class, mean_iou = calculate_iou(preds, masks, num_classes=4)
    print(f"  平均IoU: {mean_iou.item():.4f}")
    print(f"  各类别IoU: {[f'{x:.4f}' for x in iou_per_class.tolist()]}")
except Exception as e:
    print(f"✗ 损失计算失败: {e}")
    sys.exit(1)

print("\n" + "="*60)
print("✓ 所有测试通过! 系统准备就绪")
print("="*60)
print("\n下一步操作:")
print("1. 开始训练 (CPU): python3 train.py --batch_size 4 --epochs 50 --use_gpu False")
print("2. 开始训练 (GPU): python3 train.py --batch_size 16 --epochs 100 --use_gpu True")
print("3. 模型推理: python3 inference.py --model_path outputs/checkpoints/best_model.pth")
print("="*60)
