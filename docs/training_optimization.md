# 训练优化方案文档

## 概述

本文档记录了对道路车辆语义分割项目进行的训练优化措施，旨在提升训练速度和训练效果。

**优化日期**: 2026-04-03  
**优化目标**: 
- 提升训练速度 30-50%
- 改善前景小目标分割效果
- 提高训练稳定性

---

## 优化内容

### 1. 混合精度训练 (AMP)

#### 功能说明
使用 `torch.cuda.amp` 实现自动混合精度训练，同时使用 FP16 和 FP32 进行计算。

#### 技术实现
- **前向传播**: 使用 FP16 加速计算
- **损失缩放**: 使用 `GradScaler` 避免梯度下溢
- **反向传播**: 使用 FP16
- **权重更新**: 使用 FP32 保持精度

#### 代码位置
- `src/training/train.py`: 第 303-318 行（训练阶段）
- `src/training/train.py`: 第 395-401 行（验证阶段）

#### 配置参数
```bash
--use_amp True    # 启用混合精度训练（默认: True）
```

#### 支持设备
- NVIDIA CUDA GPU (推荐 V100, RTX 20/30/40 系列)
- Apple M 系列 GPU (MPS)

#### 预期收益
| 指标 | 改进 |
|------|------|
| 训练速度 | 提升 30-50% |
| 显存占用 | 减少 30-50% |
| 模型精度 | 几乎无影响 |

---

### 2. 类别权重

#### 功能说明
根据数据集中各类别的像素分布自动计算权重，解决类别不平衡问题。

#### 技术实现
使用 inverse frequency 方法计算权重：

```
权重 = 总像素数 / (类别数 × 该类别像素数)
```

#### 代码位置
- `src/data/dataset.py`: `calculate_class_weights()` 函数（第 339-384 行）
- `src/utils/losses.py`: `CombinedLoss` 类（第 45-76 行）

#### 配置参数
```bash
--use_class_weights True    # 启用类别权重（默认: True）
```

#### 输出示例
```
正在计算类别权重，扫描 1000 张掩码...

类别像素分布:
  类别 0: 50,000,000 像素 (85.00%), 权重: 0.2941
  类别 1: 5,000,000 像素 (8.50%), 权重: 1.1765
  类别 2: 3,000,000 像素 (5.10%), 权重: 1.5686
  类别 3: 1,000,000 像素 (1.70%), 权重: 2.9412
```

#### 预期收益
| 指标 | 改进 |
|------|------|
| 前景 IoU | 提升 1-2% |
| 小目标检测 | 显著改善 |

---

### 3. LRU 数据缓存

#### 功能说明
使用 LRU (Least Recently Used) 缓存机制存储预处理后的图像和掩码，减少重复 IO 开销。

#### 技术实现
- 缓存原始图像和掩码数据（变换前）
- 当缓存达到上限时，自动淘汰最久未使用的数据
- 基于 `collections.OrderedDict` 实现

#### 代码位置
- `src/data/dataset.py`: `LRUCache` 类（第 18-59 行）
- `src/data/dataset.py`: `RoadVehicleDataset.__getitem__()` 方法（第 115-161 行）

#### 配置参数
```bash
--use_cache True      # 启用缓存（默认: True）
--cache_size 1000     # 缓存最大容量（默认: 1000）
```

#### 工作流程
```
┌─────────────────────────────────────────────────────┐
│                    获取数据                           │
└─────────────────────────────────────────────────────┘
                        │
                        ▼
              ┌─────────────────┐
              │  缓存中是否存在？  │
              └─────────────────┘
              │               │
         存在 │               │ 不存在
              ▼               ▼
      ┌───────────┐   ┌───────────────┐
      │ 从缓存获取 │   │  从磁盘读取    │
      └───────────┘   └───────────────┘
              │               │
              │               ▼
              │       ┌───────────────┐
              │       │ 存入缓存       │
              │       └───────────────┘
              │               │
              └───────┬───────┘
                      ▼
              ┌───────────────┐
              │ 应用数据增强   │
              └───────────────┘
                      │
                      ▼
              ┌───────────────┐
              │ 返回 Tensor   │
              └───────────────┘
```

#### 预期收益
| 指标 | 改进 |
|------|------|
| 数据加载时间 | 减少 20-40% |
| 内存占用 | 根据缓存大小增加 |

---

### 4. DataLoader 优化

#### 功能说明
优化 DataLoader 参数，提高数据预取效率。

#### 技术实现
```python
DataLoader(
    dataset=dataset,
    batch_size=batch_size,
    shuffle=shuffle,
    num_workers=num_workers,
    pin_memory=pin_memory,
    prefetch_factor=2,          # 新增：每个worker预取2个批次
    persistent_workers=True     # 新增：保持worker进程活跃
)
```

