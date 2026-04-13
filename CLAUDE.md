# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

基于 U-Net++ 架构的道路车辆语义分割系统，从道路场景图像中精确分割 car、truck、bus 三类车辆。支持 Web 可视化平台。

## 项目结构

```
maesx.github.io/
├── train.py                   # 训练入口脚本（代理）
├── inference.py               # 推理入口脚本（代理）
├── start_server.py            # Web平台统一启动脚本（跨平台）
├── configs/                   # 配置文件
│   └── config.py
├── src/
│   ├── data/                  # 数据处理模块
│   ├── models/                # 模型架构 (U-Net++)
│   ├── utils/                 # 损失函数和评估指标
│   ├── inference/             # 推理模块
│   ├── training/              # 训练模块
│   └── web/                   # Web可视化平台
│       ├── backend/           # Flask后端 (API端口5000)
│       └── frontend/          # Vue3前端 (开发端口3000)
├── tests/                     # 测试文件
├── outputs/                   # 输出目录
│   ├── checkpoints/           # 模型检查点
│   ├── uploads/               # Web上传的图像
│   └── results/               # 分割结果
└── road_vehicle_pedestrian_det_datasets/  # 数据集
```

## 常用命令

### 环境安装
```bash
pip install -r requirements.txt
```

### 数据预处理（YOLO标注转分割掩码）
```bash
python src/data/yolo_to_mask.py \
    --data_dir road_vehicle_pedestrian_det_datasets \
    --output_dir outputs/masks \
    --classes car truck bus
```

### 训练
```bash
# CPU训练
python train.py --batch_size 4 --epochs 50 --use_gpu False

# GPU训练
python train.py --batch_size 16 --epochs 100 --use_gpu True

# 使用数据子集快速验证（推荐用于调试）
python train.py --subset_ratio 0.1 --epochs 10

# 恢复训练
python train.py --resume outputs/checkpoints/best_model.pth

# Apple M系列芯片
python train.py --device mps
```

### 推理
```bash
# 验证集推理
python inference.py --split val --num_samples 20

# 单张图像推理
python inference.py --image_path path/to/image.jpg --output_dir outputs/visualizations

# 增强推理（多种颜色方案）
python src/inference/inference_enhanced.py --color_scheme bright

# 实例分割推理
python src/inference/inference_instance.py --split val --num_samples 20 --device mps
```

### 测试
```bash
# 系统测试
python tests/test_system.py

# 模型测试
python tests/test_model.py --split val
```

### 训练监控
```bash
tensorboard --logdir outputs/logs
```

### Web平台
```bash
# 统一启动（自动安装依赖）
python start_server.py

# Windows
start_windows.bat

# macOS/Linux
./restart_services.sh

# 访问地址
# 前端: http://localhost:3000
# 后端API: http://localhost:5000
```

## 核心设计

### 配置结构
- `DATA_CONFIG`: 数据路径、类别定义（4类：背景+car+truck+bus）
- `MODEL_CONFIG`: 编码器(vgg19)、预训练、深度监督
- `TRAIN_CONFIG_CPU/GPU`: 批次大小、学习率、图像尺寸等
- `CLASS_COLORS`: BGR格式颜色映射

### 模型特性
- **U-Net++**: 嵌套跳跃连接，缓解语义差距
- **深度监督**: 多尺度输出加速收敛
- **编码器**: VGG19/VGG19-BN (ImageNet预训练)

### 损失函数
- `CombinedLoss`: CrossEntropyLoss + DiceLoss 组合
- `DeepSupervisionLoss`: 包装器，处理多尺度输出

### 数据增强（albumentations）
- 训练集: 翻转、旋转、缩放、亮度对比度、高斯模糊/噪声、弹性形变
- 验证/测试集: 仅Resize + Normalize

### 设备支持
- CPU / CUDA GPU / Apple M系列 (MPS)

### Web平台架构
- **后端**: Flask + Flask-RESTful + Flask-CORS
- **前端**: Vue 3 + Vite + Element Plus + ECharts
- **API端点**:
  - `/api/models` - 模型管理
  - `/api/segment` - 图像分割
  - `/api/segment/batch` - 批量分割
  - `/api/augmentation/preview` - 数据增强预览
  - `/api/gpu/status` - GPU状态监控

## 分割类别

| 类别ID | 名称 | 颜色(BGR) |
|--------|------|-----------|
| 0 | 背景 | [0,0,0] 黑色 |
| 1 | car | [0,0,255] 红色 |
| 2 | truck | [0,255,0] 绿色 |
| 3 | bus | [255,0,0] 蓝色 |

## 关键文件

| 用途 | 文件 |
|------|------|
| 训练入口 | `train.py` → `src/training/train.py` |
| 推理入口 | `inference.py` → `src/inference/inference.py` |
| Web启动 | `start_server.py` |
| 配置中心 | `configs/config.py` |
| 模型定义 | `src/models/unet_plusplus.py` |
| Web后端 | `src/web/backend/app.py` |
| Web前端 | `src/web/frontend/src/App.vue` |

## 文档参考

- `README.md` - 完整使用流程
- `docs/INFERENCE_GUIDE.md` - 推理可视化指南
- `docs/INSTANCE_SEGMENTATION_GUIDE.md` - 实例分割功能
- `scripts/README.md` - 辅助脚本说明