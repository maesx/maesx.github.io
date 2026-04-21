# 模型评估结果报告

## 一、测试集最终结果（论文使用）

### 1.1 整体性能指标

| 指标 | 测试集结果 | 验证集结果 |
|------|-----------|-----------|
| **mIoU (排除背景)** | **57.96%** | 56.12% |
| **Pixel Accuracy** | **92.53%** | 92.01% |
| **Precision** | **65.38%** | 64.02% |
| **Recall** | **85.96%** | 85.83% |
| **F1-Score** | **62.56%** | 60.67% |
| **样本数量** | 1,000 | 1,000 |

### 1.2 各类别详细指标

#### 测试集结果

| 类别 | IoU | Precision | Recall | F1-Score |
|------|-----|-----------|--------|----------|
| Background | 92.36% | 98.52% | 93.64% | 95.88% |
| Car | 52.23% | 55.07% | 92.00% | 64.83% |
| Truck | 36.25% | 45.66% | 76.78% | 37.45% |
| Bus | 85.40% | 95.40% | 89.10% | 85.41% |

#### 验证集结果

| 类别 | IoU | Precision | Recall | F1-Score |
|------|-----|-----------|--------|----------|
| Background | 91.93% | 98.57% | 93.13% | 95.63% |
| Car | 51.44% | 54.31% | 91.85% | 64.01% |
| Truck | 33.79% | 42.33% | 78.73% | 34.88% |
| Bus | 83.12% | 95.42% | 86.92% | 83.13% |

---

## 二、模型配置信息

### 2.1 模型架构

| 配置项 | 值 |
|--------|-----|
| **模型名称** | U-Net++ (Nested U-Net) |
| **编码器** | VGG19 (ImageNet预训练) |
| **深度监督** | 开启 (4层输出) |
| **输入尺寸** | 512 × 512 |
| **输出类别** | 4 类 (Background, Car, Truck, Bus) |
| **总参数量** | ~36M |

### 2.2 类别定义与权重

| 类别 ID | 类别名称 | 类别权重 | 说明 |
|---------|----------|----------|------|
| 0 | Background | 0.05 | 大量样本，低权重 |
| 1 | Car | 1.0 | 基准权重 |
| 2 | Truck | 2.5 | 较少样本，高权重 |
| 3 | Bus | 4.0 | 最少样本，最高权重 |

---

## 三、数据集信息

### 3.1 数据集划分

| 划分 | 数量 | 比例 |
|------|------|------|
| 训练集 | 8,000 | 80% |
| 验证集 | 1,000 | 10% |
| 测试集 | 1,000 | 10% |
| **总计** | **10,000** | 100% |

### 3.2 数据集路径

```
road_vehicle_pedestrian_det_datasets/
├── images/
│   ├── train/    # 8000 张训练图像
│   ├── val/      # 1000 张验证图像
│   └── test/     # 1000 张测试图像
└── annotations/  # COCO格式标注

outputs/masks_car/
├── train/        # 8000 张训练掩码
├── val/          # 1000 张验证掩码
└── test/         # 1000 张测试掩码
```

---

## 四、训练配置

### 4.1 训练参数

```bash
python3 src/training/train.py \
    --use_gpu True \
    --subset_ratio 1.0 \
    --epochs 50 \
    --batch_size 8 \
    --lr 1e-4 \
    --weight_decay 1e-5 \
    --grad_clip 1.0 \
    --save_interval 10 \
    --early_stopping_patience 10 \
    --num_workers 4 \
    --model_name car-best_model
```

### 4.2 关键参数说明

| 参数 | 值 | 说明 |
|------|-----|------|
| `epochs` | 50 | 最大训练轮数 |
| `batch_size` | 8 | 批次大小 |
| `lr` | 1e-4 | 初始学习率 |
| `weight_decay` | 1e-5 | 权重衰减 |
| `grad_clip` | 1.0 | 梯度裁剪阈值 |
| `early_stopping_patience` | 10 | 早停耐心值 |

### 4.3 损失函数

```python
L_total = λ_ce · L_CE + λ_dice · L_Dice

其中:
- λ_ce = 1.0 (CrossEntropy权重)
- λ_dice = 2.0 (Dice权重)
```

深度监督损失权重：`[0.5, 0.75, 1.0, 1.25]`（浅层到深层）

---

## 五、结果分析

### 5.1 模型优势

1. **背景分离效果好**：Background IoU > 92%，说明模型能够准确区分前景和背景

2. **公交车辆检测优秀**：Bus IoU = 85.40%，Precision 高达 95.40%

3. **高召回率**：整体 Recall 达到 85.96%，模型对目标的检测覆盖较好

### 5.2 待改进方向

1. **小目标检测困难**：Truck IoU 仅为 36.25%，可能是由于卡车样本数量较少

2. **精确度偏低**：整体 Precision 65.38%，存在一定的过预测现象

3. **类别不平衡影响**：Car 虽然样本多但 Precison 仅 55%，可能需要调整类别权重

### 5.3 可能的优化方向

1. 增加小目标类别的数据增强
2. 调整类别权重或使用 Focal Loss
3. 增加后处理（如 CRF）优化边界
4. 尝试其他编码器（如 ResNet-50/101）

---

## 六、评估命令

### 在测试集上评估

```bash
python scripts/evaluate.py \
    --model_path outputs/checkpoints/car-best_model.pth \
    --data_dir road_vehicle_pedestrian_det_datasets \
    --masks_dir outputs/masks_car \
    --split test \
    --batch_size 8 \
    --device mps \
    --output outputs/test_results.json
```

### 在验证集上评估

```bash
python scripts/evaluate.py \
    --model_path outputs/checkpoints/car-best_model.pth \
    --split val \
    --output outputs/val_results.json
```

---

## 七、文件结构

```
outputs/
├── checkpoints/
│   ├── car-best_model.pth          # 最佳模型权重
│   └── training_resume_config.json # 训练恢复配置
├── test_results.json               # 测试集评估结果
└── val_results.json                # 验证集评估结果
```

---

*评估时间: 2026-04-21*  
*模型版本: U-Net++ with VGG19 encoder*  
*评估设备: Apple Silicon MPS*
