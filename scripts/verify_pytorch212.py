#!/usr/bin/env python3
"""
PyTorch 2.1.2 兼容性验证脚本
验证所有关键特性在AutoDL环境中可用
"""

import sys

def check_pytorch_version():
    """检查PyTorch版本"""
    try:
        import torch
        import torchvision
        
        print("="*80)
        print("PyTorch 版本检查")
        print("="*80)
        print(f"PyTorch版本:     {torch.__version__}")
        print(f"TorchVision版本: {torchvision.__version__}")
        print(f"Python版本:      {sys.version.split()[0]}")
        
        # 检查是否是2.x版本
        major_version = int(torch.__version__.split('.')[0])
        if major_version >= 2:
            print("✅ PyTorch 2.x 版本 - 支持最新特性")
        else:
            print("⚠️  PyTorch 1.x 版本 - 建议升级到2.x")
        
        return True
    except ImportError as e:
        print(f"❌ PyTorch导入失败: {e}")
        return False

def check_cuda():
    """检查CUDA支持"""
    print("\n" + "="*80)
    print("CUDA 检查")
    print("="*80)
    
    import torch
    
    if torch.cuda.is_available():
        print(f"✅ CUDA可用: {torch.version.cuda}")
        print(f"✅ GPU设备: {torch.cuda.get_device_name(0)}")
        print(f"✅ GPU显存: {torch.cuda.get_device_properties(0).total_memory/1024**3:.1f} GB")
        print(f"✅ GPU数量: {torch.cuda.device_count()}")
        return True
    else:
        print("⚠️  CUDA不可用 - 将使用CPU训练")
        return False

def check_resnet101_api():
    """检查ResNet-101新API"""
    print("\n" + "="*80)
    print("ResNet-101 新API检查")
    print("="*80)
    
    try:
        from torchvision.models import resnet101, ResNet101_Weights
        print("✅ ResNet101_Weights.IMAGENET1K_V1 可用")
        
        # 测试加载模型
        model = resnet101(weights=ResNet101_Weights.IMAGENET1K_V1)
        print("✅ ResNet-101 ImageNet预训练权重加载成功")
        
        # 统计参数
        total_params = sum(p.numel() for p in model.parameters())
        print(f"✅ 模型参数量: {total_params:,} ({total_params/1e6:.1f}M)")
        
        return True
    except ImportError as e:
        print(f"❌ ResNet-101 API不可用: {e}")
        print("   需要TorchVision 0.13+ (PyTorch 1.12+)")
        return False

def check_attention_mechanism():
    """检查注意力机制支持"""
    print("\n" + "="*80)
    print("注意力机制支持检查")
    print("="*80)
    
    import torch
    import torch.nn.functional as F
    
    # 检查scaled_dot_product_attention
    try:
        if hasattr(F, 'scaled_dot_product_attention'):
            print("✅ F.scaled_dot_product_attention 可用 (高效注意力)")
            
            # 测试
            q = torch.randn(2, 8, 512, 64)
            k = torch.randn(2, 8, 512, 64)
            v = torch.randn(2, 8, 512, 64)
            
            output = F.scaled_dot_product_attention(q, k, v)
            print(f"✅ 注意力机制测试通过: {output.shape}")
            return True
        else:
            print("⚠️  F.scaled_dot_product_attention 不可用")
            print("   将使用传统注意力实现")
            return False
    except Exception as e:
        print(f"❌ 注意力机制检查失败: {e}")
        return False