#### 配置参数
```bash
--num_workers 4    # 数据加载进程数（默认: 4）
```

#### 参数说明
| 参数 | 说明 |
|------|------|
| `prefetch_factor=2` | 每个 worker 预取的批次数，提高 GPU 利用率 |
| `persistent_workers=True` | 保持 worker 进程在整个训练期间活跃，减少重启开销 |

#### 注意事项
- `prefetch_factor` 和 `persistent_workers` 仅在 `num_workers > 0` 时生效
- 建议根据 CPU 核心数调整 `num_workers`

---

### 5. 梯度裁剪

#### 功能说明
限制梯度范数，防止梯度爆炸，提高训练稳定性。

#### 技术实现
```python
# AMP 模式下
self.scaler.unscale_(self.optimizer)
torch.nn.utils.clip_grad_norm_(self.model.parameters(), self.grad_clip_norm)

# 普通模式下
torch.nn.utils.clip_grad_norm_(self.model.parameters(), self.grad_clip_norm)
```

#### 代码位置
- `src/training/train.py`: 第 313-315 行（AMP 模式）
- `src/training/train.py`: 第 328-329 行（普通模式）

#### 配置参数
```bash
--grad_clip_norm 1.0    # 梯度裁剪最大范数（默认: 1.0，设为 0 禁用）
```

#### 预期收益
| 指标 | 改进 |
|------|------|
| 训练稳定性 | 显著提升 |
| 梯度爆炸 | 有效防止 |

---

## 命令行参数汇总

### 新增参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `--use_amp` | bool | True | 是否使用混合精度训练 |
| `--grad_clip_norm` | float | 1.0 | 梯度裁剪最大范数，0 表示禁用 |
| `--use_class_weights` | bool | True | 是否使用类别权重 |
| `--use_cache` | bool | True | 是否使用 LRU 缓存 |
| `--cache_size` | int | 1000 | 缓存最大容量 |

### 使用示例

```bash
# 使用 GPU 训练，启用所有优化（默认配置）
python train.py --use_gpu True

# 自定义配置示例
python train.py \
    --use_gpu True \
    --batch_size 16 \
    --epochs 50 \
    --lr 1e-4 \
    --use_amp True \
    --grad_clip_norm 1.0 \
    --use_class_weights True \
    --use_cache True \
    --cache_size 2000

# 禁用特定优化
python train.py \
    --use_gpu True \
    --use_amp False \
    --use_class_weights False

# 使用 CPU 训练（AMP 将自动禁用）
python train.py \
    --use_gpu False \
    --batch_size 4 \
    --num_workers 0
```

---

## 修改文件清单

| 文件 | 修改内容 |
|------|----------|
| `src/utils/losses.py` | `CombinedLoss` 添加 `class_weights` 参数 |
| `src/data/dataset.py` | 新增 `LRUCache` 类、`calculate_class_weights()` 函数，优化 `get_dataloader()` |
| `src/training/train.py` | 添加 AMP 支持、梯度裁剪、类别权重集成、新增命令行参数 |

---

## 预期整体收益

| 优化项 | 训练速度 | 内存/显存 | 模型效果 |
|--------|----------|-----------|----------|
| 混合精度训练 | +30-50% | -30-50% | 无影响 |
| 类别权重 | - | 略增 | +1-2% IoU |
| LRU 缓存 | +10-20% | +内存 | 无影响 |
| DataLoader 优化 | +5-10% | 无影响 | 无影响 |
| 梯度裁剪 | 无影响 | 无影响 | 稳定性提升 |

---

## 注意事项

1. **混合精度训练**
   - 仅支持 CUDA 和 MPS 设备
   - CPU 训练时自动禁用
   - 部分旧 GPU 可能不支持

2. **类别权重**
   - 首次运行时需要扫描训练集掩码，可能需要额外时间
   - 如数据分布变化，建议重新计算

3. **LRU 缓存**
   - 缓存会增加内存占用
   - 建议根据可用内存调整 `cache_size`
   - 训练集较小时可考虑增大缓存

4. **梯度裁剪**
   - 裁剪值过小可能影响收敛速度
   - 建议从 1.0 开始调整

---

## 测试验证

建议运行以下测试确保优化正确：

```bash
# 1. 快速功能测试（使用小数据子集）
python train.py --use_gpu True --subset_ratio 0.05 --epochs 2

# 2. 完整训练测试
python train.py --use_gpu True --subset_ratio 0.2 --epochs 10
```

---

## 参考资料

- [PyTorch AMP 文档](https://pytorch.org/docs/stable/amp.html)
- [PyTorch 梯度裁剪](https://pytorch.org/docs/stable/generated/torch.nn.utils.clip_grad_norm_.html)
- [PyTorch DataLoader 优化](https://pytorch.org/docs/stable/data.html)
