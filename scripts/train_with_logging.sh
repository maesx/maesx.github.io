#!/bin/bash
# AutoDL训练脚本 - 包含完整日志保存
# 支持自动打包模型和日志供下载

# 切换到项目根目录
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

echo "=========================================="
echo "U-Net++ 极致优化训练 - AutoDL云GPU版本"
echo "=========================================="
echo ""

# 创建日志目录
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_DIR="outputs/logs/ultimate_${TIMESTAMP}"
MODEL_DIR="outputs/checkpoints/ultimate_${TIMESTAMP}"
TENSORBOARD_DIR="outputs/tensorboard/ultimate_${TIMESTAMP}"

mkdir -p "$LOG_DIR"
mkdir -p "$MODEL_DIR"
mkdir -p "$TENSORBOARD_DIR"

echo "📁 创建输出目录:"
echo "   日志目录: $LOG_DIR"
echo "   模型目录: $MODEL_DIR"
echo "   TensorBoard目录: $TENSORBOARD_DIR"
echo ""

# 配置训练参数
TRAINING_CONFIG="
训练配置:
- 模型: UNetPlusPlusUltimate (ResNet-101 + FPN + CBAM + ASPP + 边界优化)
- 编码器: ResNet-101 (ImageNet预训练)
- 数据集: road_vehicle_pedestrian_det_datasets (8000张训练, 1000张验证)
- 训练轮数: 120
- 批次大小: 6
- 学习率: 0.0001
- 优化器: AdamW
- 损失函数: Dice + BCE + 边界损失
- 混合精度: 启用 (FP16)
- 硬件加速: GPU (CUDA)
"

echo "$TRAINING_CONFIG" | tee "$LOG_DIR/training_config.txt"
echo ""

# 开始训练
echo "🚀 开始训练..."
echo ""

python src/training/train_ultimate.py \
    --use_gpu True \
    --use_fpn True \
    --attention cbam_aspp \
    --use_boundary_refinement True \
    --use_separable_conv True \
    --use_aggressive_weights True \
    --epochs 120 \
    --batch_size 6 \
    --lr 1e-4 \
    --save_dir "$MODEL_DIR" \
    --log_dir "$LOG_DIR" \
    --tensorboard_dir "$TENSORBOARD_DIR" \
    2>&1 | tee "$LOG_DIR/training.log"

# 训练完成
echo ""
echo "=========================================="
echo "✅ 训练完成!"
echo "=========================================="
echo ""

# 显示训练结果
echo "📊 训练结果:"
if [ -f "$MODEL_DIR/best_model.pth" ]; then
    echo "   ✅ 最佳模型: $MODEL_DIR/best_model.pth"
    ls -lh "$MODEL_DIR/best_model.pth"
fi

echo ""
echo "📄 训练日志:"
ls -lh "$LOG_DIR/"
echo ""

echo "📈 TensorBoard日志:"
ls -lh "$TENSORBOARD_DIR/"
echo ""

# 创建下载包
echo "📦 创建下载包..."
DOWNLOAD_PACKAGE="training_results_${TIMESTAMP}.tar.gz"

# 打包模型、日志和TensorBoard文件
tar -czf "$DOWNLOAD_PACKAGE" \
    "$MODEL_DIR" \
    "$LOG_DIR" \
    "$TENSORBOARD_DIR"

echo ""
echo "✅ 下载包已创建: $DOWNLOAD_PACKAGE"
ls -lh "$DOWNLOAD_PACKAGE"
echo ""

# 显示下载命令
echo "=========================================="
echo "📥 下载训练结果"
echo "=========================================="
echo ""
echo "方式1: SCP下载 (推荐)"
echo "--------------------------------------"
echo "# 在本地终端执行 (不是SSH会话):"
echo "scp -P <端口> root@<IP>:/root/${DOWNLOAD_PACKAGE} ./"
echo ""
echo "方式2: JupyterLab下载"
echo "--------------------------------------"
echo "1. 打开JupyterLab"
echo "2. 导航到文件: ${DOWNLOAD_PACKAGE}"
echo "3. 右键 -> Download"
echo ""
echo "方式3: 分开下载 (如果网络不稳定)"
echo "--------------------------------------"
echo "# 下载模型"
echo "scp -P <端口> root@<IP>:/root/${MODEL_DIR}/best_model.pth ./"
echo ""
echo "# 下载日志"
echo "scp -P <端口> root@<IP>:/root/${LOG_DIR}/training.log ./"
echo ""
echo "# 下载TensorBoard"
echo "scp -r -P <端口> root@<IP>:/root/${TENSORBOARD_DIR} ./"
echo ""

# 创建下载说明文件
cat > "DOWNLOAD_INSTRUCTIONS_${TIMESTAMP}.txt" << EOF
========================================
训练结果下载指南
========================================

生成时间: $(date)
训练批次: ${TIMESTAMP}

文件位置:
- 训练结果包: ${DOWNLOAD_PACKAGE}
- 最佳模型: ${MODEL_DIR}/best_model.pth
- 训练日志: ${LOG_DIR}/training.log
- TensorBoard: ${TENSORBOARD_DIR}/

下载命令:
--------------------------------------
# 方式1: 下载完整结果包 (推荐)
scp -P <端口> root@<IP>:/root/${DOWNLOAD_PACKAGE} ./

# 方式2: 只下载模型 (最小文件)
scp -P <端口> root@<IP>:/root/${MODEL_DIR}/best_model.pth ./

# 方式3: 分别下载 (网络不稳定时)
# 下载模型
scp -P <端口> root@<IP>:/root/${MODEL_DIR}/best_model.pth ./

# 下载日志
scp -P <端口> root@<IP>:/root/${LOG_DIR}/training.log ./

# 下载TensorBoard
scp -r -P <端口> root@<IP>:/root/${TENSORBOARD_DIR} ./

查看日志:
--------------------------------------
# 查看训练日志
cat ${LOG_DIR}/training.log

# 查看训练配置
cat ${LOG_DIR}/training_config.txt

# 启动TensorBoard (本地)
tensorboard --logdir=${TENSORBOARD_DIR} --port 6006

TensorBoard使用:
--------------------------------------
1. 下载TensorBoard目录到本地
2. 运行: tensorboard --logdir=${TENSORBOARD_DIR} --port 6006
3. 浏览器访问: http://localhost:6006

模型使用:
--------------------------------------
# 加载模型
import torch
model = torch.load('${MODEL_DIR}/best_model.pth')
print(model['best_miou'])  # 查看最佳mIoU

数据持久化:
--------------------------------------
如果勾选了AutoDL数据盘,文件会保存在:
/root/autodl-tmp/

下次创建实例时会自动挂载,无需重新下载。
EOF

echo "📄 下载说明已保存: DOWNLOAD_INSTRUCTIONS_${TIMESTAMP}.txt"
echo ""
echo "=========================================="
echo "🎉 训练完成! 请按照上述说明下载结果"
echo "==========================================
