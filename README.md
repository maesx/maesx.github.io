# 道路车辆分割系统 - U-Net++

## 项目概述

基于U-Net++架构的道路车辆语义分割系统，支持 Web 可视化平台，跨平台部署（Windows、macOS、Linux）。

### 主要特性

- ✅ **U-Net++架构**: 采用Nested U-Net结构，具有更好的特征融合能力
- ✅ **深度监督**: 使用深度监督策略加速收敛，提升性能
- ✅ **Web可视化**: 提供直观的Web界面进行图像分割和结果可视化
- ✅ **跨平台支持**: 支持 Windows、macOS、Linux 部署
- ✅ **GPU加速**: 支持 NVIDIA GPU (CUDA) 和 Apple Silicon (MPS)
- ✅ **数据增强**: 丰富的数据增强策略(翻转、旋转、缩放、弹性形变等)
- ✅ **组合损失**: 结合CrossEntropy和Dice损失，提升分割精度
- ✅ **目标IoU**: 训练目标IoU≥80%

## 快速开始

### 方式一：Web可视化平台（推荐）

#### Windows
```cmd
# 双击运行
start_windows.bat

# 或命令行运行
python start_server.py
```

#### macOS / Linux
```bash
# 一键启动
python3 start_server.py

# 或使用脚本
./restart_services.sh
```

访问：http://localhost:3000

详细说明请查看 [SCRIPTS.md](SCRIPTS.md)

#### 方式二：命令行工具

训练和推理使用传统的命令行方式，详见下文。

## 系统要求

### 硬件要求

| 组件 | 最低配置 | 推荐配置 |
|------|----------|----------|
| CPU | 4核心 | 8核心+ |
| 内存 | 8GB | 16GB+ |
| 硬盘 | 5GB | 10GB SSD |
| 显卡 | 无要求 | NVIDIA GPU / Apple Silicon |

### 软件要求

- Python 3.8+
- Node.js 16+
- CUDA Toolkit（可选，用于 NVIDIA GPU）

详细要求请查看 [REQUIREMENTS.md](REQUIREMENTS.md)

## 项目结构

```
maesx.github.io/
├── README.md                  # 项目入口文档
├── REQUIREMENTS.md            # 系统要求说明
├── SCRIPTS.md                 # 启动脚本说明
├── requirements.txt           # Python 依赖
├── start_server.py            # 统一启动脚本（跨平台）
├── start_windows.bat          # Windows 启动脚本
├── restart_services.sh        # macOS/Linux 启动脚本
├── train.py                   # 训练入口脚本
├── inference.py               # 推理入口脚本
├── configs/                   # 配置文件
│   └── config.py
├── docs/                      # 文档目录
│   ├── INFERENCE_GUIDE.md
│   ├── INSTANCE_SEGMENTATION_GUIDE.md
│   ├── COLOR_SCHEME_GUIDE.md
│   ├── UNETPP_SEGMENTATION_PROMPT.md
│   └── optimization_expert_report.md
├── scripts/                   # 辅助脚本
│   ├── README.md
│   ├── quick_train.sh
│   └── train_and_infer.sh
├── tests/                     # 测试文件
│   ├── test_model.py
│   └── test_system.py
├── src/                       # 源代码
│   ├── data/                  # 数据处理
│   │   ├── dataset.py         # 数据加载和增强
│   │   └── yolo_to_mask.py    # YOLO标注转换
│   ├── models/                # 模型架构
│   │   └── unet_plusplus.py   # U-Net++模型
│   ├── utils/                 # 工具函数
│   │   └── losses.py          # 损失函数和评估指标
│   ├── inference/             # 推理模块
│   │   ├── inference.py
│   │   ├── inference_enhanced.py
│   │   └── inference_instance.py
│   ├── training/              # 训练模块
│   │   └── train.py
│   └── web/                   # Web可视化平台
│       ├── backend/           # Flask后端
│       │   ├── app.py
│       │   ├── config.py
│       │   └── routes/
│       └── frontend/          # Vue前端
│           ├── src/
│           ├── vite.config.js
│           └── package.json
├── outputs/                   # 输出目录
│   ├── masks/                 # 转换后的分割掩码
│   ├── checkpoints/           # 模型检查点
│   ├── logs/                  # TensorBoard日志
│   ├── visualizations/        # 可视化结果
│   ├── uploads/               # 上传的图像
│   └── results/               # 分割结果
└── road_vehicle_pedestrian_det_datasets/  # 数据集
    ├── images/
    ├── labels/
    └── classes.txt
```

