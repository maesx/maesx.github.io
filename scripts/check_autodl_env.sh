#!/bin/bash
# AutoDL环境检查和依赖安装脚本

echo "=========================================="
echo "AutoDL环境检查"
echo "=========================================="
echo ""

# 检查Python版本
echo "1. 检查Python版本..."
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "   Python版本: $python_version"

# 提取主版本号和次版本号
major=$(echo $python_version | cut -d. -f1)
minor=$(echo $python_version | cut -d. -f2)

# 数值比较版本号
if [ "$major" -lt 3 ] || ([ "$major" -eq 3 ] && [ "$minor" -lt 8 ]); then
    echo "   ❌ Python版本过低,需要3.8+ (当前: $python_version)"
    exit 1
else
    echo "   ✅ Python版本符合要求 (Python $python_version >= 3.8)"
fi
echo ""

# 检查PyTorch和CUDA
echo "2. 检查PyTorch和GPU..."
python << 'EOF'
import torch
import torchvision
print(f"   PyTorch版本: {torch.__version__}")
print(f"   TorchVision版本: {torchvision.__version__}")

if torch.cuda.is_available():
    print(f"   ✅ CUDA可用: {torch.version.cuda}")
    print(f"   ✅ GPU设备: {torch.cuda.get_device_name(0)}")
    print(f"   ✅ GPU显存: {torch.cuda.get_device_properties(0).total_memory/1024**3:.1f} GB")
    
    # 检查是否支持新特性
    if torch.__version__.startswith('2.'):
        print(f"   ✅ PyTorch 2.x 新特性: torch.compile, 优化注意力机制")
else:
    print("   ⚠️  CUDA不可用,将使用CPU训练(速度慢)")
EOF
echo ""

# 检查已安装的包
echo "3. 检查已安装的包..."
packages=("numpy" "pillow" "tqdm" "matplotlib" "tensorboard" "albumentations" "cv2")

for pkg in "${packages[@]}"; do
    if python -c "import $pkg" 2>/dev/null; then
        version=$(python -c "import $pkg; print($pkg.__version__)" 2>/dev/null || echo "未知")
        echo "   ✅ $pkg: $version"
    else
        echo "   ❌ $pkg: 未安装"
    fi
done
echo ""

# 安装缺失的依赖
echo "4. 安装缺失的依赖..."
read -p "是否安装缺失的依赖? (y/n): " install_deps

if [ "$install_deps" = "y" ] || [ "$install_deps" = "Y" ]; then
    echo "   安装核心依赖..."
    pip install -q albumentations==1.3.0 opencv-python==4.8.0.76
    pip install -q matplotlib==3.7.1 tensorboard==2.13.0
    pip install -q Pillow==9.5.0 tqdm==4.65.0
    
    echo "   ✅ 依赖安装完成"
else
    echo "   跳过依赖安装"
fi
echo ""

# 检查磁盘空间
echo "5. 检查磁盘空间..."
df -h /root | tail -1 | awk '{print "   根分区可用空间: "$4}'
df -h /root/autodl-tmp 2>/dev/null | tail -1 | awk '{print "   数据盘可用空间: "$4}' || echo "   ⚠️  数据盘未挂载"
echo ""

# 环境总结
echo "=========================================="
echo "环境检查完成"
echo "=========================================="
echo ""
echo "✅ 准备就绪! 可以开始训练"
echo ""
echo "启动训练命令:"
echo "  方式1: bash start_training.sh"
echo "  方式2: bash scripts/train_ultimate.sh"
echo "  方式3: python src/training/train_ultimate.py --use_gpu True"
echo ""
