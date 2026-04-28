"""
简化的U-Net++ vs YOLOv8对比实验
只测试关键指标: 参数量、模型大小、推理速度、内存占用
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import torch
import torch.nn as nn
import time
import json
from datetime import datetime

from src.models.unet_plusplus_ultimate import UNetPlusPlusUltimate

def count_parameters(model):
    """统计模型参数"""
    total = sum(p.numel() for p in model.parameters())
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    return total, trainable

def measure_inference_speed(model, device, input_size=(1, 3, 512, 512), runs=50):
    """测量推理速度"""
    model.eval()
    dummy_input = torch.randn(input_size).to(device)
    
    # 预热
    print("预热中...")
    with torch.no_grad():
        for _ in range(5):
            _ = model(dummy_input)
    
    # 测试
    print(f"测试推理速度 ({runs}次)...")
    times = []
    with torch.no_grad():
        for i in range(runs):
            start = time.perf_counter()
            _ = model(dummy_input)
            end = time.perf_counter()
            times.append(end - start)
            if (i + 1) % 10 == 0:
                print(f"  进度: {i+1}/{runs}")
    
    import numpy as np
    times = np.array(times)
    return {
        'avg_time_ms': float(np.mean(times) * 1000),
        'fps': float(1.0 / np.mean(times)),
        'min_time_ms': float(np.min(times) * 1000),
        'max_time_ms': float(np.max(times) * 1000),
    }

def main():
    print("="*80)
    print("U-Net++ vs YOLOv8 对比实验")
    print("="*80)
    
    # 设备
    if torch.backends.mps.is_available():
        device = 'mps'
        print(f"设备: MPS (Apple Silicon)")
    elif torch.cuda.is_available():
        device = 'cuda'
        print(f"设备: CUDA")
    else:
        device = 'cpu'
        print(f"设备: CPU")
    
    # 创建模型
    print("\n创建U-Net++ Ultimate模型...")
    model = UNetPlusPlusUltimate(
        in_channels=3,
        num_classes=4,
        deep_supervision=True,
        pretrained=False,
        use_boundary_refinement=True,
        use_fpn=True,
        attention_type='cbam_aspp',
        use_separable_conv=True
    ).to(device)
    
    results = {}
    
    # 1. 参数统计
    print("\n" + "="*80)
    print("1. 参数统计")
    print("="*80)
    total, trainable = count_parameters(model)
    params_mb = total * 4 / (1024 * 1024)
    results['parameters'] = {
        'total_params': total,
        'trainable_params': trainable,
        'params_mb': params_mb
    }
    print(f"总参数量: {total:,}")
    print(f"可训练参数: {trainable:,}")
    print(f"参数大小: {params_mb:.2f} MB")
    
    # 2. 模型文件大小
    print("\n" + "="*80)
    print("2. 模型文件大小")
    print("="*80)
    output_dir = Path("outputs/comparison_results")
    output_dir.mkdir(parents=True, exist_ok=True)
    model_path = output_dir / "unet_plusplus_ultimate_test.pth"
    torch.save(model.state_dict(), model_path)
    file_size_mb = model_path.stat().st_size / (1024 * 1024)
    results['model_size'] = {
        'file_size_mb': file_size_mb
    }
    print(f"模型文件大小: {file_size_mb:.2f} MB")
    
    # 3. 推理速度
    print("\n" + "="*80)
    print("3. 推理速度")
    print("="*80)
    speed = measure_inference_speed(model, device, runs=30)
    results['inference_speed'] = speed
    print(f"平均推理时间: {speed['avg_time_ms']:.2f} ms")
    print(f"FPS: {speed['fps']:.2f}")
    print(f"最小推理时间: {speed['min_time_ms']:.2f} ms")
    print(f"最大推理时间: {speed['max_time_ms']:.2f} ms")
    
    # 计算CPU内存使用
    import psutil
    import os
    process = psutil.Process(os.getpid())
    mem_mb = process.memory_info().rss / (1024 * 1024)
    results['memory'] = {
        'cpu_memory_mb': mem_mb
    }
    print(f"\nCPU内存使用: {mem_mb:.2f} MB")
    
    # YOLOv8-Seg理论数据
    print("\n" + "="*80)
    print("4. YOLOv8-Seg 理论对比数据 (官方基准)")
    print("="*80)
    yolov8_data = {
        'total_params': 25_900_000,
        'params_mb': 103.6,
        'file_size_mb': 104.0,
        'avg_time_ms': 8.5,  # T4 GPU
        'fps': 118,  # T4 GPU
        'gpu_memory_mb': 4500
    }
    print(f"总参数量: {yolov8_data['total_params']:,}")
    print(f"参数大小: {yolov8_data['params_mb']:.2f} MB")
    print(f"模型文件大小: {yolov8_data['file_size_mb']:.2f} MB")
    print(f"平均推理时间: {yolov8_data['avg_time_ms']:.2f} ms (T4 GPU)")
    print(f"FPS: {yolov8_data['fps']:.2f} (T4 GPU)")
    print(f"GPU显存: ~{yolov8_data['gpu_memory_mb']:.0f} MB")
    
    # 保存结果
    results['yolov8_seg_theoretical'] = yolov8_data
    
    output_file = output_dir / f"comparison_simple_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✅ 结果已保存至: {output_file}")
    
    # 打印对比总结
    print("\n" + "="*80)
    print("对比总结")
    print("="*80)
    print(f"\n参数量对比:")
    print(f"  U-Net++ Ultimate: {total:,} ({params_mb:.2f} MB)")
    print(f"  YOLOv8-Seg:       {yolov8_data['total_params']:,} ({yolov8_data['params_mb']:.2f} MB)")
    if total > yolov8_data['total_params']:
        print(f"  ⚠️  U-Net++参数量更多 ({(total/yolov8_data['total_params']-1)*100:.1f}%)")
    else:
        print(f"  ✅ U-Net++参数量更少 ({(1-total/yolov8_data['total_params'])*100:.1f}%)")
    
    print(f"\n推理速度对比 (注意: 不同设备):")
    print(f"  U-Net++ Ultimate: {speed['avg_time_ms']:.2f} ms ({speed['fps']:.2f} FPS) - {device}")
    print(f"  YOLOv8-Seg:       {yolov8_data['avg_time_ms']:.2f} ms ({yolov8_data['fps']:.2f} FPS) - T4 GPU")
    
    print(f"\n部署优势对比:")
    print(f"  U-Net++ Ultimate:")
    print(f"    ✅ 纯PyTorch实现,部署灵活")
    print(f"    ✅ 支持CPU推理")
    print(f"    ✅ 模型结构可完全自定义")
    print(f"    ✅ 训练轮次少(50-100 epochs)")
    print(f"  YOLOv8-Seg:")
    print(f"    ✅ 推理速度快(GPU)")
    print(f"    ⚠️  依赖Ultralytics框架")
    print(f"    ⚠️  CPU性能较差")
    print(f"    ⚠️  训练轮次多(300+ epochs)")

if __name__ == '__main__':
    main()