## 环境配置

### 1. 安装依赖

#### Python 依赖

```bash
# macOS / Linux
pip install -r requirements.txt

# Windows
python -m pip install -r requirements.txt
```

#### CUDA 支持（可选，NVIDIA GPU）

```bash
# 安装支持 CUDA 的 PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

#### Node.js 依赖（Web平台）

```bash
cd src/web/frontend
npm install
```

### 2. 数据准备

数据集已经包含在`road_vehicle_pedestrian_det_datasets/`目录下。

## 使用流程

### 第1步: 转换标注格式

将YOLO格式的边界框标注转换为语义分割掩码:

```bash
python src/data/yolo_to_mask.py \
    --data_dir road_vehicle_pedestrian_det_datasets \
    --output_dir outputs/masks \
    --classes car truck bus
```

这将创建分割掩码,每个车辆类别用不同的像素值表示:
- 背景: 0 (黑色)
- Car: 1
- Truck: 2
- Bus: 3

### 第2步: 训练模型

#### CPU训练 (默认)

```bash
python train.py \
    --data_dir road_vehicle_pedestrian_det_datasets \
    --masks_dir outputs/masks \
    --batch_size 4 \
    --epochs 50 \
    --use_gpu False
```

#### GPU训练

```bash
python train.py \
    --data_dir road_vehicle_pedestrian_det_datasets \
    --masks_dir outputs/masks \
    --batch_size 16 \
    --epochs 100 \
    --use_gpu True
```

**训练参数说明:**
- `--batch_size`: 批次大小 (CPU建议4, GPU建议16)
- `--epochs`: 训练轮数
- `--lr`: 学习率 (默认1e-4)
- `--img_size`: 输入图像尺寸 (默认512x512)
- `--num_workers`: 数据加载进程数 (CPU设为0)
- `--deep_supervision`: 是否使用深度监督 (默认True)

### 第3步: 监控训练

使用TensorBoard监控训练过程:

```bash
tensorboard --logdir outputs/logs
```

然后在浏览器中打开 `http://localhost:6006`

### 第4步: 推理预测

#### 单张图像预测

```bash
python inference.py \
    --model_path outputs/checkpoints/best_model.pth \
    --image_path path/to/image.jpg \
    --output_dir outputs/visualizations
```

#### 批量预测

```bash
python inference.py \
    --model_path outputs/checkpoints/best_model.pth \
    --images_dir road_vehicle_pedestrian_det_datasets/images/test \
    --output_dir outputs/visualizations
```

## 分割类别和颜色

系统分割以下3类车辆+背景:

| 类别 | 颜色 | 说明 |
|------|------|------|
| 背景 | 黑色 | 非车辆区域 |
| Car | 红色 | 小轿车 |
| Truck | 绿色 | 卡车 |
| Bus | 蓝色 | 公交车 |

## 性能指标

模型训练过程中会计算以下指标:
- **IoU (Intersection over Union)**: 交并比,目标≥80%
- **Pixel Accuracy**: 像素准确率
- **Dice Coefficient**: Dice系数

## 数据增强策略

训练集使用以下数据增强:
1. **几何变换**: 水平翻转、垂直翻转、随机旋转90°
2. **尺度变换**: 随机缩放(±20%)、随机裁剪
3. **颜色变换**: 亮度/对比度调整
4. **噪声和模糊**: 高斯模糊、高斯噪声
5. **弹性形变**: ElasticTransform、GridDistortion

## 注意事项

### CPU vs GPU训练

- **CPU训练**: 
  - 优点: 无需GPU,任何机器都可运行
  - 缺点: 训练速度慢,建议减小batch_size和epochs
  - 推荐: `batch_size=4, epochs=50`

- **GPU训练**:
  - 优点: 训练速度快,可以使用更大的batch_size
  - 缺点: 需要NVIDIA GPU和CUDA环境
  - 推荐: `batch_size=16, epochs=100`

### 标注转换说明

由于原始数据集使用YOLO格式的边界框标注,转换为分割掩码时:
- 边界框内部区域被填充为对应类别
- 这是一种近似转换,可能不如真实的像素级标注精确
- 如果有条件,建议使用真实的像素级分割标注

### 提升IoU的方法

如果训练后IoU未达到80%,可以尝试:
1. 增加训练轮数
2. 使用更大的batch_size
3. 调整学习率
4. 使用更强的数据增强
5. 尝试其他backbone(如ResNet50)
6. 使用真实的像素级分割标注

## 项目作者

Created by 友久 (suxiang.su)

## 许可证

MIT License
