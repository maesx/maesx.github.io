#!/bin/bash
# 打包训练代码和数据 - 用于AutoDL上传

echo "=========================================="
echo "AutoDL训练包准备"
echo "=========================================="
echo ""

# 设置项目根目录
PROJECT_ROOT="/Users/sux/IdeaProjects/maesx.github.io"
cd "$PROJECT_ROOT"

# 创建临时目录
TEMP_DIR="autodl_package"
mkdir -p "$TEMP_DIR"

echo "1. 复制代码文件..."
cp -r src "$TEMP_DIR/"
cp -r scripts "$TEMP_DIR/"

echo "2. 复制训练数据..."
echo "   - 训练图像..."
cp -r road_vehicle_pedestrian_det_datasets/images "$TEMP_DIR/images"

echo "   - 训练掩码..."
mkdir -p "$TEMP_DIR/masks"
cp -r outputs/masks_car/train "$TEMP_DIR/masks/"
cp -r outputs/masks_car/val "$TEMP_DIR/masks/"

echo "3. 创建依赖文件..."
cat > "$TEMP_DIR/requirements.txt" << 'EOF'
torch==2.0.1
torchvision==0.15.2
tensorboard==2.13.0
Pillow==9.5.0
numpy==1.24.3
tqdm==4.65.0
EOF

echo "4. 创建AutoDL启动脚本..."
cat > "$TEMP_DIR/start_training.sh" << 'EOF'
#!/bin/bash
# AutoDL训练启动脚本

echo "=========================================="
echo "AutoDL训练环境检查"
echo "=========================================="

# 检查GPU
python -c "import torch; print(f'GPU: {torch.cuda.get_device_name(0)}'); print(f'显存: {torch.cuda.get_device_properties(0).total_memory/1024**3:.1f}GB')"

# 安装依赖
echo ""
echo "安装依赖..."
pip install -q -r requirements.txt

# 设置Python路径
export PYTHONPATH=/root:$PYTHONPATH

echo ""
echo "=========================================="
echo "选择训练方案:"
echo "  1. VGG19快速验证 (5小时, ¥7.5, mIoU:60-65%)"
echo "  2. VGG19激进训练 (5小时, ¥7.5, mIoU:66-70%)"
echo "  3. ResNet-101标准 (15小时, ¥22.5, mIoU:70-75%)"
echo "  4. ResNet-101极致 (15小时, ¥22.5, mIoU:75-80%)"
echo "=========================================="
read -p "请选择 (1-4): " choice

case $choice in
    1)
        echo "启动VGG19快速验证..."
        bash scripts/train_optimized.sh
        ;;
    2)
        echo "启动VGG19激进训练..."
        python src/training/train_optimized.py \
            --use_gpu True \
            --attention cbam_aspp \
            --epochs 80 \
            --batch_size 8 \
            --use_aggressive_weights \
            --lr 2e-4
        ;;
    3)
        echo "启动ResNet-101标准训练..."
        python src/training/train_ultimate.py \
            --use_gpu True \
            --use_fpn True \
            --attention cbam_aspp \
            --use_boundary_refinement False \
            --use_separable_conv True \
            --use_aggressive_weights True \
            --epochs 100 \
            --batch_size 6 \
            --lr 1e-4
        ;;
    4)
        echo "启动ResNet-101极致训练..."
        bash scripts/train_ultimate.sh
        ;;
    *)
        echo "无效选择,启动VGG19激进训练..."
        bash scripts/train_optimized.sh
        ;;
esac
EOF

chmod +x "$TEMP_DIR/start_training.sh"

echo "5. 创建README..."
cat > "$TEMP_DIR/README_AutoDL.md" << 'EOF'
# AutoDL训练指南

## 快速开始 (5步)

### 1. 创建实例
- 访问: https://www.autodl.com/
- 选择镜像: PyTorch 2.0.1 + Python 3.9
- 选择GPU: RTX 3090 (¥1.5/h)
- 系统盘: 30GB
- 数据盘: 50GB ⭐ 重要! 数据持久化

### 2. 连接实例
SSH或JupyterLab连接实例

### 3. 上传文件
上传 autodl_package.tar.gz 到 /root/

### 4. 解压并启动
```bash
cd /root
tar -xzf autodl_package.tar.gz
bash start_training.sh
```

### 5. 下载模型
训练完成后,下载:
- outputs/checkpoints/best_model.pth
- outputs/logs/ (训练日志)

## 推荐方案

方案2: VGG19激进训练
- 时间: 5小时
- 成本: ¥7.5
- mIoU: 66-70%

方案4: ResNet-101极致训练
- 时间: 15小时
- 成本: ¥22.5
- mIoU: 75-80% ⭐ 推荐

## 监控训练

```bash
# TensorBoard
tensorboard --logdir outputs/logs --port 6006

# 查看实时日志
tail -f outputs/logs/*.log
```

## 下载模型

```bash
# 方式1: JupyterLab下载 (右键 -> Download)
outputs/checkpoints/ultimate_*/best_model.pth

# 方式2: SCP下载
scp -P <端口> root@<IP>:/root/outputs/checkpoints/best_model.pth ./
```
EOF

echo "6. 打包文件..."
tar -czf autodl_package.tar.gz "$TEMP_DIR"

# 清理临时目录
rm -rf "$TEMP_DIR"

# 显示打包信息
echo ""
echo "=========================================="
echo "✓ 打包完成!"
echo "=========================================="
echo ""
echo "打包文件: autodl_package.tar.gz"
echo "文件大小:"
ls -lh autodl_package.tar.gz
echo ""
echo "包含内容:"
echo "  - 完整代码 (src/, scripts/)"
echo "  - 训练数据 (images/, masks/)"
echo "  - 启动脚本 (start_training.sh)"
echo "  - 训练说明 (README_AutoDL.md)"
echo ""
echo "上传位置: /root/autodl_package.tar.gz"
echo "解压命令: tar -xzf autodl_package.tar.gz"
echo "启动训练: bash start_training.sh"
echo ""
echo "=========================================="