def check_torch_compile():
    """检查torch.compile支持"""
    print("\n" + "="*80)
    print("torch.compile 优化检查")
    print("="*80)
    
    import torch
    
    try:
        if hasattr(torch, 'compile'):
            print("✅ torch.compile 可用 (模型优化)")
            
            # 测试简单模型
            class SimpleModel(torch.nn.Module):
                def __init__(self):
                    super().__init__()
                    self.conv = torch.nn.Conv2d(3, 64, 3, padding=1)
                
                def forward(self, x):
                    return self.conv(x)
            
            model = SimpleModel()
            compiled_model = torch.compile(model)
            x = torch.randn(1, 3, 256, 256)
            output = compiled_model(x)
            
            print(f"✅ torch.compile 测试通过: {output.shape}")
            print("   可用于加速训练 (提升10-20%)")
            return True
        else:
            print("⚠️  torch.compile 不可用 (需要PyTorch 2.0+)")
            return False
    except Exception as e:
        print(f"⚠️  torch.compile 检查失败: {e}")
        print("   不影响训练,但无法使用编译优化")
        return False

def check_mixed_precision():
    """检查混合精度训练支持"""
    print("\n" + "="*80)
    print("混合精度训练检查")
    print("="*80)
    
    import torch
    
    try:
        if torch.cuda.is_available():
            # 检查FP16支持
            device = torch.device('cuda')
            x = torch.randn(10, 10, dtype=torch.float16, device=device)
            y = torch.randn(10, 10, dtype=torch.float16, device=device)
            z = torch.matmul(x, y)
            
            print("✅ FP16混合精度训练可用")
            
            # 检查Automatic Mixed Precision
            scaler = torch.cuda.amp.GradScaler()
            print("✅ Automatic Mixed Precision (AMP) 可用")
            print("   可节省显存20-30%, 加速训练10-15%")
            return True
        else:
            print("⚠️  GPU不可用,无法测试混合精度")
            return False
    except Exception as e:
        print(f"❌ 混合精度检查失败: {e}")
        return False

def check_dependencies():
    """检查其他依赖"""
    print("\n" + "="*80)
    print("其他依赖检查")
    print("="*80)
    
    packages = {
        'numpy': '数据处理',
        'PIL': '图像处理',
        'tqdm': '进度条',
        'albumentations': '数据增强',
        'cv2': 'OpenCV',
        'matplotlib': '可视化',
        'tensorboard': '训练监控'
    }
    
    all_ok = True
    for pkg, desc in packages.items():
        try:
            module = __import__(pkg)
            version = getattr(module, '__version__', '未知')
            print(f"✅ {pkg:15} {version:10} - {desc}")
        except ImportError:
            print(f"❌ {pkg:15} 未安装   - {desc}")
            all_ok = False
    
    return all_ok

def main():
    """主函数"""
    print("\n" + "="*80)
    print("AutoDL PyTorch 2.1.2 兼容性验证")
    print("="*80)
    
    results = {
        'PyTorch版本': check_pytorch_version(),
        'CUDA支持': check_cuda(),
        'ResNet-101 API': check_resnet101_api(),
        '注意力机制': check_attention_mechanism(),
        'torch.compile': check_torch_compile(),
        '混合精度': check_mixed_precision(),
        '其他依赖': check_dependencies()
    }
    
    print("\n" + "="*80)
    print("验证结果总结")
    print("="*80)
    
    for name, result in results.items():
        status = "✅ 通过" if result else "⚠️  警告"
        print(f"{name:20} {status}")
    
    print("\n" + "="*80)
    
    if all(results.values()):
        print("✅ 所有检查通过! 环境完全兼容,可以开始训练")
    else:
        print("⚠️  部分检查未通过,但不影响核心训练功能")
        print("   建议安装缺失的依赖: pip install albumentations opencv-python matplotlib tensorboard")
    
    print("="*80 + "\n")
    
    # 性能建议
    print("💡 性能优化建议:")
    print("   1. 使用 torch.compile(model) 编译模型 (加速10-20%)")
    print("   2. 启用混合精度训练 (节省显存20-30%)")
    print("   3. 使用 F.scaled_dot_product_attention (高效注意力)")
    print("   4. Batch Size: RTX 3090推荐6-8, V100推荐4-6")
    print("")

if __name__ == '__main__':
    main()
