#!/usr/bin/env python3
"""检查所有模型的IoU指标"""

import torch
import os
import glob

model_dir = 'outputs/checkpoints'
model_files = sorted(glob.glob(os.path.join(model_dir, '*.pth')))

print("=" * 70)
print("所有模型文件的IoU指标对比")
print("=" * 70)
print()

results = []

for model_file in model_files:
    model_name = os.path.basename(model_file)
    file_size = os.path.getsize(model_file) / (1024*1024)
    
    try:
        checkpoint = torch.load(model_file, map_location='cpu', weights_only=False)
        
        if isinstance(checkpoint, dict):
            epoch = checkpoint.get('epoch', 'N/A')
            best_iou = checkpoint.get('best_iou', None)
            
            result = {
                'name': model_name,
                'size': file_size,
                'epoch': epoch,
                'iou': best_iou
            }
            results.append(result)
            
            print(f"📦 {model_name}")
            print(f"   文件大小: {file_size:.1f} MB")
            print(f"   训练轮数: Epoch {epoch}")
            
            if best_iou is not None:
                print(f"   ✅ 最佳IoU: {best_iou:.4f} ({best_iou*100:.2f}%)")
            else:
                print(f"   ⚠️  未找到best_iou字段")
        else:
            print(f"📦 {model_name}")
            print(f"   文件大小: {file_size:.1f} MB")
            print(f"   ⚠️  checkpoint类型: {type(checkpoint).__name__}")
            
    except Exception as e:
        print(f"📦 {model_name}")
        print(f"   ❌ 加载失败: {e}")
    
    print()

print("=" * 70)
print("📊 IoU排名 (从高到低)")
print("=" * 70)
results_with_iou = [r for r in results if r['iou'] is not None]
results_with_iou.sort(key=lambda x: x['iou'], reverse=True)

for i, r in enumerate(results_with_iou, 1):
    print(f"{i}. {r['name']}")
    print(f"   IoU: {r['iou']*100:.2f}% | Epoch {r['epoch']} | {r['size']:.1f} MB")

print()
print("=" * 70)
